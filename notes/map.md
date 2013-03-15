# Map

## General

A map is a grid-type representation of the world. No dimension of the map will exceed 1000 squares. The internal representation of the game map is named `gameMap`, which is a 2d array. The square at `(x, y) = (2, 4)` is accessed with `gameMap[2][4]`.

Each square has an associated Tile object (see below).

## Squares/terrain

Internally, map squares are represented by a Tile class with the following attributes:

    tile.terrain:  TERRAIN
    tile.owner:    id OR None
    tile.spreadTo: TERRAIN OR None

where `spreadTo` indicates the presense of a nanoswarm that spreads to terrain this type (see nano.md).

`TERRAIN` is a set of terrain types as follows:

    TERRAIN = {
        1: False,
        2: False,
        ...
        n: False,
        'f': True, # factory
        'c': True, # collector
        ...
    }

where each terrain type is mapped to a boolean value indicating whether the particular terrain type can have ownership. Types `1, ..., n` will represent generic terrain types, and characters will be used for specialized squares.

The conversion costs from terrain type A to terrain type B are passed to each player bot at the beginning of each game.
