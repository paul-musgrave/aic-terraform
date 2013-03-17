import sys

class TestBot(object):
    """Simple player to test the engine"""
    def __init__(self):
        super(TestBot, self).__init__()

    def run(self):
        # get game start info until 'ready' once there is some
        while(True):
            try:
                #turn start
                self.factories = []
                ## DEBUG
                l = sys.stdin.readline()
                print >> sys.stderr, "l: " + l
                self.power = float(l)
                line = sys.stdin.readline()
                while(not 'go' in line):
                    x, y, terrain, owner, spreadTo = line.split()
                    if terrain == 'f' and int(owner) == 1:
                        self.factories.append( (int(x),int(y)) )
                    line = sys.stdin.readline()
                self.doTurn()
                sys.stdout.flush()
                print >> sys.stderr, "did turn"
            except EOFError:
                break

    def doTurn(self):
        (x,y) = self.factories[0]
        if self.power > 50:
            print x, (y+1), 'f', '1'
        print 'go'

if __name__ == "__main__":
    b = TestBot()
    b.run()
