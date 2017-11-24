Crafty.c('Grid', {
	init: function() {
		this.attr({
			w: Game1.get_tilesize(),
			h: Game1.get_tilesize()
		});
	},
	at: function(x, y) {
		if (x === undefined && y === undefined) {
			return {
				x: this.x / Game1.get_tilesize(),
				y: this.y / Game1.get_tilesize()
			};
		} else {
			this.attr({ x: x * Game1.get_tilesize(), y: y * Game1.get_tilesize() });
			return this;
		}
	}
});

Crafty.c('Actor', {
	init: function() {
		this.requires('2D, Canvas, Grid');
	}
});
Crafty.c('Tree', {
	init: function() {
		this.requires('Actor, Color, Solid');
		this.color('rgb(20, 125, 25)');
	}
});

Crafty.c('Bush', {
	init: function() {
		this.requires('Actor, Color, Solid');
		this.color('rgb(20, 185, 25)');
	}
});

Crafty.c('Player', {
	init: function() {
		var old_key = null;
		this.requires('Actor, Fourway, Color, Collision')
			.color('rgb(20, 75, 25)')
			.bind('KeyDown', function(e) {
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
				}
			})
			.collision()
			.onHit('Solid', function() {
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
	}
});
Crafty.c('Player2', {
	init: function() {
		var old_key = null;
		this.requires('Actor, Fourway, Color, Collision')
			.color('rgb(255, 25, 25)')
			.bind('KeyDown', function(e) {
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
			.collision()
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
			})
			.collision()
			.onHit('PLayer', function() {
				console.log('Hitting player 1');
			});
	}
});

Crafty.c('WinTileP1', {
	init: function() {
		this.requires('Actor, Color, Collision').color('rgb(170, 125, 40)');
	},
	reach: function() {
		this.collision().onHit('Player', function() {
			//console.log("PLayer1 Win");
			Crafty.trigger('EndGame', '1');
		});
	}
});
Crafty.c('WinTileP2', {
	init: function() {
		this.requires('Actor, Color, Collision').color('rgb(170, 125, 40)');
	},
	reach: function() {
		this.collision().onHit('Player2', function() {
			Crafty.trigger('EndGame', '2');
			//console.log("PLayer2 Win");
		});
	}
});
