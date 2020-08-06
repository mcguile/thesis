import os

swarm_wins = 0
opp_wins = 0
draws = 0

for filename in os.listdir('logs/swarm_vs_mcts'):
    with open('logs/swarm_vs_mcts/' + filename, 'r') as f:
        for i, line in enumerate(f):
            pass
        if i == 141:
            draws += 1
        elif line.split()[0] == 'm':
            opp_wins += 1
        elif line.split()[0] == 's':
            swarm_wins += 1

print(swarm_wins, opp_wins, draws)
