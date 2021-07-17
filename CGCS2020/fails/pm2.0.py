from collections import namedtuple, defaultdict
import sys
import math
import random

"""
THIS IS A BIG UPDATE !
got me 29.9
"""
############################## Params
"""
PROCESS:
    - CHECK AROUND AND GIVES A VALUE (POSS_RANGE TIMES SUMMATION):
        - PELLET_VALUE FOR EACH PELLET
        - EXPLORATION_VALUE FOR ALL PLACES WE DIDNT GO (MAYBE ITS A BAD IDEA TO COUNT LIKE THAT...)
        - EAT_VALUE FOR THE ONES I CAN KILL
        - we remove a debit if its an endpoint (CDS_DEBIT)
        - PROGRESS VALUE IS TO AVOID 1BY1 STEPS
    - THE PREVIOUS STILL HAS A VALUE (PREV POINTS)
    - THEN WE HAVE THE SECURITY : IF WE DIDNT MOVE? WE CHECK OUR PACMEN AROUND
    - IF IT SUCKS WE GO RANDOM
    - it doesnt accelerate if it is aiming for a big coin or if nb of walls around not respected
"""
POSS_RANGE = 3
PREV_POINTS = 2

BIG_PELLET_VALUE = 17
PELLET_VALUE = 4
PROGRESS_VALUE = 2
EAT_VALUE = 18
EXPLORATION_VALUE = 3

# negatives
CDS_DEBIT = 2
FLEE = 40


RANDOM_SENSITIVITY = 0

# MODIFY_TO_SAME_PROBA = 0.4

MIN_WALLS = 5

############################## Init

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

############################## Class


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

############################## First Datas


available = []
to_explore = []
culsdesacs = []
init_big_pellets = []

last_pos = dict()
targets = dict()
long_shot = dict()

foe_pos_last_turn = set()

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

############################## Lists and dictionaries updates


def remove_from_explore(pm):
    if pm.pos in to_explore:
        to_explore.remove(pm.pos)
    for direct in DIRECTIONS:
        tmp = add(pm.pos, direct)
        if tmp in to_explore and grid.get_cell(tmp.x, tmp.y):
            to_explore.remove(tmp)


def remove_sight_from_explore(pm):
    for d in DIRECTIONS:
        tmp = add(pm.pos, d)
        while tmp in available:  # big pellets are handeld before those.
            if grid.get_cell(tmp.x, tmp.y) != 1 and grid.get_cell(tmp.x, tmp.y) != ' ' and tmp in to_explore:
                to_explore.remove(tmp)
            tmp = add(tmp, d)

############################## Global Utils


def debug(arg):
    print(arg, file=sys.stderr)


def dist(a, b):
    if any([line[0] != '#' for line in grid.cells]):
        if width - abs(a.x - b.x) < abs(a.x - b.x):
            return (width - abs(a.x - b.x)) + abs(a.y - b.y)
    return abs(a.x - b.x) + abs(a.y - b.y)


def add(a, b):
    return Coord((a.x + b.x) % width, (a.y + b.y) % height)

############################## Grid Utils


def around(pos):
    l = []
    for di in DIRECTIONS:
        tmp = add(pos, di)
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
    for direct in DIRECTIONS:
        tmp = add(pos, direct)
        if grid.get_cell(tmp.x, tmp.y) == '#':
            tot += 1
    return tot >= n


# culsdesacs filling
for cell in available:
    if (min_walls_around(cell, 6)):
        culsdesacs.append(cell)
        l = around(cell)
        while len(l) == 1:
            culsdesacs.append(l[0])
            last = l[0]
            l = [i for i in around(l[0]) if i not in culsdesacs]
        if last:
            culsdesacs.remove(last)


############################## Dict Utils


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


############################## Typs Utils

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

############################## Actual Code


#### THREATS LVLS
NOTHING = 0     #
IGNORE = 1      #
FREEZE = 2      #
SAME = 3        #
THREAT = 4      #
RUN = 5         #
KILL = 6        #
#################

# GET THE THREAT LVL


def filter_threat(pm, accessible):
    lst = []
    for foe_pos in ennemies_in_sight(pm):
        unit = grid.get_cell(foe_pos.x, foe_pos.y)
#### THREAT HANDLING
        if (eval(pm.typ) + 1) % 3 == eval(unit.typ):
            if (dist(unit.pos, pm.pos) == 2 and unit.stl):  # it can eat me anyway
                lst.append(RUN)
                accessible.discard(unit.pos)
                for i in around(unit.pos):
                    accessible.discard(i)
            elif dist(unit.pos, pm.pos) == 1:
                if pm.cld == 0 and unit.cld != 0:
                    lst.append(THREAT)
                elif pm.cld == 0 and unit.cld == 0:
                    lst.append(SAME)
                else:
                    lst.append(RUN)
                    accessible.discard(unit.pos)
                    for i in around(unit.pos):
                        accessible.discard(i)
            else:
                lst.append(IGNORE)
                accessible.discard(unit.pos)
                for i in around(unit.pos):
                    if i in accessible:
                        accessible.remove(i)
    ### I AM THE THREAT
        elif (eval(pm.typ) - 1) % 3 == eval(unit.typ):
            if unit.cld == 0 and pm.cld != 0:
                lst.append(RUN)
                accessible.discard(unit.pos)
                for i in around(unit.pos):
                    accessible.discard(i)
            elif (unit.cld == 0 and pm.cld == 0 and dist(unit.pos, pm.pos) == 1):
                lst.append(THREAT)
            else:
                accessible.clear()
                accessible.add(unit.pos)
                lst.append(KILL)
    ### WHO CARES
        else:
            if (pm.cld == 0 and dist(unit.pos, pm.pos) == 1):  # si il est acculé
                if (pm.cld == unit.cld):
                    lst.append(THREAT)
                elif (pm.cld == 0 and unit.cld >= 1):
                    lst.append(SAME)
                else:
                    lst.append(RUN)
                    accessible.discard(unit.pos)
                    for i in around(unit.pos):
                        accessible.discard(i)
            else:
                lst.append(IGNORE)
                accessible.discard(unit.pos)
                for i in around(unit.pos):
                    accessible.discard(i)

    my_close_pacmen = [m.pos for m in my_pacmen if dist(
        m.pos, pm.pos) == 1 or dist(m.pos, pm.pos) == 2]
    for p in my_close_pacmen:
        lst.append(FREEZE)
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

# CHOOSING AMONGST THE 13 POSITIONS


def less_walls_decision(lst):
    rem = lst[0]
    for pos in lst:
        if len(get_accessible(pos)) > len(get_accessible(rem)):
            rem = pos
        elif len(get_accessible(pos)) == len(get_accessible(rem)):
            rem = random.choice(list((rem, pos)))
    return rem


def choose_direction(pm):  # care not mess up with accessible vs available
    # simpler version of possible as a SET set()
    accessible = get_accessible(pm.pos)
    threat_degree = filter_threat(pm, accessible)

    debug(accessible)
    accessible = set([i for i in accessible if i not in last_pos.values()])

    if pm.id in long_shot:
        if (pm.pos == long_shot[pm.id] or long_shot[pm.id] not in to_explore + big_pellets or pm.pos in last_pos.values()):
            long_shot[pm.id] = random.choice(to_explore)

    if threat_degree == THREAT:
        debug(f"pm {pm.id} THREAT")
        if pm.id in long_shot and long_shot[pm.id] in big_pellets:
            targets[pm.id] = long_shot[pm.id]
            return
        targets[pm.id] = modify_typ_to_threat(pm)
        return

    if threat_degree == RUN:
        debug(f"pm {pm.id} RUN")
        if pm.id in long_shot:
            if any([dist(a, long_shot[pm.id]) <= dist(pm.pos, long_shot[pm.id]) for a in accessible]):
                accessible = set(
                    [a for a in accessible if a not in culsdesacs])
        if any([a not in culsdesacs for a in accessible]):
            accessible = set([a for a in accessible if a not in culsdesacs])
        if any([dist(a, pm.pos) == 2 for a in accessible]):
            accessible = set([a for a in accessible if dist(a, pm.pos) == 2])
        if any([not min_walls_around(a, 4) for a in accessible]):
            accessible = set(
                [a for a in accessible if not min_walls_around(a, 5)])
        if accessible:
            targets[pm.id] = random.choice(available)
        else:
            debug(f"Nothing accessible for pm{pm.id}")
            targets[pm.id] = pm.pos
    if threat_degree == FREEZE:  # une chance sur 10 de freeze
        debug(f"pm {pm.id} FREEZE")
        if random.random() * 10 < 1:
            targets[pm.id] = pm.pos
            return
        else:
            threat_degree = NOTHING

    if threat_degree == NOTHING or threat_degree == IGNORE:
        debug(f"pm {pm.id} NOTHING")
        if pm.id in long_shot and long_shot[pm.id] in big_pellets and pm.pos not in init_big_pellets:
            targets[pm.id] = long_shot[pm.id]
            return
        if pm.cld == 0 and not any([dist(foe, pm.pos) < 3 for foe in foe_pos_last_turn]) and threat_degree == NOTHING:
            targets[pm.id] = "SPEED"
            return
        if not pm.stl:
            if any([dist(a, pm.pos) == 1 for a in accessible]):
                accessible = set(
                    [a for a in accessible if dist(a, pm.pos) == 1])
        if any([a in pellets for a in accessible]):  # D'abord on check pour des pellets
            accessible = set([a for a in accessible if a in pellets])
        elif pm.id in long_shot:  # si y a pas de pellets, on va vers la destination random
            accessible = set([long_shot[pm.id]])
        else:
            accessible = set([random.choice(to_explore)])
        if len(culsdesacs) / (width * height) < 0.15:
            if any([a not in culsdesacs for a in accessible]):  # ensuite on évite les culs de sac
                accessible = set(
                    [a for a in accessible if a not in culsdesacs])
        else:
            if any([a in culsdesacs for a in accessible]):  # ensuite on évite PAS les culs de sac
                accessible = set([a for a in accessible if a in culsdesacs])
        if any([dist(a, pm.pos) == 2 for a in accessible]):
            accessible = set([a for a in accessible if dist(a, pm.pos) == 2])
    if threat_degree == KILL:  # big pellets passent avant la vie des autres
        if pm.id in long_shot and long_shot[pm.id] in big_pellets:
            targets[pm.id] = long_shot[pm.id]
            return

    if accessible:
        targets[pm.id] = less_walls_decision(list(accessible))
    else:
        targets[pm.id] = pm.pos
    debug(targets[pm.id])



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
        long_shot[closest_id] = dup
    for coord in unique_values(closest_big_by_id):
        for pm in my_pacmen:
            if pm.id in closest_big_by_id and closest_big_by_id[pm.id] == coord:
                long_shot[pm.id] = coord


############################## The Loop

r = 0

while True:

    my_pacmen = []
    foe_pacmen = []
    pellets = []
    big_pellets = []

    grid.reset()

    my_score, opponent_score = [int(i) for i in input().split()]

#### GETTING PACS
    pacmen_count = int(input())
    for n in range(pacmen_count):
        inputs = input().split()
        id, me, x, y = map(int, inputs[:4])
        typ = inputs[4]
        stl, cld = map(int, inputs[5:])
        pos = Coord(x, y)
        pm = Unit(id, me, pos, typ, stl, cld)
        if me == 1:
            my_pacmen.append(pm)
        else:
            foe_pacmen.append(pm)

#### GETTING PELLETS
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
        init_big_pellets = list(big_pellets)

#### EXPLORATION REMOVAL
    for foe in foe_pacmen:
        remove_from_explore(foe)
        grid.add_cell(foe.pos.x, foe.pos.y, foe)
    for pm in my_pacmen:
        remove_sight_from_explore(pm)
        remove_from_explore(pm)  # old implementation
        grid.add_cell(pm.pos.x, pm.pos.y, pm)

#### ASSIGN BP
    if big_pellets:
        assign_bp()

    for pm in my_pacmen:
        choose_direction(pm)
        last_pos[pm.id] = pm.pos

    print_directives(my_pacmen, big_pellets)

    foe_pos_last_turn = set([foe.pos for foe in foe_pacmen])

    r += 1
