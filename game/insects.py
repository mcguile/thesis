import pygame


class Bee:
    def __init__(self, player, row=0, col=0, image=None):
        self.player = player
        self.image_loc = f'../img_assets/{self.player}_bee.png'
        self.image = image if image else pygame.image.load(self.image_loc)
        self.in_play = False
        self.rect = None
        self.r = row
        self.c = col


class Ant:
    def __init__(self, player, row=0, col=0, image=None):
        self.player = player
        self.image_loc = f'../img_assets/{self.player}_ant.png'
        self.image = image if image else pygame.image.load(self.image_loc)
        self.image_o = pygame.image.load(f'../img_assets/{player}_ant.png')
        self.in_play = False
        self.rect = None
        self.r = row
        self.c = col


class Beetle:
    def __init__(self, player, row=0, col=0, image=None):
        self.player = player
        self.image_loc = f'../img_assets/{self.player}_beetle.png'
        self.image = image if image else pygame.image.load(self.image_loc)
        self.image_o = pygame.image.load(f'../img_assets/{player}_beetle.png')
        self.in_play = False
        self.rect = None
        self.r = row
        self.c = col


class Grasshopper:
    def __init__(self, player, row=0, col=0, image=None):
        self.player = player
        self.image_loc = f'../img_assets/{self.player}_grasshopper.png'
        self.image = image if image else pygame.image.load(self.image_loc)
        self.image_o = pygame.image.load(f'../img_assets/{player}_grasshopper.png')
        self.in_play = False
        self.rect = None
        self.r = row
        self.c = col


class Spider:
    def __init__(self, player, row=0, col=0, image=None):
        self.player = player
        self.image_loc = f'../img_assets/{self.player}_spider.png'
        self.image = image if image else pygame.image.load(self.image_loc)
        self.image_o = pygame.image.load(f'../img_assets/{player}_spider.png')
        self.in_play = False
        self.rect = None
        self.r = row
        self.c = col


class Blank:
    def __init__(self, row=0, col=0):
        self.player = None
        self.image = pygame.image.load(f'../img_assets/blank.png')
        self.image_o = pygame.image.load(f'../img_assets/blank.png')
        self.image_loc = '../img_assets/blank.png'
        self.image_playable = pygame.image.load('../img_assets/possible.png')
        self.rect = None
        self.r = row
        self.c = col