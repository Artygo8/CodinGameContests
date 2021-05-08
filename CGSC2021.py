import sys
import math
from enum import Enum
import random

# I was 945th

DAYS_TO_SEED = 5
MAX_AMONT_TREE = 5
COMPLETE_TIME = 23

def debug(*s):
    print(*s, file=sys.stderr, flush=True)


# Action Type
class AT(Enum):
    WAIT = "WAIT"
    SEED = "SEED"
    GROW = "GROW"
    COMPLETE = "COMPLETE"

#  ____  _                       
# |  _ \| | __ _ _   _  ___ _ __ 
# | |_) | |/ _` | | | |/ _ \ '__|
# |  __/| | (_| | |_| |  __/ |   
# |_|   |_|\__,_|\__, |\___|_|   
#                |___/           

class Player:
    def __init__(self):
        self.possible_actions = []
        self.sun = 0
        self.score = 0
        self.is_waiting = 0
        self.trees = [] # these are positions

    def __str__(self):
        return f"{[tree for tree in self.trees]}"

    def update(self, sun, score, is_waiting=0):
        self.sun = sun
        self.score = score
        self.is_waiting = is_waiting
        self.trees.clear()

    def get_input_actions(self):
        # Possible actions, probably useless
        self.possible_actions.clear()
        for _ in range(int(input())):
            action = Action.parse(input())
            if action.type != AT.WAIT:
                self.possible_actions.append(action)

    def compute_possible_actions(self, bd):
        computed_actions = []
        for pos in self.trees:
            if bd[pos].is_dormant:
                continue
            # seedables
            seedable = set()
            for _ in range(bd[pos].size):
                for neigh in set(bd[pos].neighbors).union(seedable):
                    seedable.add(neigh)
            for s in seedable:
                if bd[s].tree == False:
                    computed_actions.append(Action(AT.SEED, s, pos))
            # complete
            if bd[pos].size == 3:
                computed_actions.append(Action(AT.COMPLETE, pos))
            # grow
            else:
                computed_actions.append(Action(AT.GROW, pos))
        return computed_actions

    def current_total_cost(self, bd):
        total = 0
        nb_by_size = [sum(pos for pos in self.trees if bd[pos].size == i) for i in range(4)]
        for pos in self.trees:
            if bd[pos].size == 3:
                total += 4
            if bd[pos].size == 2:
                total += 7 + nb_by_size[3]
                nb_by_size[3] += 1
            if bd[pos].size == 1:
                total += 3 + nb_by_size[2]
                nb_by_size[2] += 1
            if bd[pos].size == 0:
                total += 1 + nb_by_size[1]
                nb_by_size[1] += 1
        return total

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
        self.tree_neigh = 0

    def __str__(self):
        return f"Cell {self.cell_index} r({self.richness}) s({self.shadow}) n({self.neighbors}):" + f"T size = {self.size}, is {('not','')[self.is_mine]} mine {('','(dormant)')[self.is_dormant]}:" if self.tree else ''

    def put_tree(self, size, is_mine, is_dormant):
        self.tree = True
        self.size = size
        self.is_mine = is_mine
        (foe, me)[is_mine].trees.append(self.cell_index)
        self.is_dormant = is_dormant

    def sun_points(self):
        if self.tree and self.tree.is_mine and self.shadow < self.tree.size and self.richness:
            return self.tree.size + (self.richness - 1) * 2

    def reset(self):
        self.tree = False
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
        if split[0] == AT.WAIT.name:
            return Action(AT.WAIT)
        if split[0] == AT.SEED.name:
            return Action(AT.SEED, int(split[2]), int(split[1]))
        if split[0] == AT.GROW.name:
            return Action(AT.GROW, int(split[1]))
        if split[0] == AT.COMPLETE.name:
            return Action(AT.COMPLETE, int(split[1]))


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

    def append(self, stuff):
        return self.board.append(stuff)

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.size:
            self.n += 1
            return self[self.n - 1]
        else:
            raise StopIteration

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
        for pos in self.tree_pos:
            height = self[pos].size
            for _ in range(height):
                pos = self[pos].neighbors[day % 6]
                if pos == -1:
                    break
                self[pos].shadow = height

# Utils
    def count_my_trees(self):
        return sum([(cell.tree and cell.is_mine) for cell in self])


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

me = Player()
foe = Player()

while True:

    day = int(input())
    game.get_input()

    debug("nut =", game.nutrients, ", ")
    debug("me:", me)
    debug("foe:", foe)

    board.compute_tree_neigh()
    board.compute_shadows(day)

    print(game.basic_compute_next_action())
