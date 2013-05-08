import random
from molecule import GameMolecule,ActorMolecule
def _all_strings(f):
    """
    This is a decorator to make sure
    all keys sent to memory are strings
    """
    def wrapped(self,*args):
        args = [str(a) for a in args]
        return f(self,*args)
    return wrapped

class GameActorPair(object):
    def __init__(self,game,actor,fitness=0):
        self.game = game
        self.actor = actor
        if isinstance(self.game,GameMolecule) is False:
            raise TypeError ("game must be a GameMolecule")
        if isinstance(self.actor,ActorMolecule) is False:
            raise TypeError ("actor must be a ActorMolecule")
        self.fitness = fitness

    def set_fitness(self,fitness):
        self.fitness = fitness

class Messages(object):
    """
    Central register for messages to be stored
    """
    def __init__(self):
        super(Messages, self).__init__()
        self.message_list = {}
        self.molecules = {}
        self.atoms = {}
        self.atom_count = 0
        self.molecule_count = 0
        self.archive = []
    @_all_strings
    def add_key_to_memory(self,id):
        self.message_list[id]={}

    def send_message(self,id,key,value):
        """
        Stores data centrally for other atoms
        to access
        """
        self.message_list[str(id)][str(key)] = value

    @_all_strings
    def clear_all_from_memory(self,id):
        self.message_list[id]={}

    @_all_strings
    def get_message(self,id,key):
        try:
            message = self.message_list[id][key]
        except:
            message = None
        return message

    @_all_strings
    def get_all_messages(self,id):
        message = self.message_list[id]
        return message

    @_all_strings
    def get_atom(self,id):
        if id in self.atoms:
            return self.atoms[id]
        else:
            return None

    def add_atom(self,atom,atom_id = None):
        if atom_id == None:
            atom_id = atom.create_id(self.get_atom_count())
        atom.set_id(atom_id)
        self.atoms[atom.get_id()] = atom
        atom.register_atom()
        self.atom_count += 1

    def get_atom_count(self):
        return self.atom_count

    @_all_strings
    def get_molecule(self,id):
        if id in self.molecules:
            return self.molecules[id]
        else:
            return None

    def get_molecule_count(self):
        return self.molecule_count

    def add_molecule(self,molecule,molecule_id = None):
        if molecule_id == None:
            molecule_id = molecule.create_id(self.get_molecule_count())
        molecule.set_id(molecule_id)
        self.molecules[molecule.get_id()] = molecule
        self.molecule_count += 1

    @_all_strings
    def delete_molecule(self,id):
        pass

    def add_best_game_act_pair(self,game,actor,fitness=0):
        if isinstance(game,GameMolecule) is False:
            raise TypeError ("game must be a GameMolecule")
        if isinstance(actor,ActorMolecule) is False:
            raise TypeError ("actor must be a ActorMolecule")
        actor_copy = actor.duplicate()
        self.add_molecule(actor_copy)
        game_copy = game.duplicate()
        self.add_molecule(game_copy)
        gap = GameActorPair(game_copy,actor_copy,fitness)
        self.archive.append(gap)
