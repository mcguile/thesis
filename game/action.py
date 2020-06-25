class Action:
    def __init__(self, player, r_f, c_f, r_t, c_t):
        self.player = player
        self.r_f = r_f
        self.c_f = c_f
        self.r_t = r_t
        self.c_t = c_t

    def __str__(self):
        return '(' + str(self.r_f) + ', ' + str(self.c_f) + ' to ' + str(self.r_t) + ', ' + str(self.c_t) + ')'

    def __repr__(self):
        return str((self.r_f, self.c_f, self.r_t, self.c_t))

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.r_f == other.r_f and self.c_f == other.c_f and \
               self.player == other.player and self.r_t == other.r_t and self.c_t == other.c_t

    def __hash__(self):
        return hash((self.r_f, self.c_f, self.r_t, self.c_t, self.player))
