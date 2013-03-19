import json, subprocess, argparse, math
from itertools import islice
from collections import OrderedDict


class Terraform(object):
    """A simple terraform engine"""

    ## TODO: move this and other global constants to constants file
    TERRAIN = {
        # generic terrain types
        1: False,
        2: False,
        3: False,
        # owned terrain types
        'f': True,
        'c': True
    }

    # counterclockwise from east
    DIRS = [ (1,0),
             (1,-1),
             (0,-1),
             (-1,-1),
             (-1,0),
             (-1,1),
             (0,1),
             (1,1) ]

    def __init__(self, mapFile):
        super(Terraform, self).__init__()
        self.nanoQueue = OrderedDict()
        self.bots = {}
        self.replay = { 'turns':[] }
        with open(mapFile, 'r') as f:
            mapFormat = f.readline() # read map type
            if 'plain' in mapFormat:
                # read first line of metadata
                self.terrainTypes, self.initPower, self.maxTurns, self.viewRad = [int(x) for x in f.readline().split()]
                # read nano costs matrix
                self.nanoCosts = [[int(x) for x in line.split()] for line in list(islice(f, self.terrainTypes + 2))]
                self.stableFactor = int(next(f))
                # read initial factory owners
                nFact = int(next(f))
                factories = [[int(x) for x in line.split()] for line in list(islice(f, nFact))]
                # read map
                self.gameMap = [map(Tile,list(line.rstrip())) for line in f]
            else:
                raise Exception('Error: Unknown map format.')


        # assign factories
        self.players = {}  # used to put initial factories in bot.factories once they exist... a bit ugly
        for f in factories:
            self.gameMap[f[0]][f[1]].owner = f[2]
            if(f[2] in self.players):
                self.players[f[2]].append( (f[0],f[1]) )
            else:
                self.players[f[2]] = [(f[0],f[1])]
        self.replay['map'] = [[t.json() for t in x] for x in self.gameMap]

        # pad map with false Tile to avoid most inbounds checking
        # (only need outside since python wraps negative indicies)
        self.mapX = len(self.gameMap)
        self.mapY = len(self.gameMap[0])
        falseTile = Tile(False, False, False)
        for c in self.gameMap:
            c.append(falseTile)
        self.gameMap.append([falseTile] * (self.mapY + 1))

        self.viewMasks = computeViewMasks(self.viewRad)
        self.turnNo = 0

    def run(self, botFiles):
        for i, f in enumerate(botFiles):
            self.bots[i+1] = Bot(i+1, f, self.players[i+1])
            self.bots[i+1].start(self.initPower)

        while self.turnNo < self.maxTurns and len([b for b in self.bots.values() if b.alive]) > 1:
            print "Turn", self.turnNo
            self.replay['turns'].append([])
            self.propagateNano()
            self.rmDead()
            for b in self.bots.values():
                if b.alive:
                    # provide each bot with their current power
                    b.stdin.write( str(b.power) + '\n' )
                    for (x,y), t in self.getBotView(b).items():
                        # make all bots see themselves as player 1
                        apparentOwner = ((t.owner - b.id) % len(self.players)) + 1 if t.owner else 0
                        b.stdin.write( "%d %d %s %d %s\n" % (x, y, t.terrain, apparentOwner, t.spreadTo or 0) )
                    b.stdin.write("go\n")
                    b.stdin.flush()
                    b.genPower()
                    self.doTurn(b)
                    self.rmDead()
            self.turnNo += 1

        print "Surviving bots:"
        for b in self.bots.values():
            if b.alive:
                print b.id
                b.stop()

        # could just write directly; would want to for streaming
        # buffered writer otherwise
        f = open('replay.json', 'w')
        f.write(json.dumps(self.replay))
        f.close()


    def doTurn(self, bot):
        botcmd = bot.stdout.readline()
        while (not 'go' in botcmd):
            print "Bot", bot.id, ":", botcmd,
            try:
                x, y, resType, spread = botcmd.split()
                x = int(x)
                y = int(y)
                spread = int(spread)  # booleanize

                # validate input
                if not self.inBounds(x,y):
                    raise GameError("outside of map.")

                adjacentFactory = False
                for dx,dy in Terraform.DIRS:
                    if (x+dx,y+dy) in bot.factories:
                        adjacentFactory = True
                        break;
                if (x,y) in bot.factories:
                    adjacentFactory = True
                if not adjacentFactory:
                    raise GameError("no adjacent factory.")

                cost = self.getCost(self.gameMap[x][y].terrain, resType, spread)
                if bot.power < cost:
                    raise GameError("not enough power.")

                bot.power -= cost
                owner = bot.id if Terraform.TERRAIN[resType] else None
                spreadTo = self.gameMap[x][y].terrain if spread else None
                self.setTile(x, y, Tile(resType, owner, spreadTo))

                if spread:
                    self.nanoQueue.pop((x,y), None)  # delete if exists
                    self.nanoQueue[(x,y)] = True  # unused value
            except GameError as e:
                print "Invalid move:", e
            except ValueError:
                print "Invalid move: bad command format."

            botcmd = bot.stdout.readline()  # read next cmd (for next loop)


    def propagateNano(self):
        q = self.nanoQueue
        self.nanoQueue = OrderedDict()
        for (nx,ny) in q:
            nt = self.gameMap[nx][ny]
            for dx,dy in Terraform.DIRS:
                x = nx + dx; y = ny + dy
                if(self.gameMap[x][y].terrain == nt.spreadTo):
                    self.setTile(x,y,nt.copy())
                    self.nanoQueue.pop((x,y), None)
                    self.nanoQueue[(x,y)] = True
            #remove old nano
            nt.spreadTo = None
            self.replay['turns'][-1].append({'x': nx, 'y': ny, 't': nt.json()})

    def setTile(self, x, y, tile):
        prev = self.gameMap[x][y]
        self.gameMap[x][y] = tile
        if(prev.owner != None and self.bots[prev.owner].alive):
            self.bots[prev.owner].remTer(x, y, prev.terrain)
        if(tile.owner in self.bots and self.bots[tile.owner].alive):
            self.bots[tile.owner].addTer(x, y, tile.terrain)
        self.replay['turns'][-1].append({'x': x, 'y': y, 't': tile.json()})

    def inBounds(self, x,y):
        return 0 <= x < self.mapX and 0 <= y < self.mapY

    #assuming non wrapping map
    def getBotView(self, b):
        gameMap = self.gameMap
        viewMasks = self.viewMasks
        view = {}
        for (xt,yt) in b.ownedTiles():
            adj = [0,0,0,0,0,0,0,0]
            for i, (dx, dy) in enumerate(Terraform.DIRS):
                if gameMap[xt+dx][yt+dy].owner == b.id:
                    adj[i] = 1
            for dx,dy in viewMasks[tuple(adj)]:
                x = xt + dx; y = yt + dy
                if self.inBounds(x,y):
                    view[(x,y)] = gameMap[x][y]

        return view

    def rmDead(self):
        for b in self.bots.values():
            if len(b.factories) == 0 and b.alive:
                b.stop()
                print "bot ", b.id, " killed."

    # Get the cost of a nanoswarm
    def getCost(self, base, result, spreading):
        conversions = {'f': -2, 'c': -1}
        base = conversions[base] if base in conversions else int(base)
        result = conversions[result] if result in conversions else int(result)
        return self.nanoCosts[base][result] * (1 if spreading else self.stableFactor)


def computeViewMasks(rad):
    adjs = [[]]
    for i in xrange(0,8):
        tmp = []
        for a in adjs:
            tmp.append(a+[0])
            tmp.append(a+[1])
        adjs = tmp
    return dict((tuple(a), computeMask(a, rad)) for a in adjs)

# this is not very efficient, it needlessly recomputes the segments each time
def computeMask(a, rad):
    # east counterclockwise adjacency
    # east-north counterclockwise segments
    rad2 = rad*rad
    segs = ( lambda i,j: (i,-j),
             lambda i,j: (-j,i),
             lambda i,j: (-j,-i),
             lambda i,j: (-i,-j),
             lambda i,j: (-i,j),
             lambda i,j: (j,-i),
             lambda i,j: (j,i),
             lambda i,j: (i,j) )
    # exclude the half-plane centered on directions with an adjacent
    # owned tile
    viewsegs = [ segs[i] for i in xrange(0,8)
                 if not (a[i-1] or a[i] or a[(i+1) % 8] or a[(i+2) % 8]) ]
    # exclude segment borders (+ and x) if strictly inside excluded
    # half-plane
    crossd = [ segs[i] for i in xrange(0,8,2)
                if not (a[i-1] or a[i] or a[i+1 % 8]) ]
    xd = [ segs[i] for i in xrange(-1,7,2)
            if not (a[i-1] or a[i] or a[i+1 % 8]) ]

    mask = [(0,0)]
    for i in xrange(1,rad+1):
        for d in crossd:
            mask.append( d(i,0) )
        if 2*i*i <= rad2:
            for d in xd:
                mask.append( d(i,i) )

        for j in xrange(1,i):
            if i*i + j*j <= rad2:
                for s in viewsegs:
                    mask.append( s(i,j) )
    return mask


class Tile(object):
    """A square of the game map"""
    def __init__(self, terrain, owner=None, spreadTo=None):
        self.terrain = terrain
        self.owner = owner
        self.spreadTo = spreadTo

    def json(self):
        return { "t": self.terrain, "o": self.owner, "s": self.spreadTo }

    def copy(self):
        return Tile(self.terrain, self.owner, self.spreadTo)


class Bot(object):
    """A player bot"""
    def __init__(self, bId, handle, initFactories):
        super(Bot, self).__init__()
        self.id = bId
        self.factories = initFactories
        self.collectors = []
        self.handle = handle
        self.alive = False

    def start(self, initPower):
        ## we will use a fully buffered io stream (bufsize = -1)
        self.io = subprocess.Popen(['python', self.handle], bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.stdin = self.io.stdin
        self.stdout = self.io.stdout

        self.power = initPower
        self.alive = True

    def stop(self):
        self.io.terminate()
        self.alive = False

    # these are almost, but not quite, easy to do functionally in python
    def addTer(self, x, y, ter):
        if(ter == 'f'):
            self.factories.append( (x,y) )
        elif(ter == 'c'):
            self.collectors.append( (x,y) )

    def remTer(self, x, y, ter):
        if(ter == 'f'):
            self.factories.remove( (x,y) )
        elif(ter == 'c'):
            self.collectors.remove( (x,y) )

    def ownedTiles(self):
        return self.factories + self.collectors

    def genPower(self):
        self.power += 10 + 3*math.log(len(self.collectors)+1, 2)


class GameError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('bots', nargs='+',
                       help='bots to run (currently python)')
    parser.add_argument('-m',
                       help='map file')
    args = parser.parse_args()
    print "Running Terraform"
    Terraform(args.m).run(args.bots)
