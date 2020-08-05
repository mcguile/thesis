total = 0
vel = 0
dgt = 0
with open('logs/freq_vel_or_dgt.txt', 'r') as f:
    for v in f:
        total += 1
        if v.strip() == 'V':
            vel += 1
        if v.strip() == 'D':
            dgt += 1

print('Total intentions assigned in 100 games:', total)
print('Frequency of velocity intentions:', vel/total)
print('Frequency of DGT intentions:', dgt/total)
