import sys
import os
from pygame.locals import *
import pygame
from board import *
from game import *
from mcts import MCTS
import numpy as np
from src_swarm.swarm import Space
# import ray

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


# ray.init()

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
    g.state.bee_pos_black = [9, 8]
    g.state.white_positions = {(8, 6), (7, 7), (8, 8), (8, 9)}
    g.state.black_positions = {(9, 7), (9, 8), (9, 9), (10, 8), (10, 9)}
    g.state.first_move_black = False
    g.state.first_move_white = False
    g.state.turn_count_black = 5
    g.state.turn_count_white = 4
    testboard.board_count = 9
    g.state.board = testboard


class UI:
    def __init__(self, game):
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
        self.game = game

    def draw_rack_tiles(self):
        y = 0
        self.rack_bottom_surf.fill((0, 0, 0, 0))
        self.rack_top_surf.fill((0, 0, 0, 0))
        for r, _ in enumerate(self.game.state.start_tiles.board):
            add_height = self.pixel_height - self.rack_pixel_height if r >= self.game.state.start_tiles.height // 2 else 0
            if r == self.game.state.start_tiles.height // 2:
                y = 0
            rack_surf = self.rack_top_surf if r < 3 else self.rack_bottom_surf
            x = int(self.pixel_width / 6) - self.hexa_width / 2
            y += 20
            for hexa in self.game.state.start_tiles.board[r]:
                rack_surf.blit(get_pygame_image(hexa.id, hexa.player), (x, y))
                hexa.rect = pygame.Rect((x, y + add_height), self.hexa_size)
                x += int(self.pixel_width / 6)

    def draw_board_tiles(self):
        x_o, y_o = self.drag_surf_rect.x, self.drag_surf_rect.y
        self.drag_surf.fill((0, 0, 0, 0))
        for r, _ in enumerate(self.game.state.board.board):
            x, y = x_o, y_o
            for c, hexa in enumerate(self.game.state.board.board[r]):
                sel = self.game.state.hexa_selected and self.game.state.hexa_selected_is_on_board and (self.game.state.hexa_selected.r, self.game.state.hexa_selected.c) == (r, c)
                poss = (r, c) in self.game.state.possible_moves
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
        start, stop = (0, self.game.state.start_tiles.height // 2) if self.game.state.players_turn == W else (
            self.game.state.start_tiles.height // 2, self.game.state.start_tiles.height)
        for row in range(start, stop):
            for col, hexa in enumerate(self.game.state.start_tiles.board[row]):
                if type(hexa) is not Blank and hexa.rect.collidepoint(mouse_pos):
                    self.game.state.hexa_selected = hexa
                    self.game.state.hexa_selected_is_on_board = False
                    self.mouse_pos.x, self.mouse_pos.y = np.subtract(mouse_pos, (self.hexa_width // 2,
                                                                                 self.hexa_height // 2))

    def select_from_board(self, event):
        for row in range(self.game.state.board.height):
            for col, hexa in enumerate(self.game.state.board.board[row]):
                if type(hexa) is not Blank and hexa.rect.collidepoint(event.pos) and hexa.player == self.game.state.players_turn:
                    self.game.state.hexa_selected = hexa
                    self.game.state.hexa_selected_is_on_board = True
                    self.mouse_pos.x, self.mouse_pos.y = np.subtract(event.pos, (self.hexa_width // 2,
                                                                                 self.hexa_height // 2))
                    return

    def deselect(self):
        self.game.state.possible_moves = set()
        self.mouse_pos.x, self.mouse_pos.y = 0, 0
        self.game.state.hexa_selected = None

    def play_full_game(self, player1, player2, time_per_move=0.5):
        make_first_move_each(self.game.state)
        if player1 == player_mcts or player2 == player_mcts:
            mcts_ = MCTS(time_limit=self.game.time_limit, iter_limit=self.game.iter_limit)
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if not isGameOver(self.game.state):
                    if self.game.state.players_turn == -1:
                        if player1 == player_random:
                            make_random_move_from_anywhere(self.game.state)
                        elif player1 == player_mcts:
                            action = mcts_.multiprocess_search(self.game.state)
                            make_mcts_move(self.game.state, action)
                        else:
                            pass
                    elif self.game.state.players_turn == 1:
                        if player2 == player_random:
                            make_random_move_from_anywhere(self.game.state)
                        elif player2 == player_mcts:
                            action = mcts_.multiprocess_search(self.game.state)
                            make_mcts_move(self.game.state, action)
                        else:
                            pass
                else:
                    if has_won(self.game.state, -1):
                        print(f"White wins after {self.game.state.turn_count_white} turns")
                    else:
                        print(f"Black wins after {self.game.state.turn_count_black} turns")
                self.draw_game()
                pygame.display.update()
                self.clock.tick(30)
                time.sleep(time_per_move)


    def playbyplay(self):
        move_from = None
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if not isGameOver(self.game.state):
                    if event.type == pygame.KEYDOWN:
                        if event.key == K_n:
                            self.numbers = not self.numbers
                        # elif event.key == K_BACKSPACE and self.game.state.turn_count_black > 3:
                        #     self.game.state = self.game.state.prev_state
                        #     self.deselect()
                        elif event.key == K_RIGHT:
                            space = Space(self.game.state)
                            space.set_pbest()
                            space.set_gbest()
                            for particle, from_pos, new_vel in space.move_particles():
                                f_r, f_c = from_pos
                                new_vel = convert_vel(new_vel, type(self.game.state.board.board[f_r][f_c]))
                                particle.vel = new_vel
                                if new_vel[0] != 0 or new_vel[1] != 0:
                                    self.game.state.hexa_selected = self.game.state.board.board[f_r][f_c]
                                    set_of_new_pos = transform_cell_pos_from_velocity(new_vel, from_pos)
                                    possible_moves = get_possible_moves_from_board(self.game.state)
                                    if possible_moves:
                                        r, c = nearest_move_after_vel(set_of_new_pos, possible_moves, space.target)
                                        print(f'nearest move to {f_r+new_vel[0], f_c+new_vel[1]} is {r,c}')
                                        make_move(self.game.state, r, c, self.game.state.board)
                                        particle.move()
                                        self.draw_game()
                                        pygame.display.update()
                                        self.clock.tick(30)
                                        time.sleep(1)
                                self.game.state.players_turn = -1
                        elif event.key == K_LEFT:
                            if self.game.state.players_turn == -1:
                                print('\nWhite')
                                print('MCTS is searching for the best action...')
                                mcts_ = MCTS(time_limit=self.game.time_limit, iter_limit=self.game.iter_limit)
                                action = mcts_.multiprocess_search(self.game.state)
                                print(action.r_f)
                                if action.r_f < 0:
                                    action.r_f = abs(action.r_f)-1
                                    self.game.state.hexa_selected = self.game.state.start_tiles.board[action.r_f][action.c_f]
                                    make_move(self.game.state, action.r_t, action.c_t, self.game.state.start_tiles)
                                    print("start tiles")
                                else:
                                    self.game.state.hexa_selected = self.game.state.board.board[action.r_f][action.c_f]
                                    make_move(self.game.state, action.r_t, action.c_t, self.game.state.board)
                                    print("board")
                                print(action)
                            else:
                                print('\nBlack')
                                print(make_random_move_from_board(self.game.state))
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if self.game.state.hexa_selected:
                            if self.mouse_pos.collidepoint(event.pos):
                                self.deselect()
                            else:
                                move_to_board(self.game.state, event, move_from)
                                if self.game.state.first_move_black and black_has_moved(self.game.state):
                                    self.game.state.first_move_black = False
                        else:
                            mouse_x, mouse_y = event.pos
                            if self.game.state.turn_count_white == 3 and self.game.state.players_turn == W and not is_bee_placed(self.game.state, W):
                                mouse_x, mouse_y = self.game.state.start_tiles.board[0][3].rect.centerx, self.game.state.start_tiles.board[0][
                                    3].rect.centery
                            elif self.game.state.turn_count_black == 3 and self.game.state.players_turn == B and not is_bee_placed(self.game.state, B):
                                mouse_x, mouse_y = self.game.state.start_tiles.board[3][3].rect.centerx, self.game.state.start_tiles.board[3][
                                    3].rect.centery
                            if mouse_y < self.rack_pixel_height or mouse_y > self.pixel_height - self.rack_pixel_height:
                                move_from = self.game.state.start_tiles
                                if self.game.state.first_move_white:
                                    self.game.state.first_move_white = move_white_first(self.game.state, self.game.state.first_move_white, event)
                                else:
                                    self.select_from_rack_tiles((mouse_x, mouse_y))
                            else:
                                move_from = self.game.state.board
                                self.select_from_board(event)

                            if self.game.state.hexa_selected:
                                if self.game.state.first_move_black:
                                    self.game.state.possible_moves = get_possible_first_moves_black(self.game.state)
                                elif move_from.height <= 6:
                                    self.game.state.possible_moves = get_possible_moves_from_rack(self.game.state)
                                else:
                                    self.game.state.possible_moves = get_possible_moves_from_board(self.game.state)
                else:
                    if has_won(self.game.state, -1):
                        print(f"White wins after {self.game.state.turn_count_white} turns")
                    else:
                        print(f"Black wins after {self.game.state.turn_count_black} turns")
            self.draw_game()
            pygame.display.update()
            self.clock.tick(30)


pygame.init()
g = Game(time_limit=None, iter_limit=100)
ui = UI(g)
# use_testboard()
generate_random_full_board(g.state)


## COMMENT/UNCOMMENT BELOW FOR PLAY-BY-PLAY OR FULL GAME RUN

ui.playbyplay()
# ui.play_full_game(player_random, player_random)