import os
def getenv(name, default=None):
    v = os.environ.get(name)
    return v if v is not None and v != "" else default
def getenv_int(name, default):
    v = os.environ.get(name)
    try: return int(v) if v else default
    except: return default
def getenv_list_csv(name, default):
    v = os.environ.get(name, "")
    return [x.strip() for x in v.split(",") if x.strip()] if v.strip() else default
