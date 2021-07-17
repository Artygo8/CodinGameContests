from collections import namedtuple, defaultdict
import sys
import math
import random

"""
"""
random.seed(19)

Coord = namedtuple('Coord', ['x', 'y'])
Unit = namedtuple('Unit', ['id', 'me', 'pos', 'typ', 'stl', 'cld'])

UP = Coord(0, -1)
DOWN = Coord(0, 1)
RIGHT = Coord(1, 0)
LEFT = Coord(-1, 0)
STAY = Coord(0, 0)

DIRECTIONS = (LEFT, UP, RIGHT, DOWN)
DIAGONALS = (Coord(-1, -1), Coord(-1, 1), Coord(1, -1), Coord(1, 1))

TYPS = ('ROCK', 'PAPER', 'SCISSORS')

ROCK = 0
PAPER = 1
SCISSORS = 2

# Class


class Grid:
    def __init__(self, width, height):
        self.cells = []
        self.width = width
        self.height = height
        self.cells = [[None for x in range(width)] for y in range(height)]

    def add_cell(self, x, y, cell):
        self.cells[y][x] = cell

    def get_cell(self, x, y):
        if width > x >= 0 and height > y >= 0:
            return self.cells[y][x]
        return None

    def reset(self):
        for j in range(self.height):
            for i in range(self.width):
                if self.get_cell(i, j) != '#':
                    self.add_cell(i, j, ' ')

# First Datas


available = []
to_explore = []
culsdesacs = []
init_big_pellets = []

last_pos = dict()
targets = dict()
long_shot = dict()

foe_last_turn = []

width, height = map(int, input().split())

# to_explore, available filling
grid = Grid(width, height)
for y in range(height):
    line = input()
    for x in range(width):
        c = line[x]
        grid.add_cell(x, y, c)
        if c == '.' or c == ' ':
            to_explore.append(Coord(x, y))
            available.append(Coord(x, y))

# Lists and dictionaries updates


def remove_from_explore(pm):
    if pm.pos in to_explore:
        to_explore.remove(pm.pos)
#    for direct in DIRECTIONS:
#        tmp = add(pm.pos, direct)
#        if tmp in to_explore and grid.get_cell(tmp.x, tmp.y):
#            to_explore.remove(tmp)


def remove_sight_from_explore(pm):
    for d in DIRECTIONS:
        tmp = add(pm.pos, d)
        i = width + height + 1
        while tmp in available and i > 0:  # big pellets are handeld before those.
            i -= 1
            if grid.get_cell(tmp.x, tmp.y) != 1 and tmp not in big_pellets and tmp in to_explore:
                to_explore.remove(tmp)
            tmp = add(tmp, d)
        # while tmp and len(around(tmp)) == 2:
        #     ar = around(tmp)
        #     tmp = 0
        #     for i in ar:
        #         if i in to_explore:
        #             tmp = i
        #             to_explore.remove(i)

# Global Utils


def debug(arg):
    print(arg, file=sys.stderr)


def dist(a, b):
    if any([line[0] != '#' for line in grid.cells]):
        if width - abs(a.x - b.x) < abs(a.x - b.x):
            return (width - abs(a.x - b.x)) + abs(a.y - b.y)
    return abs(a.x - b.x) + abs(a.y - b.y)


def add(a, b):
    return Coord((a.x + b.x) % width, (a.y + b.y) % height)

# Grid Utils


def around(pos):
    l = []
    for di in DIRECTIONS:
        tmp = add(pos, di)
        if (grid.get_cell(tmp.x, tmp.y) != '#'):
            l.append(tmp)
    return l


def diagonals(pos):
    diago = []
    diago.append(add(pos, Coord(-1, -1)))
    diago.append(add(pos, Coord(-1, 1)))
    diago.append(add(pos, Coord(1, -1)))
    diago.append(add(pos, Coord(1, 1)))
    l = []
    for tmp in diago:
        if (grid.get_cell(tmp.x, tmp.y) != '#'):
            l.append(tmp)
    return l


def ennemies_in_sight(pm):  # or close
    ennemies = set()
    for d in DIRECTIONS:
        tmp = add(pm.pos, d)
        i = 0
        while tmp in available and i < height + width:
            i += 1
            cell = grid.get_cell(tmp.x, tmp.y)
            if type(cell) == Unit and cell.me == 0:
                ennemies.add(cell.pos)
            tmp = add(tmp, d)
    # for foe in foe_pacmen:
    #     if dist(pm.pos, foe.pos) < 3:
    #         return 1
    return ennemies


def min_walls_around(pos, n):
    tot = 0
    for direct in DIRECTIONS:
        tmp = add(pos, direct)
        if grid.get_cell(tmp.x, tmp.y) == '#':
            tot += 1
    for direct in DIAGONALS:
        tmp = add(pos, direct)
        if grid.get_cell(tmp.x, tmp.y) == '#':
            tot += 1
    return tot >= n


def walls_around(pos):
    tot = 0
    for direct in DIRECTIONS:
        tmp = add(pos, direct)
        if grid.get_cell(tmp.x, tmp.y) == '#':
            tot += 1
    for direct in DIAGNONALS:
        tmp = add(pos, direct)
        if grid.get_cell(tmp.x, tmp.y) == '#':
            tot += 1
    return tot


# culsdesacs filling
for cell in available:
    if (min_walls_around(cell, 6)):
        culsdesacs.append(cell)
        last = 0
        l = around(cell)
        i = width + height + 1
        while len(l) == 1 and i > 0:
            i -= 1
            culsdesacs.append(l[0])
            last = l[0]
            l = [i for i in around(l[0]) if i not in culsdesacs]
        if last:
            culsdesacs.remove(last)

# tunnel filling
intersect = list()
tunnels = list(list())
for cell in available:
    if (len(around(cell)) <= 2):
        condition = 0
        for ar in around(cell):
            for tu in tunnels:
                if ar in tu:
                    condition = 1
                    tu.append(cell)
        if condition == 0:
            tunnels.append([cell])
    else:
        intersect.append(cell)


# Dict Utils
def duplicate_values(dico):
    rev_dict = {}
    for key, value in dico.items():
        rev_dict.setdefault(value, set()).add(key)
    result = []
    for i in [key for key, values in rev_dict.items() if len(values) > 1]:
        if i not in TYPS:
            result.append(i)
    return result


def unique_values(dico):
    rev_dict = {}
    for key, value in dico.items():
        rev_dict.setdefault(value, set()).add(key)
    result = []
    for i in [key for key, values in rev_dict.items() if len(values) == 1]:
        if i not in TYPS:
            result.append(i)
    return result


# Typs Utils

def modify_typ_to_threat(pm):
    if (eval(pm.typ) == 0):
        return "SCISSORS"
    if (eval(pm.typ) == 1):
        return "ROCK"
    if (eval(pm.typ) == 2):
        return "PAPER"


def modify_typ_to_same(pm):
    if (eval(pm.typ) == 0):
        return "PAPER"
    if (eval(pm.typ) == 1):
        return "SCISSORS"
    if (eval(pm.typ) == 2):
        return "ROCK"

# Actual Code


# THREATS LVLS
NOTHING = 0     #
IGNORE = 1      #
FREEZE = 2      #
WAIT = 3        #
SPEED = 4       #
SAME = 5        #
THREAT = 6      #
RUN = 7         #
KILL = 8        #
#################


def run(accessible, pos, n):  # run repaired
    to_discard = [pos]
    while (n > 0):
        tmp_td = list(to_discard)
        n -= 1
        for td in tmp_td:
            for i in around(td):
                to_discard.append(i)
    for td in to_discard + diagonals(pos):
        accessible.discard(td)
    return(RUN)

# GET THE THREAT LVL


def filter_threat(pm, accessible):
    lst = []

# special case about last turn decision
    if pm.id in last_threat_lvl:
        if last_threat_lvl[pm.id] == RUN:
            for flt in foe_last_turn:
                if dist(flt.pos, pm.pos) <= 4:
                    run(accessible, flt.pos, 3)
                    lst.append(RUN)
        if last_threat_lvl[pm.id] == KILL:
            for flt in foe_last_turn:
                if flt.pos in culsdesacs:
                    accessible.clear()
                    accessible.add(flt.pos)
                    if flt.cld:
                        lst.append(KILL)

    for foe in foe_pacmen:
        # THREAT
        if (eval(pm.typ) + 1) % 3 == eval(foe.typ):
            if dist(foe.pos, pm.pos) == 1:
                if foe.cld == 0 or pm.cld != 0:
                    lst.append(run(accessible, foe.pos, 1))
                else:
                    lst.append(THREAT)
            elif dist(foe.pos, pm.pos) == 2 and foe.pos in accessible:  # ça c'est du génie
                if pm.cld != 0 or pm.pos in culsdesacs:
                    lst.append(run(accessible, foe.pos, 2))
                elif pm.cld == 0:
                    if foe.stl != 0:
                        lst.append(THREAT)
                    else:
                        lst.append(SPEED)
            elif dist(foe.pos, pm.pos) == 3 and any([a in accessible for a in around(foe.pos)]):
                if foe.stl > 1 or foe.cld == 0:
                    lst.append(run(accessible, foe.pos, 3))
                elif foe.stl == 1 or pm.stl:
                    lst.append(run(accessible, foe.pos, 2))
                else:
                    lst.append(IGNORE)
            elif dist(foe.pos, pm.pos) == 4:
                if foe.stl and pm.stl:
                    lst.append(run(accessible, foe.pos, 3))
        # WEAK
        elif (eval(pm.typ) - 1) % 3 == eval(foe.typ):
            if dist(foe.pos, pm.pos) == 1 or (dist(foe.pos, pm.pos) == 2 and pm.stl):
                if pm.stl:
                    if foe.cld:
                        accessible.clear()
                        accessible.add(foe.pos)
                        lst.append(KILL)
                    else:
                        lst.append(run(accessible, foe.pos, 1))
                else:
                    if foe.cld:
                        if foe.pos in culsdesacs:
                            accessible.clear()
                            accessible.add(foe.pos)
                            lst.append(KILL)
                        else:
                            accessible.discard(foe.pos)
                            for ar in around(foe.pos):
                                accessible.discard(ar)
                            lst.append(IGNORE)
                    else:
                        if pm.cld:
                            lst.append(run(accessible, foe.pos, 1))
                        else:
                            if pm.pos not in culsdesacs:
                                lst.append(SPEED)
                            else:
                                lst.append(WAIT)
            elif 4 >= dist(foe.pos, pm.pos) >= 2 and foe.pos in accessible or any([a in accessible for a in around(foe.pos)]):
                if pm.stl:
                    if foe.cld:
                        accessible.clear()
                        accessible.add(foe.pos)
                        lst.append(KILL)
                    else:
                        lst.append(IGNORE)
                else:
                    if foe.cld:
                        if foe.pos in culsdesacs:
                            accessible.clear()
                            accessible.add(foe.pos)
                            lst.append(KILL)
                        else:
                            if pm.cld:
                                lst.append(IGNORE)
                            else:
                                lst.append(SPEED)
                    else:
                        if pm.cld >= dist(foe.pos, pm.pos):
                            lst.append(run(accessible, foe.pos, 1))
                        else:
                            lst.append(WAIT)
# SAME
        else:
            if dist(foe.pos, pm.pos) == 1:
                if pm.cld < foe.cld:
                    if foe.cld > 1:
                        lst.append(SAME)
                    elif foe.pos in culsdesacs:
                        lst.append(WAIT)
                else:
                    accessible.discard(foe.pos)
                    for ar in around(foe.pos):
                        accessible.discard(ar)
                    lst.append(IGNORE)
            elif dist(foe.pos, pm.pos) <= 4:
                if pm.pos not in culsdesacs:
                    if pm.cld == 0:
                        lst.append(SPEED)
                    else:
                        lst.append(IGNORE)
                else:
                    if pm.cld < foe.cld and foe.pos in culsdesacs:
                        accessible.clear()
                        accessible.add(foe.pos)
                        lst.append(KILL)
                    else:
                        lst.append(run(accessible, foe.pos, 1))

    my_close_pacmen = [m for m in my_pacmen if (
        m.pos in accessible and m.id in last_pos and last_pos[m.id] == m.pos and pm.id != m.id)]
    if my_close_pacmen:
        for mcp in my_close_pacmen:
            if r % 2:
                if mcp.id - pm.id < 0:
                    lst.append(WAIT)
            else:
                if mcp.id - pm.id > 0:
                    lst.append(WAIT)
    elif pm.id in last_pos and last_pos[pm.id] == pm.pos:
        if pm.cld == 0:
            lst.append(SAME)
    if lst:
        return (max(lst))
    return NOTHING


# GET THE 2 STEPS CASES AROUND
def get_accessible(pos):
    accessible = set()
    accessible.add(pos)
    for i in range(2):
        acc_copy = set(accessible)
        for a in acc_copy:
            for di in DIRECTIONS:
                tmp = add(a, di)
                if grid.get_cell(tmp.x, tmp.y) == '#':
                    continue
                else:
                    accessible.add(tmp)
    return accessible


def final_decision(pm, lst):  # choose the one that is the farest from my own team
    rem = lst[0]
    tot = 0
    for pos in lst:
        summ = 0
        for p in my_pacmen:
            summ += dist(p.pos, pos)
        # parce qu'on ne veut pas revenir sur ses pas
        if summ > tot and pm.id in last_pos and dist(pm.pos, pos) <= dist(last_pos[pm.id], pos) and not any([a in last_pos for a in around(pos)]):
            tot = summ
            rem = pos
    return rem


def get_keys(dico, value):
    lst = []
    for key, val in dico.items():
        if value == val:
            lst.append(key)
    return lst


# closest but farest from allies
def get_closest(pm, to_explore):
    res = 0
    distance = width + height + 1
    m = 9  # ?????????????????????????????????
    while not res and m > 0:
        for key in get_keys(most_to_explore, m):
            if dist(key, pm.pos) < distance and dist(key, pm.pos) <= dist(key, last_pos[pm.id]):
                # THIS IS WEIRD BUT I TRUST MY OTHER SELF
                #        if key in closer_from[pm.id] or len(closer_from[pm.id]) < len(to_explore):
                distance = dist(key, pm.pos)
                res = key
        m -= 1
    m = 9
    if not res:
        while not res and m > 0:
            for key in get_keys(most_to_explore, m):
                if dist(key, pm.pos) < distance:  # not sure about it
                    distance = dist(key, pm.pos)
                    res = key
            m -= 1
    # for a in available:
    #     if len(around(a)) >= 3 and any([ar in to_explore for ar in around(a)]):
    #         if dist(a, pos) < distance:  # not sure about it
    #             if not any([(dist(a, o.pos) <= dist(a, pos) and o.pos != pos) for o in my_pacmen]):
    #                 distance = dist(a, pos)
    #                 res = a
#    if not res:
#        for a in available:
#            if len(around(a)) == 3 and any([ar in to_explore for ar in around(a)]):
#                if dist(a, pos) < distance:  # not sure about it
#                    if not any([(dist(a, o.pos) <= dist(a, pos) and o.pos != pos) for o in my_pacmen]):
#                        distance = dist(a, pos)
#                        res = a
    # if not res:
        # distance = width + height + 1
        # for e in to_explore:
            # if dist(e, pos) < distance:  # not sure about it
            # if not any([(dist(e, o.pos) <= dist(e, pos) and o.pos != pos) for o in my_pacmen]):
            # distance = dist(e, pos)
            # res = e
    if not res:
        res = Coord(0, 0)
    return res


def more_in_cds():
    cds_to_explore = [c for c in culsdesacs if c in to_explore]
    if len(to_explore) / 2 < len(cds_to_explore):
        return 1
    return 0


last_threat_lvl = dict()
# CHOOSING AMONGST THE 13 POSITIONS


def choose_direction(pm):  # care not mess up with accessible vs available
    # simpler version of possible as a SET set()
    accessible = get_accessible(pm.pos)
    threat_degree = filter_threat(pm, accessible)
    last_threat_lvl[pm.id] = threat_degree

    # debug(accessible)
    accessible = set([i for i in accessible if i not in last_pos.values()])

    if pm.id in long_shot:
        if long_shot[pm.id] == pm.pos or long_shot[pm.id] not in to_explore + big_pellets:
            # tant qu'on a pas besoin d'une cible, on en genere pas !
            del long_shot[pm.id]

    if threat_degree == THREAT:
        debug(f"pm {pm.id} THREAT")
        targets[pm.id] = modify_typ_to_threat(pm)
        return

    if threat_degree == SAME:
        debug(f"pm {pm.id} SAME")
        targets[pm.id] = modify_typ_to_same(pm)
        return

    if threat_degree == FREEZE:  # une chance sur 10 de freeze
        debug(f"pm {pm.id} FREEZE")
        if random.random() * 10 < 1:
            threat_degree = WAIT
        else:
            threat_degree = NOTHING

    if threat_degree == WAIT:  # une chance sur 10 de freeze
        debug(f"pm {pm.id} WAIT")
        targets[pm.id] = pm.pos
        return

    if threat_degree == SPEED:
        targets[pm.id] = "SPEED"
        return

    if threat_degree == NOTHING or threat_degree == IGNORE or threat_degree == RUN:
        accessible.discard(pm.pos)  # no threat so i wont stay on place
        if threat_degree == IGNORE:
            debug(f"pm {pm.id} IGNORE")
        elif threat_degree == RUN:
            debug(f"pm {pm.id} RUN")
        else:
            debug(f"pm {pm.id} NOTHING")
        if pm.cld == 0 and threat_degree == NOTHING:
            debug(f" - {pm.id} speed?")
            targets[pm.id] = "SPEED"
            return
        if pm.id in long_shot and long_shot[pm.id] in big_pellets:
            debug(f" - {pm.id} ls {long_shot[pm.id]}")
            if threat_degree == RUN:
                if any([dist(a, long_shot[pm.id]) < dist(pm.pos, long_shot[pm.id]) for a in accessible]):
                    targets[pm.id] = long_shot[pm.id]
                    return
            else:
                targets[pm.id] = long_shot[pm.id]
                return
        if not pm.stl:
            if any([dist(a, pm.pos) == 1 for a in accessible]):
                debug(f" - {pm.id} dist == 1")
                accessible = set(
                    [a for a in accessible if dist(a, pm.pos) == 1])
            if any([a in pellets for a in accessible]):  # D'abord on check pour des pellets
                debug(f" - {pm.id} pellets !")
                accessible = set([a for a in accessible if a in pellets])
            elif any([any([pos in to_explore and pos in around(pm.pos) for pos in around(a)]) for a in accessible]):
                accessible = set([a for a in accessible if any(
                    [pos in to_explore and pos in around(pm.pos) for pos in around(a)])])
            # REMOVED to_explore because we are at dist 1 anyway and bugged wausing FREEZE
            # si y a pas de pellets, on va vers la destination random
            elif threat_degree != RUN:
                debug(f" - {pm.id} long s !")
                if not pm.id in long_shot:
                    long_shot[pm.id] = get_closest(pm, to_explore)
                accessible = set([long_shot[pm.id]])
            # if any([any([type(grid.get_cell(pos.x, pos.y)) == int for pos in around(a)]) for a in accessible]):
            #     debug(f" - {pm.id} good stuff around")
            #     accessible = set([a for a in accessible if any(
            #         [type(grid.get_cell(pos.x, pos.y)) == int for pos in around(a)])])
            # if we need to run we dont go in cul de sac
            if not more_in_c:
                if any([a not in culsdesacs for a in accessible]):
                    accessible = set(
                        [a for a in accessible if a not in culsdesacs])
            else:
                if any([a in culsdesacs and a in pellets for a in accessible]):
                    accessible = set(
                        [a for a in accessible if a in culsdesacs and a in pellets])
        else:
            if any([dist(a, pm.pos) == 2 for a in accessible]):
                accessible = set(
                    [a for a in accessible if dist(a, pm.pos) == 2])
            # 2 cases ago but on my way to a pellet
            if any([any([pos in pellets and pos in around(pm.pos) for pos in around(a)]) for a in accessible]):
                accessible = set([a for a in accessible if any(
                    [pos in pellets and pos in around(pm.pos) for pos in around(a)])])
            if any(a in pellets for a in accessible):
                accessible = set([a for a in accessible if a in pellets])
            if any(a in to_explore for a in accessible):
                accessible = set([a for a in accessible if a in to_explore])
            elif any([any([pos in to_explore and pos in around(pm.pos) for pos in around(a)]) for a in accessible]):
                accessible = set([a for a in accessible if any(
                    [pos in to_explore and pos in around(pm.pos) for pos in around(a)])])
            elif threat_degree != RUN:
                if not pm.id in long_shot:
                    long_shot[pm.id] = get_closest(pm, to_explore)
                accessible = set([long_shot[pm.id]])
            if not more_in_c:
                if any([a not in culsdesacs for a in accessible]):
                    accessible = set(
                        [a for a in accessible if a not in culsdesacs])
            else:
                if any([a in culsdesacs and a in pellets for a in accessible]):
                    accessible = set(
                        [a for a in accessible if a in culsdesacs and a in pellets])

    if threat_degree == KILL:  # big pellets passent avant la vie des autres
        debug(f"pm {pm.id} KILL {accessible}")
        if pm.id in long_shot and long_shot[pm.id] in big_pellets:
            targets[pm.id] = long_shot[pm.id]
            return

    if accessible:
        targets[pm.id] = final_decision(pm, list(accessible))
    else:
        targets[pm.id] = pm.pos
    # debug(targets[pm.id])#


def print_directives(my_pacmen, big_pellets):
    commands = []
    for pm in my_pacmen:
        if targets[pm.id] in TYPS:
            commands.append(f"SWITCH {pm.id} {targets[pm.id]}")
        elif targets[pm.id] == "SPEED":
            commands.append(f"SPEED {pm.id}")
        else:
            commands.append(
                f"MOVE {pm.id} {targets[pm.id].x} {targets[pm.id].y}")
    print("|".join(commands))


def assign_bp():
    closest_big_by_id = dict()
    for pm in my_pacmen:
        closest_big = big_pellets[0]
        for big in big_pellets:
            if dist(pm.pos, big) < dist(pm.pos, closest_big):
                closest_big = big
        closest_big_by_id[pm.id] = closest_big
    for dup in duplicate_values(closest_big_by_id):
        distance = width + height + 1
        for pm in my_pacmen:
            if dist(pm.pos, dup) < distance:
                closest_id = pm.id
                distance = dist(pm.pos, dup)
        if not (closest_id in long_shot and long_shot[closest_id] in big_pellets):
            long_shot[closest_id] = closest_big_by_id[closest_id]
    for coord in unique_values(closest_big_by_id):
        for pm in my_pacmen:
            if pm.id in closest_big_by_id and closest_big_by_id[pm.id] == coord:
                if not (pm.id in long_shot and long_shot[pm.id] in big_pellets):
                    long_shot[pm.id] = coord


# The Loop
def get_explorable(pos):
    explorable = set()
    explorable.add(pos)
    for i in range(2):  # 3 to_explore around
        exp_copy = set(explorable)
        for e in exp_copy:
            for di in DIRECTIONS:
                tmp = add(e, di)
                if tmp in to_explore:
                    explorable.add(tmp)
    return explorable


occupied_tunnels = dict()
more_in_c = True
r = 0

while True:

    more_in_c = more_in_cds()
    # debug(f"len avalable = {len(available)}")

    my_dead_pacmen = []
    foe_dead_pacmen = []

    my_pacmen = []
    foe_pacmen = []
    pellets = []
    big_pellets = []

    grid.reset()

    my_score, opponent_score = [int(i) for i in input().split()]

# GETTING PACS
    pacmen_count = int(input())
    for n in range(pacmen_count):
        inputs = input().split()
        id, me, x, y = map(int, inputs[:4])
        typ = inputs[4]
        stl, cld = map(int, inputs[5:])
        pos = Coord(x, y)
        pm = Unit(id, me, pos, typ, stl, cld)
        if me == 1 and typ == "DEAD":
            my_dead_pacmen.append(pm)
        elif typ == "DEAD":
            foe_dead_pacmen.append(pm)
        elif me == 1:
            my_pacmen.append(pm)
        else:
            foe_pacmen.append(pm)

# GETTING PELLETS
    pellet_count = int(input())
    for n in range(pellet_count):
        inp = input()
        x, y, value = map(int, inp.split())
        pellet = Coord(x, y)
        if value == 10:
            big_pellets.append(pellet)
        for _ in range(value):
            pellets.append(pellet)
        grid.add_cell(pellet.x, pellet.y, value)
    if r == 0:
        init_pm_count = len(my_pacmen)
        init_big_pellets = list(big_pellets)

# EXPLORATION REMOVAL
    for foe in foe_pacmen:
        remove_from_explore(foe)
        grid.add_cell(foe.pos.x, foe.pos.y, foe)
    for pm in my_pacmen:
        remove_sight_from_explore(pm)
        remove_from_explore(pm)  # old implementation
        grid.add_cell(pm.pos.x, pm.pos.y, pm)
    for e in [bp for bp in init_big_pellets if not bp in big_pellets]:  # 23h23 smells bad
        if e in to_explore:
            to_explore.remove(e)

# FILLING MOST_TO_EXPLORE
    most_to_explore = dict()
    for av in available:
        most_to_explore[av] = len(get_explorable(av))

# FILLING CLOSER_FROM
    closer_from = dict()
    for p in my_pacmen:
        closer_from[p.id] = []
    for av in available:
        closest_id = 0
        distance = height + width + 1
        for p in my_pacmen:  # what about theirs
            if dist(p.pos, av) < distance:
                distance = dist(p.pos, av)
                closest_id = p.id
        closer_from[closest_id].append(av)

# ASSIGN BP
    if big_pellets:
        assign_bp()

    for pm in my_pacmen:
        choose_direction(pm)
        last_pos[pm.id] = pm.pos

    print_directives(my_pacmen, big_pellets)

    foe_last_turn = [foe for foe in foe_pacmen]

    r += 1
