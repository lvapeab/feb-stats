# feb-stats
Basketball stats parser.
 
# Build and run app
```
docker-compose up --build
```

# Run the python service

```shell script
bazel run //python/service:image
```

# Run the NodeJS app

```shell script
bazel run //js/node:app
```

# Run tests

```shell script
bazel test //...
```


# TODO:

- [x] Webapp (although now it's quite simple).
- [ ] Temporal data (evolution of teams/players).
- [ ] Link with a database.
- [ ] Query/crawl data from sources.
