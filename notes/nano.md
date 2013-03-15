# Nanoswarms (Nanos)

## Nano types

Each nanoswarm will have a `baseType` and a `resType`, such that the nano converts tiles of terrain type `baseType` to `resType` **immediately** upon being placed upon a tile.

The presence of nano on a tile is indicated by a non-None value of `tile.spreadTo`. This indicates a nano that converts tiles of type `tile.spreadTo` to type `tile.terrain`.

Tiles may eventually have a `nano` attribute, which would contain the vale of `spreadTo` and other hypothetical nano properties such as speed.
