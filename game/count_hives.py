from insects import Blank


class HiveGraph:

    def __init__(self, board):
        self.ROW = board.height
        self.COL = board.width
        self.graph = board.board

    # A function to check if a given cell
    # (row, col) can be included in DFS
    def is_safe(self, row, col, visited):
        # row number is in range, column number
        # is in range and value is 1
        # and not yet visited
        return (0 <= row < self.ROW and
                0 <= col < self.COL and
                not visited[row][col] and type(self.graph[row][col]) != Blank)

    # A utility function to do DFS for a 2D
    # boolean matrix. It only considers
    # the 6 neighbours as adjacent vertices
    def dfs(self, row, col, visited):
        # These arrays are used to get row and
        # column numbers of 8 neighbours
        # of a given cell
        if col % 2 == 1:
            row_nbr = [-1,  0, 0,  1, 1, 1]
            col_nbr = [ 0, -1, 1, -1, 0, 1]
        else:
            row_nbr = [-1, -1, -1,  0, 0, 1]
            col_nbr = [-1,  0,  1, -1, 1, 0]

        # Mark this cell as visited
        visited[row][col] = True

        # Recur for all connected neighbours
        for k in range(6):
            if self.is_safe(row + row_nbr[k], col + col_nbr[k], visited):
                self.dfs(row + row_nbr[k], col + col_nbr[k], visited)

    def count_hives(self):
        # Make a bool array to mark visited cells.
        # Initially all cells are unvisited
        visited = [[False for _ in range(self.COL)] for _ in range(self.ROW)]

        # Initialize count as 0 and travese
        # through the all cells of
        # given matrix
        count = 0
        for row in range(self.ROW):
            for col in range(self.COL):
                # If a cell with value 1 is not visited yet,
                # then new island found
                if not visited[row][col] and type(self.graph[row][col]) != Blank:
                    # Visit all cells in this island
                    # and increment island count
                    self.dfs(row, col, visited)
                    count += 1

        return count
