import subprocess, requests
from agent.common.env import getenv
from agent.common.redisq import redis_conn

def _git(args): subprocess.run(["git"]+args, check=True, cwd="/workdir")

def create_pr(branch, title, body):
    token=getenv("GITHUB_TOKEN"); repo=getenv("GITHUB_REPOSITORY")
    url=f"https://api.github.com/repos/{repo}/pulls"
    r=requests.post(url,headers={"Authorization":f"token {token}"},
                   json={"title":title,"body":body,"head":branch,"base":"main"},timeout=30)
    r.raise_for_status(); return r.json().get("html_url","")

def git_commit_push_pr(branch, commit_msg, files, pr_title, pr_body):
    lock=redis_conn().lock("git-lock",timeout=600)
    if not lock.acquire(blocking=True,blocking_timeout=60): raise RuntimeError("No git lock")
    try:
        _git(["config","user.email","agent@superparty.local"])
        _git(["config","user.name","superparty-agent"])
        _git(["checkout","-B",branch])
        _git(["add"]+list(files)) if files else _git(["add","-A"])
        subprocess.run(["git","commit","-m",commit_msg],check=False,cwd="/workdir")
        _git(["push","-u","origin",branch,"--force-with-lease"])
        return create_pr(branch,pr_title,pr_body)
    finally: lock.release()
