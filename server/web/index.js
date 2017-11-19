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

app.use('/api', api);

/**
 * Get port from environment and store in Express.
 */
const port = process.env.PORT || '8080';
app.set('port', port);

/**
 * Create HTTP server.
 */
const server = http.createServer(app);
const sockets = require('./sockets');
sockets.socketServer(app, server);

/**
 * Listen on provided port, on all network interfaces.
 */
server.listen(port, () =>
	console.log(`Web server running on localhost:${port}`)
);

module.exports = server;
