from insects import Blank
from collections import deque


class HiveGraph:
    def __init__(self, board):
        self.row = board.height
        self.col = board.width
        self.visited = [[False for _ in range(self.col)] for _ in range(self.row)]
        self.graph = board.board

    # A function to check if a given hexagon can be included in DFS
    def is_safe(self, row, col):
        # row number is in range,
        # column number is in range,
        # and hexagon is Blank and not yet visited
        return (0 <= row < self.row and
                0 <= col < self.col and
                not self.visited[row][col] and
                type(self.graph[row][col]) is not Blank)

    # DFS for a 2D matrix. It only considers
    # the 6 neighbours as adjacent pieces
    def dfs(self, row, col):
        # These arrays are used to get row and
        # column numbers of 6 neighbours
        # of a given hexagon
        if col % 2 == 1:
            row_nbr = [-1,  0, 0,  1, 1, 1]
            col_nbr = [ 0, -1, 1, -1, 0, 1]
        else:
            row_nbr = [-1, -1, -1,  0, 0, 1]
            col_nbr = [-1,  0,  1, -1, 1, 0]

        # Mark this hexagon as visited
        self.visited[row][col] = True

        # Recur for all connected neighbours
        for k in range(6):
            if self.is_safe(row + row_nbr[k], col + col_nbr[k]):
                self.dfs(row + row_nbr[k], col + col_nbr[k])

    def one_hive(self):
        # Initialize count as 0 and traverse
        # through the all hexagons of given matrix
        count = 0
        for row in range(self.row):
            for col in range(self.col):
                # If a hexagon not Blank and is not visited yet,
                # then new hive found
                if not self.visited[row][col] and type(self.graph[row][col]) is not Blank:
                    # Visit all hexagons in this hive
                    # and increment hive count
                    count += 1
                    if count > 1:
                        return False
                    self.dfs(row, col)
        return True
