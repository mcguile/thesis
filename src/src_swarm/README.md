### Implementation Notes

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
