import sys, random

class TestBot(object):
    """A more persistant random bot"""
    def __init__(self):
        super(TestBot, self).__init__()

    def run(self):
        # get game start info until 'ready' once there is some
        while(True):
            try:
                #turn start
                self.factories = []
                self.power = float(sys.stdin.readline())
                line = sys.stdin.readline()
                while(not 'go' in line):
                    x, y, terrain, owner, spreadTo = line.split()
                    if terrain == 'f' and int(owner) == 1:
                        self.factories.append( (int(x),int(y)) )
                    line = sys.stdin.readline()
                self.doTurn()
                sys.stdout.flush()
            except EOFError:
                break

    def doTurn(self):
        if self.power > 50:
            for (x,y) in random.sample(self.factories, len(self.factories)):
                x += random.randint(-1,1)
                y += random.randint(-1,1)
                if not (x,y) in self.factories:
                    print x, y, 'f', '1'
                    break
        #print >> sys.stderr, self.factories ## DEBUG
        #print >> sys.stderr, x, y ## DEBUG
        print 'go'

if __name__ == "__main__":
    b = TestBot()
    b.run()
