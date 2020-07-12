Known Bugs:
- Selection from rack not highlighted - functionality not affected
- Beetle is occasionally broken - reason unknown, need investigation
- Insect (Ant noted) can occasionally slide into space that breaks Freedom-to-move rule

#### 16/06/2020 - 23/06/2020
Known bugs:
- ~~Beetle was allowed to break hive~~

Notes:
- Option to start game with all pieces on the board in random state with seed
- MCTS implemented but extremely slow when given the choice of all pieces to select moves from
- Steps taken to optimise include:
    - Moves from rack only consider each insect rather than each piece
    - Noted that the length of time to determine possible moves is drastically different depending on insect (random seed = 13):
        - Grasshopper: 0.08 seconds
        - Beetle: 0.5 seconds
        - Bee: 0.17 seconds
        - Spider: 1.3 seconds
        - Ant: 4.8 seconds
    - Optimised Spider to a time of 0.08 seconds (!) by removing one of the two One-Hive checkers and implementing custom approach
    - Optimised Ant to a time of 0.08 seconds (!) by removing one of the two One-Hive checkers and implementing custom approach
    - Optimised Beetle to a time of 0.08 in the same manner
    - Optimised Bee to a time of 0.08 in the same manner
    - Grasshopper modified in the same manner to no benefit or detriment
- Noted that the current One-Hive check which determines if merely moving away from position breaks the hive increases time taken by a factor of 4000!

#### 24/06/2020 - 01/07/2020
Notes:
- Speed optimised for MCTS by profiling the code - deep copies were the source of major slowdowns
- Freedom to move rule was completely wrong - now fixed
- Numbers can be displayed over the board for debugging purposes (N key) - the format is (row, col) NOT (x, y)
- Bee fixed
- Spider fixed and is now based on three Bee movements
- Reward for MCTS is proportional to the number of (any player) pieces surrounding opponent queen
- MCTS is now parallelised using Ray and Root Parallelisation - multiple trees are created and the summation root nodes gives the final best move
- Positions of placed pieces are now stored to save time iterating over the whole board during MCTS (<12 iterations vs 256).

#### 02/07/2020 - 08/07/2020
Notes:
- Refactored `game_init` to `game_with_ui` and moved any non-PyGame code to `game`
- Created `game_without_ui` as entry point to play a complete game with two computer players using random moves, MCTS, or Swarm AI
- Researched possible design and implementation of Swarm AI

### Swarm Implementation Notes

#### 11/07/2020

- PSO velocities calculated for pieces, if they could move with any velocity, such that their optimisation target is the opponent bee
- Applied to board full of beetles and two bees such that the new velocities are capped to `min(1,new_vel)` or `max(-1, new_vel)` and the new velocity given is actually a possible move allowed by the beetle
    - For example, if a beetle desires to move South-East and that move conforms to the freedom to move and one-hive rules then it is allowed

- Noted that the direction a beetle desires to move is not necessarily unit length 1 for both row and column as it depends on the current column being even or odd
- Noted that swarming is restricted as a piece may desire to move one direction, but must first move a different direction to do so while conforming to rules
 
#### 12/07/2020

- Implemented velocity conversion to unit move for beetle
- Fixed game logic bug where a position is removed from set of known positions after move made when it was a stack
- Beetle appears to successfully converge towards the opponent bee, limited by the rules of the game
    - Demonstrated by hardcoding so black cannot move and white repeatedly moves

- Trials with Ants
    - First, fixed and refactored Ant to use a Bee's move recursively
    - As ants can move any number of hexagons, the velocity vector is trimmed to the nearest int (+/- 1 if over a threshold of 0.25)
    - When added to original position, the new position this vector gives may not be valid move for the Ant. Therefore, the nearest valid move to the desired position is selected.
        - This has the side effect of multiple moves being equidistant to the desired position, resulting in the Ant possibly moving away from goal
        - To prevent Ant moving away from goal, the nearest move to goal is chosen if there is a tie in distance to desired position

TODO 
determine communication to decide what moves first

       