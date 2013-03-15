# Map

## General

A map is a grid-type representation of the world. No dimension of the map will exceed 1000 squares. The internal representation of the game map is named `gameMap`, which is a 2d array. The square at `(x, y) = (2, 4)` is accessed with `gameMap[2][4]`.

Each square will have a particular terrain type (see below).

## Squares/terrain

Internally, each square will have the following properties associated with it:

    gameMap[x][y] = {
        'terrain': TERRAIN,
        'owner': id OR None
        'nano': baseType OR None
    }

where `baseType` specifies the base type of the nanoswarm (see nano.md).

`TERRAIN` is a set of terrain types as follows:

    TERRAIN = {
        1: False,
        2: False,
        ...
        n: False,
        'H': True, # HQ
        'f': True, # factory
        ...
    }

where each terrain type is mapped to a boolean value indicating whether the particular terrain type can have ownership. Types `1, ..., n` will represent generic terrain types, and characters will be used for specialized squares.

The conversion costs from terrain type A to terrain type B are passed to each player bot at the beginning of each game.