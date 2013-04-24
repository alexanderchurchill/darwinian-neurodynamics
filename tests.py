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
memory = Messages()
#Create an instance of a basic motor function module. 
global bmf_global
bmf_global = NaoMotorFunction("bmf","127.0.0.1")

basic_molecule = NAOActorMolecule(memory,nao_mem_global)