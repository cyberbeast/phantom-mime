Game = {
  // Initialize and start our game
  map_grid: {
    width:  30,
    height: 30,
    tile: {
      width:  25,
      height: 25
    }
  },
  width: function() {
    return this.map_grid.width * this.map_grid.tile.width;
  },
 
  // The total height of the game screen. Since our grid takes up the entire screen
  //  this is just the height of a tile times the height of the grid
  height: function() {
    return this.map_grid.height * this.map_grid.tile.height;
  },
  start: function() {
    // Start crafty and set a background color so that we can see it's working
    Crafty.init(Game.width(), Game.height());
    // console.log(Game.map_grid);
    Crafty.background('rgb(249, 223, 125)');
    Crafty.scene('Game');
  }
}