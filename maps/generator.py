# Map generator
# (currently random)

import argparse, random, json

# read arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('w', type=int, help='width of map to generate')
argparser.add_argument('h', type=int, help='height of map to generate')
argparser.add_argument('n', type=int, help='number of different terrain types')
argparser.add_argument('t', type=str, help='type of map (rnd, etc.)')
args = argparser.parse_args();

# seed rng
random.seed()

# random generator
def genRndMap():
    # generate w x h 2d list of random map data (including only terrain type)
    mapData = [[random.randint(1, args.n) for y in xrange(args.h)] for x in xrange(args.w)]

    # place initial factories at random locations
    mapData[0][0] = mapData[args.w - 1][args.h - 1] = 'f'

    # write output file
    with open('rnd-' + str(args.w) + '-' + str(args.h) + '-' + str(args.n) + '.map', 'w') as outputFile:
        for row in mapData:
            for tile in row:
                outputFile.write(str(tile))
            outputFile.write('\n')

# pick generator!
if args.t == 'rnd':
    genRndMap()
