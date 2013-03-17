# Map generator
# (currently random)

import argparse, random, json

# game parameters
viewRad = 5
maxTurns = 1000
initPower = 100
terrainTypes = 5

# terrain types 1..n, 'f', 'c' as columns
nanoCosts = [[00, 10, 10, 10, 10, 50, 30], #turn terrain 1 into terrain n
             [10, 00, 10, 10, 10, 50, 30], #turn terrain 2 into terrain n
             [10, 10, 00, 10, 10, 50, 30], #...
             [10, 10, 10, 00, 10, 50, 30],
             [10, 10, 10, 10, 00, 50, 30],
             [05, 05, 05, 05, 05, 00, 10],
             [05, 05, 05, 05, 05, 30, 00]]
stableFactor = 1

if len(nanoCosts) != terrainTypes + 2:
    raise Exception('nanoCosts matrix has incorrect dimension')

# read arguments
argparser = argparse.ArgumentParser()
argparser.add_argument('w', type=int, help='width of map to generate')
argparser.add_argument('h', type=int, help='height of map to generate')
argparser.add_argument('t', type=str, help='type of map (rnd, etc.)')
args = argparser.parse_args();

# seed rng
random.seed()

# random generator
def genRndMap(outputFile):
    # generate w * h 2d list of random map data (including only terrain type)
    mapData = [[random.randint(1, terrainTypes) for y in xrange(args.h)] for x in xrange(args.w)]

    # place initial factories at random locations
    mapData[0][0] = mapData[args.w - 1][args.h - 1] = 'f'

    # assign factory owners
    outputFile.write("2\n")  # number of factories
    outputFile.write("%d %d 1\n" % (0, 0))  # x y owner
    outputFile.write("%d %d 2\n" % (args.w-1, args.h-1))

    # write output file
    for row in mapData:
        for tile in row:
            outputFile.write(str(tile))
        outputFile.write('\n')

# write metadata
with open('-'.join([str(args.t), str(args.w), str(args.h), str(terrainTypes)]) + '.map', 'w') as outputFile:
    outputFile.write('plain\n')
    outputFile.write(' '.join([str(terrainTypes), str(initPower), str(maxTurns), str(viewRad)]) + '\n')

    for row in nanoCosts:
        for entry in row:
            outputFile.write(str(entry) + ' ')
        outputFile.write('\n')
    outputFile.write(str(stableFactor) + '\n')

    # pick generator!
    if args.t == 'rnd':
        genRndMap(outputFile)
