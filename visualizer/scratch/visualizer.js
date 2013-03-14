//Notes:
//fog interface is not currently right

var TILES = [ [], ... ] @

var map;

//tile: {row col type owner}

function updateTiles(tiles) {
    
    var t;
    for (var i = tiles.length - 1; i >= 0; i--) {
        t = tiles[i];
        drawTile(t);
        //updateFogAt(t); 
        map[t.row][t.col] = {owner: t.owner, type: t.type};
    }

}

function drawMap(newMap){
    map = newMap;
    for (var i = 0; i < map.length; i++) { //## right order?
        for (var j = 0; j < map[0].length; j++) {
            drawTile(map[i][j]);
        }
    }
}

function drawTile(tile){
    terrainCanvas.ctx.setFillStyle(TILES[tile.type][tile.owner]); //## can't get context like this
    terrainCanvas.ctx.drawRect(tile.col*TILE_W, tile.row*TILE_H, TILE_W, TILE_H); //## always square?
}

function updateFogAt(tile){
    //## in practice, if one tile is a changed viewtile, many will be...
    if(fogPlayer){
        if(fogPlayer != map[tile.row][tile.col] && fogPlayer == tile.owner){
            //clear fog
        } else if (fogPlayer == map[tile.row][tile.col] && fogPlayer != tile.owner){
            //replace fog in area
        }
    }
}

