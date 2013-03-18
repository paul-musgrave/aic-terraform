// could easily do streaming with websocket: for each turn diff recived, add to replay data, update a mapState, check if keyframe.
// if streaming, in controller use: if(selectedTurn < loadedTurn){[draw] getMap}

var replayData;
/*
{
    gameLength: ,
    turns: [
        {row:, col:, owner:, type:}
    ],
    map: [ //##?
        [
            [owner,type]
        ]
    ]
}

*/

var keyframes;

var KEYFRAME_INTERVAL = 20;


function Replay() {

}



function load(data) {
    replayData = JSON.parse(data);
    keyframes = new Array(replayData.gameLength / KEYFRAME_INTERVAL);
    computeKeyFrames();
}

//## if anything needs cpu limiting, it's this
function computeKeyFrames(){
    var mapState = keyframes[0] = replayData.map;
    for (var i = 0; i < replayData.gameLength; ) {
        applyTurn(mapState, i++);
        if(i % KEYFRAME_INTERVAL === 0) keyframes[i] = mapState;
    }
}


function getDiff(turn){
    return replayData.turns[turn];
}

function getMap(turn){
    var prevkey = Math.floor(turn/KEYFRAME_INTERVAL) * KEYFRAME_INTERVAL;
    var mapState = keyframes[prevkey];
    for (var i = 0; i < turn - prevkey; i++) {
        applyTurn(mapState, i);
    }
    return mapState;
}


function applyTurn (state, turnNo) {
    var t = replayData.turns[turnNo];
    for (var i = t.length - 1; i >=0 ; i--) {
        state[t[i].row][t[i].col] = {owner: t[i].owner, type: t[i].type};
    }
}
