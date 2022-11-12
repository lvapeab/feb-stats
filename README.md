# [FEB Stats](http://35.209.155.221/)

Basketball stats parser and analyzer [→ Go to the website (in Spanish)](http://35.209.155.221/).

It takes game boxscores and analyzes them, 
computing simple and advanced statistics of players and teams. The stats are saved with XLS 
format. Refer to [the website](http://35.209.155.221) for examples and docs about the data extracted.

It currently supports boxscores from all [FEB (Federación Española de Baloncesto)](http://www.feb.es) categories. 
The boxscores are analyzed from the game stats pages (`.html`). 

***

### Run the python service in local

```shell script
poetry run gunicorn --umask 4 --bind 0.0.0.0:80 feb_stats.web.webapp:app
```

### Run linting and tests

```shell script
poetry run black . ; poetry run isort . ; poetry run mypy . ; poetry run flake8 .;
poetry run pytest tests ;
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

***

*Disclaimer: This is not a* Federación Española de Baloncesto *product nor has any relationship with it.*