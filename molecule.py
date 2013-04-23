"""
Everything related to a molecule is in here
"""
from atom import *

class Molecule(object):
    """
    Base class for a Molecule
    """
    def __init__(self):
        self.atoms = []
        self.type = "base"

    def constructor(self):
        pass

class GameMolecule(Molecule):
    """
    The data structure for a game molecule
    """
    def __init__(self):
        super(GameMolecule, self).__init__()
        self.arg = arg
        self.type = "game"

class ActorMolecule(Molecule):
    """
    The data structure for an actor molecule
    """
    def __init__(self, arg):
        super(ActorMolecule, self).__init__()
        self.arg = arg
        self.type = "actor"

class NAOActorMolecule(Actor):
    """
    The data structure for an actor molecule
    """
    def __init__(self, arg):
        super(ActorMolecule, self).__init__()
        self.nao_memory = arg
    def contructor(self):
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [143],messages = [self.totalCount], messageDelays = [1],motors = None, function = "position", parameters = None)
        # self.totalCount = self.totalCount + 1
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1] , messageDelays = [1],motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5),2*(random.random()-0.5),2*(random.random()-0.5)], [1, 1, 1]])
        # self.totalCount = self.totalCount + 1
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1], messageDelays = [2], motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5), 2*(random.random()-0.5), 2*(random.random()-0.5)], [1, 1, 1]])
        # self.totalCount = self.totalCount + 1
        atom_1 = SensorAtom(id=1,sensors=[143],messages=[1],message_delays=[0])
        atom_2 = TransformAtom(id=2,messages=[1],message_delays=[1])
        atom_3 = MotorAtom(id=3,messages=[2],message_delays=[1],motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], parameters = [[random.randint(0,3)], [2*(random.random()-0.5),2*(random.random()-0.5),2*(random.random()-0.5)], [1, 1, 1]]))

