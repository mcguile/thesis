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
- `python3 log_replay.py -f [log_file]`
- Optional flag `-ai` to start control after the random moves
- Use `LEFT` and `RIGHT` arrow keys to go back and forward in time
- The terminal displays if a random move or an AI move is being executed


### Class Descriptions
- `game` - all algorithms and logic to play the game of Hive, mainly insect move algorithms
- `game_with_ui` - directly executable to play a game using the UI, with each move given the option to be controlled manually or by AI (see instructions above)
- `game_without_ui` - can be instantiated and started with `.play_full_game()` to play a game with only AIs and save to logs
- `insects` - base classes for each playable insect, including meta-insects `Stack` and `Blank`
- `log_replay` - directly executable via the above instructions to replay a log using the UI
- `mcts` - implementation of root-parallelised Monte-Carlo Search Tree
- `state` - data class holding the current state of the game
- `board` - data class holding the matrix of insects/meta-insects
- `action` - data class holding a single action for MCTS to execute
- `swarm` - implementation of PSO, allowing for global/local PSO and intentions communications
- `tests` - test class to gather logs
- `utils` - helper functions which do not require game state
- `count_hives` - Depth-first search to count the number of Hives present on the board (One-Hive Rule)