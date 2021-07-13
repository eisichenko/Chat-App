import redis
import app
import project
import config

from rq import Connection, Worker
from rq.worker import HerokuWorker

redis_connection = redis.from_url(config.REDIS_URL)

if __name__ == '__main__':
    with Connection(redis_connection):
        queues = ['high', 'default', 'low']
        if config.ENV == config.HEROKU_ENV:
            w = HerokuWorker(queues)
        else:
            w = Worker(queues)
        w.work()