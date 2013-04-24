"""
Everything related to a molecule is in here
"""
from atom import *
import random
class Molecule(object):
    """
    Base class for a Molecule
    """
    def __init__(self,memory):
        self.atoms = []
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
    def __init__(self, memory,nao_memory):
        super(NAOActorMolecule, self).__init__(memory)
        self.nao_memory = nao_memory
        self.memory = memory
        self.constructor()
    def constructor(self):
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "sensory", nameA = "actor",count = self.totalCount, sensors = [143],messages = [self.totalCount], messageDelays = [1],motors = None, function = "position", parameters = None)
        # self.totalCount = self.totalCount + 1
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1] , messageDelays = [1],motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5),2*(random.random()-0.5),2*(random.random()-0.5)], [1, 1, 1]])
        # self.totalCount = self.totalCount + 1
        # self.actors[self.totalCount] = actorClass(copyA = False, atomA = None, typeA = "motorP", nameA = "actor",count = self.totalCount, sensors = None, messages = [self.totalCount-1], messageDelays = [2], motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], function = "sequence", parameters = [[random.randint(0,3)], [2*(random.random()-0.5), 2*(random.random()-0.5), 2*(random.random()-0.5)], [1, 1, 1]])
        # self.totalCount = self.totalCount + 1
        atom_1 = SensorAtom(id=1,memory=self.memory,sensors=[143],messages=[1],message_delays=[0])
        atom_2 = TransformAtom(id=2,memory=self.memory,messages=[1],message_delays=[1])
        atom_3 = MotorAtom(id=3,memory=self.memory,messages=[2],message_delays=[1],motors = [self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor(),self.nao_memory.getRandomMotor()], parameters = [[random.randint(0,3)], [2*(random.random()-0.5),2*(random.random()-0.5),2*(random.random()-0.5)], [1, 1, 1]])
        self.atoms = [atom_1,atom_2,atom_3]

