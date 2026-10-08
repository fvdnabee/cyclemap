#!/usr/bin/env python
"""Script that imports mastodon statuses into mongo db."""
import argparse
import asyncio
import datetime
import json
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
posts_collection: AsyncIOMotorCollection = None
STORE_JSON = None
STORE_MONGO = None


async def crawl_statuses(url: str, limit: int = 40) -> list[dict]:
    """Crawl mastodon statuses for an account API link, url should
    be of https://mastodon.example/api/v1/accounts/:id/statuses"""
    params: dict = {}
    if limit is not None:
        params['limit'] = limit

    all_posts = []
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            statuses: dict = await resp.json()
            logger.info('Fetched %s, response status = %d, %d status items',
                        resp.url, resp.status, len(statuses))
            process_task = asyncio.create_task(process_statuses(statuses))

            next_url: Optional[str]
            if next_url := get_link_url(resp, "next"):
                next_posts = await asyncio.create_task(crawl_statuses(next_url, limit))
                all_posts.extend(next_posts)

            posts = await process_task
            all_posts.extend(posts)

    return all_posts


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


async def process_statuses(statuses: dict) -> list[dict]:
    """Insert statuses as posts into mongodb."""
    status_keys = ['id', 'created_at', 'url', 'content', 'media_attachments']
    posts = []
    for status in statuses:
        # only keep a number of fields:
        post = {k: status[k] for k in status_keys if status.get(k) is not None}

        # post['account'] = {
        #     'display_name': status['account']['display_name'],
        #     'url': status['account']['url']}
        post['media_attachments'] = [
            {
                'preview_url': attachment['preview_url'],
                'meta': {'small': attachment['meta']['small']},
            }
            for attachment in post.get('media_attachments', [])
        ]

        add_geo_json(post)
        convert_iso8601_dt_string(post, 'created_at')
        posts.append(post)

        if STORE_MONGO:
            await store_mongo(post)

    return posts


async def store_mongo(post: dict):
    document = await posts_collection.find_one({'url': post['url']})
    if document:  # Skip post that exists already.
        return

    await posts_collection.insert_one(post)
    logger.info('Inserted document into posts collection with id %s, url = %s',
                post['id'], post['url'])


def add_geo_json(post) -> None:
    """Parse post text and add GeoJSON object named LOCATION_FIELD,
    latitude/longitude based on osm url in status text."""
    if 'content' not in post:
        return

    # Find osm.org url
    if re_match := re.search(r"(?P<url>https?://(www.)?osm.org/[^\s]+)", post['content']):
        url = re_match.group("url")
        lat, lon = None, None
        if re_match := re.search(r"lat=(?P<lat>[-+]?\d+\.?\d*)", url):
            lat = re_match.group('lat')

        if re_match := re.search(r"lon=(?P<lon>[-+]?\d+\.?\d*)", url):
            lon = re_match.group('lon')

        if lat and lon:
            try:
                # from https://docs.mongodb.com/manual/geospatial-queries/#geospatial-data
                post[LOCATION_FIELD] = {'type': 'Point',
                                        'coordinates': [float(lon), float(lat)]}
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
        logger.error(
            "Failed to parse %s as a valid ISO-8601 datetime string: %s", post[key], ex)
    else:
        post[key] = dt_obj


async def create_mongo_indexess():
    """Create indexes in mongodb."""
    await posts_collection.create_index([(LOCATION_FIELD, GEOSPHERE)])
    logger.info("Created geosphere index on `%s` field", LOCATION_FIELD)
    await posts_collection.create_index([('created_at', ASCENDING)])
    logger.info("Created ascending index on `created_at` field")


def serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError(
        f"Object of type {type(obj).__name__} is not JSON serializable")


def run(api_url: str):
    """Run import_masto script."""
    loop = asyncio.get_event_loop()
    posts = loop.run_until_complete(crawl_statuses(api_url))
    if STORE_JSON:
        with open('posts.json', 'w') as f:
            json.dump(posts, f, default=serializer)
    if STORE_MONGO:
        loop.run_until_complete(create_mongo_indexess())


def cli():
    """Script CLI interface."""
    global STORE_JSON, STORE_MONGO, posts_collection
    parser = argparse.ArgumentParser(
        description="Import mastodon statuses into mongodb")
    parser.add_argument(
        "--json", help="Store output in JSON file", action='store_true')
    parser.add_argument(
        "--mongo", help="Store output in MongoDB collection", action='store_true')
    parser.add_argument("api_url", help="Mastodon statuses API url to import toots \
            from: https://mastodon.example/api/v1/accounts/:id/statuses")
    args = parser.parse_args()
    STORE_JSON, STORE_MONGO = args.json, args.mongo
    if STORE_MONGO:
        posts_collection = get_posts_collection()

    run(args.api_url)


if __name__ == '__main__':
    cli()
