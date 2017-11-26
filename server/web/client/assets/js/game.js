var moves = function(data) {
	var key = data.key;
	var entity = data.entity;
	if (key == Crafty.keys.LEFT_ARROW) {
		entity.x = entity.x - Game1.get_tilesize();
		// old_key = key;
	} else if (key == Crafty.keys.RIGHT_ARROW) {
		entity.x = entity.x + Game1.get_tilesize();
		// old_key = key;
	} else if (key == Crafty.keys.UP_ARROW) {
		entity.y = entity.y - Game1.get_tilesize();
		// old_key = key;
	} else if (key == Crafty.keys.DOWN_ARROW) {
		entity.y = entity.y + Game1.get_tilesize();
		// old_key = key;
	}
};
var hits = function() {
	// if (old_key == Crafty.keys.LEFT_ARROW) {
	// 	this.x = this.x + Game1.get_tilesize();
	// } else if (old_key == Crafty.keys.RIGHT_ARROW) {
	// 	this.x = this.x - Game1.get_tilesize();
	// } else if (old_key == Crafty.keys.UP_ARROW) {
	// 	this.y = this.y + Game1.get_tilesize();
	// } else if (old_key == Crafty.keys.DOWN_ARROW) {
	// 	this.y = this.y - Game1.get_tilesize();
	// }
};

var getUrlParameter = function getUrlParameter(sParam) {
	var sPageURL = decodeURIComponent(window.location.search.substring(1)),
		sURLVariables = sPageURL.split('&'),
		sParameterName,
		i;

	for (i = 0; i < sURLVariables.length; i++) {
		sParameterName = sURLVariables[i].split('=');

		if (sParameterName[0] === sParam) {
			return sParameterName[1] === undefined ? true : sParameterName[1];
		}
	}
};

Game = {
	start: function(socket, data) {
		console.log(socket);
		Game1 = new grid(socket, data);
		Crafty.init(Game1.width(), Game1.height());
		Crafty.background('rgb(87,109,20)');
		Crafty.scene('Game');
	},
	move: function(turn, key) {
		var possibleKeys = [
			Crafty.keys.LEFT_ARROW,
			Crafty.keys.RIGHT_ARROW,
			Crafty.keys.DOWN_ARROW,
			Crafty.keys.UP_ARROW
		];
		if (possibleKeys.includes(key)) {
			turn.trigger('move', { t: turn, k: key });
		}
	},
	find_entity(identity) {
		var player1_ls = Crafty('Player1').get();
		var player2_ls = Crafty('Player2').get();
		var something = ['a'];
		console.log(player1_ls[0].identity);
		var my_entity = 'bleh';
		for (var idx in player1_ls) {
			// console.log(el);
			console.log(idx);
			if (identity === player1_ls[idx].identity) {
				my_entity = player1_ls[idx];
			}
		}
		// console.log(my_entity);
		for (var idx in player2_ls) {
			if (identity === player2_ls[idx].identity) {
				my_entity = player2_ls[idx];
			}
		}
		// console.log;
		return my_entity;
	},
	create_players: function() {
		var positions = Game1.get_playerPosition();
		var tile_value = positions[0];
		var tile_value2 = positions[1];
		var gameid = getUrlParameter('gameID');
		var player1Token = getUrlParameter('player1');
		var player2Token = getUrlParameter('player2');
		var player1 = Crafty.e('Player1').at(tile_value[0], tile_value[1]);
		player1.setName('player1');
		player1.identity = player1Token;
		var player2 = Crafty.e('Player2').at(tile_value2[0], tile_value2[1]);
		player2.setName('player2');
		player2.identity = player2Token;
		//var turn = player1;
		player1
			.bind('move', function(data) {
				moves(data);
			})
			.onHit('Solid', hits());

		player2
			.bind('move', function(data) {
				moves(data);
			})
			.onHit('Solid', hits());

		return {
			p1: player1,
			p2: player2
		};
	}
};
