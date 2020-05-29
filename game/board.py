import numpy as np
from insects import Blank

class Board:
    def __init__(self, width=40, height=40, with_blanks=True):
        self.width = width
        self.height = height
        self.board = [[Blank() for _ in range(height)] for _ in range(width)]
