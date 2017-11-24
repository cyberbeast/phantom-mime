import hug
from handlers import request
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())

@hug.extend_api('')
def api():
    return [request]