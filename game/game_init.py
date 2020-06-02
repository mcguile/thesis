import pygame
import sys
from pygame.locals import *
from insects import *
from board import *
from count_hives import HiveGraph

W = 'white'
B = 'black'


def init_board(rows, cols):
    return Board(rows, cols)


def init_rack(player):
    rack = Board(3, 5)
    rack.board[0][0] = Ant(player, 0, 0)
    rack.board[2][0] = Ant(player, 2, 0)
    rack.board[0][1] = Beetle(player, 0, 1)
    rack.board[1][1] = Beetle(player, 1, 1)
    rack.board[0][2] = Grasshopper(player, 0, 2)
    rack.board[1][2] = Grasshopper(player, 1, 2)
    rack.board[2][2] = Grasshopper(player, 2, 2)
    rack.board[0][3] = Bee(player, 0, 3)
    rack.board[0][4] = Spider(player, 0, 4)
    rack.board[1][4] = Spider(player, 1, 4)
    return rack


def init_start_tiles():
    rack = Board(6,5)
    for i in range(2):
        x, player = (0, W) if i == 0 else (3, B)
        rack.board[0+x][0] = Ant(player, 0+x, 0)
        rack.board[2+x][0] = Ant(player, 2+x, 0)
        rack.board[0+x][1] = Beetle(player, 0+x, 1)
        rack.board[1+x][1] = Beetle(player, 1+x, 1)
        rack.board[0+x][2] = Grasshopper(player, 0+x, 2)
        rack.board[1+x][2] = Grasshopper(player, 1+x, 2)
        rack.board[2+x][2] = Grasshopper(player, 2+x, 2)
        rack.board[0+x][3] = Bee(player, 0+x, 3)
        rack.board[0+x][4] = Spider(player, 0+x, 4)
        rack.board[1+x][4] = Spider(player, 1+x, 4)
    return rack


def opp(player):
    return B if player == W else W


def get_shape_minmax_rowcol(r, c, num_rows, num_cols):
    min_r = max(r - 1, 0)
    max_r = min(r + 1, num_rows - 1)
    min_c = max(c - 1, 0)
    max_c = min(c + 1, num_cols - 1)
    return min_r, max_r, min_c, max_c


def get_cell_neighbours(r, c, num_rows, num_cols):
    neighbours = []
    min_r, max_r, min_c, max_c = get_shape_minmax_rowcol(r, c, num_rows, num_cols)
    for row in range(min_r, max_r + 1):
        for col in range(min_c, max_c + 1):
            if col == c and row == r:
                continue
            elif (c % 2 == 0) and ((col == c + 1 and row == r + 1) or (row == r + 1 and col == c - 1)):
                continue
            elif (c % 2 == 1) and ((col == c - 1 and row == r - 1) or (row == r - 1 and col == c + 1)):
                continue
            else:
                neighbours.append((row, col))
    return neighbours


class Game:
    def __init__(self):
        pygame.display.set_caption('Hive!')
        self.pixel_width = 1000
        self.pixel_height = 1000
        self.rack_pixel_height = 160
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.pixel_width, self.pixel_height), 0, 32)
        self.bg = pygame.image.load('../img_assets/wood.jpg')
        self.img_selected = pygame.image.load('../img_assets/selected.png')
        self.rack_top_surf = pygame.Surface((self.pixel_width, self.rack_pixel_height), pygame.SRCALPHA,
                                            32).convert_alpha()
        self.rack_bottom_surf = pygame.Surface((self.pixel_width, self.rack_pixel_height), pygame.SRCALPHA,
                                               32).convert_alpha()
        self.drag_surf = pygame.Surface((self.pixel_width, self.pixel_height), pygame.SRCALPHA, 32).convert_alpha()
        self.drag_surf_rect = self.drag_surf.get_rect()
        self.drag_surf_rect.x += 23  # Center first piece
        self.hexa_size = pygame.image.load('../img_assets/blank.png').get_rect().size
        self.hexa_width, _ = self.hexa_size
        self.players_turn = W
        self.bee_placed_white, self.bee_placed_black = False, False
        self.bee_pos_black, self.bee_pos_white = (0, 3), (0, 3)
        self.turn_count = 0
        self.hexa_selected = None
        self.board = init_board(16, 16)
        self.start_tiles = init_start_tiles()
        self.top_rack = init_rack(W)
        self.bottom_rack = init_rack(B)
        self.possible_moves = set()

    def setup_tiles(self):
        y = 0
        self.rack_bottom_surf.fill((0, 0, 0, 0))
        self.rack_top_surf.fill((0, 0, 0, 0))
        for r, _ in enumerate(self.start_tiles.board):
            add_height = self.pixel_height - self.rack_pixel_height if r >= self.start_tiles.height//2 else 0
            if r == self.start_tiles.height//2:
                y = 0
            rack_surf = self.rack_top_surf if r < 3 else self.rack_bottom_surf
            x = int(self.pixel_width / 6) - self.hexa_width / 2
            y += 20
            for hexa in self.start_tiles.board[r]:
                rack_surf.blit(hexa.image, (x, y))
                hexa.rect = pygame.Rect((x, y+add_height), self.hexa_size)
                x += int(self.pixel_width / 6)

    def draw_placed_tiles(self):
        x_o, y_o = self.drag_surf_rect.x, self.drag_surf_rect.y
        self.drag_surf.fill((0, 0, 0, 0))
        for r, _ in enumerate(self.board.board):
            x, y = x_o, y_o
            for c, hexa in enumerate(self.board.board[r]):
                if type(hexa) is Blank:
                    if (r, c) in self.possible_moves:
                        hexa.image = hexa.image_playable
                    else:
                        hexa.image = hexa.image_o
                self.drag_surf.blit(hexa.image, (x, y))
                hexa.rect = pygame.Rect((x, y), self.hexa_size)
                y += 30 if c % 2 == 0 else -30
                x += 52
            y_o += 60

    def get_possible_moves(self):
        possible_moves = set()
        for r, _ in enumerate(self.board.board):
            for c, hexa in enumerate(self.board.board[r]):
                neighbours = get_cell_neighbours(r, c, self.board.height, self.board.width)
                valid_placement = True
                found_own_tile = False
                for x, y in neighbours:
                    if self.board.board[x][y].player == self.players_turn:
                        found_own_tile = True
                    elif self.board.board[x][y].player == opp(self.players_turn) or type(
                            self.board.board[r][c]) != Blank:
                        valid_placement = False
                if found_own_tile and valid_placement:
                    possible_moves.add((r, c))
        return possible_moves

    def get_possible_first_moves_black(self):
        return set(get_cell_neighbours(self.board.width // 2, self.board.height // 2,
                                       self.board.height, self.board.width))

    def draw_board(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(pygame.transform.scale(self.bg, (self.pixel_width, self.pixel_height)), (0, 0))
        self.screen.blit(self.drag_surf, self.drag_surf_rect)
        self.screen.blit(self.rack_top_surf, (0, 0))
        self.screen.blit(self.rack_bottom_surf, (0, self.pixel_height - self.rack_pixel_height))
        self.setup_tiles()
        self.draw_placed_tiles()

    def move_to_board(self, event, last_event_pos):
        if pygame.Rect(last_event_pos, self.hexa_size).collidepoint(event.pos):
            self.hexa_selected.image = pygame.image.load(self.hexa_selected.image_loc)
            return
        for row in range(self.board.height):
            for col, hexa in enumerate(self.board.board[row]):
                if hexa.rect.collidepoint(event.pos) and (row, col) in self.possible_moves:
                    self.make_move(row, col)
                    return

    def select_from_rack_tiles(self, event):
        start, stop = (0, self.start_tiles.height//2) if self.players_turn == W else (self.start_tiles.height//2, self.start_tiles.height)
        for row in range(start, stop):
            for col, hexa in enumerate(self.start_tiles.board[row]):
                if type(hexa) is not Blank and hexa.rect.collidepoint(event.pos):
                    if self.hexa_selected:
                        self.hexa_selected.image = pygame.image.load(self.hexa_selected.image_loc)
                    hexa.image.blit(self.img_selected, (0, 0))
                    self.hexa_selected = hexa

    def select_from_board(self, event):
        for row in range(self.board.height):
            for col, hexa in enumerate(self.board.board[row]):
                if type(hexa) is not Blank and hexa.rect.collidepoint(event.pos):
                    self.board.board[row][col] = Blank()
                    hives = HiveGraph(self.board).count_hives()
                    self.board.board[row][col] = hexa
                    if hives == 1:
                        if self.hexa_selected:
                            self.hexa_selected.image = pygame.image.load(self.hexa_selected.image_loc)
                        hexa.image.blit(self.img_selected, (0, 0))
                        self.hexa_selected = hexa
                        return

    def make_move(self, row, col):
        self.start_tiles.board[self.hexa_selected.r][self.hexa_selected.c] = Blank()
        self.board.board[row][col] = self.hexa_selected
        self.board.board[row][col].r, self.board.board[row][col].c = row, col
        self.board.board[row][col].image = pygame.image.load(self.board.board[row][col].image_loc)
        if type(self.hexa_selected) == Bee:
            if self.players_turn == W:
                self.bee_placed_white = True
                self.bee_pos_white = [self.hexa_selected.r, self.hexa_selected.c]
            else:
                self.bee_placed_black = True
                self.bee_pos_black = [self.hexa_selected.r, self.hexa_selected.c]
        self.players_turn = opp(self.players_turn)
        self.turn_count += 1
        self.hexa_selected = None

    def move_white_first(self, first_move, event):
        r, c = self.board.height // 2, self.board.width // 2
        if first_move:
            for row in range(self.start_tiles.height//2):
                for col, hexa in enumerate(self.start_tiles.board[row]):
                    if hexa.rect.collidepoint(event.pos):
                        self.hexa_selected = hexa
                        self.make_move(r, c)
                        self.hexa_selected = None
                        return False
        return first_move

    def is_bee_placed(self, player):
        if player == W:
            return self.bee_placed_white
        else:
            return self.bee_placed_black

    def isGameOver(self):
        surrounded = True
        if opp(self.players_turn) == W:
            bee_pos = self.bee_pos_black
        else:
            bee_pos = self.bee_pos_white
        for n in get_cell_neighbours(*bee_pos, self.board.height, self.board.width):
            hexa = self.board.board[n[0]][n[1]]
            if type(hexa) is Blank:
                surrounded = False
        return surrounded

    def get_bee(self, player):
        return self.get_rack(player).board[0][3]


    def run_game(self):
        game_won = False
        first_move_white = True
        first_move_black = True
        last_event_pos = (0, 0)
        while not game_won:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if self.is_bee_placed(W) and self.is_bee_placed(B) and self.isGameOver():
                    game_won = True

                # if turn_count == 3 and not is_bee_placed(players_turn):
                #    TODO
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.hexa_selected:
                        self.move_to_board(event, last_event_pos)
                    else:
                        mouse_x, mouse_y = event.pos
                        if mouse_y < self.rack_pixel_height or mouse_y > self.pixel_height - self.rack_pixel_height:
                            if first_move_white:
                                first_move_white = self.move_white_first(first_move_white, event)
                            else:
                                self.select_from_rack_tiles(event)
                        else:
                            self.select_from_board(event)

                        if self.hexa_selected:
                            if first_move_black:
                                self.possible_moves = self.get_possible_first_moves_black()
                                first_move_black = False
                            else:
                                self.possible_moves = self.get_possible_moves()

                    last_event_pos = event.pos

            self.draw_board()
            pygame.display.update()
            self.clock.tick(30)


game = Game()
game.run_game()
