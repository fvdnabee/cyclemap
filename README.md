# Cyclemap
## Run development server
`QUART_ENV=development python cyclemap/app.py`

## Create python wheel
`make wheel`

## docker-compose dev server:
First, build the image:
`make build`

Bring up the services:
`docker-compose up`

## Import mastodon statuses
Run `import_masto` script in a running container, where `MONGODB_URI` is set
from docker-compose.yaml:
```
docker exec -it cyclemap_web_1 import_masto https://mastodon.example/api/v1/accounts/:id/statuses
```

Run `import_masto` script in a new container, where `MONGODB_URI` is set on
CLI (e.g. MongoDb Atlas):
```
docker-compose run  web /bin/bash
export MONGODB_URI="mongodb+srv://dbUser:<password>@cluster0.7vfqm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority
import_masto https://mastodon.example/api/v1/accounts/:id/statuses
```

## Empty posts collection:
```
 mongo "mongodb+srv://dbUser:<password>@cluster0.7vfqm.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
MongoDB shell version v4.4.6
connecting to: mongodb://xxx
Implicit session: session { "id" : UUID("f4994525-bfda-45a6-9b65-58dfd866962c") }
MongoDB server version: 4.4.6
MongoDB Enterprise atlas-karyn4-shard-0:PRIMARY> use cyclemap_db;
switched to db cyclemap_db
MongoDB Enterprise atlas-karyn4-shard-0:PRIMARY> show collections;
posts_collection
MongoDB Enterprise atlas-karyn4-shard-0:PRIMARY> db.posts_collection.remove({})
WriteResult({ "nRemoved" : 125 })
```
