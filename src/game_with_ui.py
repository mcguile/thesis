import sys
import os
from pygame.locals import *
import pygame
from board import *
from game import *
from state import State
from mcts import MCTS
import numpy as np
from swarm import Space
import ray
import logging
import ast

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

pygame.init()
ray.init()

W = -1
B = 1
NW = 'North-West'
NE = 'North-East'
SE = 'South-East'
SW = 'South-West'
ALL = "All"
player_random = 'RANDOM'
player_mcts = 'MCTS'
player_swarm = 'SWARM'


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


# def use_testboard():
#     testboard = Board(16, 16)
#     testboard.board[8][6] = Beetle(player=B, row=8, col=6)
#     testboard.board[7][7] = Grasshopper(player=B, row=7, col=7)
#     testboard.board[8][8] = Bee(player=B, row=8, col=8)
#     testboard.board[8][9] = Beetle(player=B, row=8, col=9)
#     testboard.board[9][7] = Beetle(player=W, row=9, col=7)
#     testboard.board[9][8] = Bee(player=W, row=9, col=8)
#     testboard.board[9][9] = Beetle(player=W, row=9, col=9)
#     testboard.board[10][8] = Grasshopper(player=W, row=10, col=8)
#     testboard.board[10][9] = Grasshopper(player=W, row=10, col=9)
#     g.bee_pos_black = [8, 8]
#     g.bee_pos_white = [9, 8]
#     g.bee_placed_white = True
#     g.bee_placed_black = True
#     g.black_positions = {(8, 6), (7, 7), (8, 8), (8, 9)}
#     g.white_positions = {(9, 7), (9, 8), (9, 9), (10, 8), (10, 9)}
#     g.first_move_black = False
#     g.first_move_white = False
#     g.turn_count_black = 4
#     g.turn_count_white = 5
#     testboard.board_count = 9
#     g.board = testboard
#     g.players_turn = 1


class GameUI:
    def __init__(self, state, log_file=None):
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
        self.numbers = True
        self.state = state
        if log_file:
            logging.basicConfig(filename=log_file, level=logging.INFO)

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
                    text = self.font.render(str(r) + ' ' + str(c), True, (255, 0, 0))
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

    def play_game_from_log(self, log_file, time_per_turn=0.5, start_at_first_ai_move=False):
        ai_line_found = False
        with open(log_file, 'r') as f:
            for line in f.readlines():
                if line == "\n":
                    continue
                if line.strip() == 'ai':
                    ai_line_found = True
                elif line.strip() == 'pass':
                    if self.state.players_turn == W:
                        self.state.turn_count_white += 1
                    else:
                        self.state.turn_count_black += 1
                    self.state.players_turn = opp(self.state.players_turn)
                else:
                    parts = line.split(' ')
                    board = self.state.board if parts[1] == 'b' else self.state.start_tiles
                    rf, cf = ast.literal_eval(parts[3])
                    rt, ct = ast.literal_eval(parts[4])
                    self.state.hexa_selected = board.board[rf][cf]
                    make_move(self.state, rt, ct, board)
                    if not start_at_first_ai_move or (start_at_first_ai_move and ai_line_found):
                        self.draw_game()
                        pygame.display.update()
                        self.clock.tick(30)
                        time.sleep(time_per_turn)
            self.draw_game()
            pygame.display.update()
            self.clock.tick(30)
            time.sleep(6000)

    def play_full_game(self, player1, player2, time_per_move=0.5):
        printed_game_result = False
        # logging.info(make_first_move_each(self.state))
        while self.state.turn_count_white < 31:
            try:
                logging.info(make_random_move_from_board(self.state))
            except IndexError:
                self.state.players_turn = opp(self.state.players_turn)
        self.draw_game()
        pygame.display.update()
        self.clock.tick(30)
        time.sleep(time_per_move)
        space = Space(self.state, vicinities=True, vicin_radius=1)
        mcts_ = MCTS(time_limit=self.state.time_limit, iter_limit=self.state.iter_limit)
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if not isGameOver(self.state):
                    if self.state.players_turn == -1:
                        if player1 == player_random:
                            logging.info(make_random_move_from_anywhere(self.state))
                        elif player1 == player_mcts:
                            action = mcts_.multiprocess_search(self.state)
                            logging.info(make_mcts_move(self.state, action))
                        else:
                            logging.info(make_swarm_move(self.state, space))
                    elif self.state.players_turn == 1:
                        if player2 == player_random:
                            logging.info(make_random_move_from_anywhere(self.state))
                        elif player2 == player_mcts:
                            action = mcts_.multiprocess_search(self.state)
                            logging.info(make_mcts_move(self.state, action))
                        else:
                            logging.info(make_swarm_move(self.state, space))
                    self.draw_game()
                    pygame.display.update()
                    self.clock.tick(30)
                    time.sleep(time_per_move)
                else:
                    if not printed_game_result:
                        printed_game_result = True
                        if has_won(self.state, -1):
                            print(f"White wins after {self.state.turn_count_white} turns")
                        else:
                            print(f"Black wins after {self.state.turn_count_black} turns")

    def playbyplay(self):
        move_from = None
        printed_game_result = False
        mcts_ = MCTS(time_limit=self.state.time_limit, iter_limit=self.state.iter_limit)
        while self.state.turn_count_white < 31:
            try:
                logging.info(make_random_move_from_board(self.state))
            except IndexError:
                self.state.players_turn = opp(self.state.players_turn)
        self.state.players_turn = -1
        space = Space(self.state, vicinities=True, vicin_radius=2)
        logging.info('ai')
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
                        elif event.key == K_RIGHT:
                            logging.info(make_swarm_move(self.state, space, intention_criteria=0, infinite_moves=True))
                        elif event.key == K_LEFT:
                            action = mcts_.multiprocess_search(self.state)
                            logging.info(make_mcts_move(self.state, action))
                        elif event.key == K_DOWN:
                            logging.info(make_random_move_from_board(self.state))
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if self.state.hexa_selected:
                            if self.mouse_pos.collidepoint(event.pos):
                                self.deselect()
                            else:
                                logging.info(move_to_board(self.state, event, move_from))
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
                            elif is_bee_placed(self.state, self.state.players_turn):
                                move_from = self.state.board
                                self.select_from_board(event)

                            if self.state.hexa_selected:
                                if self.state.first_move_black:
                                    self.state.possible_moves = get_possible_first_moves_black(self.state)
                                elif move_from.height <= 6:
                                    self.state.possible_moves = get_possible_moves_from_rack(self.state)
                                else:
                                    self.state.possible_moves = get_possible_moves_from_board(self.state)
                else:
                    if not printed_game_result:
                        printed_game_result = True
                        if has_won(self.state, -1):
                            print(f"White wins after {self.state.turn_count_white} turns")
                        else:
                            print(f"Black wins after {self.state.turn_count_black} turns")
            self.draw_game()
            pygame.display.update()
            self.clock.tick(30)

# np.random.seed(38)
# random.seed(38)
# g = State(time_limit=None, iter_limit=100)
# game = GameUI(g)
# generate_random_full_board(g)
# game.playbyplay()