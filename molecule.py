"""
Everything related to a molecule is in here
"""
from atom import *
import random
import networkx as nx
import matplotlib.pyplot as plt

graph_colours = {
        "motor":"red",
        "sensory":"blue",
        "transform":"green"
        }

######################
# Base Molecules
######################

class Molecule(object):
    """
    Base class for a Molecule
    """
    def __init__(self,memory,atoms):
        self.atoms = atoms
        self.molecular_graph = None
        self.active = True
        self.active_hist = True
        self.memory = memory
        self.type = "base"
        self.times_tested = 0
        id = ""
        self.fitness = -999999
    def constructor(self):
        pass

    def conditional_activate(self):
        """
        previous: conditionalActivate
        """
        pass
    def set_connections(self):
        """
        takes graph connections between nodes and
        converts them to atom.messages
        """
        for n in self.molecular_graph:
            atom = self.atoms[n]
            connections = self.molecular_graph.predecessors(n)
            atom.messages = connections
    def get_atoms_as_list(self):
        atoms = []
        for n in self.molecular_graph:
            atom = self.atoms[n]
            atoms.append(atom)
        return atoms

    def get_atom(self,id):
        return self.memory.get_atom(id)

    def deactivate(self):
        self.active = False
        self.active_hist = False

    def mutate(self):
        pass

    def __str__(self):
        # long oneliner!
        return " - ".join(
            ["[id:{0} active:{1}]".format(self.atoms[a].id,self.atoms[a].active)
             for a in self.molecular_graph.nodes()
            ])


class GameMolecule(Molecule):
    """
    The data structure for a game molecule
    """
    def __init__(self,*args):
        super(GameMolecule, self).__init__(*args)
        self.type = "game"
        self.game_atoms = []
    def activate(self):
        """
        activate molecule
        """
        self.times_tested += 1
        for atom in self.get_atoms_as_list():
            if atom.type == "sensory":
                atom.activate()
                # check to see if sensory conditions have been met
                if atom.active:
                    self.active = True
                    self.active_hist = True

    def act(self):
        self.times_tested += 1
        for atom in [atom for atom in self.get_atoms_as_list() if atom.active is True]:
            if atom.active is True:
                atom.act()
    def conditional_activate(self):
        for atom in [atom for atom in self.get_atoms_as_list() if atom.active is False]:
            atom.conditional_activate()

    def get_fitness(self):
        fitness = -999999
        for game in self.game_atoms:
            fitness = self.get_atom(game).get_fitness()
        return fitness

    def get_state_history(self):
        for game in self.game_atoms:
            state = self.get_atom(game).state
        return state

    def deactivate(self):
        Molecule.deactivate(self)
        for game in self.game_atoms:
            game = self.get_atom(game)
            if game is not None:
                game.state = []

class ActorMolecule(Molecule):
    """
    The data structure for an actor molecule
    """
    def __init__(self,*args):
        super(ActorMolecule, self).__init__(*args)
        self.type = "actor_molecule"

    def activate(self):
        """
        activate molecule
        """
        self.times_tested += 1
        for atom in self.get_atoms_as_list():
            if atom.type == "sensory":
                atom.activate()
                # check to see if sensory conditions have been met
                if atom.active:
                    self.active = True
                    self.active_hist = True

    def conditional_activate(self):
        for atom in [atom for atom in self.get_atoms_as_list() if atom.active is False]:
            atom.conditional_activate()

    def act(self):
        self.times_tested += 1
        for atom in [atom for atom in self.get_atoms_as_list() if atom.active is True]:
            if atom.active is True:
                atom.act()

######################
# Nao Molecules
######################

class NaoMaxSensorGameMolecule(GameMolecule):
    """
    The data structure for a basic game molecule
    """
    def __init__(self, memory,atoms,nao_memory):
        super(NaoMaxSensorGameMolecule, self).__init__(memory,atoms)
        self.nao_memory = nao_memory
        self.constructor()
        self.set_connections()
        id = "g-{0}".format(random.randint(1,5000))
        while id in self.memory.molecules:
            id = "g-{0}".format(random.randint(1,5000))
        self.id = id

    def constructor(self):
        atom_1 = NaoSensorAtom(memory=self.memory,nao_memory=self.nao_memory,
            sensors=[141],
            sensory_conditions=[-10.0],
            messages=[],
            message_delays=[0])
        atom_2 = TransformAtom(memory=self.memory,messages=[],message_delays=[0],
            parameters = {
            "time_active":"always",
            })
        atom_3 = NaoMaxSensorGame(
            memory=self.memory,messages=[],message_delays=[0]
            )
        # add atom to shared list of atoms
        for a in [atom_1,atom_2,atom_3]:
            self.atoms[a.get_id()] = a
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id())
        self.molecular_graph.add_node(atom_2.get_id())
        self.molecular_graph.add_node(atom_3.get_id())
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id())
            ])
        self.game_atoms.append(atom_3.get_id())

class NAOActorMolecule(ActorMolecule):
    """
    The data structure for a Nao Actor molecule
    """
    def __init__(self, memory,atoms,nao_memory,nao_motion,duplication=False):
        super(NAOActorMolecule, self).__init__(memory,atoms)
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        if duplication == False:
            self.constructor()
            self.set_connections()
        id = "m-{0}".format(random.randint(1,5000))
        while id in self.memory.molecules:
            id = "m-{0}".format(random.randint(1,5000))
        self.id = id
    def constructor(self):
        atom_1 = NaoSensorAtom(memory=self.memory,nao_memory=self.nao_memory,
            sensors=[141],
            sensory_conditions=[-10.0],
            messages=[],
            message_delays=[0])
        atom_2 = TransformAtom(memory=self.memory,messages=[],message_delays=[2],
            parameters = {
            "time_active":random.randint(0,5),
            })

        atom_3 = NaoMotorAtom(
            memory=self.memory,nao_memory=self.nao_memory,nao_motion=self.nao_motion,
            messages=[],
            message_delays=[2],
            motors = self.get_random_motors(self.nao_memory,3),
            parameters = {
            "time_active":random.randint(0,3),
            "motor_parameters":[
            2*(random.random()-0.5),
            2*(random.random()-0.5),
            2*(random.random()-0.5)
            ],
            "times":[1, 1, 1]
            })

        atom_4 = NaoMotorAtom(
            memory=self.memory,nao_memory=self.nao_memory,nao_motion=self.nao_motion,
            messages=[],
            message_delays=[3],
            motors = self.get_random_motors(self.nao_memory,3),
            parameters = {
            "time_active":random.randint(0,3),
            "motor_parameters":[
            2*(random.random()-0.5),
            2*(random.random()-0.5),
            2*(random.random()-0.5)
            ],
            "times":[1, 1, 1]
            })
        # add atom to shared list of atoms
        # for i,a in enumerate([atom_1,atom_2,atom_3,atom_4]):
        #     a.id=str(1+i)
        for a in [atom_1,atom_2,atom_3,atom_4]:
            self.atoms[a.get_id()]=a
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id(),color=graph_colours[atom_1.type])
        self.molecular_graph.add_node(atom_2.get_id(),color=graph_colours[atom_2.type])
        self.molecular_graph.add_node(atom_3.get_id(),color=graph_colours[atom_2.type])
        self.molecular_graph.add_node(atom_4.get_id(),color=graph_colours[atom_4.type])
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            (atom_2.get_id(),atom_4.get_id())
            ])

    def get_random_motors(self,nao_memory,n_motors):
        motors = []
        for i in range(0,n_motors):
            motor = nao_memory.getRandomMotor()
            while motor in motors:
                motor = nao_memory.getRandomMotor()
            motors.append(motor)
        return motors
    def mutate(self):
        for atom in self.get_atoms_as_list():
            atom.mutate()
    def deactivate(self):
        for atom in self.get_atoms_as_list():
            atom.deactivate()

    def duplicate(self):
        new_molecule = NAOActorMolecule(memory=self.memory,
                                        atoms=self.atoms,
                                        nao_memory=self.nao_memory,
                                        nao_motion=self.nao_motion,
                                        duplication=True)
        graph_dict = {}
        new_graph_dict = {}
        new_graph = nx.DiGraph()
        # duplicate graph with new atoms
        for node in self.molecular_graph.nodes():
            graph_dict[node]={}
            graph_dict[node]["predecessors"]=self.molecular_graph.predecessors(node)
            new_atom = self.atoms[node].duplicate()
            self.atoms[new_atom.get_id()]=new_atom
            graph_dict[node]["child"] = new_atom.get_id()
            new_graph_dict[new_atom.get_id()]={}
            new_graph_dict[new_atom.get_id()]["parent"]=node
            new_graph.add_node(new_atom.get_id())
        # add edges
        for node in new_graph.nodes():
            parent = new_graph_dict[node]["parent"]
            for p in self.molecular_graph.predecessors(parent):
                new_graph.add_edge(graph_dict[p]["child"],node)
        new_molecule.molecular_graph=new_graph
        new_molecule.set_connections()
        return new_molecule
