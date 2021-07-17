import sys
import time
import numpy as np
import random
from collections import deque

# Mal organisé après reorganise

                                                             
     ######  ##            ##                  ##            
  ##        ##    ####    ######      ######  ##    ######   
 ##  ####  ##  ##    ##  ##    ##  ##    ##  ##  ####        
##    ##  ##  ##    ##  ##    ##  ##    ##  ##      ####     
 ######  ##    ####    ######      ######  ##  ######        
                                                             
learning = 8

all_times = []
timer = time.time()
nodes = 0




                                         
   ##    ##    ##      ##  ##            
  ##    ##  ########      ##    ######   
 ##    ##    ##      ##  ##  ####        
##    ##    ##      ##  ##      ####     
 ####        ####  ##  ##  ######        
                                         
                                         
def reset_timer():
    global timer
    timer = time.time()

def get_timing():
    return (time.time() - timer) * 1000

def show_timing():
    debug(f"{get_timing()}ms")

def time_up(ms):
    return get_timing() > ms

def debug(*s):
    # pass
    print(*s, file=sys.stderr, flush=True)




                                                                                           
      ######  ##                         
   ##            ######  ####    ##    ##
    ####    ##  ##    ##    ##  ##    ## 
       ##  ##  ##    ##    ##  ##    ##  
######    ##  ##    ##    ##    ######   
                                                                                           
                                                                                           
class Simulation:

    def __init__(self):
        # all the arrays have the form np.array([id, d0, d1, d2, d3])
        self.nodes = 0
        self.best_bet = list()
        self.saved = list()
        self.total = 0

    def reorganise(self, lst):
        # peu importe l'ordre, tant que lst_learn est juste apres lst[0] (parce qu'on n'utilise pas les saved) 
        lst_learn = [i for i in lst if i[0] < 42]
        lst = [i for i in lst if i[0] >= 42]
        lst = [lst[0]] + lst_learn + lst[1:]
        return lst

    def bfs_shortest_path(self, castables, initial, targets):
        queue = deque([[initial]])

        for i in range(len(targets)):
            if (initial[1:] >= targets[i][1:]).all():
                new_path = list([initial.copy()])
                new_path[0][0] = targets[i][0]
                targets.pop(i)
                yield new_path
                break

        while queue and targets and not (time_up(700) or (turns != 1 and time_up(40))):
            
            path = queue.popleft()
            node = path[-1].copy()
            node[0] = 0
            neighbours = [node + c for c in castables if c[0] % 1000 not in [i[0] % 1000 for i in path]]

            for neighbour in neighbours:
                if (neighbour < 0).any() or sum(neighbour[1:]) > 10:
                    continue
                new_path = list([p.copy() for p in path])
                new_path.append(neighbour)
                if neighbour[0] < 42:
                    new_path.append(neighbour)
                queue.append(new_path)
                for i in range(len(targets)):
                    if (neighbour[1:] >= targets[i][1:]).all():
                        new_path[0][0] = targets[i][0]
                        # targets.pop(i)
                        yield new_path
                        break

    def show_results(self):
        pass
        # debug("---BFS---")
        # for sub in self.best_subset_sums:
        #     action = actions.get_action_by_id(sub[0][0])
        #     debug("price:", action.price, ", turns:", len(sub))

    def keep_shortest_of_each(self):
        d = {lst_a[0][0]:100 for lst_a in self.best_subset_sums}
        for lst_a in self.best_subset_sums:
            if d[lst_a[0][0]] > len(lst_a):
                d[lst_a[0][0]] = len(lst_a)
        self.best_subset_sums = [lst_a for lst_a in self.best_subset_sums if len(lst_a) == d[lst_a[0][0]]]

    def get_best(self):
        # best is calculated as highest price - turns_to_get
        brew_ids = {j:i for i, j in enumerate([b.id for b in actions.brew])}
        self.keep_shortest_of_each()
        self.best_subset_sums.sort(key=lambda sub: len(sub), reverse=True)
        best_score = 20 # best if lowest
        best_sub = list()
        for sub in self.best_subset_sums:
            if me.pots == 5 and other.pots < 5 and other.score > me.score:
                score = len(sub) + brew_ids[sub[0][0]] * 1.5
            if (me.pots == 5 or other.pots == 5) and me.ahead and other.score > me.score + 8:
                score = len(sub) + (brew_ids[sub[0][0]] + 1) // 3
            elif (me.pots >= 3 or other.pots >= 3) and me.ahead:
               score = len(sub) + brew_ids[sub[0][0]] // 2
            elif (me.pots >= 3 or other.pots >= 3) and other.ahead:
                score = len(sub) 
            elif other.ahead:
                score = len(sub) + brew_ids[sub[0][0]] // 2
            else:
                score = len(sub) + brew_ids[sub[0][0]]
            if score < best_score:
                best_score = score
                best_sub = sub
        return best_sub

    def do_simu(self):
        # reset
        self.nodes = 0
        self.best_bet = list()
        self.castables = actions.cast_to_arrays()
        self.initial = np.concatenate((0, me.inv), axis=None)
        self.best_subset_sums = list()

        targets = [np.concatenate((-b.id, b.deltas), axis=None) * -1 for b in actions.brew]
        generator = self.bfs_shortest_path(self.castables, self.initial, targets)
        self.best_subset_sums = [sub for sub in generator]

        for i in range(len(self.best_subset_sums)):
            self.best_subset_sums[i] = self.reorganise(self.best_subset_sums[i])

        self.total += len(self.best_subset_sums)

        if len(self.best_subset_sums):
            self.best_bet = self.get_best()

        self.show_results()
        return self.best_bet





      ####                ##      ##                     
   ##    ##    ######  ########        ####    ######    
  ########  ##          ##      ##  ##    ##  ##    ##   
 ##    ##  ##          ##      ##  ##    ##  ##    ##    
##    ##    ######      ####  ##    ####    ##    ##     
                                                         
                                                         
class Action:
    
    def __init__(self, _id, type, d0, d1, d2, d3, price, tome_index, tax_count, castable, repeatable):
        self.id = int(_id)
        self.type = type
        self.deltas = np.array([d0, d1, d2, d3], dtype=np.int16)
        self.price = int(price)
        self.ti = int(tome_index)
        self.tc = int(tax_count)
        self.castable = int(castable)
        self.repeatable = int(repeatable)
        self.bnf = 0

    def __str__(self):
        return f"{self.type} {self.id}, +={self.bnf}, {self.deltas}, ${self.price}, ti={self.ti}, tc={self.tc}, ca={self.castable}, rep={self.repeatable}"

    def __copy__(self):
        return Action(self.id, self.type, self.deltas[0], self.deltas[1], self.deltas[2], self.deltas[3], self.price, self.ti, self.tc, self.castable, self.repeatable)

    def to_array(self):
        return np.concatenate((self.id, self.deltas), axis=None)

    def learnable(self):
        negative_deltas = [- i if i < 0 else 0 for i in self.deltas] # directly passed as positive integers
        total_positive_deltas = [0,0,0,0]
        for c in actions.cast:
            for i in range(4):
                bonus = c.deltas[i] if c.deltas[i] > 0 else 0
                total_positive_deltas[i] += bonus * 2 if self.repeatable else bonus                
        return all([total_positive_deltas[i] >= negative_deltas[i] for i in range(4)])

    # ALL
    def benef(self):
        total = 0
        if self.type == "LEARN":
            if self.id > 1000:
                return 0
            total = self.tc - self.ti * 2
            if learning > 0:
                total += 10

            total += sum([(1, 1.5)[int(self.deltas[i] < 0)] * self.deltas[i] * (i + 1) for i in range(4)])
        else:    
            total += sum([(1, 1)[int(self.deltas[i] < 0)] * self.deltas[i] * (i + 1) for i in range(4)])
        return total





                                                          
    ######    ##                                          
   ##    ##  ##    ######  ##    ##    ####    ##  ####   
  ######    ##  ##    ##  ##    ##  ########  ####        
 ##        ##  ##    ##  ##    ##  ##        ##           
##        ##    ######    ######    ######  ##            
                             ##                           
                        ####                              

class Player:

    def __init__(self, inv0, inv1, inv2, inv3, score):
        self.inv = np.array([inv0, inv1, inv2, inv3], dtype=np.int16)
        self.score = int(score)
        self.pots = 0
        self.ahead = False
        
    def __str__(self):
        return f"inv={self.inv}"

    def __copy__(self):
        copy = Player(self.inv[0], self.inv[1], self.inv[2], self.inv[3], self.score)
        return copy

    def update(self, inv0, inv1, inv2, inv3, score):
        self.inv = np.array([inv0, inv1, inv2, inv3], dtype=np.int16)
        if self.score != int(score):
            self.pots += 1
        self.score = int(score)

    def new_balance(self, action):
        return [i + j for i,j in zip(self.inv, action.deltas)]

    def can_apply(self, action):
        new_inv = np.array(self.inv)
        new_inv[0] += action.tc - action.ti
        new_inv += action.deltas
        return all(i >= 0 for i in new_inv)

    def can_do(self, action):
        if action.type == "LEARN":
            return self.inv[0] >= action.ti
        else:
            return (all(d >= 0 for d in action.deltas + self.inv)) and sum(self.inv + action.deltas) <= 10



            
                                                                                        
      ####                ##      ##                        ######              ##      
   ##    ##    ######  ########        ####    ######    ##          ####    ########   
  ########  ##          ##      ##  ##    ##  ##    ##    ####    ########    ##        
 ##    ##  ##          ##      ##  ##    ##  ##    ##        ##  ##          ##         
##    ##    ######      ####  ##    ####    ##    ##  ######      ######      ####      
                                                                                        

class ActionSet:

    def __init__(self):
        # Unmodified
        self.original = []
        self.brew = []
        self.learn = []
        self.cast = []
        self.rest = [Action(0,"REST",0,0,0,0,0,0,0,0,0)]

    def __str__(self):
        NL = "\n"
        return f"=== BREW ==={NL}{NL.join([str(b) for b in self.brew])}{NL}=== LEARN ==={NL}{NL.join([str(b) for b in self.learn])}{NL}=== CAST ==={NL}{NL.join([str(b) for b in self.cast])}"

    def __copy__(self):
        copy = ActionSet()
        copy.brew = [action.__copy__() for action in self.brew]
        copy.cast = [action.__copy__() for action in self.cast]
        copy.learn = [action.__copy__() for action in self.learn]
        return copy

    def cast_to_arrays(self):
        # special stuff for the simulation
        self.learn.sort(key=lambda x: x.ti)
        new_lst = []
        for c in self.cast + self.learn:
        # for c in self.cast:
            if c.castable or (c.type == "LEARN" and me.inv[0] >= c.ti):
                array_c = c.to_array()
                if c.type == "LEARN":
                    array_c[1] += c.tc - c.ti
                new_lst.append(array_c)
        new_lst = np.asarray(new_lst)
        return new_lst

    def remove_other_can_brew_and_i_cant(self):
        b_to_remove = []
        for b in self.brew:
            if all(abs(b.deltas[i]) <= other.inv[i] for i in range(4)):
                if not all(abs(b.deltas[i]) <= me.inv[i] for i in range(4)):
                    b_to_remove.append(b)
        for b in b_to_remove:
            self.brew.remove(b)

    def to_list(self):
        cast_learn = self.cast + self.learn
        cast_learn.sort(key=lambda a: a.benef(), reverse=True)
        return self.brew + cast_learn

    def append(self, action):
        if action.type == "BREW":
            self.brew.append(action)
        if action.type == "LEARN":
            self.learn.append(action)
        if action.type == "CAST":
            self.cast.append(action)

    def get_action_by_id(self, its_id):
        for a in self.original:
            if its_id % 1000 == a.id:
                return a

    def get_action_by_array(self, array):
        # tolerence pour le deltas[0] parce qu'on ne suit pas son évolution
        for a in self.cast + self.learn:
            if a.deltas[1] == array[1] and a.deltas[2] == array[2] and a.deltas[3] == array[3]:
                return a

    def get_input(self):
        self.__init__()
        for _ in range(int(input())):
            self.append(Action(*input().split()))
        self.original = list(a.__copy__() for a in self.brew + self.cast + self.learn)
        self.add_repeatable()
        self.sort_highest_reward()

    def sort_highest_reward(self):
        self.cast.sort(key=lambda a: a.benef(), reverse=True)
        self.learn.sort(key=lambda a: a.benef(), reverse=True)
        self.brew.sort(key=lambda a: a.price, reverse=True)

    def remove_unavailable(self):
        self.brew = [act for act in self.brew if me.can_do(act)]
        # new_learn = [act for act in self.learn if act.learnable and me.can_do(act)]
        # if learning > 0:
        #     new_learn = [act for act in self.learn if me.can_do(act)]
        new_learn = [act for act in self.learn if me.can_apply(act) and me.can_do(act)]
        if learning > 0:
            new_learn = [act for act in self.learn if me.can_do(act)]
        self.learn = new_learn
        self.cast = [act for act in self.cast if act.castable and me.can_do(act)]
        self.oppo = []

    def remove_overdo(self, n=0):
        delta_max = [10, 0, 0, 0] # on met le max pour les delta0 pour ne pas rester bloque
        for action in self.brew[0:5-n]:
            delta_max = [max(abs(action.deltas[i]), abs(delta_max[i])) for i in range(4)]
        # Avoid holes
        for i in range(3):
            if delta_max[i + 1] > delta_max[i]:
                delta_max[i] = delta_max[i + 1]
        for i in range(4):
            if me.inv[i] >= delta_max[i]:
                self.cast = [action for action in self.cast if action.deltas[i] <= 0]
        for i in range(4):
            self.cast = [action for action in self.cast if not action.repeatable or action.deltas[i] + me.inv[i] <= delta_max[i]]

    def add_repeatable(self):
        rep_actions = []
        for action in self.cast + self.learn:
            if action.repeatable:
                for i in range(2, 6):
                    new_action = action.__copy__()
                    new_action.deltas *= i
                    if any([abs(d) > 10 for d in new_action.deltas]):
                        break
                    new_action.repeatable = i
                    new_action.id += 1000 * i
                    rep_actions.append(new_action)
            action.repeatable = 0
        for action in rep_actions:
            self.append(action)

    def clean(self):
        # self.remove_overdo(2)
        # if me.score >= other.score:
        #     self.remove_less_rentable(2) # when i win i take the best
        self.remove_unavailable()
        # self.remove_null_viab()

                                                
     ######                                     
  ##          ######  ######  ####      ####    
 ##  ####  ##    ##  ##    ##    ##  ########   
##    ##  ##    ##  ##    ##    ##  ##          
 ######    ######  ##    ##    ##    ######     
                                                

class Game:

    def __init__(self):
        self.target = None
        self.rest_turns = 0
        # last turn type can be SIMU, AUTO, REST
        self.last_turn_type = "REST"

    def debug(self):
        debug("turns", turns)
        debug("pots:", me.pots, "vs", other.pots)
        debug("learn", learning)
        debug("time:", (end - start) * 1000)

    def get_input(self):
        actions.get_input()
        me.update(*input().split())
        other.update(*input().split())

    def play(self):
        
        global learning
        
        # lst of possibilities
        lst = actions.to_list()

        if lst == []:
            print("REST")
            self.rest_turns += 1
        else:
            if lst[0].repeatable and lst[0].type == "CAST":
                print(f"{lst[0].type} {lst[0].id % 1000} {lst[0].id // 1000}")
            else:
                print(f"{lst[0].type} {lst[0].id % 1000}")
            if lst[0].type == "LEARN":
                learning -= 1

    def turn(self):

        global start
        global learning
        global end

        self.get_input() 
        reset_timer()

        # actions.remove_other_can_brew_and_i_cant()

        if me.pots > other.pots and turns < 20 and turns % 2:
            learning += 1

        sim = simu.do_simu()

        # debug(sim)
        # show_timing()

        # One left
        if len(sim) == 1:
            self.last_turn_type = "BREW"
            for b in actions.brew:
                if me.can_do(b):
                    print(f"BREW {b.id} smells like beer!")
                    return

        # last turn findings
        # if (not sim or len(sim) == 0) and len(simu.saved) > 1:
        #     my_id = simu.saved[1][0]
        #     my_action = actions.get_action_by_id(my_id)
        #     if my_action != None and me.can_do(my_action):
        #         simu.saved.pop(1)
        #         print(f"{my_action.type} {my_id % 1000}", ("", my_id // 1000)[int((my_id // 1000) != 0)], f"last turn findings {simu.saved[0][0]}! eta:{len(simu.saved)}")
        #         return

        # SIMU FOUND SOMETHING
        if sim and len(sim) > 1 and (turns > 5 or (len(sim) < 6 and sim[0][0] in [b.id for b in actions.brew[:2]])):
            self.last_turn_type = "SIMU"
            my_id = sim[1][0]
            my_action = actions.get_action_by_id(my_id)
            simu.best_bet.pop(1)
            simu.saved = simu.best_bet
            if "CAST" in my_action.type:
                print(f"CAST {my_id % 1000}", ("", my_id // 1000)[int((my_id // 1000) != 0)], f"Found {sim[0][0]}! eta:{len(simu.best_bet)}")
            else:
                print(f"{my_action.type} {my_id % 1000}", f"Found {sim[0][0]}! eta:{len(simu.best_bet)}")
                if my_action.type == "LEARN":
                    learning -= 1
                

        # FORCING REST
        elif len(actions.cast) / 1.6  > len([a for a in actions.cast if a.castable]) \
                or self.rest_turns < me.pots // 2 or self.last_turn_type == "BREW":
            self.last_turn_type = "REST"
            self.rest_turns += 1
            print("REST daddy told me I should rest")

        # GENERAL CASE
        else:
            debug("AUTOPILOT")
            self.last_turn_type = "AUTO"
            actions.clean()
            # Cas pour supprimer le learn
            if learning <= 0 and (actions.learn and actions.learn[0].tc < 4) and self.last_turn_type != "REST":
                actions.learn = []
            self.play()

        # self.debug()

# Globals
me = Player(0,0,0,0,0)
other = Player(0,0,0,0,0)
actions = ActionSet()
simu = Simulation()

start = 0
end = 0

# game loop
turns = 0
game = Game()

while True:
    turns += 1
    game.turn()
    all_times.append(get_timing())
    debug("max all_times=", max(all_times))
    if turns == 1:
        all_times.pop(0)

    # Who is in advance?
    if other.pots > me.pots:
        other.ahead = True
        me.ahead = False
    if other.pots < me.pots:
        other.ahead = False
        me.ahead = True



# in the first league: BREW <id> | WAIT; later: BREW <id> | CAST <id> [<times>] | LEARN <id> | REST | WAIT

