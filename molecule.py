"""
Everything related to a molecule is in here
"""
from atom import *
import random
import networkx as nx
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
            print "looking at:",atom.id
            atom.conditional_activate()

    def act(self):
        self.times_tested += 1
        for atom in [atom for atom in self.get_atoms_as_list() if atom.active is True]:
            atom.act()

class NAOActorMolecule(ActorMolecule):
    """
    The data structure for an actor molecule
    """
    def __init__(self, memory,atoms,nao_memory,nao_motion):
        super(NAOActorMolecule, self).__init__(memory,atoms)
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        self.constructor()
        self.set_connections()
    def constructor(self):
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [143],messages = [self.totalCount], messageDelays = [1],motors = None, function = "position", parameters = None)
        # self.totalCount = self.totalCount + 1
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1] , messageDelays = [1],motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5),2*(random.random()-0.5),2*(random.random()-0.5)], [1, 1, 1]])
        # self.totalCount = self.totalCount + 1
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1], messageDelays = [2], motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5), 2*(random.random()-0.5), 2*(random.random()-0.5)], [1, 1, 1]])
        # self.totalCount = self.totalCount + 1
        atom_1 = NaoSensorAtom(id=1,memory=self.memory,nao_memory=self.nao_memory,
            sensors=[143],
            sensory_conditions=[-10.0],
            messages=[],
            message_delays=[0])
        atom_2 = TransformAtom(id=2,memory=self.memory,messages=[],message_delays=[1])
        
        atom_3 = NaoMotorAtom(
            id=3,memory=self.memory,nao_memory=self.nao_memory,nao_motion=self.nao_motion,
            messages=[],
            message_delays=[1],
            motors = [
            self.nao_memory.getRandomMotor(),
            self.nao_memory.getRandomMotor(),
            self.nao_memory.getRandomMotor()
            ],
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
        for a in [atom_1,atom_2,atom_3]:
            self.atoms[a.get_id()]=a
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id())
        self.molecular_graph.add_node(atom_2.get_id())
        self.molecular_graph.add_node(atom_3.get_id())
        self.molecular_graph.add_edges_from([(atom_1.get_id(),atom_2.get_id()),(atom_2.get_id(),atom_3.get_id())])

