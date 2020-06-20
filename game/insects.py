class Bee:
    def __init__(self, player, row=0, col=0):
        self.player = player
        self.id = 0
        self.in_play = False
        self.rect = None
        self.r = row
        self.c = col


class Ant:
    def __init__(self, player, row=0, col=0):
        self.player = player
        self.id = 1
        self.in_play = False
        self.rect = None
        self.r = row
        self.c = col


class Beetle:
    def __init__(self, player, row=0, col=0):
        self.player = player
        self.id = 2
        self.in_play = False
        self.rect = None
        self.r = row
        self.c = col


class Grasshopper:
    def __init__(self, player, row=0, col=0):
        self.player = player
        self.id = 3
        self.in_play = False
        self.rect = None
        self.r = row
        self.c = col


class Spider:
    def __init__(self, player, row=0, col=0):
        self.player = player
        self.id = 4
        self.in_play = False
        self.rect = None
        self.r = row
        self.c = col


class Blank:
    def __init__(self, row=0, col=0):
        self.player = None
        self.id = 5
        self.rect = None
        self.r = row
        self.c = col


class Stack:
    def __init__(self, first_piece=None, stacked_piece=None, stack=None, row=0, col=0):
        self.id = 6
        self.stack = [first_piece, stacked_piece] if not stack else stack
        self.player = self.stack[-1].player
        self.r = row
        self.c = col
        self.rect = None

    def add_piece(self, piece):
        self.stack.append(piece)
        self.player = self.stack[-1].player
        self.stack[-1].r = self.r
        self.stack[-1].c = self.c

    def remove_piece(self):
        piece = self.stack.pop()
        self.player = self.stack[-1].player
        return piece
