Game = {
	start: function(data) {
		Game1 = new grid(data);
		Crafty.init(Game1.width(), Game1.height());
		Crafty.background('rgb(87,109,20)');
		Crafty.scene('Game');
	}
};
