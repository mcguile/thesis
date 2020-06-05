from insects import Blank


class HiveGraph:
    def __init__(self, board):
        self.ROW = board.height
        self.COL = board.width
        self.graph = board.board

    # A function to check if a given hexagon can be included in DFS
    def is_safe(self, row, col, visited):
        # row number is in range,
        # column number is in range,
        # and hexagon is Blank and not yet visited
        return (0 <= row < self.ROW and
                0 <= col < self.COL and
                not visited[row][col] and type(self.graph[row][col]) != Blank)

    # DFS for a 2D matrix. It only considers
    # the 6 neighbours as adjacent pieces
    def dfs(self, row, col, visited):
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
        visited[row][col] = True

        # Recur for all connected neighbours
        for k in range(6):
            if self.is_safe(row + row_nbr[k], col + col_nbr[k], visited):
                self.dfs(row + row_nbr[k], col + col_nbr[k], visited)

    def count_hives(self):
        # Make a bool array to mark visited hexagons.
        # Initially all hexagons are unvisited
        visited = [[False for _ in range(self.COL)] for _ in range(self.ROW)]

        # Initialize count as 0 and traverse
        # through the all hexagons of given matrix
        count = 0
        for row in range(self.ROW):
            for col in range(self.COL):
                # If a hexagon not Blank and is not visited yet,
                # then new island found
                if not visited[row][col] and type(self.graph[row][col]) != Blank:
                    # Visit all hexagons in this hive
                    # and increment hive count
                    self.dfs(row, col, visited)
                    count += 1
        return count
