Game = {
  start: function(data) {
    // Start crafty and set a background color so that we can see it's working
    console.log("reciever value");
    Game1 = new grid(data);
    Crafty.init(Game1.width(), Game1.height());
    Crafty.background('rgb(87, 109, 20)');
    Crafty.scene('Game');
  }
}