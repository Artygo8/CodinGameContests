import sys
import math

def debug(*s):
    print(*s, file=sys.stderr, flush=True)

neighbs = []
grid = []

number_of_cells = int(input())  # 37
for i in range(number_of_cells):
    index, richness, *neigh = map(int, input().split())
    neighbs.append(neigh) # -1 for no neigh


# game loop
while True:

    day = int(input())  # the game lasts 24 days: 0-23
    debug("day", day)
    nutrients = int(input())  # the base score you gain from the next COMPLETE action
    sun, score = map(int, input().split())
    opp_sun, opp_score, opp_is_waiting = map(int, input().split())

    number_of_trees = int(input())  # the current amount of trees


    trees = [0 for i in range(number_of_cells)]
    for i in range(number_of_trees):
        cell_index, size, is_mine, is_dormant = map(int, input().split())
        trees[cell_index] = size * is_mine

    possible_moves = []
    for i in range(int(input())):
        inputs = input().split()
        if inputs[0] == "WAIT":
            pass
        elif inputs[0] == "COMPLETE":
            possible_moves = [[inputs[0], int(inputs[1])]] + possible_moves
        else:
            possible_moves.append([inputs[0], int(inputs[1])])


    debug(possible_moves)

    # GROW cellIdx | SEED sourceIdx targetIdx | COMPLETE cellIdx | WAIT <message>
    for pm in possible_moves:
        debug(pm)
        # costs
        if pm[0] == "COMPLETE":
            cost = 4
        elif pm[0] == "GROW" and trees[pm[1]] == 1:
            cost = 3 + trees.count(2)
        elif pm[0] == "GROW" and trees[pm[1]] == 2:
            cost = 7 + trees.count(3)
        
        debug("sun", sun, ", cost", cost)
        if sun < cost: break

        print(*pm)
        sun -= cost

    print("WAIT")

