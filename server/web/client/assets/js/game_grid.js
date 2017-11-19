class grid{
    constructor(data)
    {
        this.mapGridWidth = data['boardSize']['width'];
        this.mapGridHeight = data['boardSize']['height'];
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
        return this.obstaclePositions;
    }
    get_playerPosition()
    {
        return this.playerPositions;
    }

}
