Crafty.scene('Game', function() {
    // console.log(Game.map_grid);
    var tile_value = 28; // hardcoding the value of tile for now to prevent players's position to be populated with trees.
    this.occupied = new Array(Game.map_grid.width);
    for (var i = 0; i < Game.map_grid.width; i++) {
        this.occupied[i] = new Array(Game.map_grid.height);
        for (var y = 0; y < Game.map_grid.height; y++) {
            if ((i==tile_value | y == tile_value) & i!=y)
            {
                this.occupied[i][y] = true;
            }
            else
            {
            this.occupied[i][y] = false;
            }
        }
    }
    for (var x = 0 ; x<Game.map_grid.width;x++)
    {
        for (var y = 0 ; y<Game.map_grid.height;y++)
        {
            var at_edge = x == 0 || x == Game.map_grid.width - 1 || y == 0 || y == Game.map_grid.height - 1;
        if (at_edge)
        {
            Crafty.e('Tree').at(x,y);
            this.occupied[x][y]=true;
        }
        else if (Math.random() < 0.006 && !this.occupied[x][y]) {
          // Place a bush entity at the current tile
          Crafty.e('Bush').at(x, y);
          this.occupied[x][y]=true;
        }
        }
    }
    console.log(this.occupied);
    Crafty.e('Player').at(1, 28);
    Crafty.e('Player2').at(28, 1);
    Crafty.e('WinTileP1').at(28, 1).reach();
    Crafty.e('WinTileP2').at(1, 28).reach();

    this.show_victory = this.bind('EndGame', function(e) {
        console.log("Player:",e," Wins!")
          Crafty.scene('Victory');
      });
  }, function() {
    this.unbind('VillageVisited');
  });
  Crafty.scene('Victory', function() {
    // Display some text in celebration of the victory
    Crafty.e('2D, DOM, Text')
      .attr({ x: 15, y: 15 })
      .text('Victory!');
    this.restart_game = this.bind('KeyDown', function() {
      Crafty.scene('Game');
    });
  }, function() {
    this.unbind('KeyDown');
  });
