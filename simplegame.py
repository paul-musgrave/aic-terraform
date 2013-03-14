import json, subprocess, argparse


def doTurn(id, botInput):
    x, y, to = botInput.split()
    if(to == 'b'): ## blank tile, doesn't spread
        gameMap[x][y] = {'terrain': 'b', 'owner': None}
    else:
        spreadNano(x, y, {'terrain': to, 'owner': id if TERRAIN[to] else None})

# naive implementation loops infinitely on x->x nano (shouldn't exist)
def spreadNano(x, y, to):
    prev = gameMap[x][y]
    gameMap[x][y] = to
    for i in xrange(-1,1):
        for j in xrange(-1,1):
            if(inBounds(x+i,y+j) and gameMap[x+i][x+j] == prev):
                spreadNano(x+i, y+j, to)

    to['x'] = x, to['y'] = y
    if(prev['terrain'] == 'HQ'): #check HQ destruction
        killBot(prev['owner'])
    if(prev['owner'] != None):
        bots[prev['owner']]['tiles'].remove(to) #@@
    if(to['owner'] != None):
        bots[to['owner']]['tiles'].append(to)
    replay[-1].append(to)


def inBounds(x,y):
    return 0 <= x and x < len(gameMap) and 0 <= y and y < len(gameMap[0])

#assuming non wrapping map
def getBotView(ownedTiles):
    visible = [[False] * len(gameMap[0])] * len(gameMap) #map, init to False
    for t in ownedTiles:
        x0 = t['x'] - viewRad
        y = y0 = t['y'] - viewRad
        for i in xrange(0,maskSize):
            x0 += 1
            if(not inBounds(x0)):
                continue
            for j in xrange(0,maskSize):
                y += 1
                if(not inBounds(y)):
                    continue
                if viewMask[i][j]:
                    visible[x0][y] = True
            y = y0
    return visible


def killBot(id):
    bots[id].close()
    del bots[id]
    print "bot "+i+" killed."


#main
parser = argparse.ArgumentParser()
parser.add_argument('bots', nargs='+',
                   help='bots to run (currently python)')
parser.add_argument('-m',
                   help='map file')
args = parser.parse_args()

#read map
f = open('map', 'r')
mapData = json.loads(f.read())
f.close()

#open bots
bots = {}
for i, b in enumerate(args.bots):
    bots[i] = subprocess.Popen(['python', b], bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

botTiles = [] * len(bots)

#run
maxTurn = 1000

viewRad = 5
viewRad2 = viewRad*viewRad
maskSize = 2*viewRad + 1
viewMask = [[False] * maskSize] * maskSize
for i in xrange(0, viewRad):
    for j in xrange(0, viewRad):
        if (i*i + j*j <= viewRad2):
            viewMask[viewRad+i][viewRad+j] = True
            viewMask[viewRad+i][viewRad-j] = True
            viewMask[viewRad-i][viewRad+j] = True
            viewMask[viewRad-i][viewRad-j] = True

turnNo = 0
gameMap = mapData
replay = []

TERRAIN = {
    1: False,
    2: False,
    3: False,
    'b': False,
    'HQ': True,
    'f': True
} ##

while(turnNo < 1000 and len(bots) >= 1):
    replay.append([])
    for i,b in bots:
        b.stdin.write(json.dumps(getBotView(botTiles[i]))) #//@
        # initially only need one line of input
        doTurn(i, b.stdout.read())

for i,b in bots:
    b.close()

# could just write directly; would want to for streaming
# buffered writer otherwise
f = open('replay', 'w')
f.write(json.dumps(replay))
f.close()

print "Surviving bots:"
for i in bots:
    print i

