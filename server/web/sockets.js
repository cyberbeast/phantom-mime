var gameNamespace = socket => {
	// console.log(socket.request.session);
	if (socket.request.sessionID !== undefined) {
		console.log(socket.request.sessionID + ' has joined!');
	}

	socket.on('disconnect', function() {
		console.log(socket.request.sessionID + ' has disconnected!');
	});

	socket.on('gameInit', function(data) {
		console.log('REC: ' + JSON.stringify(data));

		socket.send('RECEIVED SAFELY.');
	});
};

module.exports.gameNamespace = gameNamespace;
