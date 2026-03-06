from redis import Redis
from agent.common.env import getenv

try:
    from rq import Queue
except (ImportError, ValueError):
    class Queue:
        def __init__(self, name, connection=None): self.name = name
        def enqueue(self, *args, **kwargs): pass

def redis_conn(): return Redis.from_url(getenv("REDIS_URL","redis://localhost:6379"))
def get_queue(name): return Queue(name, connection=redis_conn())
