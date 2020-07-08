Known Bugs:
- Selection from rack not highlighted - functionality not affected
- Beetle is occasionally broken - reason unknown, need investigation
- Insect (Ant noted) can occasionally slide into space that breaks Freedom-to-move rule

#### 02/07/2020 - 08/07/2020
Notes:
- Refactored `game_init` to `game_playbyplay_ui` and moved any non-PyGame code to `game_logic`
- Created `game_fullrun_no_ui` as entry point to play a complete game with two computer players using random moves, MCTS, or Swarm AI
- Researched possible design and implementation of Swarm AI

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
- Noted that the current One-Hive check which detemimes if merely moving away from position breaks the hive increases time taken by a factor of 4000!