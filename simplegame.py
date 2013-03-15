import json, subprocess, argparse
from collections import deque


class Terraform(object):
    """A simple terraform engine"""
    TERRAIN = {
        # generic terrain types
        1: False,
        2: False,
        3: False,
        # owned terrain types
        'f': True,
        'c': True
    }

    def __init__(self, mapFile, maxTurn=1000, viewRad=5):
        super(Terraform, self).__init__()
        self.nanoQueue = deque()
        self.bots = {}
        # alternately, these could be map metadata
        self.maxTurn = maxTurn
        self.viewRad = viewRad
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
        self.viewMask = viewMask

        f = open(mapFile, 'r')
        self.gameMap = json.loads(f.read())
        f.close()

        self.turnNo = 0
        self.replay = []

    def run(self, botFiles):
        for i, f in enumerate(botFiles):
            self.bots[i] = Bot(i, f)
            self.bots[i].start()

        while self.turnNo < self.maxTurn and len(self.bots) >= 1:
            self.replay.append([])
            self.propagateNano()
            for b in self.bots:
                b.stdin.write(json.dumps(self.getBotView(b)))
                # initially only need one line of input
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
        x, y, to, spread = bot.stdout.read().split()
        ## TODO: validate input
        owner = bot.id if Terraform.TERRAIN[to] else None
        base = self.gameMap[x][y] if spread else None
        tile = Tile(to, owner, base)
        self.gameMap[x][y] = tile

        if(spread):
            self.nanoQueue.append({'x': x, 'y': y, 't': tile})

    def propagateNano(self):
        q = self.nanoQueue
        self.nanoQueue = None
        for n in q:
            for i in xrange(-1,1):
                for j in xrange(-1,1):
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
        visible = [[False] * len(self.gameMap[0])] * len(self.gameMap)  # map, init to False
        for (xt,yt) in b.ownedTiles():
            x0 = xt - self.viewRad
            y = y0 = yt - self.viewRad
            for i in xrange(0, len(self.viewMask)):
                x0 += 1
                if(not self.inBounds(x0)):
                    continue
                for j in xrange(0, self.maskSize):
                    y += 1
                    if(not self.inBounds(y)):
                        continue
                    if self.viewMask[i][j]:
                        visible[x0][y] = True
                y = y0
        return visible

    def rmDead(self):
        for b in self.bots:
            if len(b.factories) == 0:
                self.killBot(b)

    def killBot(self, bId):
        self.bots[bId].stop()
        del self.bots[bId]
        print "bot " + bId + " killed."


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

    def start(self):
        self.io = subprocess.Popen(['python', self.handle], bufsize=1, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.stdin = self.io.stdin
        self.stdout = self.io.stdout

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


def __main__():
    parser = argparse.ArgumentParser()
    parser.add_argument('bots', nargs='+',
                       help='bots to run (currently python)')
    parser.add_argument('-m',
                       help='map file')
    args = parser.parse_args()

    Terraform(args.m).run(args.bots)
