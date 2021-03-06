const express = require('express'),
	session = require('express-session'),
	socketio = require('socket.io'),
	api = require('./routes/api.js'),
	sockets = require('./sockets'),
	redis = require('redis'),
	config = require('./config'),
	path = require('path'),
	redisStore = require('connect-redis')(session);

const client = redis.createClient({
	host: config.redis.host,
	port: config.redis.port
});
client.on('error', function(err) {
	console.log(err);
});

var app = express();
/**
 * Get port from environment and store in Express.
 */
const port = process.env.PORT || '8080';
app.set('port', port);

/**
 * 		Listen on provided port, on all network interfaces.
 */
var server = app.listen(port, () => {
	console.log(`Web server running on localhost:${port}`);
});

/**
 * 		Expose socketio server on the same port, on all network interfaces.
 */
var io = socketio(server);

var sessionMiddleware = session({
	secret: 'ssshhhhhh',
	store: new redisStore({
		host: config.redis.host,
		port: config.redis.port,
		client: client,
		disableTTL: true
	}),
	resave: false,
	saveUninitialized: true
});

/**
 * 		'/' : Homepage (login)
 */
app.get('/', function(req, res) {
	res.sendFile(path.join(__dirname + '/client/index.html'));
});

/**
 * 		paths for static files
 */
app.use('*/js', express.static(path.join(__dirname, 'client/assets/js')));
app.use('*/css', express.static(path.join(__dirname, 'client/assets/css')));
app.use(
	'*/sprites',
	express.static(path.join(__dirname, 'client/assets/sprites'))
);
io.use((socket, next) => {
	sessionMiddleware(socket.request, {}, next);
});

var game = io.of('/game');
game.on('connection', sockets.gameNamespace);

var lounge = io.of('/lounge');
lounge.on('connection', sockets.loungeNamespace);

export function sendToGame(room, event, data) {
	game.to(room).emit(event, data);
}

app.use(sessionMiddleware);
app.use((req, res, next) => {
	console.log(`From Express: ${req.sessionID}`);
	next();
});

/**
 * 		'/api' : Login routes
 */
app.use('/api', api);
