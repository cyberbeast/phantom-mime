const redis = require('redis'),
	config = require('./config'),
	request = require('request-promise');

var gameNamespace = socket => {
	const client = redis.createClient({
		host: config.redis.host,
		port: config.redis.port
	});

	client.on('error', function(err) {
		console.log(err);
	});
	// console.log(socket.request.session);
	if (socket.request.sessionID !== undefined) {
		console.log(socket.request.sessionID + ' has joined!');
		// console.log('FB ID IS: ' + socket.request.session.fbid);
		client.set(socket.request.sessionID, 'READY');
	}

	socket.on('disconnect', function() {
		// client.get(socket.request.sessionID, function(err, reply) {
		// 	console.log(reply);
		// });
		// console.log(client.get(socket.request.sessionID));
		console.log(socket.request.sessionID + ' has disconnected!');
	});

	socket.on('gameInit', function(data) {
		console.log('REC: ' + JSON.stringify(data));
		var options = {
			method: 'GET',
			uri:
				config.engine.host +
				':' +
				config.engine.port +
				config.engine.gameInitRoute,
			qs: {
				key: socket.request.sessionID,
				fbid: socket.request.session.fbid
			},
			json: true
		};

		request(options)
			.then(function(response) {
				// Request was successful, use the response object at will
				socket.send({
					event: 'gameInit',
					data: response
				});
			})
			.catch(function(err) {
				// Something bad happened, handle the error
				console.log('API: Search failed', err);
				socket.send(err);
			});
	});
};

module.exports.gameNamespace = gameNamespace;
