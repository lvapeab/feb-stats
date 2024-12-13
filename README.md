# [FEB Stats](https://feb-stats-11741086955.europe-west9.run.app/)

Basketball stats parser and analyzer [→ Go to the website (in Spanish)](https://feb-stats-11741086955.europe-west9.run.app).

It takes game boxscores and analyzes them, 
computing simple and advanced statistics of players and teams. The stats are saved with XLS 
format. Refer to [the website](https://feb-stats-11741086955.europe-west9.run.app) for examples and docs about the data extracted.

It currently supports boxscores from all [FEB (Federación Española de Baloncesto)](http://www.feb.es) categories. 
The boxscores are analyzed from the game stats pages (`.html` or `htm`). 

***

### Run the python service in local

```shell script
pipenv run gunicorn feb_stats.web.webapp:app
```

### Run linting and tests

```shell script
pipenv run lint ; 
pipenv run pytest tests ;
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
- [ ] Automatically extract more advanced insights from the data.
- [ ] Automatically crawl past seasons.
- [ ] Link with a database.
- [ ] Add support for another orchestrator (Kubernetes). Likely unnecessary given the expected traffic, but fun to do :)

***

*Disclaimer: This is not a* Federación Española de Baloncesto *product nor has any relationship with it.*