Crafty.scene('Game', function() {
    console.log(Game.map_grid.width);
    var tile_value = Game.map_grid.width-2; 
    Crafty.sprite("assets/sprites/castle1_50x50.gif", {castle_sprite:[0,0,50,50]});
    Crafty.sprite("assets/sprites/castle2_50x50.png", {castle_sprite2:[0,0,50,50]});
    Crafty.sprite("assets/sprites/rocks1_50x50.png", {rocks1:[0,0,50,50]});
    Crafty.sprite("assets/sprites/rocks2_50x50.png", {rocks2:[0,0,50,50]});
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
    Crafty.sprite("assets/sprites/tree_50x50.png", {Tree_sprite:[0,0,50,50]});
    for (var x = 0 ; x<Game.map_grid.width;x++)
    {
        for (var y = 0 ; y<Game.map_grid.height;y++)
        {
            var at_edge = x == 0 || x == Game.map_grid.width - 1 || y == 0 || y == Game.map_grid.height - 1;
        if (at_edge)
        {
            Crafty.e('Tree','Tree_sprite').at(x,y).color('rgb(87, 109, 20)');
            this.occupied[x][y]=true;
        }
        else if (Math.random() < 0.06 && !this.occupied[x][y]) {
          // Place a bush entity at the current tile
          var rocks = Math.round(Math.random());
          if (rocks == 1)
          {
          Crafty.e('Bush','rocks1').at(x, y).color('rgb(87, 109, 20)');
          }
          else{
            Crafty.e('Bush','rocks2').at(x, y).color('rgb(87, 109, 20)');
          }
          this.occupied[x][y]=true;
        }
        }
    }  

    
    console.log(this.occupied);
    var end = tile_value;
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
