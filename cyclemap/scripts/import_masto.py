#!/usr/bin/env python
"""Script that imports mastodon statuses into mongo db."""
import argparse
import asyncio
import re
from typing import Optional

import aiohttp
import dateutil.parser
from pymongo import GEOSPHERE, ASCENDING
from motor.motor_asyncio import AsyncIOMotorCollection

from cyclemap.log import Log
from cyclemap.mongodb import get_posts_collection

LOCATION_FIELD = "location"
logger = Log.get_logger(__name__)
posts_collection: AsyncIOMotorCollection = get_posts_collection()


async def crawl_statuses(url: str, limit: int = 40) -> None:
    """Crawl mastodon statuses for an account API link, url should
    be of https://mastodon.example/api/v1/accounts/:id/statuses"""
    params: dict = {}
    if limit is not None:
        params['limit'] = limit

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            statuses: dict = await resp.json()
            logger.info('Fetched %s, response status = %d, %d status items',
                        resp.url, resp.status, len(statuses))
            process_task = asyncio.create_task(process_statuses(statuses))

            next_url: Optional[str]
            if next_url := get_link_url(resp, "next"):
                await asyncio.create_task(crawl_statuses(next_url, None))

            await process_task


def get_link_url(resp: aiohttp.ClientResponse, rel_filter="next") -> Optional[str]:
    """Parse link response header and return either prev/next link depending on rel_filter"""
    if 'link' in resp.headers:
        link_entry: str
        for link_entry in resp.headers['link'].split(','):
            url: str
            rel: str
            url, rel = [i.strip() for i in link_entry.split(';')]

            if rel == 'rel="{}"'.format(rel_filter):
                return url[1:-1]

    return None


async def process_statuses(statuses: dict) -> None:
    """Insert statuses as posts into mongodb."""
    status_keys = ['id', 'created_at', 'url', 'content', 'media_attachments']
    for status in statuses:
        # only keep a number of fields:
        post = {k: status[k] for k in status_keys if status.get(k) is not None}

        post['account'] = {
            'display_name': status['account']['display_name'],
            'url': status['account']['url']}
        add_geo_json(post)
        convert_iso8601_dt_string(post, 'created_at')

        document = await posts_collection.find_one({'url': post['url']})
        if not document:
            await posts_collection.insert_one(post)
            logger.info('Inserted document into posts collection with id %s, url = %s',
                        post['id'], post['url'])


def add_geo_json(post) -> None:
    """Parse post text and add GeoJSON object named LOCATION_FIELD,
    latitude/longitude based on osm url in status text."""
    if 'content' not in post:
        return

    # Find osm.org url
    if re_match := re.search(r"(?P<url>https?://osm.org/[^\s]+)", post['content']):
        url = re_match.group("url")
        lat, lon = None, None
        if re_match := re.search(r"lat=(?P<lat>[-+]?\d+\.?\d*)", url):
            lat = re_match.group('lat')

        if re_match := re.search(r"lon=(?P<lon>[-+]?\d+\.?\d*)", url):
            lon = re_match.group('lon')

        if lat and lon:
            try:
                # from https://docs.mongodb.com/manual/geospatial-queries/#geospatial-data
                post[LOCATION_FIELD] = {'type': 'Point', 'coordinates': [float(lon), float(lat)]}
            except ValueError as ex:
                logger.error("Failed to parse latitude/longitude from url %s: exception: %s",
                             url, ex)


def convert_iso8601_dt_string(post: dict, key: str) -> None:
    """Try to parse post[field] as an ISO-8601 datetime string and replace
    it with a python datetime object"""
    if key not in post:
        return

    try:
        dt_obj = dateutil.parser.isoparse(post[key])
    except ValueError as ex:
        logger.error("Failed to parse %s as a valid ISO-8601 datetime string: %s", post[key], ex)
    else:
        post[key] = dt_obj


async def create_mongo_indexess():
    """Create indexes in mongodb."""
    await posts_collection.create_index([(LOCATION_FIELD, GEOSPHERE)])
    logger.info("Created geosphere index on `%s` field", LOCATION_FIELD)
    await posts_collection.create_index([('created_at', ASCENDING)])
    logger.info("Created ascending index on `created_at` field")


def run(api_url: str):
    """Run import_masto script."""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawl_statuses(api_url))
    loop.run_until_complete(create_mongo_indexess())


def cli():
    """Script CLI interface."""
    parser = argparse.ArgumentParser(description="Import mastodon statuses into mongodb")
    parser.add_argument("api_url", help="Mastodon statuses API url to import toots \
            from: https://mastodon.example/api/v1/accounts/:id/statuses")
    args = parser.parse_args()
    run(args.api_url)


if __name__ == '__main__':
    cli()
