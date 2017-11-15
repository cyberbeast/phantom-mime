import hug
from handlers import request

@hug.extend_api('')
def api():
    return [request]