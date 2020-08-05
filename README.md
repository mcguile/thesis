### Execution Instructions
To play the game from a random state with all pieces on the board:
- From terminal, CD into `thesis/src`
- `python3 game_with_ui.py` will run the game
- Optional flag `-f [filename]` allows you to log the game to a text file
- Either point and click to select pieces or press keys to execute AI for a single move
    - `R` key executes a random move
    - `M` key executes MCTS
    - `S` key executes Swarm AI
    
### Log Replay Instructions
To play a game from a saved log file:
- From terminal, CD into `thesis/src`
- `python3 log_replay.py -f [log_file]
- Use `LEFT` and `RIGHT` arrow keys to go back and forward in time
- The terminal displays if a random move or an AI move is being executed



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

- Due to the implementation of swarming for PSO, a particle does not stop when the goal is reached. It continues with some velocity and slows down spiralling into the minima (if it could move freely).
    - A modification could be to stop once at goal but this begins to move away from swarm behaviour and more into "just head to goal if you know where it is" behaviour
    
#### 16/07/2020
- Trials with all insects conducted and work well
- Noted that as the movement process is iterative, a Beetle may move twice if it moves on top of an insect which has not yet moved; irrelevant for the real turn-by-turn game
- Refactored the non-ui class so it can be used in the test class
- Implemented Local Vicinity PSO with varying vicinity radii and conducted comparison against Global PSO. Local Vicinity will be used herein to allow for intra- and inter-vicinity communication.
       
#### 17/07/2020 - 22/07/2020
- Beginning testing using turn-by-turn PSO - move selection is the primary focus
- INTENTION factors are researched to determine move to be selected
    - Factors include velocity, accuracy, fitness, danger theory, and movement ability
    - Winner of each vicinity by intention score face off against each other if score is equal highest. Tiebreaker is one of the above factors not used for initial intention calc.
- Non-PSO approach considered using "direct to goal" method
    - Danger theory can, and most likely will, be incorporated
- Beginning to implement logs for games played so they can be replayed via UI
