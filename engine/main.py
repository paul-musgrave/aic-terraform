import json, subprocess, argparse, math
from itertools import islice
from collections import deque

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

    def __init__(self, mapFile):
        super(Terraform, self).__init__()
        self.nanoQueue = deque()
        self.bots = {}

        with open(mapFile, 'w') as f:
            mapFormat = f.readline() # read map type
            if 'plain' in mapFormat:
                # read first line of metadata
                self.terrainTypes, self.initPower, self.maxTurnss, self.viewRad = [int(x) for x in f.readline().split()]
                # read nano costs matrix
                self.nanoCosts = [[int(x) for x in line.split()] for line in list(islice(f, self.terrainTypes + 2))]
                self.nanoCosts['stableFactor'] = int(f.readline())
                # read map
                self.gameMap = [map(Tile,list(line)) for line in f]
            elif 'json' in mapFormat:
                ## TODO: Metadata in JSON?
                mapData = json.loads(f.read())
                self.gameMap = mapData.map
                self.nanoCosts = mapData.costs # Where is this going to be in plain text?
            else:
                raise Exception('Error: Unknown map format.')

        # initialize view radius and mask
        viewRad = self.viewRad
        viewRad2 = viewRad**2
        maskSize = 2*viewRad + 1
        viewMask = [[False for i in xrange(maskSize)] for j in xrange(maskSize)]
        for i in xrange(-viewRad, viewRad+1):
            for j in xrange(-viewRad, viewRad+1):
                if (i*i + j*j <= viewRad2):
                    viewMask[viewRad+i][viewRad+j] = True

        self.viewMask = viewMask
        ## Alternatively (immutable):
        # self.viewMask = tuple(tuple((True if (viewRad-r)**2 + (viewRad-c)**2 <= viewRad2
                                          # else False)
                                     # for c in xrange(maskSize))
                              # for r in xrange(maskSize))
        self.turnNo = 0
        self.replay = []

    def run(self, botFiles):
        for i, f in enumerate(botFiles):
            self.bots[i] = Bot(i, f)
            self.bots[i].start(self.initPower)

        while self.turnNo < self.maxTurns and len(self.bots) >= 1:
            self.replay.append([])
            self.propagateNano()
            for b in self.bots:
                # should we be providing their current power?
                for (x,y), t in self.getBotView(b).items():
                    b.stdin.write( "%d %d %s %d %s\n".format(x, y, t.terrain, t.owner or 0, t.spreadTo or 0) )
                b.stdin.write("go\n")
                b.genPower()
                self.doTurn(b)
            self.rmDead()

        for b in self.bots:
            b.stop()

        # could just write directly; would want to for streaming
        # buffered writer otherwise
        f = open('replay', 'w')
        f.write(json.dumps(self.replay))
        f.close()

        print "Surviving bots:"
        for b in self.bots:
            print b.id

    def doTurn(self, bot):
        botcmd = bot.stdout.readline()
        while (botcmd != 'go'):
            x, y, to, spread = botcmd.split()
            spread = int(spread)  # booleanize
            botcmd = bot.stdout.readline()  # read next cmd (for next loop)

            # validate input
            adjacentFactory = False
            for i in xrange(-1, 2):
                for j in xrange(-1, 2):
                    if (self.inBounds(x+i,y+j) and (x+i,y+j) in bot.factories):
                        adjacentFactory = True

            cost = self.getCost(self.gameMap[x][y].terrain, to, spread)
            if(adjacentFactory and bot.power >= cost):
                bot.power -= cost
                owner = bot.id if Terraform.TERRAIN[to] else None
                spreadTo = self.gameMap[x][y].terrain if spread else None
                tile = Tile(to, owner, spreadTo)
                self.gameMap[x][y] = tile

                if spread:
                    self.nanoQueue.append({'x': x, 'y': y, 't': tile})
            else:
                print "Invalid move by %d: %s" % bot.id, " ".join([x,y,to,spread])


    def propagateNano(self):
        q = self.nanoQueue
        self.nanoQueue = None
        for n in q:
            for i in xrange(-1, 2):
                for j in xrange(-1, 2):
                    x = n['x'] + i
                    y = n['y'] + j
                    if(self.inBounds(x,y) and self.gameMap[x][y].terrain == n['t'].spreadTo):
                        prev = self.gameMap[x][y]
                        #update owning bots
                        if(prev.owner != None):
                            self.bots[prev.owner].remTer(x, y, prev.terrain)
                        if(n['t'].owner != None):
                            self.bots[n['t'].owner].addTer(x, y, n['t'].terrain)
                        #update map and nanoQueue
                        self.gameMap[x][y] = n['t']
                        self.nanoQueue.append({'x': x, 'y': y, 't': n['t']})
                        self.replay[-1].append(n['t'])
                        #remove old nano
                        self.gameMap[n['x']][n['y']].spreadTo = None
                        self.replay[-1].append({'x': x, 'y': y, 't': self.gameMap[n['x']][n['y']]})

    def inBounds(self, x,y):
        return 0 <= x and x < len(self.gameMap) and 0 <= y and y < len(self.gameMap[0])

    #assuming non wrapping map
    def getBotView(self, b):
        view = {}
        for (xt,yt) in b.ownedTiles():
            for i,x in enumerate(xt-self.viewRad, xt+self.viewRad+1):
                if not self.inBounds(x,0):
                    continue
                for j,y in enumerate(yt-self.viewRad, yt+self.viewRad+1):
                    if not self.inBounds(0,y):
                        continue
                    if self.viewMask[i][j]:
                        view[(x,y)] = self.gameMap[x][y]
        return view

    def rmDead(self):
        for b in self.bots:
            if len(b.factories) == 0:
                self.killBot(b)

    def killBot(self, bId):
        self.bots[bId].stop()
        del self.bots[bId]
        print "bot " + bId + " killed."

    # Get the cost of a nanoswarm
    def getCost(self, base, result, spreading):
        return self.nanoCosts[base][result] * (1 if spreading else self.nanoCosts['stableFactor'])


class Tile(object):
    """A square of the game map"""
    def __init__(self, terrain, owner=None, spreadTo=None):
        super(Tile, self).__init__()
        self.terrain = terrain
        self.owner = owner
        self.spreadTo = spreadTo


class Bot(object):
    """A player bot"""
    def __init__(self, bId, handle):
        super(Bot, self).__init__()
        self.id = bId
        self.factories = []
        self.collectors = []
        self.handle = handle

    def start(self, initPower):
        ## doubtful about this buffer size now that we have multiple input lines
        self.io = subprocess.Popen(['python', self.handle], bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.stdin = self.io.stdin
        self.stdout = self.io.stdout

        self.power = initPower

    def stop(self):
        self.io.close()

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
        return 10 + 3*math.log(len(self.collectors)+1, 2)


def __main__():
    parser = argparse.ArgumentParser()
    parser.add_argument('bots', nargs='+',
                       help='bots to run (currently python)')
    parser.add_argument('-m',
                       help='map file')
    args = parser.parse_args()

    Terraform(args.m).run(args.bots)
