import sys
import math
from enum import Enum
import random

DAYS_TO_PLANT = 6
MAX_AMONT_TREE = 36
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

class Tree:
    def __init__(self, cell_index, size, is_mine, is_dormant):
        self.cell_index = cell_index
        self.size = size
        self.is_mine = is_mine
        self.is_dormant = is_dormant

class Action:
    def __init__(self, type, target_cell_id=None, origin_cell_id=None):
        self.type = type
        self.target_cell_id = target_cell_id
        self.origin_cell_id = origin_cell_id

    def __str__(self):
        if self.type == ActionType.WAIT:
            return 'WAIT'
        elif self.type == ActionType.SEED:
            return f'SEED {self.origin_cell_id} {self.target_cell_id}'
        else:
            return f'{self.type.name} {self.target_cell_id}'

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

class Game:
    def __init__(self):
        self.day = 0
        self.nutrients = 0
        self.board = []
        self.trees = []
        self.possible_actions = []
        self.my_sun = 0
        self.my_score = 0
        self.foe_sun = 0
        self.foe_score = 0
        self.foe_is_waiting = 0

        # first inputs
        self.grid_size = int(input())
        for i in range(self.grid_size):
            cell_index, richness, *neigh = map(int, input().split())
            self.board.append(Cell(cell_index, richness, neigh))

    def get_input(self):
        self.day = int(input())
        self.nutrients = int(input())
        self.my_sun, self.my_score = map(int, input().split())
        self.foe_sun, self.foe_score, self.foe_is_waiting = map(int, input().split())

        self.trees.clear()
        for _ in range(int(input())):
            cell_index, size, is_mine, is_dormant = map(int, input().split())
            self.trees.append(Tree(cell_index, size, is_mine == 1, is_dormant))

        self.possible_actions.clear()
        for _ in range(int(input())):
            action = Action.parse(input())
            if action.type != ActionType.WAIT:
                self.possible_actions.append(action)

    def compute_next_action(self):
        debug([po for po in self.possible_actions])

        # remove SEED
        if self.day > DAYS_TO_PLANT or sum([tree.is_mine for tree in self.trees]) > MAX_AMONT_TREE:
            while self.possible_actions and self.possible_actions[0].type == ActionType.SEED:
                self.possible_actions.pop(0)

        # remove COMPLETE
        if self.day < COMPLETE_TIME and (sum([(tree.size == 3, 0)[tree.is_mine] for tree in self.trees]) < 4):
            while self.possible_actions and self.possible_actions[0].type == ActionType.COMPLETE:
                self.possible_actions.pop(0)

        # order by case number
        self.possible_actions.sort(key=lambda x:x.target_cell_id)
        debug([po for po in self.possible_actions])

        # Put COMPLETE as First
        complete_actions = [action for action in self.possible_actions if action.type == ActionType.COMPLETE]

        return complete_actions[0] if complete_actions else (self.possible_actions[0] if self.possible_actions else "WAIT")


game = Game()

while True:
    debug("nutrients =", game.nutrients)
    game.get_input()
    print(game.compute_next_action())
