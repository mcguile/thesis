import pygame


class Bee:
    def __init__(self, player, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/{player}_bee.png')
        self.in_play = False
        self.player = player
        self.image_loc = f'../img_assets/{self.player}_bee.png'
        self.rect = None
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Bee):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.player == other.player and self.rect == other.rect


class Ant:
    def __init__(self, player, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/{player}_ant.png')
        self.image_o = pygame.image.load(f'../img_assets/{player}_ant.png')
        self.in_play = False
        self.player = player
        self.image_loc = f'../img_assets/{self.player}_ant.png'
        self.rect = None
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Ant):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.player == other.player and self.rect == other.rect


class Beetle:
    def __init__(self, player, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/{player}_beetle.png')
        self.image_o = pygame.image.load(f'../img_assets/{player}_beetle.png')
        self.in_play = False
        self.player = player
        self.image_loc = f'../img_assets/{self.player}_beetle.png'
        self.rect = None
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Beetle):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.player == other.player and self.rect == other.rect


class Grasshopper:
    def __init__(self, player, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/{player}_grasshopper.png')
        self.image_o = pygame.image.load(f'../img_assets/{player}_grasshopper.png')
        self.in_play = False
        self.player = player
        self.image_loc = f'../img_assets/{self.player}_grasshopper.png'
        self.rect = None
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Grasshopper):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.player == other.player and self.rect == other.rect


class Spider:
    def __init__(self, player, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/{player}_spider.png')
        self.image_o = pygame.image.load(f'../img_assets/{player}_spider.png')
        self.in_play = False
        self.player = player
        self.image_loc = f'../img_assets/{self.player}_spider.png'
        self.rect = None
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Spider):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.player == other.player and self.rect == other.rect


class Blank:
    def __init__(self, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/blank.png')
        self.image_o = pygame.image.load(f'../img_assets/blank.png')
        self.in_play = False
        self.playable = True
        self.player = None
        self.rect = None
        self.x = x
        self.y = y


class Possible:
    def __init__(self, x=0, y=0):
        self.image = pygame.image.load(f'../img_assets/possible.png')
        self.image_o = pygame.image.load(f'../img_assets/possible.png')
        self.in_play = False
        self.rect = None
        self.x = x
        self.y = y