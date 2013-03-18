import cairo
import pygame, json, math, time


# Initialize pygame with 32-bit colors.
pygame.init()
size = 400, 400
screen = pygame.display.set_mode(size, 0, 32)
clock = pygame.time.Clock()

mapColors = {'1': [pygame.Color(47, 189, 47, 1)],
             '2': [pygame.Color(47, 57, 189, 1)],
             '3': [pygame.Color(140, 108, 21, 1)],
             '4': [pygame.Color(115, 109, 92, 1)],
             '5': [pygame.Color(110, 48, 52, 1)],
             'f': [pygame.Color(0, 251, 255, 1), pygame.Color(255, 0, 255, 1), pygame.Color(255, 255, 0, 1)],
             'c': [pygame.Color(0, 251, 255, 1), pygame.Color(255, 0, 255, 1), pygame.Color(255, 255, 0, 1)]}
def drawMap(mapFile, array=False):
  if array:
    res = []
    gridWidth, gridHeight = size[0]/len(mapFile[0]), size[1]/len(mapFile)
    for y, row in enumerate(mapFile):
      res.append([pygame.draw.rect(screen,
                                   mapColors[box['t']][box['o'] or 0],
                                   (x*gridWidth, y*gridHeight, gridWidth, gridHeight))
                                   for x, box in enumerate(row)])
  else:
    f = open(mapFile, 'r')
    mapGrid = [list(line.rstrip()) for line in f]
    gridWidth, gridHeight = size[0]/len(mapGrid[0]), size[1]/len(mapGrid)
    res = []
    for y, row in enumerate(mapGrid):
      res.append([pygame.draw.rect(screen,
                                   mapColors[box][0],
                                   (x*gridWidth, y*gridHeight, gridWidth, gridHeight))
                                   for x, box in enumerate(row)])
  return res
 
def viewReplay(replayFile):
  f = open(replayFile, 'r')
  print "Loading replay file..."
  replayObj = json.loads(f.read())
  f.close()
  gameMap = replayObj['map']
  mapGrid = drawMap(gameMap, array=True)

  turnNum = 0
  turns = replayObj['turns']
  # Run "main" loop for viewing replays.
  for turn in turns:
    turnNum += 1
    for move in turn:
      pygame.draw.rect(screen, mapColors[move['t']['t']][move['t']['o'] or 0], mapGrid[move['x']][move['y']])
    pygame.display.flip()
    yield
  showReplay = False
      
replay = viewReplay('../replay.json')
showReplay = True
while pygame.QUIT not in [e.type for e in pygame.event.get()]:

  if showReplay:
    try:
      replay.next()
    except StopIteration:
      showReplay = False
      print "Replay has finished."
  clock.tick(60)
