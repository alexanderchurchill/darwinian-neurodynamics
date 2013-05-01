"""
Everything related to a molecule is in here
"""
from atom import *
import random
import networkx as nx
import pygraphviz as pgv
import matplotlib.pyplot as plt
from networkx.readwrite import json_graph

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
        self.json = {}
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

    def add_atom(self):
        pass

    def delete_atom(self):
        pass

    def find_atoms_of_types(self,graph,types):
        nodes = []
        for node in graph.nodes():
            atom = self.get_atom(node)
            if atom.type in types:
                nodes.append(node)
        return nodes

    def print_graph(self,filename):
        graph = nx.to_agraph(self.molecular_graph)
        for n in graph.nodes():
            try:
                colour = graph_colours[self.get_atom(n)].type
            except:
                colour = 'black'
            graph.get_node(n).attr['color'] = colour
        graph.layout()
        graph.draw('{0}.png'.format(filename))

    def to_json(self):
        self.json["molecular_graph"] = json_graph.dumps(self.molecular_graph)
        self.json["type"] = self.type
        self.json["class"]=self.__class__.__name__
        self.json["atoms"] = [a.get_json() for a in self.get_atoms_as_list()]

    def get_json(self):
        self.to_json()
        return self.json

    def __str__(self):
        # long oneliner!
        return " - ".join(
            ["[id:{0} active:{1} type:{2}]".format(self.atoms[a].id,self.atoms[a].active,self.atoms[a].type)
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
        id = "g-{0}".format(random.randint(1,500000))
        while id in self.memory.molecules:
            id = "g-{0}".format(random.randint(1,500000))
        self.id = id

    def constructor(self):
        atom_1 = NaoSensorAtom(memory=self.memory,nao_memory=self.nao_memory,
            sensors=[143],
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
            sensors=[143],
            sensory_conditions=[-10.0],
            messages=[],
            message_delays=[0])
        atom_2 = TransformAtom(memory=self.memory,messages=[],message_delays=[2],
            parameters = {
            "time_active":random.randint(0,100),
            })

        atom_3 = NaoMotorAtom(
            memory=self.memory,nao_memory=self.nao_memory,nao_motion=self.nao_motion,
            messages=[],
            message_delays=[random.randint(0,300)],
            motors = self.get_random_motors(self.nao_memory,3),
            parameters = {
            "time_active":random.randint(0,100),
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
            message_delays=[random.randint(0,300)],
            motors = self.get_random_motors(self.nao_memory,3),
            parameters = {
            "time_active":random.randint(0,100),
            "motor_parameters":[
            2*(random.random()-0.5),
            2*(random.random()-0.5),
            2*(random.random()-0.5)
            ],
            "times":[1, 1, 1]
            })
        atom_5 = NaoMotorAtom(
            memory=self.memory,nao_memory=self.nao_memory,nao_motion=self.nao_motion,
            messages=[],
            message_delays=[random.randint(0,300)],
            motors = self.get_random_motors(self.nao_memory,3),
            parameters = {
            "time_active":random.randint(0,100),
            "motor_parameters":[
            2*(random.random()-0.5),
            2*(random.random()-0.5),
            2*(random.random()-0.5)
            ],
            "times":[1, 1, 1]
            })
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5]:
            self.atoms[a.get_id()]=a
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id(),color=graph_colours[atom_1.type])
        self.molecular_graph.add_node(atom_2.get_id(),color=graph_colours[atom_2.type])
        self.molecular_graph.add_node(atom_3.get_id(),color=graph_colours[atom_3.type])
        self.molecular_graph.add_node(atom_4.get_id(),color=graph_colours[atom_4.type])
        self.molecular_graph.add_node(atom_5.get_id(),color=graph_colours[atom_5.type])
        self.molecular_graph.add_edges_from([
            (atom_1.get_id(),atom_2.get_id()),
            (atom_2.get_id(),atom_3.get_id()),
            (atom_2.get_id(),atom_4.get_id()),
            (atom_2.get_id(),atom_5.get_id())
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
        # intra atomic mutations
        for atom in self.get_atoms_as_list():
            atom.mutate()
        if random.random() < 0.05:
            self.create_and_add_motor_atom()
        if random.random() < 0.05:
            self.delete_atom_mutation()
        self.set_connections()

    def create_random_motor_atom(self):
        no_motors = random.choice([1,2,3,4])
        # message_delays_mean = random.choice([0,50,100,150,250])
        # message_delays = [int(random.gauss(message_delays_mean,0.1)*100)]
        # for i in message_delays:
        #     if i < 0:
        #         i = 0
        #     elif i > 300:
        #         i = 300
        atom = NaoMotorAtom(
                    memory=self.memory,nao_memory=self.nao_memory,nao_motion=self.nao_motion,
                    messages=[],
                    message_delays=[random.randint(0,300)],
                    motors = self.get_random_motors(self.nao_memory,no_motors),
                    parameters = {
                    "time_active":random.randint(5,50),
                    "motor_parameters":[2*(random.random()-0.5) for i in range(0,no_motors)],
                    "times":[1, 1, 1]
                    })
        self.memory.add_atom(atom)
        return atom

    def create_and_add_motor_atom(self):
        atom = self.create_random_motor_atom()
        allowed_connectors = self.find_atoms_of_types(self.molecular_graph,atom.can_connect_to())
        parent = random.choice(allowed_connectors)
        self.add_atom(atom.get_id(),parent=parent)

    def create_add_add_sensor_atom(self):
        atom = self.create_random_sensor_atom()
        allowed_connectors = self.find_atoms_of_types(self.molecular_graph,atom.can_connect_to())
        parent = random.choice(allowed_connectors)
        self.add_atom(atom.get_id(),parent=parent)

    def create_random_sensor_atom(self):
        atom = NaoSensorAtom(memory=self.memory,nao_memory=self.nao_memory,
            sensors=[self.nao_memory.getRandomSensor()],
            sensory_conditions=[-10.0],
            messages=[],
            message_delays=[0])
        self.memory.add_atom(atom)
        return atom

    def create_add_add_transform_atom(self):
        atom = self.create_random_transform_atom()
        allowed_connectors = self.find_atoms_of_types(self.molecular_graph,atom.can_connect_to())
        parent = random.choice(allowed_connectors)
        self.add_atom(atom.get_id(),parent=parent)

    def create_random_transform_atom(self):
        atom = LinearTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[random.randint(0,300)],
            n=5
            )
        self.memory.add_atom(atom)
        return atom

    def add_atom(self,atom_id,parent=None,):
        if parent == None:
            parent = []
        atom = self.get_atom(atom_id)
        self.molecular_graph.add_node(atom_id)
        if len(parent) > 0:
            self.molecular_graph.add_edge(parent,atom_id)

    def delete_atom(self,atom_id):
        delete_list = [atom_id]
        atom = self.get_atom(atom_id)
        successors = self.molecular_graph.successors(atom_id)
        open_list = successors
        while len(open_list) > 0:
            node = open_list.pop(0)
            open_list += [s for s in self.molecular_graph.successors(node) if s not in open_list]
            to_delete = True
            for n in self.molecular_graph.predecessors(node):
                if n not in delete_list:
                    to_delete = False
            if to_delete:
                delete_list.append(node)
        for node in delete_list:
            self.molecular_graph.remove_node(node)

    def delete_atom_mutation(self):
        atoms = self.find_atoms_of_types(self.molecular_graph,'motor')
        deleting = random.choice(atoms)
        self.delete_atom(deleting)

    def crossover(self,other_molecule):
        self.single_point_crossover(other_molecule)

    def single_point_crossover(self,other_molecule):
        other_atom = random.choice([atom for atom in other_molecule.get_atoms_as_list()
                                    if atom.type in ["motor","sensory"]]).duplicate()
        print "atom being moved:",other_atom.get_id()
        memory.add_atom(other_atom)
        self.add_other_atom(self,other_atom.get_id())
        self.replace_with_other_atom(self,other_atom.get_id())


    def add_other_atom(self,other_atom):
        atom = self.get_atom(other_atom.get_id())
        allowed_connectors = self.find_atoms_of_types(self.molecular_graph,atom.can_connect_to())
        parent = random.choice(allowed_connectors)
        self.add_atom(other_atom,parent)

    def replace_with_other_atom(self,other_atom):
        atom = self.get_atom(atom_id)
        allowed_connectors = self.find_atoms_of_types(self.molecular_graph,atom.can_connect_to())
        parent = random.choice(allowed_connectors)
        self.molecular_graph.add_node(other_atom)
        for p in self.molecular_graph.predecessors(parent):
            self.molecular_graph.add_edge(p,other_atom)
        for s in self.molecular_graph.successors(parent):
            self.molecular_graph.add_edge(other_atom,s)
        self.molecular_graph.remove_node(parent)

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
