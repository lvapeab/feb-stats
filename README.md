# [FEB Stats](http://35.209.155.221/)

Basketball stats parser and analyzer [→ Go to the website (in Spanish)](http://35.209.155.221/).


It takes game boxscores and analyzes them, 
computing simple and advanced statistics of players and teams. The stats are saved with XLS 
format.

It currently supports boxscores from all [FEB (Federación Española de Baloncesto)](http://www.feb.es) categories. 
The boxscores are analyzed from the game stats pages (`.html`). 

***

## Build and run app

Builds and tests are done with [Bazel](https://bazel.build/). There are two main services:

* A nodeJS service that builds the website to retrieve the data given by the user.
* A Python service that analyzes the data and returns the .xls file. 

Both services are connected via [gRPC](https://grpc.io/). 

These services are in Docker images managed by Bazel. 
There are also rules to directly run them in the local machine (without images). 

### Run the python service

```shell script
bazel run //python/service:image
```

### Run the NodeJS app

```shell script
bazel run //js/node:image
```

### Run tests

```shell script
bazel test //...
```

### Run using docker-compose

You can also run the app using [docker-compose](https://docs.docker.com/compose/compose-file): 

```shell script
docker-compose up
```

## TODO

This is an ongoing project that I code in my free time. I'm also using it to try out new things (tools, software, etc). 
Despite this, PRs are always welcome!

As a rough roadmap, some of the next steps to take are: 

- [x] Webapp.
    - [ ] Translate the website (at least to English). 
    - [ ] Improve the website (now it's somewhat clumsy). 
- [ ] Temporal data (evolution of teams/players).
- [ ] Automatically extract insights from the data.
- [ ] Link with a database.
- [ ] Query/crawl data from sources.
- [ ] Improve docker layering.
- [ ] Expose images from bazel.
- [ ] Streamline the image push and deployment workflow.
- [ ] Add support for another orchestrator (Kubernetes). Likely unnecessary given the expected traffic, but fun to do :) 