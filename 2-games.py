import os
import time
from naoqi import *
import random
import pickle 
import pprint
from nao_functions import *
from molecule import *
from memory import Messages
import networkx as nx
import pygraphviz as pgv
from networkx.readwrite import json_graph
import config

#PYTHON SCRIPT FOR RUNNING DARWINIAN NEURODYNAMICS

# Create a local broker
from naoqi import *
broker=ALBroker("localbroker","0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       "127.0.0.1",         # parent broker IP
       9560)

class WeightedRandomizer:
    def __init__ (self, weights):
        self.__max = .0
        self.__weights = []
        for value, weight in weights.items ():
            self.__max += weight
            self.__weights.append ( (self.__max, value) )

    def random (self):
        r = random.random () * self.__max
        for ceil, value in self.__weights:
            if ceil > r: return value

    def get_weights(self):
        return self.__weights

    def get_max(self):
        return self.__max

class GameResults(object):
    def __init__(self,game):
        self.game = game
        self.fitness_history = []
        
    def add_fitness(self,population):
        fitnesses = []
        for p in population:
            fitnesses.append(p.fitness)
        self.fitness_history.append(fitnesses)

    def get_game_fitness(self):
        starting_fitness = numpy.median(fitness_history[0])
        ending_fitness = numpy.median(fitness_history[-1])
        medians = []
        for f in fitness_history:
            medians.append(numpy.median(f))
        overall_median = numpy.median(medians)
        if overall_median == 0: overall_median = 0.01
        return (ending_fitness - starting_fitness) / overall_median

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def plot_fitness(population,game,games_history):
    if not os.path.exists('graphs/game_{0}'.format(game)): os.makedirs('graphs/game_{0}'.format(game))
    plt.figure(1)
    plt.clf()
    popFit = []
    for index, i in enumerate(population):
        #      print "Molecule " + str(index) + " has fitness " + str(self.moleculeFitness[index])
        popFit.append(i.fitness)
        merged = flatten(popFit)

    games_history.append(merged)

    trans = [list(i) for i in zip(*games_history)]
    for index, i in enumerate(trans):
        plt.plot(trans[index], marker='o', linestyle='None')
    plt.draw()
    plt.ion()
#INITIALIZATION
def assess_fitness(individual,game):
    individual.activate()
    game.activate()
    sleep(0.5)
    bmf_global.rest()
    sleep(0.5)
    for t in range(0,config.time_steps_per_evaluation):
        # print "sensor:{0}".format(nao_mem_global.getSensorValue(141))
        individual.act()
        individual.conditional_activate()
        game.act()
        game.conditional_activate()
        sleep(config.time_step_length)
    individual.fitness = game.get_fitness()
    # print "state:",game.get_state_history()
    # raw_input()
    # print "fitness:",bm.fitness
    game.deactivate()
    individual.deactivate()

def save_population(g,population,game="game_1"):
    if not os.path.exists('populations'): os.makedirs('populations')
    if not os.path.exists('populations/game_{0}'.format(game)): os.makedirs('populations/game_{0}'.format(game))
    if not os.path.exists('populations/game_{0}/{1}'.format(game,g)): os.makedirs('populations/game_{0}/{1}'.format(game,g))
    for i,p in enumerate(population):
        file = open('populations/game_{0}/{1}/{2}.dat'.format(game,g,i),'w')
        file.write("member: {0}\n".format(i))
        file.write("fitness: {0}\n".format(p.fitness))
        file.write("----ATOMS----\n")
        for a in p.get_atoms_as_list():
            file.write(a.print_atom())
        file.close()
        graph = nx.to_agraph(p.molecular_graph)
        for n in graph.nodes():
            graph.get_node(n).attr['color'] = graph_colours[memory.get_atom(n).type]
            if memory.get_atom(n).type == 'motor':
                graph.get_node(n).attr['label'] = memory.get_atom(n).motors
            if memory.get_atom(n).type == 'sensory':
                graph.get_node(n).attr['label'] = memory.get_atom(n).sensors
        graph.layout()
        graph.draw('populations/game_{0}/{1}/{2}.png'.format(game,g,i))
        json_output = p.get_json()
        file = open('populations/game_{0}/{1}/{2}.json'.format(game,g,i),'w')
        file.write(str(json_output))
        file.close()

def save_archive(archive):
    if not os.path.exists('archive'): os.makedirs('archive')
    # if not os.path.exists('populations/game_{0}'.format(game)): os.makedirs('populations/game_{0}'.format(game))
    # if not os.path.exists('populations/game_{0}/{1}'.format(game,g)): os.makedirs('populations/game_{0}/{1}'.format(game,g))
    for i,m in enumerate(archive):
        p = m.actor
        file = open('archive/{0}.dat'.format(i),'w')
        file.write("member: {0}\n".format(i))
        file.write("fitness: {0}\n".format(m.fitness))
        file.write("----ATOMS----\n")
        for a in p.get_atoms_as_list():
            file.write(a.print_atom())
        file.close()
        graph = nx.to_agraph(p.molecular_graph)
        for n in graph.nodes():
            graph.get_node(n).attr['color'] = graph_colours[memory.get_atom(n).type]
            if memory.get_atom(n).type == 'motor':
                graph.get_node(n).attr['label'] = memory.get_atom(n).motors
            if memory.get_atom(n).type == 'sensory':
                graph.get_node(n).attr['label'] = memory.get_atom(n).sensors
        graph.layout()
        graph.draw('archive/{0}.png'.format(i))
        json_output = p.get_json()
        file = open('archive/{0}.json'.format(i),'w')
        file.write(str(json_output))
        file.close()

def load_molecule(json,memory,atoms,nao_memory,nao_motion):
    molecule = NAOActorMolecule(memory,atoms,nao_memory,nao_motion,duplication=True)
    atoms = json["atoms"]
    for atom in atoms:
        id = atom["id"]
        _class = atom["class"]
        message_delays = atom["message_delays"]
        if _class == 'NaoSensorAtom':
            new_atom = NaoSensorAtom(memory=memory,messages=None,message_delays=message_delays,
                 sensors=atom["sensors"],sensory_conditions=atom["sensory_conditions"],nao_memory=nao_memory,
                 parameters=["parameters"],id = id)
            memory.add_atom(new_atom,id)
        elif _class == 'TransformAtom':
            new_atom = TransformAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],id = id)
            memory.add_atom(new_atom,id)
        elif _class == 'LinearTransformAtom':
            new_atom = LinearTransformAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],id = id)
            new_atom.set_t_matrix(atom["t_matrix"])
            memory.add_atom(new_atom,id)
        elif _class == 'NaoMotorAtom':
            new_atom = NaoMotorAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],motors=atom["motors"],nao_motion=nao_motion,
                nao_memory=nao_memory, use_input=atom["use_input"],id = id)
            memory.add_atom(new_atom,id)
    molecule.molecular_graph=json_graph.loads(json["molecular_graph"])
    molecule.set_connections()
    return molecule

#Create memory manager to store dictionary of sensory and motor states
#All use of memory is through use of the memory manager module. 
global nao_mem_global
nao_mem_global = NaoMemory("memoryManager")
# where the message list is kept
memory = Messages()
# where the list of all atoms are kept
atoms = memory.atoms
#Create an instance of a basic motor function module. 
global bmf_global
bmf_global = NaoMotorFunction("bmf","127.0.0.1")
bmf_global.rest()
game_1 = NaoMaxSensorGameMolecule(memory,atoms,nao_mem_global,sensors=[143])
game_2 = NaoMaxSensorGameMolecule(memory,atoms,nao_mem_global,sensors=[142])
games = []
best_game_scores = []
all_games_history = []

for g in [game_1,game_2]:
    memory.add_molecule(g)
    games.append(GameResults(g))
    all_games_history.append([])
    best_game_scores.append(-99999.0)
m = memory.message_list

islands = []
for island in games:
    population = []
    for i in range(0,config.pop_size):
        molecule = NAOActorMolecule(memory,atoms,nao_mem_global,bmf_global)
        memory.add_molecule(molecule)
        population.append(molecule)
    islands.append(population)

for game_no,island in enumerate(islands):
    for indiv in island:
        assess_fitness(indiv,games[game_no])
for game_no,island in enumerate(islands):
    best = 0
    print "fitnesses game {0}:".format(game_no)
    for i,bm in enumerate(island):
        print "{0}: {1}".format(i,bm.fitness)
        if bm.fitness > population[best].fitness:
            best = i
    print "best = ",best
    print "fitness = ",population[best].fitness
    # memory.add_best_game_act_pair(games[game_no],population[best],fitness=population[best].fitness)

for g in range(0,config.pop_size*20):
    print "iteration:",g
    for game_no,island in enumerate(islands):
        population = island
        game = games[game_no]
        print "===looking at game {0}===".format(game_no)
        ind_1_i = random.randint(0,len(population)-1)
        ind_2_i = random.randint(0,len(population)-1)
        while ind_1_i == ind_2_i:
            ind_2_i = random.randint(0,len(population)-1)
        ind_1 = population[ind_1_i]
        ind_2 = population[ind_2_i]
        for ind in [ind_1,ind_2]:
            assess_fitness(ind,game)
        if ind_1.fitness > ind_2.fitness:
            print "ind_1 better"
            ind_2 = ind_1.duplicate()

            memory.add_molecule(ind_2)
            population[ind_2_i] = ind_2
            new_ind = ind_2
            # assess_fitness(ind_2,gm)
            ind_2.fitness = copy.deepcopy(ind_1.fitness)
        else:
            print "ind_2 better"
            ind_1 = ind_2.duplicate()
            memory.add_molecule(ind_1)
            population[ind_1_i] = ind_1
            new_ind = ind_1
            # assess_fitness(ind_1,gm)
            ind_1.fitness = copy.deepcopy(ind_2.fitness)
        if len(memory.archive) > 0 and random.random() < config.crossover_rate:
            crossover_ind_index = crossover_get_weights.random()
            print "choosing {0} to crossover".format(crossover_ind_index)
            ind_from_archive = memory.archive[crossover_ind_index].actor
            new_ind.crossover(ind_from_archive)
        new_ind.mutate()
        if g%config.pop_size == 0:
            # plt.ion()
            plot_fitness(population,game_no,all_games_history[game_no])
            plt.show()
            plt.savefig('graphs/game_{0}/{1}.png'.format(game_no,g))
            plt.close()
            save_population(g,population,game_no)
            print "fitnesses:"
            for p in population:
                print p.fitness
for game_no,island in enumerate(islands):
    for indiv in island:
        assess_fitness(indiv,games[game_no])
for game_no,island in enumerate(islands):
    best = 0
    print "fitnesses game {0}:".format(game_no)
    for i,bm in enumerate(island):
        print "{0}: {1}".format(i,bm.fitness)
        if bm.fitness > island[best].fitness:
            best = i
    print "best = ",best
    print "fitness = ",island[best].fitness
    memory.add_best_game_act_pair(games[game_no],island[best],fitness=island[best].fitness)
    if island[best].fitness > best_game_scores[game_no]:
        best_game_scores[game_no] = island[best].fitness
# crossover_weights_table = {}
# for i,b in enumerate(memory.archive):
#     normaliser = best_game_scores[i%2]
#     if normaliser == 0 : normaliser = 0.01
#     crossover_weights_table[i]=b.fitness/best_game_scores[i%2]
#     crossover_get_weights = WeightedRandomizer(crossover_weights_table)



# for game_no,island in enumerate(islands):
#     for indiv in island:
#         assess_fitness(indiv,games[game_no])
# for game_no,island in enumerate(islands):
#     best = 0
#     print "fitnesses game {0}:".format(game_no)
#     for i,bm in enumerate(island):
#         print "{0}: {1}".format(i,bm.fitness)
#         if bm.fitness > population[best].fitness:
#             best = i
#     print "best = ",best
#     print "fitness = ",population[best].fitness
