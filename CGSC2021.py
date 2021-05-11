import sys
import math
from enum import Enum
import random, copy

# I was 945th

DAYS_TO_SEED = 5
MAX_AMONT_TREE = 8
COMPLETE_TIME = 23

def debug(*s):
    print(*s, file=sys.stderr, flush=True)


# Action Type
class AT(Enum):
    WAIT = "WAIT"
    SEED = "SEED"
    GROW = "GROW"
    COMPLETE = "COMPLETE"


class Simulation:

    def __init__(self):
        self.best_score = -1

    def one_turn_simu(self, board, player, iday):

        player.possible_actions = board.compute_possible_actions(player)
        # total_cost = board.current_total_cost(player)
        best_action = Action.parse('WAIT')

        benef = 10000 # smallest

        debug(player.possible_actions)
        debug(player.sun)

        for action in player.possible_actions:
            bd = board.__copy__()
            cur_player = player.__copy__()

            price = action.price(cur_player, bd)

            if cur_player.sun >= price:
                bd.apply(action, cur_player)

                end_sun = bd.sun_points_at_end(cur_player, iday)
                debug(action, "---", end_sun)

                # THE MAGIC IS HERE
                cur_benef = end_sun
                if action.type == AT.SEED and iday < 13:
                    cur_benef = iday * 4 if iday * 4 < cur_benef else cur_benef

                if end_sun >= bd.current_total_cost(cur_player) and cur_benef < benef:
                    debug("OK !")
                    benef = cur_benef
                    best_action = action

        return best_action


#  ____  _                       
# |  _ \| | __ _ _   _  ___ _ __ 
# | |_) | |/ _` | | | |/ _ \ '__|
# |  __/| | (_| | |_| |  __/ |   
# |_|   |_|\__,_|\__, |\___|_|   
#                |___/           

class Player:
    def __init__(self, itsme, sun=0, score=0, is_waiting=False):
        self.possible_actions = []
        self.itsme = itsme
        self.sun = sun
        self.score = score
        self.is_waiting = is_waiting

    def __str__(self):
        return f'{("foe", "me")[self.itsme]} - score={self.score} - sun= {self.sun}'

    def __copy__(self):
        return Player(self.itsme, self.sun, self.score, self.is_waiting)

    def update(self, sun, score, is_waiting=0):
        self.sun = sun
        self.score = score
        self.is_waiting = is_waiting

    def get_input_actions(self):
        # Possible actions, probably useless
        self.possible_actions.clear()
        for _ in range(int(input())):
            action = Action.parse(input())
            if action.type != AT.WAIT:
                self.possible_actions.append(action)

#   ____     _ _ 
#  / ___|___| | |
# | |   / _ \ | |
# | |__|  __/ | |
#  \____\___|_|_|
#                

class Cell:
    def __init__(self, cell_index, richness, *neighbors):
        self.cell_index = cell_index
        self.richness = richness
        self.neighbors = list(neighbors)

        self.tree = False
        self.size = 0
        self.is_mine = 0
        self.is_dormant = 0 # after any action, becomes dormant

        self.shadow = 0
        self.tree_neigh = 0 # to suppress

    def __str__(self):
        return f"Cell {self.cell_index} r({self.richness}) s({self.shadow}) n({self.neighbors}):" + f"T size = {self.size}, is {('not','')[self.is_mine]} mine {('','(dormant)')[self.is_dormant]}:" if self.tree else ''

    def __copy__(self):
        new = Cell(self.cell_index, self.richness, *self.neighbors)
        new.tree = self.tree
        new.size = self.size
        new.is_mine = self.is_mine
        new.is_dormant = self.is_dormant
        new.shadow = self.shadow
        new.tree_neigh = self.tree_neigh # probably wont need that
        return new

    def put_tree(self, size=0, is_mine=1, is_dormant=0):
        self.tree = True
        self.size = size
        self.is_mine = is_mine
        self.is_dormant = is_dormant

    def seed(self, player):
        self.put_tree(size=0, is_mine=player.itsme, is_dormant=True) 

    def grow(self, player):
        self.size += 1

    def complete(self, player):
        self.reset()
        player.score += game.nutrients # not very clever

    def sun_points(self):
        if self.size == 0:return 0
        return (0, self.size + (self.richness - 1) * 2)[self.tree and self.is_mine and (self.shadow < self.size or self.shadow == 0)]

    def reset(self):
        self.tree = False
        self.size = 0
        self.is_mine = 0
        self.is_dormant = 0 # after any action, becomes dormant
        self.shadow = 0
        self.tree_neigh = 0

#     _        _   _             
#    / \   ___| |_(_) ___  _ __  
#   / _ \ / __| __| |/ _ \| '_ \ 
#  / ___ \ (__| |_| | (_) | | | |
# /_/   \_\___|\__|_|\___/|_| |_|
#                                

class Action:
    def __init__(self, type, target_cell_id=None, origin_cell_id=None):
        self.type = type
        self.target_cell_id = target_cell_id
        self.origin_cell_id = origin_cell_id or target_cell_id

    def __str__(self):
        return self.type.name + (f' {self.origin_cell_id}','')[self.type == AT.WAIT] \
            + ('', f' {self.target_cell_id}')[self.type == AT.SEED]

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def parse(action_string):
        split = action_string.split(' ')
        return Action(AT[split[0]], *map(int, split[1:][::-1]))

    def price(self, player, bd): # if sleep enters, crash.
        nb_by_size = [sum(cell.tree for cell in bd if (cell.size == i and cell.is_mine == player.itsme)) for i in range(5)] # 5 to have 0
        height = bd[self.target_cell_id].size
        return ((0, 3, 7, 4)[height] + nb_by_size[1:][height], 1)[self.type == AT.SEED]


#  ____                      _ 
# | __ )  ___   __ _ _ __ __| |
# |  _ \ / _ \ / _` | '__/ _` |
# | |_) | (_) | (_| | | | (_| |
# |____/ \___/ \__,_|_|  \__,_|
#                              

class Board:
    def __init__(self):
        self.board = []
        self.size = 0
        self.tree_pos = []

# ACCESS
    def __getitem__(self, key):
        return self.board[key]

    def __setitem__(self, key):
        return self.board[key]

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.size:
            self.n += 1
            return self[self.n - 1]
        else:
            raise StopIteration

    def __str__(self):
        s=self
        return f'''
     [{s[25].size if s[25].tree else ' '}|{s[24].size if s[24].tree else ' '}|{s[23].size if s[23].tree else ' '}|{s[22].size if s[22].tree else ' '}]
    [{s[26].size if s[26].tree else ' '}|{s[11].size if s[11].tree else ' '}|{s[10].size if s[10].tree else ' '}|{s[9].size if s[9].tree else ' '}|{s[21].size if s[21].tree else ' '}]
   [{s[27].size if s[27].tree else ' '}|{s[12].size if s[12].tree else ' '}|{s[3].size if s[3].tree else ' '}|{s[2].size if s[2].tree else ' '}|{s[8].size if s[8].tree else ' '}|{s[20].size if s[20].tree else ' '}]
  [{s[28].size if s[28].tree else ' '}|{s[13].size if s[13].tree else ' '}|{s[4].size if s[4].tree else ' '}|{s[0].size if s[0].tree else ' '}|{s[1].size if s[1].tree else ' '}|{s[7].size if s[7].tree else ' '}|{s[19].size if s[19].tree else ' '}]
   [{s[29].size if s[29].tree else ' '}|{s[14].size if s[14].tree else ' '}|{s[5].size if s[5].tree else ' '}|{s[6].size if s[6].tree else ' '}|{s[18].size if s[18].tree else ' '}|{s[36].size if s[36].tree else ' '}]
    [{s[30].size if s[30].tree else ' '}|{s[15].size if s[15].tree else ' '}|{s[16].size if s[16].tree else ' '}|{s[17].size if s[17].tree else ' '}|{s[35].size if s[35].tree else ' '}]
     [{s[31].size if s[31].tree else ' '}|{s[32].size if s[32].tree else ' '}|{s[33].size if s[33].tree else ' '}|{s[34].size if s[34].tree else ' '}]
'''

    def __copy__(self):
        bd = Board()
        for cell in self:
            bd.append(cell.__copy__())
        bd.size = self.size
        bd.tree_pos = list(self.tree_pos)
        return bd

    def append(self, stuff):
        return self.board.append(stuff)

# INPUT
    def get_first_input(self):
        self.size = int(input())
        for _ in range(self.size):
            self.append(Cell(*[int(i) for i in input().split()]))

    def get_input(self):
        # reset
        for cell in self:
            cell.reset()
        self.tree_pos = []

        for _ in range(int(input())):
            cell_index, size, is_mine, is_dormant = map(int, input().split())
            self[cell_index].put_tree(size, is_mine, is_dormant)
            self.tree_pos.append(cell_index) # I should not need that...

# COMPUTE
    def compute_tree_neigh(self):
        for pos in self.tree_pos:
            for n in self[pos].neighbors:
                if n >= 0:
                    self[n].tree_neigh += 1

    def compute_shadows(self, day):
        # reset the shadows
        for cell in self:
            cell.shadow = 0
        # compute shadows
        for pos in self.tree_pos:
            height = self[pos].size
            for _ in range(height):
                pos = self[pos].neighbors[day % 6]
                if pos == -1:
                    break
                if self[pos].shadow < height:
                    self[pos].shadow = height


    def compute_possible_actions(self, player):
        computed_actions = []
        for cell in self:
            # seedables
            seedable = set()
            for _ in range(cell.size):
                for neigh in set(cell.neighbors).union(seedable):
                    seedable.add(neigh)
            for seed in seedable:
                if self[seed].tree == False and self[seed].richness > 0 and seed != -1 and cell.is_mine == player.itsme:
                    computed_actions.append(Action(AT.SEED, seed, cell.cell_index))
            # complete + grow
            if cell.is_mine == player.itsme and cell.tree:
                computed_actions.append(Action((AT.GROW, AT.COMPLETE)[cell.size == 3], cell.cell_index))
        return computed_actions

# CALCULATE
    def current_total_cost(self, player): # for trees
        total = 0
        nb_by_size = [sum(cell.tree for cell in self if (cell.size == i and cell.is_mine == player.itsme)) for i in range(4)]
        for cell in self:
            if cell.tree and cell.is_mine == player.itsme:
                if cell.size >= 3:
                    total += 4
                if cell.size >= 2:
                    total += 7 + nb_by_size[3]
                    nb_by_size[3] += 1
                if cell.size >= 1:
                    total += 3 + nb_by_size[2]
                    nb_by_size[2] += 1
                if cell.size >= 0:
                    total += 1 + nb_by_size[1]
                    nb_by_size[1] += 1
        return total

    def sun_points(self, player, iday):
        self.compute_shadows(iday)
        return sum(cell.sun_points() for cell in self)

    def sun_points_over6days(self, player):
        return [self.sun_points(player, iday) for iday in range(6)]

    def sun_points_at_end(self, player, iday):
        sun_day_by_day = self.sun_points_over6days(player) * (24 // 6)
        return sum(sun_day_by_day[iday:]) + player.sun

    def apply(self, action, player): # care, it only works for ME (put_tree)
        if action.type == AT.SEED:
            self[action.target_cell_id].seed(player)
        elif action.type == AT.COMPLETE:
            self[action.target_cell_id].complete(player)
        elif action.type == AT.GROW:
            self[action.target_cell_id].grow(player)
        self[action.origin_cell_id].is_dormant = True

    def count_trees(self, player):
        return sum([(cell.tree and cell.is_mine == player.itsme) for cell in self])


#   ____                      
#  / ___| __ _ _ __ ___   ___ 
# | |  _ / _` | '_ ` _ \ / _ \
# | |_| | (_| | | | | | |  __/
#  \____|\__,_|_| |_| |_|\___|
#                             
class Game:

    global day

    def __init__(self):
        self.nutrients = 0

    def get_input(self):
        self.nutrients = int(input())
        me.update(*map(int, input().split()))
        foe.update(*map(int, input().split()))
        board.get_input()
        me.get_input_actions()

    def basic_compute_next_action(self):

        # order by case number
        me.possible_actions.sort(key=lambda x:x.target_cell_id, reverse=True)
        # Separate Actions
        complete_actions = [action for action in me.possible_actions if action.type == AT.COMPLETE]
        seed_actions = [action for action in me.possible_actions if action.type == AT.SEED]
        grow_actions = [action for action in me.possible_actions if action.type == AT.GROW]
        # remove COMPLETE
        if day < COMPLETE_TIME and me.score < foe.score + 20:
            complete_actions = []

        # remove SEED
        if len(me.trees) > MAX_AMONT_TREE and me.sun < me.current_total_cost(board):
            seed_actions = []
        seed_actions = [seed for seed in seed_actions if board[seed.target_cell_id].tree_neigh < 3]


        # sort
        complete_actions.sort(key=lambda x:x.target_cell_id, reverse=True)
        self.possible_actions = seed_actions + grow_actions

        self.possible_actions.sort(key=lambda x:board[x.target_cell_id].tree_neigh) # first the one with the less neigh
        self.possible_actions.sort(key=lambda x:board[x.target_cell_id].richness, reverse=True) # first the richest

        return complete_actions[0] if complete_actions else (self.possible_actions[0] if self.possible_actions else "WAIT")


game = Game()

board = Board()
board.get_first_input() # only the first time

simu = Simulation()

me = Player(itsme=True)
foe = Player(itsme=False)

while True:

    day = int(input())
    game.get_input()

    # print(game.basic_compute_next_action())
    print(simu.one_turn_simu(board, me, day))
