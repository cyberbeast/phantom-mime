const redis = require('redis'),
	config = require('./config'),
	request = require('request-promise'),
	mongoose = require('mongoose'),
	User = require('./models/user'),
	ioImport = require('./index').sendToGame,
	waterfall = require('async-waterfall');

mongoose.connect('mongodb://mongodb/', {
	useMongoClient: true
});

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

	// var currentConnection = socket.request.sessionID;
	// if (currentConnection != p1 || currentConnection != p2) {
	// viewerOnly = true;
	// }

	// if (currentConnection == p1 || currentConnection == p2) {

	socket.emit('yourIdentity', socket.request.sessionID);
	socket.join(socket.request.session.gSession, function() {
		console.log(
			socket.request.session.email +
				' with id ' +
				socket.request.sessionID +
				' has joined!' +
				socket.request.session.gSession
		);

		ioImport(socket.request.session.gSession, 'success', socket.request.session.email);
		// socket
		// 	.to(socket.request.session.gSession)
		// 	.emit('success', socket.request.session.email);
	});

	socket.on('gameServerListener', function(payload) {
		console.log('GAME sent something');
		switch (payload.event) {
			case 'newMove':
				console.log('Gman is sending', payload.data);
				console.log('GSESSION', socket.request.session.gSession);
				var log_currentPlayer = payload.data.player === 'Player1' ? 'Player2' : 'Player1';
				client.lpush(
					payload.data.game + ':moves',
					log_currentPlayer + ':' + String(payload.data.move),
					function(err, reply) {
						console.log(err);
						console.log(reply);
					}
				);
				console.log('Game Mode is: ', payload.data.mode);
				if (payload.data.mode === 'trainAI') {
					var options = {
						method: 'GET',
						uri: config.engine.host + ':' + config.engine.port + config.engine.nextMoveRoute,
						qs: {
							key: socket.request.session.gSession,
							fbid: socket.request.session.fbid,
							mode: payload.data.mode
						},
						json: true
					};

					request(options)
						.then(function(response) {
							console.log('HAVE response');
							if (response === true) {
								console.log('INSIDE here');
								client.lindex(payload.data.game + ':moves', 0, function(err, reply) {
									console.log('ENGINE response on REDIS ', reply);
									var val = reply.split(':');
									socket.send({
										event: 'trainAINewMove',
										gameMode: 'trainAI',
										player: log_currentPlayer,
										move: val[1]
									});
								});
							}
						})
						.catch(function(err) {
							// Something bad happened, handle the error
							console.log('API: Search failed', err);
							socket.to(socket.request.session.gSession).emit('gameInitResponse', err);
						});
				} else {
					console.log('Responding to newMove');
					socket.to(payload.data.game).emit(payload.event, {
						player: payload.data.player,
						move: payload.data.move
					});
				}

				break;

			case 'endGame':
				console.log('endGame data:', payload);
				console.log('EMAIL: ', socket.request.session.email)
				// client.lrange(
				// 	socket.request.session.gSession + ':moves',
				// 	0,
				// 	-1,
				// 	function(err, reply) {
				// 		console.log('Inside endGame', reply);
				// 	}
				// );
				waterfall(
					[
						function(callback) {
							console.log('HERE WF');
							var writeObject = {
								gameID: socket.request.session.gSession,
								winner: payload.data.winner
							};
							console.log('lvl1', writeObject);
							callback(null, writeObject);
						},
						function(writeObject, callback) {
							client.get(socket.request.session.gSession + ':game_meta', function(err, reply) {
								writeObject.game_meta = reply;
								console.log('inside redis session:game_meta', reply);
								console.log('lvl2', writeObject);
								callback(null, writeObject);
							});
						},
						function(writeObject, callback) {
							client.lrange(socket.request.session.gSession + ':moves', 0, -1, function(err, reply) {
								writeObject.moves = reply;
								console.log('inside redis session:moves', reply);
								console.log('lvl3', writeObject);
								callback(null, writeObject);
							});
						},
						function(writeObject, callback) {
							console.log('ENDING');
							var pushObject;
							if (socket.request.session.gameMode === 'trainAI') {
								var pushObject = { trainAI_games: writeObject };

								console.log("Inside trainAI's endGame toggle", socket.request.session.fbid);
							} else {
								var pushObject = { player_games: writeObject };
							}
							User.findOneAndUpdate(
								{ id: String(socket.request.session.fbid) },
								{ $push: pushObject },
								{ safe: true, upsert: true, new: true },
								function(err, res) {
									if (err) throw err;

									console.log('ERR', err);
									// console.log('RES', res);
									var qs = {
										fbid: socket.request.session.fbid
									};
									if (socket.request.session.gameMode === 'trainAI') {
										console.log('oOK');
										engineRequest(qs, config.engine.trainMimeRoute, function(resp) {
											console.log(config.engine.trainMimeRoute, qs, resp);
											socket.send({ event: 'mimeTrainStarted' });
										});
									}
									callback(null, 'done');
								}
							);
						}
					],
					function(err, result) {
						// result now equals 'done'
						console.log('Waterfall completed!', result);
					}
				);

				var mv;

				// client.get(soc);

				// Tell client that endGame was successfully handled by server.
				// Client will set a 5 second timer, at the end of which client will redirect the player to /dashboard.
				socket.send({
					event: 'endGameAcknowledged'
				});
				break;
		}
	});

	// console.log(socket.request.session);
	if (socket.request.sessionID !== undefined) {
		// if (!viewerOnly) {
		// console.log(
		// 	socket.request.session.email +
		// 		' with id ' +
		// 		socket.request.sessionID +
		// 		' has joined!' +
		// 		socket.request.session.gSession
		// );
		// console.log('FB ID IS: ' + socket.request.session.fbid);
		client.set(socket.request.sessionID, 'READY');
		// }
	}

	socket.on('disconnect', function() {
		// if (!viewerOnly) {
		// client.get(socket.request.sessionID, function(err, reply) {
		// 	console.log(reply);
		// });
		// console.log(client.get(socket.request.sessionID));
		console.log(socket.request.sessionID + ' has disconnected!');
		socket.leave(socket.request.session.gSession);
		// }
	});

	socket.on('gameInit', function(data) {
		// if (!viewerOnly) {
		client.set(socket.request.session.gSession, 'READY');
		console.log('REC: ' + JSON.stringify(data));
		var options = {
			method: 'GET',
			uri: config.engine.host + ':' + config.engine.port + config.engine.gameInitRoute,
			qs: {
				key: socket.request.session.gSession
				// fbid: socket.request.session.fbid
			},
			json: true
		};

		if (socket.request.session.gameMode === 'trainAI') {
			options.qs.gameMode = socket.request.session.gameMode;
			options.qs.fbid = socket.request.session.fbid;
		} else {
			options.qs.gameMode = socket.request.session.gameMode;
			options.qs.fbid = socket.request.session.fbid;
		}

		request(options)
			.then(function(response) {
				// Request was successful, use the response object at will
				// console.log('Sending this out...');
				// console.log(JSON.stringify(response));
				// console.log('RESPONSE FOR GAMEINT');
				// console.log(response);
				// socket.send('gameInitResponse', {
				// 	event: 'gameInit',
				// 	data: response
				// });
				client.lpush(socket.request.session.gSession + ':moves', 'READY -> ' + socket.request.sessionID);
				if (socket.request.session.gameMode === 'trainAI') {
					socket.send({
						event: 'trainAIGameInitResponse',
						gameMode: 'trainAI',
						response: response
					});
				} else {
					ioImport(socket.request.session.gSession, 'gameInitResponse', response);
				}
			})
			.catch(function(err) {
				// Something bad happened, handle the error
				console.log('API: Search failed', err);
				socket.to(socket.request.session.gSession).emit('gameInitResponse', err);
			});
		// }
	});
};

function engineRequest(qs, route, cb) {
	var options = {
		method: 'GET',
		uri: config.engine.host + ':' + config.engine.port + route,
		qs: qs,
		json: true
	};
	request(options)
		.then(function(response) {
			cb(response);
		})
		.catch(function(err) {
			console.log('err');
			cb(err);
		});
}

var loungeNamespace = socket => {
	console.log('Session in LOUNGE' + JSON.stringify(socket.request.session.email));

	var del = false;

	if (del) {
		client.DEL('loungeMembers', function(err, res) {
			console.log('ERR: ' + err);
			console.log('RES: ' + res);
		});
	}

	if (socket.request.sessionID !== undefined) {
		console.log(socket.request.sessionID + ' has joined! LOUNGE');
	}

	if (!del) {
		socket.on('checkIn', function(data) {
			console.log(socket.request.session);
			socket.emit('sessID', socket.request.sessionID);
			client.sadd('loungeMembers', [socket.request.session.email + ':' + socket.id]);
			client.smembers('loungeMembers', function(err, reply) {
				console.log(reply);
				socket.emit('memberList', { data: reply });
				socket.broadcast.emit('memberList', { data: reply });
			});
		});

		socket.on('challengePlayer', function(data) {
			console.log(socket.request.session.email + ':' + socket.id + ' wants to challenge ' + data.player);
			var extract = data.player.split(':');
			console.log(extract);
			socket.to(extract[1]).emit('newChallengeRequest', {
				challenger: socket.request.session.email,
				challengerID: socket.id,
				challengerUID: '&player1=' + socket.request.sessionID,
				challengeeID: extract[1],
				gSession: '?gameID=' + socket.id.replace('/lounge#', '') + extract[1].replace('/lounge#', '')
			});
		});
		socket.on('trainAI', function() {
			console.log(socket.request.session.email + ':' + socket.id + ' wants to train his/her AI agent.');
			var gSession = '?gameID=' + socket.id.replace('/lounge#', '');
			var player = '&player1=' + socket.request.sessionID;
			var mode = '&mode=trainAI';
			socket.send({ redirectParam: gSession + player + mode });
		});

		socket.on('challengeStatus', function(data) {
			console.log('status check.');
			if (data.status == 'OK') {
				var temp = data;
				temp.payload.challengeeUID = '&player2=' + socket.request.sessionID;
				socket.to(temp.payload.challengerID).emit('challengeAccepted', {
					redirectParam: temp.payload.gSession + temp.payload.challengerUID + temp.payload.challengeeUID
				});
			}
		});

		socket.on('disconnect', function() {
			client.SREM('loungeMembers', socket.request.session.email + ':' + socket.id);
			console.log(socket.request.sessionID + ' has disconnected from LOUNGE!');
			client.smembers('loungeMembers', function(err, reply) {
				console.log(reply);
				socket.broadcast.emit('memberList', { data: reply });
			});
		});
	}
};

module.exports.gameNamespace = gameNamespace;
module.exports.loungeNamespace = loungeNamespace;
