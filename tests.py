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

#PYTHON SCRIPT FOR RUNNING DARWINIAN NEURODYNAMICS

# Create a local broker
from naoqi import *
broker=ALBroker("localbroker","0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       "127.0.0.1",         # parent broker IP
       9559)

fitnessHistory = []
def flatten(x):
    result = []
    for el in x:
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def plot_fitness(population):
    if not os.path.exists('graphs'): os.makedirs('graphs')
    plt.figure(1)
    plt.clf()
    popFit = []
    for index, i in enumerate(population):
        #      print "Molecule " + str(index) + " has fitness " + str(self.moleculeFitness[index])
        popFit.append(i.fitness)
        merged = flatten(popFit)

    fitnessHistory.append(merged)

    trans = [list(i) for i in zip(*fitnessHistory)]
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
    for t in range(0,300):
        # print "sensor:{0}".format(nao_mem_global.getSensorValue(141))
        individual.act()
        individual.conditional_activate()
        game.act()
        game.conditional_activate()
        sleep(0.001)
    individual.fitness = game.get_fitness()
    # print "state:",game.get_state_history()
    # raw_input()
    # print "fitness:",bm.fitness
    game.deactivate()
    individual.deactivate()

def save_population(g,population):
    if not os.path.exists('populations'): os.makedirs('populations')
    if not os.path.exists('populations/{0}'.format(g)): os.makedirs('populations/{0}'.format(g))
    for i,p in enumerate(population):
        file = open('populations/{0}/{1}.dat'.format(g,i),'w')
        file.write("member: {0}\n".format(i))
        file.write("fitness: {0}\n".format(p.fitness))
        file.write("----ATOMS----\n")
        for a in p.get_atoms_as_list():
            file.write(a.print_atom())
        file.close()
        graph = nx.to_agraph(p.molecular_graph)
        for n in graph.nodes():
            graph.get_node(n).attr['color'] = graph_colours[memory.atoms[n].type]
        graph.layout()
        graph.draw('populations/{0}/{1}.png'.format(g,i))
        json_output = p.get_json()
        file = open('populations/{0}/{1}.json'.format(g,i),'w')
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
                 id = id)
            memory.add_atom(new_atom)
        elif _class == 'TransformAtom':
            new_atom = TransformAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],id = id)
            memory.add_atom(new_atom)
        elif _class == 'LinearTransformAtom':
            new_atom = TransformAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],id = id)
            memory.add_atom(new_atom)
        elif _class == 'NaoMotorAtom':
            new_atom = NaoMotorAtom(memory=memory,messages=None,message_delays=message_delays,
                parameters=atom["parameters"],motors=atom["motors"],nao_motion=nao_motion,
                nao_memory=nao_memory, id = id)
            memory.add_atom(new_atom)
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
# bm = NAOActorMolecule(memory,atoms,nao_mem_global,bmf_global)
gm = NaoMaxSensorGameMolecule(memory,atoms,nao_mem_global)
# memory.molecules[bm.id] = bm
memory.molecules[gm.id] = gm
# c= bm.duplicate()
# print("bm")
# for atom in bm.get_atoms_as_list():
#   atom.print_atom()
# print("c")
# for atom in c.get_atoms_as_list():
#   atom.print_atom()

# print(bm)
m = memory.message_list
print m
# for atom in bm.get_atoms_as_list():
#   if atom.type == "motor":
#       ma = atom

# bm.activate()
# gm.activate()
# for t in range(0,10):
#   print "sensor:{0}".format(nao_mem_global.getSensorValue(143))
#   bm.act()
#   bm.conditional_activate()
#   gm.act()
#   gm.conditional_activate()
#   print t
#   print m
#   sleep(0.1)


population = []
pop_size = 10
for i in range(0,pop_size):
    molecule = NAOActorMolecule(memory,atoms,nao_mem_global,bmf_global)
    memory.molecules[molecule.id] = molecule
    population.append(molecule)

gm = NaoMaxSensorGameMolecule(memory,atoms,nao_mem_global)
for bm in population:
    assess_fitness(bm,gm)
best = 0
print "fitnesses:"
for i,bm in enumerate(population):
    print "{0}: {1}".format(i,bm.fitness)
    if bm.fitness > population[best].fitness:
        best = i
print "best = ",best
print "fitness = ",population[best].fitness

# raw_input()
# for t in range(0,30):
#     assess_fitness(population[best],gm)
# raw_input()


for g in range(0,pop_size*2000):
    print "iteration:",g
    ind_1_i = random.randint(0,len(population)-1)
    ind_2_i = random.randint(0,len(population)-1)
    while ind_1_i == ind_2_i:
        ind_2_i = random.randint(0,len(population)-1)
    ind_1 = population[ind_1_i]
    ind_2 = population[ind_2_i]
    for ind in [ind_1,ind_2]:
        assess_fitness(ind,gm)
    if ind_1.fitness > ind_2.fitness:
        print "ind_1 better"
        ind_2 = ind_1.duplicate()
        # nx.draw(ind_1.molecular_graph)
        # plt.draw()
        # plt.show()
        # plt.close()
        # nx.draw(ind_2.molecular_graph)
        # plt.draw()
        # plt.show()
        # plt.close()


        memory.molecules[ind_2.id]=ind_2
        population[ind_2_i] = ind_2
        ind_2.mutate()
        # assess_fitness(ind_2,gm)
        ind_2.fitness = copy.deepcopy(ind_1.fitness)
    else:
        print "ind_2 better"
        ind_1 = ind_2.duplicate()
        memory.molecules[ind_1.id]=ind_1
        population[ind_1_i] = ind_1
        ind_1.mutate()
        # assess_fitness(ind_1,gm)
        ind_1.fitness = copy.deepcopy(ind_2.fitness)
    if g%pop_size == 0:
        # plt.ion()
        plot_fitness(population)
        plt.show()
        plt.savefig('graphs/{0}.png'.format(g))
        plt.close()
        save_population(g,population)
        print "fitnesses:"
        for p in population:
            print p.fitness

plot_fitness(population)
plt.show()
plt.savefig('graphs/{0}.png'.format(g))
plt.close()
save_population(g,population)

for i,bm in enumerate(population):
    print "{0}: {1}".format(i,bm.fitness)
    if bm.fitness > population[best].fitness:
        best = i
print "best = ",best
print "fitness = ",population[best].fitness

bmf_global.rest()
sleep(1)
population[best].activate()
gm.activate()
for t in range(0,300):
    print "sensor:{0}".format(nao_mem_global.getSensorValue(143))
    population[best].act()
    population[best].conditional_activate()
    gm.act()
    gm.conditional_activate()
    sleep(0.001)

# print gm.get_state_history()
print gm.get_fitness()
gm.deactivate()
population[best].deactivate()
# bmf_global.rest()
# sleep(0.5)
# bmf_global.rest()
# sleep(0.5)
