import sys
import math
from enum import Enum
import random

MAX_AMONT_TREE = 8 # 8 brings me to / 7 brings me to
COMPLETE_TIME = 22

def debug(*s):
    print(*s, file=sys.stderr, flush=True)


class ActionType(Enum):
    WAIT = "WAIT"
    SEED = "SEED"
    GROW = "GROW"
    COMPLETE = "COMPLETE"


# I should have all the infos on my cells.
class Cell:
    def __init__(self, cell_index, richness, neighbors):
        self.cell_index = cell_index
        self.richness = richness
        self.neighbors = neighbors
        self.tree = None
        self.shadow = 0 # need to place the shadows
        self.tree_neigh = 0 # to verify

    def sun_points(self):
        if self.tree and self.tree.is_mine and self.shadow < self.tree.size and self.richness:
            return self.tree.size + (self.richness - 1) * 2

    def reset(self):
        self.tree = None
        self.shadow = 0
        self.tree_neigh = 0


class Tree:
    def __init__(self, size, is_mine, is_dormant):
        # self.cell_index = cell_index
        self.size = size
        self.is_mine = is_mine
        self.is_dormant = is_dormant # after any action, becomes dormant


class Action:
    def __init__(self, type, target_cell_id=None, origin_cell_id=None):
        self.type = type
        self.target_cell_id = target_cell_id
        self.origin_cell_id = origin_cell_id or target_cell_id

    def __str__(self):
        if self.type == ActionType.WAIT:
            return 'WAIT'
        elif self.type == ActionType.SEED:
            return f'SEED {self.origin_cell_id} {self.target_cell_id}'
        else:
            return f'{self.type.name} {self.origin_cell_id}'

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def parse(action_string):
        split = action_string.split(' ')
        if split[0] == ActionType.WAIT.name:
            return Action(ActionType.WAIT)
        if split[0] == ActionType.SEED.name:
            return Action(ActionType.SEED, int(split[2]), int(split[1]))
        if split[0] == ActionType.GROW.name:
            return Action(ActionType.GROW, int(split[1]))
        if split[0] == ActionType.COMPLETE.name:
            return Action(ActionType.COMPLETE, int(split[1]))


class Board:
    def __init__(self):
        self.board = []
        self.size = 0
        self.trees = []

# ACCESS
    def __getitem__(self, key):
        return self.board[key]

    def __setitem__(self, key):
        return self.board[key]

    def append(self, stuff):
        return self.board.append(stuff)

# INPUT
    def get_first_input(self):
        self.size = int(input())
        for _ in range(self.size):
            cell_index, richness, *neigh = map(int, input().split())
            self.append(Cell(cell_index, richness, neigh))

    def reset_cells(self):
        for cell in self.board:cell.reset()
        self.trees = []

    def get_input(self):
        self.reset_cells()
        for _ in range(int(input())):
            cell_index, size, is_mine, is_dormant = map(int, input().split())
            self.board[cell_index].tree = Tree(size, is_mine, is_dormant)
            self.trees.append(Tree(size, is_mine, is_dormant)) # I should not need that...


# UTILS
    def get(self, cell_id):
        return self.board[cell_id] if cell_id != -1 else None

    def compute_tree_neigh(self):
        for cell in self.board:
            if cell.tree and cell.tree.is_mine:
                for n in cell.neighbors:
                    if self.get(n):self.get(n).tree_neigh += 1

    def compute_shadows(self):
        pass

    def count_my_trees(self):
        return sum([(cell.tree != None and cell.tree.is_mine) for cell in self.board])


class Game:
    def __init__(self):
        self.day = 0
        self.nutrients = 0
        # self.trees = []
        self.possible_actions = []
        self.my_sun = 0
        self.my_score = 0
        self.foe_sun = 0
        self.foe_score = 0
        self.foe_is_waiting = 0


    def get_input(self):
        self.day = int(input())
        self.nutrients = int(input())
        self.my_sun, self.my_score = map(int, input().split())
        self.foe_sun, self.foe_score, self.foe_is_waiting = map(int, input().split())

        board.get_input()

        self.possible_actions.clear()
        for _ in range(int(input())):
            action = Action.parse(input())
            if action.type != ActionType.WAIT:
                self.possible_actions.append(action)

    def compute_next_action(self):
        debug([po for po in self.possible_actions])

        # order by case number
        self.possible_actions.sort(key=lambda x:x.target_cell_id, reverse=True)

        # Separate Actions
        complete_actions = [action for action in self.possible_actions if action.type == ActionType.COMPLETE]
        seed_actions = [action for action in self.possible_actions if action.type == ActionType.SEED]
        grow_actions = [action for action in self.possible_actions if action.type == ActionType.GROW]

        # remove COMPLETE
        debug("all are 3 ?", [tree.size == 3 for tree in board.trees if tree.is_mine])
        if self.day < COMPLETE_TIME and self.my_score < self.foe_score + 20 \
            and sum([(tree.size == 3, 0)[tree.is_mine] for tree in board.trees]) < 5 \
                and not all([tree.size == 3 for tree in board.trees if tree.is_mine]):
            complete_actions = []

        # remove SEED
        if board.count_my_trees() >= MAX_AMONT_TREE - self.day // 4:
            seed_actions = []

        # sort
        complete_actions.sort(key=lambda x:x.target_cell_id, reverse=True)
        self.possible_actions = seed_actions + grow_actions

        board.compute_tree_neigh()
        self.possible_actions.sort(key=lambda x:board.get(x.target_cell_id).tree_neigh) # first the one with the less neigh
        self.possible_actions.sort(key=lambda x:board.get(x.target_cell_id).richness, reverse=True) # first the richest

        debug([po for po in self.possible_actions])

        return complete_actions[0] if complete_actions else (self.possible_actions[0] if self.possible_actions else "WAIT")


game = Game()
board = Board()
board.get_first_input() # only the first time


while True:
    debug("nutrients =", game.nutrients)
    game.get_input()
    print(game.compute_next_action())
