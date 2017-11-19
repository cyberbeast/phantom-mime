const socketio = require('socket.io');

exports.socketServer = function(app, server) {
	const io = socketio.listen(server);
	io.on('connection', function(socket) {
		console.log('User connected...');

		socket.on('disconnect', function() {
			console.log('User disconnected...');
		});

		socket.on('gameInit', function(data) {
			console.log('REC: ' + JSON.stringify(data));
			socket.send('RECEIVED SAFELY.');
		});
	});
};
