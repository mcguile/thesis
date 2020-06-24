16/06/2020 - 23/06/2020

Known bugs:
- ~~Beetle was allowed to break hive~~
- Selection from rack not highlighted - functionality not affected

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