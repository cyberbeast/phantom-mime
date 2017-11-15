'use strict';

const express = require('express');
const app = express();
const path = require('path');
const http = require('http');

/**
 * Fetch API implementation methods.
 */
const api = require('./routes/api');

/**
 * Point static path to /dist to serve game client.
 */
app.use('/', express.static(path.join(__dirname, 'dist')));

/**
 * Expose test route.
 */
app.get('/test', function(req, res) {
	res.send('Hello, world!');
});

// Integrate realtime API route with express. EXPERIMENTAL!!!
app.use('/', api);

/**
 * Get port from environment and store in Express.
 */
const port = process.env.PORT || '8080';
app.set('port', port);

/**
 * Create HTTP server.
 */
const server = http.createServer(app);
const io = require('socket.io')(server);
io.on('connection', function(socket) {
	console.log('User connected...');
	socket.on('disconnect', function() {
		console.log('User disconnected...');
	});
});
app.set('socketio', io);

app.use(function(req, res, next) {
	res.io = io;
	next();
});

/**
 * Listen on provided port, on all network interfaces.
 */
server.listen(port, () =>
	console.log(`Web server running on localhost:${port}`)
);

module.exports = server;
