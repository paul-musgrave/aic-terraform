# Bot input/output

# Output

Every turn, each bot will output a line in the following format:

    x y resType

This line represents a new nanoswarm placed at tile `(x, y)`, converting the terrain at `(x, y)` to the terrain type specified by `resType`.

# Input

At the beginning of the game, each bot will be given the following data:

    nanoCosts[x][y] # cost to create a swarm to convert terrain type x to terrain type y
    viewRadius2     # visibility radius squared for all nanoswarms (factories?)

The data that each bot receives every turn is yet to be determined.    