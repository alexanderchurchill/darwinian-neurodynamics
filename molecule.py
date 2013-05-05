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
        just_activated = []
        for atom in [atom for atom in self.get_atoms_as_list() if atom.active is False]:
            if atom.conditional_activate():
                just_activated.append(atom.get_id())
        while len(just_activated) > 0:
            atom_id = just_activated.pop(0)
            for successor_id in self.molecular_graph.successors(atom_id):
                atom = self.get_atom(successor_id)
                if atom.time_delayed == 0:
                    # print "start timers:",atom.get_id()
                    if atom.conditional_activate():
                        just_activated.append(atom.get_id())

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

    def delete_atom(self):
        pass

    def atom_connects_to(self,atom_id):
        return self.get_atom(atom_id).can_connect_to()

    def can_connect_atoms(self,from_atom_id,to_atom_id):
        if self.memory.get_atom(from_atom_id).type in self.memory.get_atom(to_atom_id).can_connect_to():
            return True
        else:
            return False
    def add_atom(self,atom_id):
        self.molecular_graph.add_node(atom_id)

    def add_atom_to(self,atom_id,child):
        self.add_atom(atom_id)
        self.molecular_graph.add_edge(atom_id,child)

    def add_atom_from(self,atom_id,parent):
        self.add_atom(atom_id)
        self.add_edge(parent,atom_id)

    def add_edge(self,from_atom_id,to_atom_id):
        if self.can_connect_atoms(from_atom_id,to_atom_id):
            self.molecular_graph.add_edge(from_atom_id,to_atom_id)

    def choose_and_add_edge(self,atom_id):
        atoms = [atom for atom in
        find_atoms_of_types(self.molecular_graph,atom_connects_to(atom_id))
        if atom not in self.molecular_graph.predecessors(atom_id)]
        parent = random.choice(atoms)
        self.add_edge(parent,atom_id)

    def add_random_edge(self):
        child = random.choice(self.molecular_graph.nodes())
        parent = random.choice(self.molecular_graph.nodes())
        while parent == child or child in self.molecular_graph.successors(parent):
            child = random.choice(self.molecular_graph.nodes())
        self.add_edge(parent,child)
        print "adding edge from {0} to {1}".format(parent,child)

    def remove_random_edge(self):
        atom = random.choice(self.molecular_graph.nodes())
        ins = self.molecular_graph.predecessors(atom)
        outs = self.molecular_graph.successors(atom)
        count = 0
        while (len(ins) == 0 and len(outs) == 0) and count < 150:
            atom = random.choice(self.molecular_graph.nodes())
            ins = self.molecular_graph.predecessors(atom)
            outs = self.molecular_graph.successors(atom)
            # maybe the graph is very disconnected?
            count += 1
        if len(ins) > 0 and len(outs) > 0:
            remove_type = random.choice(["ins","outs"])
        elif len(ins) > 0:
            remove_type = "ins"
        else:
            remove_type = "outs"
        if remove_type == "ins":
            ch = random.choice(ins)
            self.molecular_graph.remove_edge(ch,atom)
            print "removing edge {0} from {1}".format(ch,atom)
        else:
            ch = random.choice(outs)
            self.molecular_graph.remove_edge(atom,ch)
            print "removing edge {0} from {1}".format(atom,ch)

    def remove_atom(self,atom_id):
        self.molecular_graph.remove_node(atom_id)
        self.set_connections()

    def remove_random_atom(self):
        if len(self.molecular_graph.nodes()) > 1:
            atom = random.choice(self.molecular_graph.nodes())
            # print "deleting:",atom
            self.remove_atom(atom)

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
            if atom.type == "sensory" and len(atom.messages) == 0:
                atom.activate()
                # check to see if sensory conditions have been met
                if atom.active:
                    self.active = True
                    self.active_hist = True
        if self.active:
            self.conditional_activate()
    def act(self):
        self.times_tested += 1
        for atom in [atom for atom in self.get_atoms_as_list() if atom.active is True]:
            if atom.active is True:
                atom.act()

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
            if atom.type == "sensory" and len(atom.messages) == 0:
                atom.activate()
                # check to see if sensory conditions have been met
                if atom.active:
                    self.active = True
                    self.active_hist = True
        if self.active:
            self.conditional_activate()

    # def conditional_activate(self):
    #     for atom in [atom for atom in self.get_atoms_as_list() if atom.active is False]:
    #         atom.conditional_activate()

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
            message_delays=[0],
            parameters = {
            "time_active":"always",
            })
        atom_2 = TransformAtom(memory=self.memory,messages=[],message_delays=[1],
            parameters = {
            "time_active":"always",
            })
        atom_3 = NaoMaxSensorGame(
            memory=self.memory,messages=[],message_delays=[1]
            )
        # add atom to shared list of atoms
        for a in [atom_1,atom_2,atom_3]:
            self.memory.add_atom(a)
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
            sensors=[self.nao_memory.getRandomSensor()],
            sensory_conditions=[-10.0],
            messages=[],
            message_delays=[0],
            parameters = {
            "time_active":random.randint(0,100),
            })
        atom_2 = LinearTransformAtom(memory=self.memory,messages=[],message_delays=[2],
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
            },
            use_input=True)

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
            },
            use_input=True)
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
            },
            use_input=True)
        for a in [atom_1,atom_2,atom_3,atom_4,atom_5]:
            self.memory.add_atom(a)
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
            self.create_and_add_atom()
        if random.random() < 0.01:
            self.create_and_add_stm_group()
            self.set_connections()
        if random.random() < 0.05:
            self.add_random_edge()
            self.set_connections()
        if random.random() < 0.05:
            self.remove_random_edge()
            self.set_connections()
        if random.random() < 0.05:
            self.remove_random_atom()
            self.set_connections()

    def create_random_motor_atom(self):
        no_motors = random.choice([1,2,3,4])
        atom = NaoMotorAtom(
                    memory=self.memory,nao_memory=self.nao_memory,nao_motion=self.nao_motion,
                    messages=[],
                    message_delays=[random.randint(0,5)],
                    motors = self.get_random_motors(self.nao_memory,no_motors),
                    parameters = {
                    "time_active":random.randint(5,50),
                    "motor_parameters":[2*(random.random()-0.5) for i in range(0,no_motors)],
                    "times":[1, 1, 1]
                    },
                    use_input=True)
        self.memory.add_atom(atom)
        return atom

    def create_and_add_atom(self,a_type=None):
        if a_type is None:
            a_type = random.choice(["motor","sensory","transform"])
        if a_type == "motor":
            print "adding motor atom"
            atom = self.create_random_motor_atom()
        elif a_type == "sensory":
            print "adding sensory atom"
            atom = self.create_random_sensor_atom()
        elif a_type == "transform":
            print "adding transform atom"
            atom = self.create_random_transform_atom()
        connecting_atom = random.choice(self.molecular_graph.nodes())
        if random.random() < 0.5:
            self.add_atom_from(atom.get_id(),connecting_atom)
            print "adding from"
        else:
            self.add_atom_to(atom.get_id(),connecting_atom)
            print "adding to"
        self.set_connections()

    def create_random_sensor_atom(self):
        atom = NaoSensorAtom(memory=self.memory,nao_memory=self.nao_memory,
            sensors=[self.nao_memory.getRandomSensor()],
            # sensors=[random.choice([141,142,143])],
            sensory_conditions=[-10.0],
            messages=[],
            message_delays=[5],
            parameters={
            "time_active":100
            })
        self.memory.add_atom(atom)
        return atom

    def create_random_transform_atom(self):
        atom = LinearTransformAtom(memory=self.memory,
            messages=[],
            message_delays=[5],
            n=5,
            parameters={
            "time_active":50
            }
            )
        self.memory.add_atom(atom)
        return atom

    def create_and_add_stm_group(self):
        sensor = self.create_random_sensor_atom()
        transform = self.create_random_transform_atom()
        motor = self.create_random_motor_atom()
        allowed_connectors = self.find_atoms_of_types(self.molecular_graph,sensor.can_connect_to())
        parent = random.choice(allowed_connectors)
        for n in [sensor,transform,motor]:
            self.molecular_graph.add_node(n.get_id())
        self.add_edge(sensor.get_id(),transform.get_id())
        self.add_edge(transform.get_id(),motor.get_id())
        self.add_atom_from(sensor.get_id(),parent=parent)

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
        self.add_atom_from(other_atom,parent)

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
            self.memory.add_atom(new_atom)
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
