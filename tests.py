import os
import time
from naoqi import *
import random
import pickle 
import pprint
from nao_functions import *
from molecule import *
from memory import Messages
#PYTHON SCRIPT FOR RUNNING DARWINIAN NEURODYNAMICS

# Create a local broker
from naoqi import *
broker=ALBroker("localbroker","0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       "127.0.0.1",         # parent broker IP
       9559)
TRIAL_TIME = 10
from_file = False

#INITIALIZATION

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
bm = NAOActorMolecule(memory,atoms,nao_mem_global,bmf_global)
gm = NaoMaxSensorGameMolecule(memory,atoms,nao_mem_global)
memory.molecules[bm.id] = bm
memory.molecules[gm.id] = gm

print(bm)
m = memory.message_list
print m
for atom in bm.get_atoms_as_list():
	if atom.type == "motor":
		ma = atom

# bm.activate()
# gm.activate()
# for t in range(0,10):
# 	print "sensor:{0}".format(nao_mem_global.getSensorValue(143))
# 	bm.act()
# 	bm.conditional_activate()
# 	gm.act()
# 	gm.conditional_activate()
# 	print t
# 	print m
# 	sleep(0.1)


# population = []
# for i in range(0,10):
# 	molecule = NAOActorMolecule(memory,atoms,nao_mem_global,bmf_global)
# 	memory.molecules[molecule.id] = molecule
# 	population.append(molecule)

# gm = NaoMaxSensorGameMolecule(memory,atoms,nao_mem_global)
# for bm in population:
# 	bmf_global.rest()
# 	bm.activate()
# 	gm.activate()
# 	for t in range(0,10):
# 		print "sensor:{0}".format(nao_mem_global.getSensorValue(143))
# 		bm.act()
# 		bm.conditional_activate()
# 		gm.act()
# 		gm.conditional_activate()
# 		print t
# 		print m
# 		sleep(0.1)
# 		game = None
# 	bm.fitness = gm.get_fitness()
# 	print "fitness:",bm.fitness
# 	gm.deactivate()
# print "fitnesses:"
# for bm in population:
# 	print bm.fitness