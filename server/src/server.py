from aiohttp import web
import socketio
import logging

sio = socketio.AsyncServer()
app = web.Application()
sio.attach(app)

log = logging.getLogger(__name__)


async def ping(request):
    log.info('Hello, world!')
    return web.json_response({"ping": "pong"})

@sio.on('connect', namespace='/chat')
def connect(sid, environ):
    print("connect ", sid)

@sio.on('chat message', namespace='/chat')
async def message(sid, data):
    print("message ", data)
    await sio.emit('reply', room=sid)

@sio.on('disconnect', namespace='/chat')
def disconnect(sid):
    print('disconnect ', sid)

app.router.add_get('/ping', ping)

def main():
    # init logging
    logging.basicConfig(level=logging.DEBUG)
    web.run_app(app, host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
    