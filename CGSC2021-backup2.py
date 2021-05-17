import sys
import math
import time
import random
from enum import Enum

# trial 3.5

MAX_AMONT_TREE = 13
DIVIDER = 24 / (MAX_AMONT_TREE - 3)
COMPLETE_TIME = 23


def debug(*s):
    print(*s, file=sys.stderr, flush=True)


class Chrono:
    def __init__(self):
        self.moment = time.perf_counter()

    def start(self):
        self.moment = time.perf_counter()

    def stop(self, legend=''):
        debug(legend, f': { (time.perf_counter() - self.moment) * 1000:0.4f}')


class AT(Enum):
    WAIT = "WAIT"
    SEED = "SEED"
    GROW = "GROW"
    COMPLETE = "COMPLETE"


class Simulation:
    def __init__(self):
        self.best_score = -1

    def one_turn_simu(self, brd, player, iday, action_list=[]):  # 1ms
        possible_a = brd.compute_possible_actions(player)  # 0.08ms

        for act in possible_a:
            price = act.price(player, brd)  # 0.08ms

            if player.sun < price:
                continue

            bd = brd.__copy__()  # 0.1ms
            cur_player = player.__copy__()

            bd.apply(act, cur_player)  # 0.02ms

            cur_player.sun -= price
            yield {'board': bd, 'player': cur_player, 'actions': action_list + [act]}

    def one_day_simu(self, brd, player, iday):
        brd.compute_shadows(iday)

        results = [res for res in self.one_turn_simu(brd, player, iday)]
        tic = time.perf_counter()
        for _ in range(1):  # only 3 actions per day for now
            new_res = []
            for res in results:
                # I need to remove some results, if I see they are not good (but what is good ?)
                if res['actions'][-1].type != AT.WAIT:
                    for ots in self.one_turn_simu(res['board'], res['player'], iday, action_list=res['actions']):
                        new_res.append(ots)
                else:
                    new_res.append(res)
            results = new_res
        toc = time.perf_counter()
        debug(f"total simu : {toc - tic:0.4f} seconds - {len(results)}")
        return results


# class MCTS:



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

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{("foe", "me")[self.itsme]} - score={self.score} - sun= {self.sun}'

    def __copy__(self):
        return Player(self.itsme, self.sun, self.score, self.is_waiting)

    def update(self, sun, score, is_waiting=0):
        self.sun = sun
        self.score = score
        self.is_waiting = is_waiting

    def get_input_actions(self):
        self.possible_actions.clear()
        for _ in range(int(input())):
            self.possible_actions.append(Action.parse(input()))

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
        self.is_dormant = 0  # after any action, becomes dormant

        self.shadow = 0

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Cell {self.cell_index} r({self.richness}) s({self.shadow}) n({self.neighbors}):" + f"T size = {self.size}, is {('not','')[self.is_mine]} mine {('','(dormant)')[self.is_dormant]}:" if self.tree else ''

    def __copy__(self):
        new = Cell(self.cell_index, self.richness, *self.neighbors)
        new.tree = self.tree
        new.size = self.size
        new.is_mine = self.is_mine
        new.is_dormant = self.is_dormant
        new.shadow = self.shadow
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

    def complete(self, player):  # does not add the points.
        self.reset()

    def sun_points(self, board, iday, compute_shadows=True):  # Shadows must be computed first
        if compute_shadows:
            board.compute_shadows(iday)
        return (0, self.size + (self.richness - 1) * 2)[self.tree and self.size and self.is_mine and (self.shadow < self.size or self.shadow == 0)]

    def sun_points_over6days(self, board):
        return [self.sun_points(board, iday, compute_shadows=True) for iday in range(6)]

    def sun_points_at_end(self, board, iday):  # does not add current sun points
        sun_day_by_day = self.sun_points_over6days(board) * (24 // 6)
        return sum(sun_day_by_day[iday:])

    def reset(self):
        self.tree = False
        self.size = 0
        self.is_mine = 0
        self.is_dormant = 0
        self.shadow = 0
        # maybe I should remove the shadows too...

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
        return self.type.name + (f' {self.origin_cell_id}', '')[self.type == AT.WAIT] \
            + ('', f' {self.target_cell_id}')[self.type == AT.SEED]

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def parse(action_string):
        split = action_string.split(' ')
        return Action(AT[split[0]], *map(int, split[1:][::-1]))

    def price(self, player, bd):
        if self.type == AT.WAIT:
            return 0
        nb_by_size = [sum(cell.tree for cell in bd if (cell.size == i and cell.is_mine == player.itsme)) for i in range(5)]  # 5 to have 0
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

    def __getitem__(self, key):
        return self.board[key]

    def __setitem__(self, key, value):
        self.board[key] = value

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < self.size:
            self.n += 1
            return self[self.n - 1]
        else:
            raise StopIteration

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        s = self
        return f'''
             [{s[25].size if s[25].tree else ' '}|{s[24].size if s[24].tree else ' '}|{s[23].size if s[23].tree else ' '}|{s[22].size if s[22].tree else ' '}]
            [{s[26].size if s[26].tree else ' '}|{s[11].size if s[11].tree else ' '}|{s[10].size if s[10].tree else ' '}|{s[9].size if s[9].tree else ' '}|{s[21].size if s[21].tree else ' '}]
           [{s[27].size if s[27].tree else ' '}|{s[12].size if s[12].tree else ' '}|{s[3].size if s[3].tree else ' '}|{s[2].size if s[2].tree else ' '}|{s[8].size if s[8].tree else ' '}|{s[20].size if s[20].tree else ' '}]
          [{s[28].size if s[28].tree else ' '}|{s[13].size if s[13].tree else ' '}|{s[4].size if s[4].tree else ' '}|{s[0].size if s[0].tree else ' '}|{s[1].size if s[1].tree else ' '}|{s[7].size if s[7].tree else ' '}|{s[19].size if s[19].tree else ' '}]
           [{s[29].size if s[29].tree else ' '}|{s[14].size if s[14].tree else ' '}|{s[5].size if s[5].tree else ' '}|{s[6].size if s[6].tree else ' '}|{s[18].size if s[18].tree else ' '}|{s[36].size if s[36].tree else ' '}]
            [{s[30].size if s[30].tree else ' '}|{s[15].size if s[15].tree else ' '}|{s[16].size if s[16].tree else ' '}|{s[17].size if s[17].tree else ' '}|{s[35].size if s[35].tree else ' '}]
             [{s[31].size if s[31].tree else ' '}|{s[32].size if s[32].tree else ' '}|{s[33].size if s[33].tree else ' '}|{s[34].size if s[34].tree else ' '}]'''

    def __copy__(self):
        bd = Board()
        for cell in self:
            bd.append(cell.__copy__())
        bd.size = self.size
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
        for _ in range(int(input())):
            cell_index, size, is_mine, is_dormant = map(int, input().split())
            self[cell_index].put_tree(size, is_mine, is_dormant)

# COMPUTE
    def compute_shadows(self, day):
        for cell in self:
            cell.shadow = 0
        for pos in range(self.size):
            height = self[pos].size
            for _ in range(height):
                pos = self[pos].neighbors[day % 6]
                if pos == -1:
                    break
                if self[pos].shadow < height:
                    self[pos].shadow = height

    def compute_possible_actions(self, player):
        computed_actions = [Action.parse('WAIT')]
        for cell in self:
            if not cell.is_dormant and cell.is_mine == player.itsme:
                seedable = set()
                for _ in range(cell.size):
                    for neigh in set(cell.neighbors).union(seedable):
                        seedable.add(neigh)
                for seed in seedable:
                    if not self[seed].tree and self[seed].richness > 0 and seed != -1:
                        computed_actions.append(Action(AT.SEED, seed, cell.cell_index))
                if cell.tree:
                    computed_actions.append(Action((AT.GROW, AT.COMPLETE)[cell.size == 3], cell.cell_index))
        return computed_actions

# CALCULATE
    def current_total_cost(self, player):  # for trees
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

    def sun_points(self, player, iday, compute_shadows=False):  # WTF PLAYER NOT USED
        if compute_shadows:
            self.compute_shadows(iday)
        return sum(cell.sun_points() for cell in self)

    def sun_points_over6days(self, player):
        return [self.sun_points(player, iday, compute_shadows=True) for iday in range(6)]

    def sun_points_at_end(self, player, iday):  # does not add current sun points
        sun_day_by_day = self.sun_points_over6days(player) * (24 // 6)
        return sum(sun_day_by_day[iday:])

    def apply(self, action, player):  # care, it only works for ME (put_tree)
        if action.type == AT.WAIT:
            return
        elif action.type == AT.SEED:
            self[action.target_cell_id].seed(player)
        elif action.type == AT.COMPLETE:
            self[action.target_cell_id].complete(player)
        elif action.type == AT.GROW:
            self[action.target_cell_id].grow(player)
        self[action.origin_cell_id].is_dormant = True

    def count_trees(self, player):
        return sum([(cell.tree and cell.is_mine == player.itsme) for cell in self])

    def count_trees_around(self, cell):
        return sum([self[n].tree for n in cell.neighbors])

    def tree_neigh(self, player):
        neighs = set()
        for cell in self:
            if cell.tree and cell.is_mine == player.itsme:
                for n in cell.neighbors:
                    neighs.add(n)
        return neighs


#   ____
#  / ___| __ _ _ __ ___   ___
# | |  _ / _` | '_ ` _ \ / _ \
# | |_| | (_| | | | | | |  __/
#  \____|\__,_|_| |_| |_|\___|
#

class Game:

    def __init__(self, day=0, nutrients=0, me=Player(itsme=True), foe=Player(itsme=False), board=Board()):
        self.day = day
        self.last_day = 23
        self.nutrients = nutrients
        self.me = me
        self.foe = foe
        self.board = board

    def __copy__(self):
        return Game(self.day, self.nutrients, self.me.__copy__(), self.foe.__copy__(), self.board.__copy__())

    def get_input(self):
        self.day = int(input())
        self.nutrients = int(input())
        self.me.update(*map(int, input().split()))
        self.foe.update(*map(int, input().split()))
        self.board.get_input()
        self.me.get_input_actions()  # This is useless but needed

    def apply(self, action):
        self.board.apply(action, self.me)
        self.me.sun -= action.price(self.me, self.board)

    def compute_next_action(self):
        debug([po for po in self.me.possible_actions])

        # order by case number
        self.me.possible_actions = [action for action in self.me.possible_actions if action.type != AT.WAIT]
        self.me.possible_actions.sort(key=lambda x: x.target_cell_id, reverse=True)

        # Separate Actions
        complete_actions = [action for action in self.me.possible_actions if action.type == AT.COMPLETE]
        seed_actions = [action for action in self.me.possible_actions if action.type == AT.SEED]
        grow_actions = [action for action in self.me.possible_actions if action.type == AT.GROW]

        debug("before", [sum(self.board[ca.origin_cell_id].sun_points_over6days(self.board)) for ca in complete_actions])

        # remove COMPLETE
        if self.day < COMPLETE_TIME:
            # and not all([cell.size == 3 for cell in self.board if cell.is_mine]):  # and sum([(cell.size == 3, 0)[cell.is_mine] for cell in self.board]) < 5 \
            complete_actions = [ca for ca in complete_actions if sum(self.board[ca.origin_cell_id].sun_points_over6days(self.board)) < 18]  # on vire ceux qui ne rapportent pas des masses

        debug("after", len(complete_actions))

        debug("NUMBER OF TREES:", MAX_AMONT_TREE - (self.day / DIVIDER))
        # remove SEED
        if self.day > 20 or len([cell.is_mine for cell in self.board]) < MAX_AMONT_TREE - (self.day / DIVIDER):
            seed_actions = []
        # debug(self.board.tree_neigh(self.me))
        seed_actions = [action for action in seed_actions if action.target_cell_id not in self.board.tree_neigh(self.me)]

        # sort
        complete_actions.sort(key=lambda x: x.target_cell_id, reverse=True)

        self.board.compute_shadows(self.day)

        self.possible_actions = seed_actions + complete_actions + grow_actions
        # self.possible_actions.sort(key=lambda x: self.board[x.target_cell_id].richness, reverse=True)  # first the richest

        # debug([po for po in self.possible_actions])

        return self.possible_actions[0] if self.possible_actions else "WAIT"

    def play(self):

        self.board.get_first_input()  # important to call it once

        while True:
            self.get_input()
            # print(game.basic_compute_next_action())
            # for _ in simu.one_day_simu(self.board, self.me, self.day):
            #     pass
            print(self.compute_next_action())


# The code

chrono = Chrono()
simu = Simulation()
main_game = Game()

main_game.play()
