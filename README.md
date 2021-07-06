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
