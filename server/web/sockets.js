const redis = require('redis'),
	config = require('./config'),
	request = require('request-promise');

const client = redis.createClient({
	host: config.redis.host,
	port: config.redis.port
});

client.on('error', function(err) {
	console.log(err);
});

var gameNamespace = socket => {
	var p1 = socket.request.p1;
	var p2 = socket.request.p2;
	var viewerOnly;

	var currentConnection = socket.request.sessionID;
	if (currentConnection != p1 || currentConnection != p2) {
		viewerOnly = true;
	}

	if (currentConnection == p1 || currentConnection == p2) {
		socket.join(req.session.gSession);
	}

	// console.log(socket.request.session);
	if (socket.request.sessionID !== undefined) {
		if (!viewerOnly) {
			console.log(socket.request.sessionID + ' has joined!');
			// console.log('FB ID IS: ' + socket.request.session.fbid);
			client.set(socket.request.sessionID, 'READY');
		}
	}

	socket.on('disconnect', function() {
		if (!viewerOnly) {
			// client.get(socket.request.sessionID, function(err, reply) {
			// 	console.log(reply);
			// });
			// console.log(client.get(socket.request.sessionID));
			console.log(socket.request.sessionID + ' has disconnected!');
		}
	});

	socket.on('gameInit', function(data) {
		if (!viewerOnly) {
			console.log('REC: ' + JSON.stringify(data));
			var options = {
				method: 'GET',
				uri:
					config.engine.host +
					':' +
					config.engine.port +
					config.engine.gameInitRoute,
				qs: {
					key: socket.request.gSession
					// fbid: socket.request.session.fbid
				},
				json: true
			};

			request(options)
				.then(function(response) {
					// Request was successful, use the response object at will
					// console.log('Sending this out...');
					// console.log(JSON.stringify(response));
					socket.to(req.session.gSession).emit('gameInitResponse', {
						event: 'gameInit',
						data: response
					});
				})
				.catch(function(err) {
					// Something bad happened, handle the error
					console.log('API: Search failed', err);
					socket.to(req.session.gSession).emit('gameInitResponse', err);
				});
		}
	});
};

var loungeNamespace = socket => {
	console.log(
		'Session in LOUNGE' + JSON.stringify(socket.request.session.email)
	);

	// client.DEL('loungeMembers', function(err, res) {
	// 	console.log('ERR: ' + err);
	// 	console.log('RES: ' + res);
	// });

	if (socket.request.sessionID !== undefined) {
		console.log(socket.request.sessionID + ' has joined! LOUNGE');
	}

	socket.on('checkIn', function(data) {
		console.log(socket.request.session);
		socket.emit('sessID', socket.request.sessionID);
		client.sadd('loungeMembers', [
			socket.request.session.email + ':' + socket.id
		]);
		client.smembers('loungeMembers', function(err, reply) {
			console.log(reply);
			socket.emit('memberList', { data: reply });
			socket.broadcast.emit('memberList', { data: reply });
		});
	});

	socket.on('challengePlayer', function(data) {
		console.log(
			socket.request.session.email +
				':' +
				socket.id +
				' wants to challenge ' +
				data.player
		);
		var extract = data.player.split(':');
		console.log(extract);
		socket.to(extract[1]).emit('newChallengeRequest', {
			challenger: socket.request.session.email,
			challengerID: socket.id,
			challengerUID: '&player1=' + socket.request.sessionID,
			challengeeID: extract[1],
			gSession:
				'?gameID=' +
				socket.id.replace('/lounge#', '') +
				extract[1].replace('/lounge#', '')
		});
	});

	socket.on('challengeStatus', function(data) {
		console.log('status check.');
		if (data.status == 'OK') {
			var temp = data;
			temp.payload.challengeeUID = '&player2=' + socket.request.sessionID;
			socket.to(temp.payload.challengerID).emit('challengeAccepted', {
				redirectParam:
					temp.payload.gSession +
					temp.payload.challengerUID +
					temp.payload.challengeeUID
			});
		}
	});

	socket.on('disconnect', function() {
		client.SREM('loungeMembers', [socket.request.session.email]);
		console.log(socket.request.sessionID + ' has disconnected from LOUNGE!');
		client.smembers('loungeMembers', function(err, reply) {
			console.log(reply);
			socket.broadcast.emit('memberList', { data: reply });
		});
	});
};

module.exports.gameNamespace = gameNamespace;
module.exports.loungeNamespace = loungeNamespace;
