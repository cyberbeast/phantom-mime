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
    for (var x = 0 ; x<Game.map_grid.width;x++)
    {
        for (var y = 0 ; y<Game.map_grid.height;y++)
        {
            var at_edge = x == 0 || x == Game.map_grid.width - 1 || y == 0 || y == Game.map_grid.height - 1;
        if (at_edge)
        {
            Crafty.e('Tree').at(x,y);
        }
        else if (Math.random() < 0.006) {
          // Place a bush entity at the current tile
          Crafty.e('Bush').at(x, y);
        }
        }
    }
    Crafty.e('Player').at(1, 28);
    Crafty.e('Player2').at(28, 1);
    Crafty.e('WinTileP1').at(28, 1).reach();
    Crafty.e('WinTileP2').at(1, 28).reach();
  }
}