import sys
import os
from pygame.locals import *
import pygame
from board import *
from state import State
from game_logic import *
from mcts import MCTS
import numpy as np
import random
import ray

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


ray.init()

W = -1
B = 1
NW = 'North-West'
NE = 'North-East'
SE = 'South-East'
SW = 'South-West'
ALL = "All"


def get_pygame_image(insect_id, player=None, blit_selected=False, blit_possible=False):
    p = 'white' if player == -1 else 'black'
    if insect_id == 0:
        img = pygame.image.load(f'../img_assets/{p}_bee.png')
    elif insect_id == 1:
        img = pygame.image.load(f'../img_assets/{p}_ant.png')
    elif insect_id == 2:
        img = pygame.image.load(f'../img_assets/{p}_beetle.png')
    elif insect_id == 3:
        img = pygame.image.load(f'../img_assets/{p}_grasshopper.png')
    elif insect_id == 4:
        img = pygame.image.load(f'../img_assets/{p}_spider.png')
    else:
        img = pygame.image.load(f'../img_assets/blank.png')

    if blit_selected:
        img.blit(pygame.image.load('../img_assets/selected.png'), (0, 0))
    elif blit_possible:
        img.blit(pygame.image.load('../img_assets/possible.png'), (0, 0))
    return img


def use_testboard():
    testboard = Board(16, 16)
    testboard.board[8][6] = Bee(player=W, row=8, col=6)
    testboard.board[7][7] = Grasshopper(player=W, row=7, col=7)
    testboard.board[8][8] = Bee(player=W, row=8, col=8)
    testboard.board[8][9] = Beetle(player=W, row=8, col=9)
    testboard.board[9][7] = Beetle(player=B, row=9, col=7)
    testboard.board[9][8] = Bee(player=B, row=9, col=8)
    testboard.board[9][9] = Beetle(player=B, row=9, col=9)
    testboard.board[10][8] = Grasshopper(player=B, row=10, col=8)
    testboard.board[10][9] = Grasshopper(player=B, row=10, col=9)
    game.state.bee_pos_black = [9, 8]
    game.state.white_positions = {(8, 6), (7, 7), (8, 8), (8, 9)}
    game.state.black_positions = {(9, 7), (9, 8), (9, 9), (10, 8), (10, 9)}
    game.state.first_move_black = False
    game.state.first_move_white = False
    game.state.turn_count_black = 5
    game.state.turn_count_white = 4
    testboard.board_count = 9
    game.state.board = testboard


class Game:
    def __init__(self, time_limit, iter_limit):
        """User Interface ATTR START"""
        self.pixel_width = 1000
        self.pixel_height = 1000
        self.rack_pixel_height = 160
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.pixel_width, self.pixel_height), 0, 32)
        self.bg = pygame.image.load('../img_assets/wood.jpg')
        self.img_selected = pygame.image.load('../img_assets/selected.png')
        self.rack_top_surf = pygame.Surface((self.pixel_width, self.rack_pixel_height), pygame.SRCALPHA,
                                            32)
        self.rack_bottom_surf = pygame.Surface((self.pixel_width, self.rack_pixel_height), pygame.SRCALPHA,
                                               32)
        self.drag_surf = pygame.Surface((self.pixel_width, self.pixel_height), pygame.SRCALPHA, 32)
        self.drag_surf_rect = self.drag_surf.get_rect()
        # self.drag_surf_rect.x += 23  # Center first piece on screen (Commented for now as it affects click pos)
        self.hexa_size = pygame.image.load('../img_assets/blank.png').get_rect().size
        self.hexa_width, self.hexa_height = self.hexa_size
        self.mouse_pos = pygame.Rect((0, 0), self.hexa_size)
        self.font = pygame.font.Font('freesansbold.ttf', 20)
        self.numbers = False
        """User Interface ATTR END"""
        self.time_limit = time_limit
        self.iter_limit = iter_limit
        self.state = State()

    def draw_rack_tiles(self):
        y = 0
        self.rack_bottom_surf.fill((0, 0, 0, 0))
        self.rack_top_surf.fill((0, 0, 0, 0))
        for r, _ in enumerate(self.state.start_tiles.board):
            add_height = self.pixel_height - self.rack_pixel_height if r >= self.state.start_tiles.height // 2 else 0
            if r == self.state.start_tiles.height // 2:
                y = 0
            rack_surf = self.rack_top_surf if r < 3 else self.rack_bottom_surf
            x = int(self.pixel_width / 6) - self.hexa_width / 2
            y += 20
            for hexa in self.state.start_tiles.board[r]:
                rack_surf.blit(get_pygame_image(hexa.id, hexa.player), (x, y))
                hexa.rect = pygame.Rect((x, y + add_height), self.hexa_size)
                x += int(self.pixel_width / 6)

    def draw_board_tiles(self):
        x_o, y_o = self.drag_surf_rect.x, self.drag_surf_rect.y
        self.drag_surf.fill((0, 0, 0, 0))
        for r, _ in enumerate(self.state.board.board):
            x, y = x_o, y_o
            for c, hexa in enumerate(self.state.board.board[r]):
                sel = self.state.hexa_selected and self.state.hexa_selected_is_on_board and (self.state.hexa_selected.r, self.state.hexa_selected.c) == (r, c)
                poss = (r, c) in self.state.possible_moves
                hexa_id = hexa.id if type(hexa) is not Stack else hexa.stack[-1].id
                self.drag_surf.blit(get_pygame_image(hexa_id, hexa.player, sel, poss), (x, y))
                hexa.rect = pygame.Rect((x, y), self.hexa_size)
                y += 30 if c % 2 == 0 else -30
                x += 52
                if self.numbers:
                    text = self.font.render(str(r) + ' ' + str(c), True, (255, 255, 255))
                    yn = y-10 if c % 2 == 0 else y+60
                    self.drag_surf.blit(text, (x-35, yn))
            y_o += 60

    def draw_game(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.transform.scale(self.bg, (self.pixel_width, self.pixel_height)), (0, 0))
        self.screen.blit(self.drag_surf, self.drag_surf_rect)
        self.screen.blit(self.rack_top_surf, (0, 0))
        self.screen.blit(self.rack_bottom_surf, (0, self.pixel_height - self.rack_pixel_height))
        self.draw_rack_tiles()
        self.draw_board_tiles()

    def select_from_rack_tiles(self, mouse_pos):
        start, stop = (0, self.state.start_tiles.height // 2) if self.state.players_turn == W else (
            self.state.start_tiles.height // 2, self.state.start_tiles.height)
        for row in range(start, stop):
            for col, hexa in enumerate(self.state.start_tiles.board[row]):
                if type(hexa) is not Blank and hexa.rect.collidepoint(mouse_pos):
                    self.state.hexa_selected = hexa
                    self.state.hexa_selected_is_on_board = False
                    self.mouse_pos.x, self.mouse_pos.y = np.subtract(mouse_pos, (self.hexa_width // 2,
                                                                                 self.hexa_height // 2))

    def select_from_board(self, event):
        for row in range(self.state.board.height):
            for col, hexa in enumerate(self.state.board.board[row]):
                if type(hexa) is not Blank and hexa.rect.collidepoint(event.pos) and hexa.player == self.state.players_turn:
                    self.state.hexa_selected = hexa
                    self.state.hexa_selected_is_on_board = True
                    self.mouse_pos.x, self.mouse_pos.y = np.subtract(event.pos, (self.hexa_width // 2,
                                                                                 self.hexa_height // 2))
                    return

    def deselect(self):
        self.state.possible_moves = set()
        self.mouse_pos.x, self.mouse_pos.y = 0, 0
        self.state.hexa_selected = None

    def run_game(self):
        move_from = None
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if not isGameOver(self.state):
                    if event.type == pygame.KEYDOWN:
                        if event.key == K_n:
                            self.numbers = not self.numbers
                        # elif event.key == K_BACKSPACE and self.state.turn_count_black > 3:
                        #     self.state = self.state.prev_state
                        #     self.deselect()
                        elif event.key == K_LEFT:
                            if self.state.players_turn == -1:
                                print('\nWhite')
                                print('MCTS is searching for the best action...')
                                mcts_ = MCTS(time_limit=self.time_limit, iter_limit=self.iter_limit)
                                action = mcts_.multiprocess_search(self.state)
                                print(action.r_f)
                                if action.r_f < 0:
                                    action.r_f = abs(action.r_f)-1
                                    self.state.hexa_selected = self.state.start_tiles.board[action.r_f][action.c_f]
                                    make_move(self.state, action.r_t, action.c_t, self.state.start_tiles)
                                    print("start tiles")
                                else:
                                    self.state.hexa_selected = self.state.board.board[action.r_f][action.c_f]
                                    make_move(self.state, action.r_t, action.c_t, self.state.board)
                                    print("board")
                                print(action)
                            else:
                                print('\nBlack')
                                print(make_random_move_from_board(self.state))
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if self.state.hexa_selected:
                            if self.mouse_pos.collidepoint(event.pos):
                                self.deselect()
                            else:
                                move_to_board(self.state, event, move_from)
                                if self.state.first_move_black and black_has_moved(self.state):
                                    self.state.first_move_black = False
                        else:
                            mouse_x, mouse_y = event.pos
                            if self.state.turn_count_white == 3 and self.state.players_turn == W and not is_bee_placed(self.state, W):
                                mouse_x, mouse_y = self.state.start_tiles.board[0][3].rect.centerx, self.state.start_tiles.board[0][
                                    3].rect.centery
                            elif self.state.turn_count_black == 3 and self.state.players_turn == B and not is_bee_placed(self.state, B):
                                mouse_x, mouse_y = self.state.start_tiles.board[3][3].rect.centerx, self.state.start_tiles.board[3][
                                    3].rect.centery
                            if mouse_y < self.rack_pixel_height or mouse_y > self.pixel_height - self.rack_pixel_height:
                                move_from = self.state.start_tiles
                                if self.state.first_move_white:
                                    self.state.first_move_white = move_white_first(self.state, self.state.first_move_white, event)
                                else:
                                    self.select_from_rack_tiles((mouse_x, mouse_y))
                            else:
                                move_from = self.state.board
                                self.select_from_board(event)

                            if self.state.hexa_selected:
                                if self.state.first_move_black:
                                    self.state.possible_moves = get_possible_first_moves_black(self.state)
                                elif move_from.height <= 6:
                                    self.state.possible_moves = get_possible_moves_from_rack(self.state)
                                else:
                                    self.state.possible_moves = get_possible_moves_from_board(self.state)

            self.draw_game()
            pygame.display.update()
            self.clock.tick(30)


pygame.init()
game = Game(time_limit=None, iter_limit=100)
use_testboard()
#generate_random_full_board(game.state, seed=3)
game.run_game()
