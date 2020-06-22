22/06/2020

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
    - Optimised Spider to a time of 0.0002 seconds (!) by removing one of the two One-Hive checkers and implementing custom approach
    - Optimised Ant to a time of 0.085 seconds (!) by removing one of the two One-Hive checkers and implementing custom approach
    - Other insects also modified in the same manner to no benefit or detriment