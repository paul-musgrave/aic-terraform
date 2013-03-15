--- NOTE: OLD, SEVERAL PARTS ARE OUTDATED NOW ---

Land War
(Note: make an "Asia" map)

Nano theme:
    Pure nano:
        Terrain types:
        Base:
            Do any of these have any effect, or are they just arbitrary terrain divisors? In the latter case, just pick a thematic/visually appealing set and identify them by number / fixed set of letters to the player. Different maps could potentially use different themes
            Will still be used by the player if it is cheap to convert to (/from?) them
            "Desolate": Metal, Rock/Sand, Crystal/Glass, Ice, Dust, Lava
            "Earth": Wooded, Rocky, Grasslands, Water, Desert



        Owned:
            Factory
                Alternately, bases could be the only factories; role could be played by pipelines, but don't want enemies to be able to propagate back along any pipeline to the base - secondary type somehow? any other owned type also acts as connector? In the latter case, you could intersperse e.g. collectors (mines?) to segment your pipeline
                Another alternative could be to allow any owned tiles to place nano adjacent
            Sensor
                Should this be separate? Could have a smaller vision radius for all owned tiles and sensors with a large vision range
            Solar/Collector/?
            ?Attack
                Nano Mine - destroys next (contiguous area of) owned terrain belonging to another player that ends up adjacent, then turns into some base terrain. Would be countered by placing a small disconnected piece next to it
                    Presumably activates by connected region
                    Double activation of distinct mine-regions by a single enemy-region? Similar problem to conflicting nano deployment. Could have both trigger, making this a mine counter, or just one

        Special:
            Inert - single square (doesn't spread). Used to separate types.
            ?Fixed shape (e.g. line of length n) deployments
                Don't want these to dominate territory capture (well, I guess they could - it would be a different game, but perhaps still interesting)

            Nano with limited 'from' type that creates special terrain?
            e.g. generator on lava, observatory on mountain. These from types may or may not be able to be created (making it an extra step, possibly quite expensive, if you can't find the 'from' terrain naturally)

        Mechanics:
            Can place typeA -> typeB nano on any tile next to a factory, for a cost depending on the types
                Once/turn?
                    + Simple
                    - Penalizes inert, might make it hard for even a much richer enemy to assault
                    Could compensate for this by making it take several turns to save up for most nano unless you have exceptional resource generation
                Once/base?
                    How to determine which factories belong to which base?
                    Inherited from parent factory?
                    Connection to base with owned square of any type?
                        Encourages players to connect their bases
                    Is is still too expensive to separate your factories, since it takes a full turn for that base?
                Cost limited?
                    Options for conflicting nano:
                        1. Nanos propagate iteratively, resulting in the area being split
                        2. Nanos deploy completely and in order
                            a. Allow chains, e.g. 
                                y  x  x      y  y  y      a  a  a
                                y  x* f1 ->  y  y  f1 ->  a  a  f1
                                y  x@ f2     y  y@ f2     a  a  f2
                                on one turn with f1 deploying *:x->y and f2 deploying @:y->a afterwards
                            b. Only allow deployment of nano eating the current target square type; then nanos after the first do nothing because they're on the wrong source type. Needs some bookkeeping

        Goals:
            Simplest: turn your enemies' base(s) into inert matter


        Notes:
            Terminology - nano converts terrain?




Description:

The objective of the game is to take over the map and convert your enemies' nanofactories into inert matter. To do this, you transform terrain with nanoswarms. Nanoswarms change all connected squares of one type into another. You can build these nanoswarms on any square adjacent your factories. For example, if a factory 'f1' deploys a x->y nanoswarm at *:

y  x  x      y  y  y 
y  x* f1 ->  y  y  f1
y  x  z      y  y  z

Normal nanoswarms cost 10 energy. You can also build nanoswarms that create special terrain:
Factory (Cost: 100)
    Allows the creator to build nanoswarms adjacent to the factory tiles
Collector (Cost: 50)
    Increase the energy generation rate of the creator by 1/square/turn

and nanoswarms that change a single square into empty terrain (Cost: 20).

At the beginning of the game, the map consists of initial factories for each player and an unknown arrangement of the basic terrain types. Each initial factory generates 10 energy/turn. Players can see only the squares within radius 10 of one of their factories.

Players take turns sequentially, which consist of three phases:
    1. Collect energy
    2. (Optionally) place one nanoswarm
    3. Nanoswarm transforms terrain
