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

    def constructor(self):
        pass

    def conditional_activate(self):
        """
        previous: conditionalActivate
        """
        pass
    def set_connections(self):
        for n in self.molecular_graph:
            atom = self.atoms[n]
            connections = self.molecular_graph.predecessors(n)
            atom.messages = connections

    def __str__(self):
        return " - ".join(["[id:{0} active:{1}]".format(a.id,a.active) for a in self.atoms])


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

    def activate():
        self.active = True
        self.active_hist = True
        for a in atoms:
            if a.type == "sensor":
                a.active = True
                a.send_active_message()

    def conditionalActivate(self):
        if self.messages is not None:
            for index, i in enumerate(self.messages):
                if self.mm.getMessageValue(i)[0] is 1 and self.active is False: 
                    #Incremement timer
                    self.timer += 1
                    if self.timer == self.message_delays[index]:
                        self.active = True
                        self.activeHist = True
                        self.send_active_message()#Active signal

class NAOActorMolecule(ActorMolecule):
    """
    The data structure for an actor molecule
    """
    def __init__(self, memory,atoms,nao_memory):
        super(NAOActorMolecule, self).__init__(memory,atoms)
        self.nao_memory = nao_memory
        self.memory = memory
        self.constructor()
        self.set_connections()
    def constructor(self):
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [143],messages = [self.totalCount], messageDelays = [1],motors = None, function = "position", parameters = None)
        # self.totalCount = self.totalCount + 1
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1] , messageDelays = [1],motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5),2*(random.random()-0.5),2*(random.random()-0.5)], [1, 1, 1]])
        # self.totalCount = self.totalCount + 1
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1], messageDelays = [2], motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5), 2*(random.random()-0.5), 2*(random.random()-0.5)], [1, 1, 1]])
        # self.totalCount = self.totalCount + 1
        atom_1 = SensorAtom(id=1,memory=self.memory,sensors=[143],messages=[],message_delays=[0])
        atom_2 = TransformAtom(id=2,memory=self.memory,messages=[],message_delays=[1])
        atom_3 = MotorAtom(id=3,memory=self.memory,messages=[],message_delays=[1],motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], parameters = [[random.randint(0,3)], [2*(random.random()-0.5),2*(random.random()-0.5),2*(random.random()-0.5)], [1, 1, 1]])
        self.atoms += [atom_1,atom_2,atom_3]
        self.molecular_graph = nx.DiGraph()
        self.molecular_graph.add_node(atom_1.get_id())
        self.molecular_graph.add_node(atom_2.get_id())
        self.molecular_graph.add_node(atom_3.get_id())
        self.molecular_graph.add_edges_from([(atom_1.get_id(),atom_2.get_id()),(atom_2.get_id(),atom_3.get_id())])

