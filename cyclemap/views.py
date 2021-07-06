"""Cyclemap views."""
import datetime
import time

import dateutil.parser
from quart import Blueprint, current_app, request, jsonify, render_template

from cyclemap.log import Log

blueprint = Blueprint('views', __name__)
logger = Log.get_logger(__name__)


@blueprint.route('/')
async def index():
    """Serves the main map view."""
    start_value = datetime.datetime(2017, 7, 1, 0, 0, 0, 0).isoformat()
    end_value = datetime.datetime.utcfromtimestamp(time.time()).isoformat()

    return await render_template('map.html', range_selector_start_value=start_value,
                                 range_selector_end_value=end_value)


@blueprint.route('/get_map_entries/<path:subpath>')
async def get_map_entries(subpath: str):
    """Backend service that returns posts tagged inside the map viewport that lie
    within a range of dates."""
    # Parse request URI
    if subpath[-1] == '/':
        subpath = subpath[:-1]  # remove trailing slash

    tokens = subpath.split('/')
    sw_lng, sw_lat = float(tokens[0]), float(tokens[1])
    ne_lng, ne_lat = float(tokens[2]), float(tokens[3])
    begin_datetime: datetime.datetime = dateutil.parser.isoparse(tokens[4])
    end_datetime: datetime.datetime = dateutil.parser.isoparse(tokens[5])

    logger.info("%s -> returning JSON for input: %f %f %f %f %s %s", request.path,
                sw_lng, sw_lat, ne_lng, ne_lat, begin_datetime, end_datetime)

    # Build the filter dict
    filt = {}
    filt['created_at'] = {
        '$gte': begin_datetime,
        '$lte': end_datetime
    }
    filt['location'] = {'$geoWithin': {'$box': [(sw_lng, sw_lat), (ne_lng, ne_lat)]}}

    # Use aggregate lookup API instead of find, as it provides more functionality:
    aggr_dicts = list()
    aggr_dicts.append({'$match': filt})

    # exclude _id field:
    aggr_dicts.append({'$project': {'_id': False}})

    map_entries = await current_app.posts_collection.aggregate(aggr_dicts).to_list(length=None)

    return jsonify(map_entries)
