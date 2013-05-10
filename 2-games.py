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
import numpy
#PYTHON SCRIPT FOR RUNNING DARWINIAN NEURODYNAMICS

# Create a local broker
from naoqi import *
broker=ALBroker("localbroker","0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       "127.0.0.1",         # parent broker IP
       config.robot_port)

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
        self.starting_fitness = -9999
        self.ending_fitness = -9999
        self.median = -9999
        self.fitness = -9999
        self.normaliser = 0
    def add_fitness(self,population):
        fitnesses = []
        for p in population:
            fitnesses.append(p.fitness)
        self.fitness_history.append(fitnesses)

    def get_game_fitness(self):
        self.starting_fitness = numpy.median(self.fitness_history[0])
        self.ending_fitness = numpy.median(self.fitness_history[-1])
        medians = []
        self.max = -9999.0
        self.min = 9999.0
        for f in self.fitness_history:
            medians.append(numpy.median(f))
            if max(f) > self.max:
                self.max = max(f)
            if min(f) < self.min:
                self.min = min(f)
        self.median = numpy.median(medians)
        self.normaliser = self.max - self.min
        if self.normaliser == 0:
            self.normaliser = 1.0
        self.fitness = (self.ending_fitness - self.starting_fitness)/self.normaliser
        return self.fitness

    def output_results(self):
        output = []
        output.append("game: {0}".format(self.game.get_id()))
        output.append("fitness: {0}".format(self.fitness))
        output.append("starting_fitness: {0}".format(self.starting_fitness))
        output.append("median: {0}".format(self.median))
        output.append("ending_fitness: {0}".format(self.ending_fitness))
        output.append("fitness_history: {0}".format(self.fitness_history))
        return "\n".join(output)

def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def plot_fitness(population,game_gen,game,games_history):
    if not os.path.exists('graphs/game_gen_{0}_game_{1}'.format(game_gen,game)): os.makedirs('graphs/game_gen_{0}_game_{1}'.format(game_gen,game))
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

def plot_games_fitness(games,games_history):
    if not os.path.exists('games/'): os.makedirs('games/')
    plt.figure(1)
    plt.clf()
    popFit = []
    for index, i in enumerate(games):
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

def save_population(g,population,game_gen="0",game="game_1"):
    if not os.path.exists('populations'): os.makedirs('populations')
    if not os.path.exists('populations/game_gen_{0}_game_{1}'.format(game_gen,game)): os.makedirs('populations/game_gen_{0}_game_{1}'.format(game_gen,game))
    if not os.path.exists('populations/game_gen_{0}_game_{1}/{2}'.format(game_gen,game,g)): os.makedirs('populations/game_gen_{0}_game_{1}/{2}'.format(game_gen,game,g))
    for i,p in enumerate(population):
        file = open('populations/game_gen_{0}_game_{1}/{2}/{3}.dat'.format(game_gen,game,g,i),'w')
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
        graph.draw('populations/game_gen_{0}_game_{1}/{2}/{3}.png'.format(game_gen,game,g,i))
        json_output = p.get_json()
        file = open('populations/game_gen_{0}_game_{1}/{2}/{3}.json'.format(game_gen,game,g,i),'w')
        file.write(str(json_output))
        file.close()
def save_games(generation,games):
    if not os.path.exists('games'): os.makedirs('games')
    # if not os.path.exists('games/game_{0}'.format(game)): os.makedirs('populations/game_{0}'.format(game))
    for i,game in enumerate(games):
        file = open("games/game_gen_{0}_game_{1}.dat".format(generation,i),'w')
        file.write(game.output_results())
        file.write("\n----ATOMS----\n")
        for a in game.game.get_atoms_as_list():
            file.write(a.print_atom())
        file.close()
        graph = nx.to_agraph(game.game.molecular_graph)
        for n in graph.nodes():
            graph.get_node(n).attr['color'] = graph_colours[memory.get_atom(n).type]
            if memory.get_atom(n).type == 'motor':
                graph.get_node(n).attr['label'] = memory.get_atom(n).motors
            if memory.get_atom(n).type == 'sensory':
                graph.get_node(n).attr['label'] = memory.get_atom(n).sensors
        graph.layout()
        graph.draw("games/game_gen_{0}_game_{1}.png".format(generation,i))
        json_output = game.game.get_json()
        file = open('games/game_gen_{0}_game_{1}.json'.format(generation,i),'w')
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

def duplicate_population(winning_population,losing_population,probability):
    new_pop = []
    for p in range(0,len(winning_population)):
        if random.random() < probability:
            new_m = winning_population[p].duplicate()
        else:
            new_m = losing_population[p].duplicate()
        memory.add_molecule(new_m)
        new_pop.append(new_m)
    return new_pop

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
proper_games_history_list = []
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
        assess_fitness(indiv,games[game_no].game)
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
for game_gen in range(0,200):
    for i,game in enumerate(games):
        all_games_history[i]=[]
        game.fitness_history=[]
    for g in range(0,config.pop_size*10):
        print "iteration:",g
        for game_no,island in enumerate(islands):
            population = island
            game = games[game_no].game
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
            # if g%(config.pop_size) == 0:
            # plt.ion()
            plot_fitness(population,game_gen,game_no,all_games_history[game_no])
            plt.show()
            plt.savefig('graphs/game_gen_{0}_game_{1}/{2}.png'.format(game_gen,game_no,g))
            plt.close()
            save_population(g,population,game_gen,game_no)
            print "fitnesses:"
            for p in population:
                print p.fitness
            games[game_no].add_fitness(population)
    for game_no,island in enumerate(islands):
        for indiv in island:
            assess_fitness(indiv,games[game_no].game)
        games[game_no].add_fitness(island)
    for game_no,island in enumerate(islands):
        best = 0
        print "fitnesses game {0}:".format(game_no)
        for i,bm in enumerate(island):
            print "{0}: {1}".format(i,bm.fitness)
            if bm.fitness > island[best].fitness:
                best = i
        print "best = ",best
        print "fitness = ",island[best].fitness
        game_result = games[game_no]
        game_fitness = game_result.get_game_fitness()
        memory.add_best_game_act_pair(
            games[game_no].game,island[best],
            fitness=(
                (island[best].fitness)
                /(game_result.normaliser)
                )
            )
        memory.add_games_result(game_result)
    crossover_weights_table = {}
    for i,b in enumerate(memory.archive):
        crossover_weights_table[i]=b.fitness
        crossover_get_weights = WeightedRandomizer(crossover_weights_table)
    for index,island in enumerate(islands):
        print "island:",index
        for p in island:
            print p.fitness
    save_games(game_gen,games)
    plot_games_fitness(games,proper_games_history_list)
    plt.show()
    plt.savefig('games/game_gen_{0}.png'.format(game_gen))
    plt.close()
    save_population(g,population,game_gen,game_no)
    save_archive(memory.archive)
    if games[0].fitness > games[1].fitness:
        games[1] = GameResults(games[0].game.duplicate())
        memory.add_molecule(games[1].game)
        games[1].game.mutate()
        islands[1] = duplicate_population(islands[0],islands[1],0.5)
    else:
        games[0] = GameResults(games[1].game.duplicate())
        memory.add_molecule(games[0].game)
        games[0].game.mutate()
        islands[0] = duplicate_population(islands[1],islands[0],0.5)
    for game_no,island in enumerate(islands):
        for indiv in island:
            assess_fitness(indiv,games[game_no].game)
    for index,island in enumerate(islands):
        print "island:",index
        for p in island:
            print p.fitness
    # a = input()
    # if a == "y":
    #     break

