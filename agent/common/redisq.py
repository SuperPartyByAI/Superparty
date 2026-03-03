from redis import Redis
from rq import Queue
from agent.common.env import getenv
def redis_conn(): return Redis.from_url(getenv("REDIS_URL","redis://localhost:6379"))
def get_queue(name): return Queue(name, connection=redis_conn())
