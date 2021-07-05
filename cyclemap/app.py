"""Quart app global."""
from quart import Quart
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from cyclemap.views import blueprint
from cyclemap.mongodb import get_client, get_posts_collection

app = Quart(__name__)
app.register_blueprint(blueprint)


@app.before_serving
async def startup():
    """Add mongodb client objects to quart app object.
    This delays the mongodb client init until after the start of quart's event loop, ensuring mongodb and quart use the same event loop.
    See https://pgjones.gitlab.io/quart/how_to_guides/event_loop.html"""
    app.motor_client: AsyncIOMotorClient = get_client()
    app.posts_collection: AsyncIOMotorCollection = get_posts_collection()

if __name__ == "__main__":  # development server, supports autoreload
    app.run('0.0.0.0', debug=True, port=5000)
