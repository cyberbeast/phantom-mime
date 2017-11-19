Crafty.c('Grid',{
    init: function() {
    this.attr({
      w: Game.map_grid.tile.width,
      h: Game.map_grid.tile.height
    })
},
at: function(x,y)
{
if (x === undefined && y === undefined) {
      return { x: this.x/Game.map_grid.tile.width, y: this.y/Game.map_grid.tile.height }
    } else {
      this.attr({ x: x * Game.map_grid.tile.width, y: y * Game.map_grid.tile.height });
      return this;
    }
},

});

Crafty.c('Actor', {
  init: function() {
    this.requires('2D, Canvas, Grid');
  },
});
Crafty.c('Tree', {
  init: function() {
    this.requires('Actor, Color, Solid');
    this.color('rgb(20, 125, 25)');
  },
});

Crafty.c('Bush', {
  init: function() {
    this.requires('Actor, Color, Solid');
    this.color('rgb(20, 185, 25)');
  },
});

Crafty.c('Player', {
  init: function() {
    var old_key = null;
    this.requires('Actor, Fourway, Color, Collision')
      .color('rgb(20, 75, 25)')
      .bind("KeyDown",function(e) {
    if(e.key == Crafty.keys.LEFT_ARROW) {
      this.x = this.x - Game.map_grid.tile.width;
      old_key = e.key;
    } else if (e.key == Crafty.keys.RIGHT_ARROW) {
      this.x = this.x + Game.map_grid.tile.width;
      old_key = e.key;
    } else if (e.key == Crafty.keys.UP_ARROW) {
      this.y = this.y - Game.map_grid.tile.width;
      old_key = e.key;
    } else if (e.key == Crafty.keys.DOWN_ARROW) {
      this.y = this.y + Game.map_grid.tile.width;
      old_key = e.key;
  }
  }).collision().onHit('Solid',function(){
    console.log("fucking hit");
    if(old_key == Crafty.keys.LEFT_ARROW) {
      this.x = this.x + Game.map_grid.tile.width;
    } else if (old_key == Crafty.keys.RIGHT_ARROW) {
      this.x = this.x - Game.map_grid.tile.width;
    } else if (old_key == Crafty.keys.UP_ARROW) {
      this.y = this.y + Game.map_grid.tile.width;
    } else if (old_key == Crafty.keys.DOWN_ARROW) {
      this.y = this.y - Game.map_grid.tile.width;
    }
  })
  },
});
Crafty.c('Player2', {
  init: function() {
    var old_key = null;
    this.requires('Actor, Fourway, Color, Collision')
      .color('rgb(255, 25, 25)')
      .bind("KeyDown",function(e) {
    if(e.key == Crafty.keys.A) {
      this.x = this.x - Game.map_grid.tile.width;
      old_key = e.key;
    } else if (e.key == Crafty.keys.D) {
      this.x = this.x + Game.map_grid.tile.width;
      old_key = e.key;
    } else if (e.key == Crafty.keys.W) {
      this.y = this.y - Game.map_grid.tile.width;
      old_key = e.key;
    } else if (e.key == Crafty.keys.S) {
      this.y = this.y + Game.map_grid.tile.width;
      old_key = e.key;
  }
  }).collision().onHit('Solid',function(){
    if(old_key == Crafty.keys.A) {
      this.x = this.x + Game.map_grid.tile.width;
    } else if (old_key == Crafty.keys.D) {
      this.x = this.x - Game.map_grid.tile.width;
    } else if (old_key == Crafty.keys.W) {
      this.y = this.y + Game.map_grid.tile.width;
    } else if (old_key == Crafty.keys.S) {
      this.y = this.y - Game.map_grid.tile.width;
    }
  }).collision().onHit('PLayer',function(){
    console.log("Hitting player 1")
  })
  },
});

Crafty.c('WinTileP1', {
  init: function() {
    this.requires('Actor, Color, Collision')
      .color('rgb(170, 125, 40)');
  },
  reach: function(){
    this.collision().onHit('Player',function()
    {
      //console.log("PLayer1 Win");
      Crafty.trigger('EndGame', "1");
    });
  }
});
Crafty.c('WinTileP2', {
  init: function() {
    this.requires('Actor, Color, Collision')
      .color('rgb(170, 125, 40)');
  },
  reach: function(){
    this.collision().onHit('Player2',function()
    {
      Crafty.trigger('EndGame', "2");
      //console.log("PLayer2 Win");
    });
  }
});
