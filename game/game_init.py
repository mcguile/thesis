import pygame
import sys
from pygame.locals import *
from insects import *
from board import *
from count_hives import HiveGraph

W = 'white'
B = 'black'
NW = 'North-West'
NE = 'North-East'
SE = 'South-East'
SW = 'South-West'
ALL = "All"


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
    rack = Board(6, 5)
    for i in range(2):
        x, player = (0, W) if i == 0 else (3, B)
        rack.board[0 + x][0] = Ant(player, 0 + x, 0)
        rack.board[1 + x][0] = Ant(player, 1 + x, 0)
        rack.board[2 + x][0] = Ant(player, 2 + x, 0)
        rack.board[0 + x][1] = Beetle(player, 0 + x, 1)
        rack.board[1 + x][1] = Beetle(player, 1 + x, 1)
        rack.board[0 + x][2] = Grasshopper(player, 0 + x, 2)
        rack.board[1 + x][2] = Grasshopper(player, 1 + x, 2)
        rack.board[2 + x][2] = Grasshopper(player, 2 + x, 2)
        rack.board[0 + x][3] = Bee(player, 0 + x, 3)
        rack.board[0 + x][4] = Spider(player, 0 + x, 4)
        rack.board[1 + x][4] = Spider(player, 1 + x, 4)
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


def get_hexas_straight_line(fromm, w, h, direction=ALL):
    hexas_n, hexas_s, hexas_ne, hexas_se, hexas_sw, hexas_nw = [], [], [], [], [], []
    r_n, c_n = r_s, c_s = r_se, c_se = r_sw, c_sw = r_nw, c_nw = r_ne, c_ne = fromm
    for i in range(min(w, h)):
        r_n -= 1
        r_s += 1
        if r_se % 2 == 1 and c_se % 2 == 1:
            r_se += 1
            c_se += 1
            r_sw += 1
            c_sw -= 1
            c_nw -= 1
            c_ne += 1
        elif r_se % 2 == 1 and c_se % 2 == 0:
            c_se += 1
            c_sw -= 1
            r_nw -= 1
            c_nw -= 1
            r_ne -= 1
            c_ne += 1
        elif r_se % 2 == 0 and c_se % 2 == 0:
            c_se += 1
            c_sw -= 1
            r_nw -= 1
            c_nw -= 1
            r_ne -= 1
            c_ne += 1
        elif r_se % 2 == 0 and c_se % 2 == 1:
            r_se += 1
            c_se += 1
            r_sw += 1
            c_sw -= 1
            c_nw -= 1
            c_ne += 1
        hexas_n.append((r_n, c_n))
        hexas_s.append((r_s, c_s))
        hexas_nw.append((r_nw, c_nw))
        hexas_ne.append((r_ne, c_ne))
        hexas_sw.append((r_sw, c_sw))
        hexas_se.append((r_se, c_se))
    if direction == ALL:
        return hexas_n, hexas_s, hexas_ne, hexas_se, hexas_sw, hexas_nw
    elif direction == NE:
        return hexas_ne
    elif direction == SE:
        return hexas_se
    elif direction == SW:
        return hexas_sw
    else:
        return hexas_nw


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
        #self.drag_surf_rect.x += 23  # Center first piece on screen (Commented for now as it affects click pos)
        self.hexa_size = pygame.image.load('../img_assets/blank.png').get_rect().size
        self.hexa_width, self.hexa_height = self.hexa_size
        self.players_turn = W
        self.bee_placed_white, self.bee_placed_black = False, False
        self.bee_pos_white, self.bee_pos_black = (0, 3), (3, 3)
        self.turn_count_white, self.turn_count_black = 0, 0
        self.hexa_selected = None
        self.board = init_board(16, 16)
        self.start_tiles = init_start_tiles()
        self.possible_moves = set()
        self.mouse_pos = pygame.Rect((0, 0), self.hexa_size)

    def setup_tiles(self):
        y = 0
        self.rack_bottom_surf.fill((0, 0, 0, 0))
        self.rack_top_surf.fill((0, 0, 0, 0))
        for r, _ in enumerate(self.start_tiles.board):
            add_height = self.pixel_height - self.rack_pixel_height if r >= self.start_tiles.height // 2 else 0
            if r == self.start_tiles.height // 2:
                y = 0
            rack_surf = self.rack_top_surf if r < 3 else self.rack_bottom_surf
            x = int(self.pixel_width / 6) - self.hexa_width / 2
            y += 20
            for hexa in self.start_tiles.board[r]:
                rack_surf.blit(hexa.image, (x, y))
                hexa.rect = pygame.Rect((x, y + add_height), self.hexa_size)
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

    def breaks_freedom_to_move_rule(self, r, c):
        """
        Does the hex attempted to be moved to have 5 or more pieces around it?
        'Freedom to move' rule.
        :return: boolean
        """
        neighbours = get_cell_neighbours(r, c, self.board.height, self.board.width)
        count_pieces = 0
        for r, c in neighbours:
            if type(self.board.board[r][c]) != Blank:
                count_pieces += 1
        return count_pieces >= 5

    def move_wont_break_hive(self, r, c):
        """
        Check if moving piece causes break in hive.
        Hive check needs to be through entire movement of a piece.
        i.e. if the hive is ever broken by either lifting the piece
        of by placing the piece somewhere detached from the hive
        :param r:
        :param c:
        :return:
        """
        if type(self.board.board[r][c]) is not Blank:
            return True
        if type(self.hexa_selected) is Stack:
            tmp = Stack(stack=self.hexa_selected.stack, row=self.hexa_selected.r, col=self.hexa_selected.c)
        else:
            tmp = type(self.hexa_selected)(
                row=self.hexa_selected.r, col=self.hexa_selected.c,
                player=self.hexa_selected.player, image=self.hexa_selected.image)
        self.board.board[self.hexa_selected.r][self.hexa_selected.c] = Blank()
        hives1stcheck = HiveGraph(self.board).count_hives()
        self.board.board[r][c] = tmp
        hives2ndcheck = HiveGraph(self.board).count_hives()
        self.board.board[tmp.r][tmp.c] = tmp
        self.hexa_selected = tmp
        self.board.board[r][c] = Blank()
        return hives1stcheck == hives2ndcheck == 1

    def get_possible_moves_bee(self):
        possible_moves = set()
        neighbours_of_selected = get_cell_neighbours(self.hexa_selected.r, self.hexa_selected.c, self.board.height,
                                                     self.board.width)
        for r, c in neighbours_of_selected:
            if type(self.board.board[r][c]) is Blank:
                if self.move_wont_break_hive(r, c):
                    possible_moves.add((r, c))
        return possible_moves

    def get_possible_moves_spider(self):
        pass

    def get_possible_moves_ant(self):
        possible_moves = set()
        for r, _ in enumerate(self.board.board):
            for c, hexa in enumerate(self.board.board[r]):
                if (r, c) == (self.hexa_selected.r, self.hexa_selected.c):
                    continue
                if type(self.board.board[r][c]) is not Blank:
                    for n_r, n_c in get_cell_neighbours(r, c, self.board.height, self.board.width):
                        if type(self.board.board[n_r][n_c]) is Blank and \
                                not self.breaks_freedom_to_move_rule(n_r, n_c) and \
                                self.move_wont_break_hive(n_r, n_c):
                            possible_moves.add((n_r, n_c))
        return possible_moves

    def get_possible_moves_beetle(self):
        possible_moves = set()
        for r, c in get_cell_neighbours(self.hexa_selected.r, self.hexa_selected.c, self.board.height, self.board.width):
            if self.move_wont_break_hive(r, c):
                possible_moves.add((r, c))
        return possible_moves

    def valid_grasshopper_move(self, r, c):
        return (type(self.board.board[r][c]) is Blank and
                (r, c) not in get_cell_neighbours(self.hexa_selected.r, self.hexa_selected.c,
                                                  self.board.height, self.board.width) and
                self.move_wont_break_hive(r, c))

    def get_possible_moves_grasshopper(self):
        possible_moves = set()
        r, c = self.hexa_selected.r, self.hexa_selected.c
        n, s, ne, se, sw, nw = get_hexas_straight_line((r, c), self.board.width, self.board.height)
        for direction in [n, s, ne, se, sw, nw]:
            found_bug_to_jump = False
            for r, c in direction:
                if 0 <= r < self.board.height and 0 <= c < self.board.width:
                    if not found_bug_to_jump:
                        if type(self.board.board[r][c]) is Blank:
                            break
                        else:
                            found_bug_to_jump = True
                            continue
                    elif self.valid_grasshopper_move(r, c):
                        possible_moves.add((r, c))
                        break
        return possible_moves

    def get_possible_moves_from_board(self):
        t = type(self.hexa_selected)
        if t == Bee:
            return self.get_possible_moves_bee()
        elif t == Spider:
            return self.get_possible_moves_bee()
        elif t == Ant:
            return self.get_possible_moves_ant()
        elif t == Beetle or t == Stack:
            if t == Stack:
                print(self.hexa_selected.stack)
            return self.get_possible_moves_beetle()
        else:
            return self.get_possible_moves_grasshopper()

    def get_possible_moves_from_rack(self):
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

    def move_to_board(self, event, fromm):
        for row in range(self.board.height):
            for col, hexa in enumerate(self.board.board[row]):
                if hexa.rect.collidepoint(event.pos) and (row, col) in self.possible_moves:
                    self.make_move(row, col, fromm)
                    return

    def select_from_rack_tiles(self, mouse_pos):
        start, stop = (0, self.start_tiles.height // 2) if self.players_turn == W else (
            self.start_tiles.height // 2, self.start_tiles.height)
        for row in range(start, stop):
            for col, hexa in enumerate(self.start_tiles.board[row]):
                if type(hexa) is not Blank and hexa.rect.collidepoint(mouse_pos):
                    if self.hexa_selected:
                        self.hexa_selected.image = pygame.image.load(self.hexa_selected.image_loc)
                    hexa.image.blit(self.img_selected, (0, 0))
                    self.hexa_selected = hexa
                    self.mouse_pos.x, self.mouse_pos.y = np.subtract(mouse_pos, (self.hexa_width // 2,
                                                                                 self.hexa_height // 2))

    def select_from_board(self, event):
        for row in range(self.board.height):
            for col, hexa in enumerate(self.board.board[row]):
                if type(hexa) is not Blank and hexa.rect.collidepoint(event.pos) and hexa.player == self.players_turn:
                    if self.hexa_selected:
                        self.hexa_selected.image = pygame.image.load(self.hexa_selected.image_loc)
                    hexa.image.blit(self.img_selected, (0, 0))
                    self.hexa_selected = hexa
                    self.mouse_pos.x, self.mouse_pos.y = np.subtract(event.pos, (self.hexa_width // 2,
                                                                                 self.hexa_height // 2))
                    return

    def make_move(self, to_row, to_col, fromm_board):
        f_row, f_col = self.hexa_selected.r, self.hexa_selected.c
        dest_t = type(self.board.board[to_row][to_col])
        if dest_t is not Blank:
            # Must be a beetle
            # Check if selected is just a beetle or a stack
            if type(self.hexa_selected) is Stack:
                beetle = self.hexa_selected.remove_piece()
                if len(self.hexa_selected.stack) == 1:
                    fromm_board.board[f_row][f_col] = self.hexa_selected.stack[0]
                else:
                    fromm_board.board[f_row][f_col] = self.hexa_selected
                self.hexa_selected = beetle
            else:
                fromm_board.board[f_row][f_col] = Blank()
            # Create stack or append to the stack
            if dest_t is Stack:
                self.board.board[to_row][to_col].add_piece(self.hexa_selected)
            else:
                self.board.board[to_row][to_col] = Stack(first_piece=self.board.board[to_row][to_col],
                                                         stacked_piece=self.hexa_selected,
                                                         row=to_row, col=to_col)

        else:
            if type(fromm_board.board[f_row][f_col]) is not Stack:
                fromm_board.board[f_row][f_col] = Blank()
            else:
                beetle = self.hexa_selected.remove_piece()
                if len(self.hexa_selected.stack) == 1:
                    fromm_board.board[f_row][f_col] = self.hexa_selected.stack[0]
                else:
                    fromm_board.board[f_row][f_col] = self.hexa_selected
                self.hexa_selected = beetle
            self.board.board[to_row][to_col] = self.hexa_selected
            self.board.board[to_row][to_col].r, self.board.board[to_row][to_col].c = to_row, to_col
            self.board.board[to_row][to_col].image = pygame.image.load(self.board.board[to_row][to_col].image_loc)
            if type(self.hexa_selected) == Bee:
                if self.players_turn == W:
                    self.bee_placed_white = True
                    self.bee_pos_white = [to_row, to_col]
                else:
                    self.bee_placed_black = True
                    self.bee_pos_black = [to_row, to_col]
        self.increment_turn_count()
        self.players_turn = opp(self.players_turn)
        self.hexa_selected = None
        self.possible_moves = set()

    def move_white_first(self, first_move, event):
        r, c = self.board.height // 2, self.board.width // 2
        if first_move:
            for row in range(self.start_tiles.height // 2):
                for col, hexa in enumerate(self.start_tiles.board[row]):
                    if hexa.rect.collidepoint(event.pos) and type(hexa) is not Blank:
                        self.hexa_selected = hexa
                        self.make_move(r, c, self.start_tiles)
                        self.hexa_selected = None
                        return False
        return first_move

    def black_has_moved(self):
        start, stop = self.start_tiles.height // 2, self.start_tiles.height
        count = 0
        for row in range(start, stop):
            for col, hexa in enumerate(self.start_tiles.board[row]):
                if type(hexa) is not Blank:
                    count += 1
        return count < 11

    def is_bee_placed(self, player):
        if player == W:
            return self.bee_placed_white
        else:
            return self.bee_placed_black

    def isGameOver(self):
        if not self.is_bee_placed(W) or not self.is_bee_placed(B):
            return False
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

    def increment_turn_count(self):
        if self.players_turn == W:
            self.turn_count_white += 1
        else:
            self.turn_count_black += 1

    def deselect(self):
        self.hexa_selected.image = pygame.image.load(self.hexa_selected.image_loc)
        self.possible_moves = set()
        self.mouse_pos.x, self.mouse_pos.y = 0, 0
        self.hexa_selected = None

    def run_game(self):
        first_move_white = True
        first_move_black = True
        move_from = None
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                if not self.isGameOver():
                    if event.type == pygame.MOUSEBUTTONUP:
                        if self.hexa_selected:
                            if self.mouse_pos.collidepoint(event.pos):
                                self.deselect()
                            else:
                                self.move_to_board(event, move_from)
                                if first_move_black and self.black_has_moved():
                                    first_move_black = False
                        else:
                            mouse_x, mouse_y = event.pos
                            if self.turn_count_white == 3 and self.players_turn == W and not self.is_bee_placed(W):
                                mouse_x, mouse_y = self.start_tiles.board[0][3].rect.centerx, self.start_tiles.board[0][3].rect.centery
                            elif self.turn_count_black == 3 and self.players_turn == B and not self.is_bee_placed(B):
                                mouse_x, mouse_y = self.start_tiles.board[3][3].rect.centerx, self.start_tiles.board[3][3].rect.centery
                            if mouse_y < self.rack_pixel_height or mouse_y > self.pixel_height - self.rack_pixel_height:
                                move_from = self.start_tiles
                                if first_move_white:
                                    first_move_white = self.move_white_first(first_move_white, event)
                                else:
                                    self.select_from_rack_tiles((mouse_x, mouse_y))
                            else:
                                move_from = self.board
                                self.select_from_board(event)

                            if self.hexa_selected:
                                if first_move_black:
                                    self.possible_moves = self.get_possible_first_moves_black()
                                elif move_from.height <= 6:
                                    self.possible_moves = self.get_possible_moves_from_rack()
                                else:
                                    self.possible_moves = self.get_possible_moves_from_board()

            self.draw_board()
            pygame.display.update()
            self.clock.tick(30)


game = Game()
game.run_game()
