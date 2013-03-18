
var curTurn;


function nextTurn(){
    updateTiles(replay.getDiff(curTurn++));
    //if(fogChanged) renderFog();
}

function setTurn(turn){
    curTurn = turn;
    drawMap(replay.getMap(turn));
}

//zoom, scroll