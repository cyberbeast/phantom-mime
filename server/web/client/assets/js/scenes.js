Crafty.scene(
	'Game',
	function() {
		var positions = Game1.get_playerPosition();
		var tile_value = positions[0];
		var tile_value2 = positions[1];
<<<<<<< HEAD
=======
		console.log('Player position' + tile_value);
		console.log('Player position' + tile_value2);
>>>>>>> master
		var rocks = Game1.get_obstaclePosition();
		Crafty.sprite('assets/sprites/castle1_50x50.gif', {
			castle_sprite: [0, 0, 50, 50]
		});
		Crafty.sprite('assets/sprites/castle2_50x50.png', {
			castle_sprite2: [0, 0, 50, 50]
		});
		Crafty.sprite('assets/sprites/rocks1_50x50.png', {
			rocks1: [0, 0, 50, 50]
		});
		Crafty.sprite('assets/sprites/rocks2_50x50.png', {
			rocks2: [0, 0, 50, 50]
		});
		Crafty.sprite('assets/sprites/tree_50x50.png', {
			Tree_sprite: [0, 0, 50, 50]
		});
		for (var x = 0; x < Game1.get_gridwidth(); x++) {
			for (var y = 0; y < Game1.get_gridheight(); y++) {
				var at_edge =
					x == 0 ||
					x == Game1.get_gridwidth() - 1 ||
					y == 0 ||
					y == Game1.get_gridheight() - 1;
				if (at_edge) {
					Crafty.e('Tree', 'Tree_sprite')
						.at(x, y)
						.color('rgb(87, 109, 20)');
				}
			}
		}

		for (var i = 0; i < rocks.length; i++) {
			var rocks_prob = Math.round(Math.random());
			if (rocks_prob == 1) {
				Crafty.e('Bush', 'rocks1')
					.at(rocks[i][0], rocks[i][1])
					.color('rgb(87, 109, 20)');
			} else {
				Crafty.e('Bush', 'rocks2')
					.at(rocks[i][0], rocks[i][1])
					.color('rgb(87, 109, 20)');
			}
		// Player entities
		var player1 = Crafty.e('Player1').at(tile_value[0], tile_value[1]);
		var player2 = Crafty.e('Player2').at(tile_value2[0], tile_value2[1]);
		player1.bind('turn', function(e) {
			if (e.key == Crafty.keys.LEFT_ARROW) {
				this.x = this.x - Game1.get_tilesize();
				old_key = e.key;
			} else if (e.key == Crafty.keys.RIGHT_ARROW) {
				this.x = this.x + Game1.get_tilesize();
				old_key = e.key;
			} else if (e.key == Crafty.keys.UP_ARROW) {
				this.y = this.y - Game1.get_tilesize();
				old_key = e.key;
			} else if (e.key == Crafty.keys.DOWN_ARROW) {
				this.y = this.y + Game1.get_tilesize();
				old_key = e.key;
			}}).onHit('Solid', function() {
				if (old_key == Crafty.keys.LEFT_ARROW) {
					this.x = this.x + Game1.get_tilesize();
				} else if (old_key == Crafty.keys.RIGHT_ARROW) {
					this.x = this.x - Game1.get_tilesize();
				} else if (old_key == Crafty.keys.UP_ARROW) {
					this.y = this.y + Game1.get_tilesize();
				} else if (old_key == Crafty.keys.DOWN_ARROW) {
					this.y = this.y - Game1.get_tilesize();
				}
			});

		player1.bind('KeyDown',function(e)
	{
		player1.trigger('turn',e);
	});
		player2.bind('KeyDown', function(e) {
				if (e.key == Crafty.keys.A) {
					this.x = this.x - Game1.get_tilesize();
					old_key = e.key;
				} else if (e.key == Crafty.keys.D) {
					this.x = this.x + Game1.get_tilesize();
					old_key = e.key;
				} else if (e.key == Crafty.keys.W) {
					this.y = this.y - Game1.get_tilesize();
					old_key = e.key;
				} else if (e.key == Crafty.keys.S) {
					this.y = this.y + Game1.get_tilesize();
					old_key = e.key;
				}
			})
			.onHit('Solid', function() {
				if (old_key == Crafty.keys.A) {
					this.x = this.x + Game1.get_tilesize();
				} else if (old_key == Crafty.keys.D) {
					this.x = this.x - Game1.get_tilesize();
				} else if (old_key == Crafty.keys.W) {
					this.y = this.y + Game1.get_tilesize();
				} else if (old_key == Crafty.keys.S) {
					this.y = this.y - Game1.get_tilesize();
				}
			});
		Crafty.e('WinTileP1', 'castle_sprite2')
			.at(tile_value2[0], tile_value2[1])
			.color('rgb(87, 109, 20)')
			.reach();
		Crafty.e('WinTileP2', 'castle_sprite')
			.at(tile_value[0], tile_value[1])
			.color('rgb(87, 109, 20)')
			.reach();

		this.show_victory = this.bind('EndGame', function(e) {
			console.log('Player:', e, ' Wins!');
			Crafty.scene('Victory');
		});
	},
	function() {
		this.unbind('EndGame');
	}
);
Crafty.scene(
	'Victory',
	function() {
		// Display some text in celebration of the victory
		Crafty.e('2D, DOM, Text')
			.attr({ x: 15, y: 15 })
			.text('Victory!');
		//this.restart_game = this.bind('KeyDown', function() {
		//	Crafty.scene('Game');
		//});
	},
	function() {
		this.unbind('KeyDown');
	}
);
