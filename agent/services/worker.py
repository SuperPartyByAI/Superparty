import sys
from rq import Worker
from agent.common.redisq import redis_conn

def main():
    queues = [q.strip() for q in sys.argv[1].split(",")] if len(sys.argv)>1 else ["default"]
    Worker(queues,connection=redis_conn()).work(with_scheduler=True)

if __name__=="__main__": main()
