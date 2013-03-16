# Bot input/output

# Output

Every turn, each bot will output lines in the following format:

    x y resType spread

This represents a new nanoswarm placed at tile `(x, y)`, converting the terrain at `(x, y)` to the terrain type specified by `resType`.
`spread` is 1 or 0 indicating whether the nanoswarm spreads to adjacent tiles of the same type.

After the bot has finished placing nanoswarms, it will output the literal `go` as the last line.

# Input

At the beginning of the game, each bot will be given the following data:

    nanoCosts[x][y] # cost to create a swarm to convert terrain type x to terrain type y
    viewRadius2     # visibility radius squared for all nanoswarms (factories?)

Every turn, each bot will receive the following data terminated with the literal `go` as the last line.

    currentPower    # amount of power bot currently has
    for each visible tile to bot:
        x y terrain owner spreadTo

Each such tile data line will represent the tile `(x, y)`, belonging to `owner` (or 0 if ownership does not apply), and of type `terrain`. If there is a nanoswarm on the tile, `spreadTo` will indicate the resulting terrain type of the swarm.