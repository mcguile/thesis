from math import floor
NW = 'North-West'
NE = 'North-East'
SE = 'South-East'
SW = 'South-West'
ALL = "All"


def get_minmax_rowcol(r, c, num_rows, num_cols):
    min_r = max(r - 1, 0)
    max_r = min(r + 1, num_rows - 1)
    min_c = max(c - 1, 0)
    max_c = min(c + 1, num_cols - 1)
    return min_r, max_r, min_c, max_c


def get_cell_neighbours(r, c, num_rows, num_cols):
    neighbours = []
    min_r, max_r, min_c, max_c = get_minmax_rowcol(r, c, num_rows, num_cols)
    for row in range(min_r, max_r + 1):
        for col in range(min_c, max_c + 1):
            if col == c and row == r:
                continue
            elif (c % 2 == 0) and ((col == c + 1 and row == r + 1) or (row == r + 1 and col == c - 1)):
                continue
            elif (c % 2 == 1) and ((col == c - 1 and row == r - 1) or (row == r - 1 and col == c + 1)):
                continue
            else:
                neighbours.append((row, col))
    return neighbours


def get_hexas_straight_line(fromm, w, h, direction=ALL):
    hexas_n, hexas_s, hexas_ne, hexas_se, hexas_sw, hexas_nw = [], [], [], [], [], []
    r_n, c_n = r_s, c_s = r_se, c_se = r_sw, c_sw = r_nw, c_nw = r_ne, c_ne = fromm
    for i in range(min(w, h)):
        r_n -= 1
        r_s += 1
        if r_se % 2 == 1 and c_se % 2 == 1:
            r_se += 1
            c_se += 1
            r_sw += 1
            c_sw -= 1
            c_nw -= 1
            c_ne += 1
        elif r_se % 2 == 1 and c_se % 2 == 0:
            c_se += 1
            c_sw -= 1
            r_nw -= 1
            c_nw -= 1
            r_ne -= 1
            c_ne += 1
        elif r_se % 2 == 0 and c_se % 2 == 0:
            c_se += 1
            c_sw -= 1
            r_nw -= 1
            c_nw -= 1
            r_ne -= 1
            c_ne += 1
        elif r_se % 2 == 0 and c_se % 2 == 1:
            r_se += 1
            c_se += 1
            r_sw += 1
            c_sw -= 1
            c_nw -= 1
            c_ne += 1
        hexas_n.append((r_n, c_n))
        hexas_s.append((r_s, c_s))
        hexas_nw.append((r_nw, c_nw))
        hexas_ne.append((r_ne, c_ne))
        hexas_sw.append((r_sw, c_sw))
        hexas_se.append((r_se, c_se))
    if direction == ALL:
        return hexas_n, hexas_s, hexas_ne, hexas_se, hexas_sw, hexas_nw
    elif direction == NE:
        return hexas_ne
    elif direction == SE:
        return hexas_se
    elif direction == SW:
        return hexas_sw
    else:
        return hexas_nw


def distance_between_hex_cells(cell1, cell2):
    r1, c1 = cell1
    r2, c2 = cell2
    x0 = r1 - floor(c1 / 2)
    x1 = r2 - floor(c2 / 2)
    dx = x1 - x0
    dy = c2 - c1
    return max(abs(dx), abs(dy), abs(dx + dy))
