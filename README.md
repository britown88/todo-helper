todo-helper
===========

A helpful tool to assist with tracking TODOs on GitHub projects

Install stuff:

```
fab vagrant build deploy config web_build
```

Start redis and the website:
```
fab vagrant restart_redis restart_webapp
```

Start the workers:
```
fab vagrant workers_start
fab vagrant workers_stop
```
