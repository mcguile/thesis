from insects import *

W = -1
B = 1


class Board:
    def __init__(self, height=40, width=40, start_tiles=False):
        self.width = width
        self.height = height
        self.board = [[Blank() for _ in range(width)] for _ in range(height)]
        self.board_count = 0
        self.board_count_w = 11
        self.board_count_b = 11
        if start_tiles:
            self._init_start_tiles()

    def _init_start_tiles(self):
        for i in range(2):
            x, player = (0, W) if i == 0 else (3, B)
            # self.board[0 + x][0] = Ant(player, 0 + x, 0)
            # self.board[1 + x][0] = Ant(player, 1 + x, 0)
            # self.board[2 + x][0] = Ant(player, 2 + x, 0)
            # self.board[0 + x][1] = Beetle(player, 0 + x, 1)
            # self.board[1 + x][1] = Beetle(player, 1 + x, 1)
            # self.board[0 + x][2] = Grasshopper(player, 0 + x, 2)
            # self.board[1 + x][2] = Grasshopper(player, 1 + x, 2)
            # self.board[2 + x][2] = Grasshopper(player, 2 + x, 2)
            # self.board[0 + x][3] = Bee(player, 0 + x, 3)
            # self.board[0 + x][4] = Spider(player, 0 + x, 4)
            # self.board[1 + x][4] = Spider(player, 1 + x, 4)
            self.board[0 + x][0] = Spider(player, 0 + x, 0)
            self.board[1 + x][0] = Spider(player, 1 + x, 0)
            self.board[2 + x][0] = Spider(player, 2 + x, 0)
            self.board[0 + x][1] = Spider(player, 0 + x, 1)
            self.board[1 + x][1] = Spider(player, 1 + x, 1)
            self.board[0 + x][2] = Spider(player, 0 + x, 2)
            self.board[1 + x][2] = Spider(player, 1 + x, 2)
            self.board[2 + x][2] = Spider(player, 2 + x, 2)
            self.board[0 + x][3] = Bee(player, 0 + x, 3)
            self.board[0 + x][4] = Spider(player, 0 + x, 4)
            self.board[1 + x][4] = Spider(player, 1 + x, 4)