import pygame


class Bee:
    def __init__(self, player, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/{player}_bee.png')
        self.in_play = False
        self.player = player
        self.x = x
        self.y = y


class Ant:
    def __init__(self, player, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/{player}_ant.png')
        self.in_play = False
        self.player = player
        self.x = x
        self.y = y


class Beetle:
    def __init__(self, player, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/{player}_beetle.png')
        self.in_play = False
        self.player = player
        self.x = x
        self.y = y


class Grasshopper:
    def __init__(self, player, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/{player}_grasshopper.png')
        self.in_play = False
        self.player = player
        self.x = x
        self.y = y


class Spider:
    def __init__(self, player, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/{player}_spider.png')
        self.in_play = False
        self.player = player
        self.x = x
        self.y = y


class Blank:
    def __init__(self, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/blank.png')
        self.in_play = False
        self.playable = True
        self.player = None
        self.x = x
        self.y = y


class Possible:
    def __init__(self, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/possible.png')
        self.in_play = False
        self.x = x
        self.y = y