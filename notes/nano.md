# Nanoswarms (Nanos)

## Nano types

Each nanoswarm will have a `baseType` and a `resType`, such that the nano converts tiles of terrain type `baseType` to `resType` **immediately** upon being placed upon a tile.

The internal representation of this will be in each `gameMap[x][y].nano`, but we will only store the `baseType` of each nano. The `resType` can be retrieved using the `terrain` key of `gameMap[x][y]`.