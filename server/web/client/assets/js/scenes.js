Crafty.scene('Game', function() {
    console.log("Passing value",Game1.get_gridwidth());
    var playerPositions = Game1.get_playerPosition();
    var tile_value = playerPositions[0];
    var tile_value2 = playerPositions[1];
    var rocks = Game1.get_obstaclePosition();
    console.log(tile_value[0][1]);
    Crafty.sprite("assets/sprites/castle1_50x50.gif", {castle_sprite:[0,0,50,50]});
    Crafty.sprite("assets/sprites/castle2_50x50.png", {castle_sprite2:[0,0,50,50]});
    Crafty.sprite("assets/sprites/rocks1_50x50.png", {rocks1:[0,0,50,50]});
    Crafty.sprite("assets/sprites/rocks2_50x50.png", {rocks2:[0,0,50,50]});
    this.occupied = new Array(Game1.get_gridwidth());
    for (var i = 0; i < Game1.get_gridwidth(); i++) {
        this.occupied[i] = new Array(Game1.get_gridheight());
        for (var y = 0; y < Game1.get_gridheight(); y++) {
            if ((i==tile_value[1] | y == tile_value[1]) | (i==tile_value[0] | y == tile_value[0]) & i!=y)
            {
                this.occupied[i][y] = true;
            }
            else
            {
            this.occupied[i][y] = false;
            }
        }
    }
    Crafty.sprite("assets/sprites/tree_50x50.png", {Tree_sprite:[0,0,50,50]});
    for (var x = 0 ; x<Game1.get_gridwidth();x++)
    {
        for (var y = 0 ; y<Game1.get_gridheight();y++)
        {
            var at_edge = x == 0 || x == Game1.get_gridwidth() - 1 || y == 0 || y == Game1.get_gridheight() - 1;
        if (at_edge)
        {
            Crafty.e('Tree','Tree_sprite').at(x,y).color('rgb(87, 109, 20)');
            this.occupied[x][y]=true;
        }
        else if (this.occupied[x][y]) {
          // Place a bush entity at the current tile

          var rocks_prob = Math.round(Math.random());
          for (i = 0 ;i <rocks.length;i++)
          {
          if (rocks_prob == 1)
          {
          Crafty.e('Bush','rocks1').at(rocks[i][0], rocks[i][1]).color('rgb(87, 109, 20)');
          }
          else{
            Crafty.e('Bush','rocks2').at(rocks[i][0], rocks[i][1]).color('rgb(87, 109, 20)');
          }
          this.occupied[x][y]=true;
        }
        }
        }
    }  

    
    console.log(this.occupied);
    var end = Game1.get_gridwidth()-2;
    Crafty.e('Player').at(1, end);
    Crafty.e('Player2').at(end, 1);
    Crafty.e('WinTileP1','castle_sprite2').at(end, 1).color('rgb(87, 109, 20)').reach();
    Crafty.e('WinTileP2','castle_sprite').at(1, end).color('rgb(87, 109, 20)').reach();

    this.show_victory = this.bind('EndGame', function(e) {
        console.log("Player:",e," Wins!")
          Crafty.scene('Victory');
      });
  }, function() {
    this.unbind('EndGame');
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
