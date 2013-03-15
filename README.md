
### Mechanics / tactics ###
Another subtle ordering issue: to be consistent with a "earlier seeds move first" rule and
comprehesibility, existing seeds need to spread at the beginning of the turn (before all players), not the end. Otherwise,
you would have to simulate one step to know what state the seeds you place will be acting on.

Should tiles of the same type with different owners count as different for the purpose of 
spreading? This can have significant effects.

Let's consider the following situation with a few different mechanics assumptions.

    fa fa fa fa fa
    1  1  1* 1  1
    2  2  2  2  2
    fb fb fb fb fb

First, manhatten spreading and order-of-creation.
Suppose 'a' wants to attack. If 'a' places *:1->2, then next turn @:2->fa on the same spot:

    fa  fa  fa  fa  fa          fa  fa  fa  fa  fa         fa  fa  fa  fa  fa        fa  fa  fa  fa  fa
    1  *2  @fa *2   1    t1->  *2  @fa  fa @fa *2   b:->  *2  @fa  fa @fa *2   t2-> @fa  fa $1   fa @fa
    2   2  *2   2   2           2   2  @fa  2   2          2   2  $1   2   2         2  $1   1  $1   2 
    fb  fb  fb  fb  fb          fb  fb  fb  fb  fb         fb  fb  fb  fb  fb        fb  fb  fb  fb  fb

This is bad for 'a', assuming 'b' does the obvious $:fa->1. 'a' can counter with a 1->2 on $, which saves his original factories but nothing else.
(Is there a better move for 'a'?)

(It seems like king spreading favors the attacker a bit more, and team-independant spreading opens up some new attacks, but not sure - more complicated attacks get complicated :P)

Ok, in the process of doing that, I changed my mind about what would happen like three times.
We really need to make a simulator where we can manually control the moves and ideally also tweak the mechanics - this is hard.
(On a side note, this could actually be a fun game for humans, appropriately modified. Might do that at some point.)

