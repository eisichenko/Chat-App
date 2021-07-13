# Chat App

[![codecov](https://codecov.io/gh/eisichenko/ChatApp/branch/production/graph/badge.svg?token=Z6ZDF5AHCW)](https://codecov.io/gh/eisichenko/ChatApp)

- `docker-compose up` - start app on localhost (url:  http://127.0.0.1:5000)

- `docker-compose down -v` - remove containers with **deleting** DB data

- `docker-compose down` - remove containers with **saving** DB data

- Use `incognito` to login from multiple accounts or `MultiLogin` extension in Google Chrome

- Used `Github Actions` for development with ci/cd

- Added `redis task queue` to scheduling jobs

- Dockerhub: https://hub.docker.com/repository/docker/eisichenko/chat_app_flask

- App is deployable on Heroku
