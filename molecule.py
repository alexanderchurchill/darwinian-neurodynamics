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

class ActorMSMolecule(Molecule):
    """
    The data structure for an actor molecule
    """
    def __init__(self, arg):
        super(ActorMolecule, self).__init__()
        self.arg = arg
    def contructor(self):
        atom_1 = SensorAtom()
        atom_2 = TransformAtom()
        atom_3 = MotorAtom()