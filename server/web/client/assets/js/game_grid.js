class grid{
    constructor(data)
    {
        this.mapGridWidth = data['boardSize']['width']+2;
        this.mapGridHeight = data['boardSize']['height']+2;
        this.playerPositions = data['playerPositions'];
        this.obstaclePositions = data['obstaclePositions'];
        this.tileWidth = 50;
        this.tileHeight = 50;
    }
    get_gridwidth()
    {
        return this.mapGridWidth;
    }
    get_gridheight()
    {
        return this.mapGridWidth;
    }
    get_tilesize()
    {
        return this.tileWidth;
    }
    width() {
        return this.mapGridWidth * this.tileWidth;
      }
    height()
    {
    return this.mapGridHeight * this.tileHeight;
    }
    get_obstaclePosition()
    {
        for (var i = 0;i<this.obstaclePositions.length;i++)
        {
            this.obstaclePositions[i]=[this.obstaclePositions[i][1]+1,this.obstaclePositions[i][0]+1];
        }
        
        return this.obstaclePositions;
    }
    get_playerPosition()
    {
        this.playerPositions[1] = [this.playerPositions[1][0]+1,this.playerPositions[1][1]+1];
        this.playerPositions[0] = [this.playerPositions[0][0]+1,this.playerPositions[0][1]+1];
        return [this.playerPositions[1],this.playerPositions[0]];
    }

}
