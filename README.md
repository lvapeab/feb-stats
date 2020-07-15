# feb-stats
Basketball stats parser and analyzer [→ Go to the website (in Spanish)](http://35.209.155.221/).


It takes game boxscores and analyzes them, 
computing simple and advanced statistics of players and teams. The stats are saved with XLS 
format.

It currently supports boxscores from all [FEB (Federación Española de Baloncesto)](http://www.feb.es) categories. 
The boxscores are analyzed from the game stats pages (`.html`). 

***

# Build and run app

Builds and tests are done with [Bazel](https://bazel.build/). There are two main services:

* A nodeJS service that builds the website to retrieve the data given by the user.
* A Python service that analyzes the data and returns the .xls file. 

Both services are connected via [gRPC](https://grpc.io/). 

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


In case you want to build your own images, you can tell Bazel to build and push them. You'll need to edit the 
`WORKSPACE` files, the rules `//python/service:push_feb-stats` and `//js/node:push_feb-stats_web` and the 
`docker-compose.yml` file, with your own paths. Next, you can run the app using 
[docker-compose](https://docs.docker.com/compose/compose-file): 


```shell script
bazel run //python/service:push_feb-stats; 
bazel run //js/node:push_feb-stats_web ; 
docker-compose up
```

# TODO:

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
- [ ] Streamline image push and deployment.

