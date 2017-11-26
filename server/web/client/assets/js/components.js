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

Crafty.c('Player1', {
	init: function() {
		var old_key = null;
		this.requires('Actor, Fourway, Color, Collision')
			.color('rgb(20, 75, 25)')
			.collision();
	}
});
Crafty.c('Player2', {
	init: function() {
		var old_key = null;
		this.requires('Actor, Fourway, Color, Collision').color('rgb(255, 25, 25)');
	}
});

Crafty.c('WinTileP1', {
	init: function() {
		this.requires('Actor, Color, Collision').color('rgb(170, 125, 40)');
	},
	reach: function() {
		this.collision().onHit('Player1', function() {
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
