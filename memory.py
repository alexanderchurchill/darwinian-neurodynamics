import random

def _all_strings(f):
    """
    This is a decorator to make sure
    all keys sent to memory are strings
    """
    def wrapped(self,*args):
        args = [str(a) for a in args]
        return f(self,*args)
    return wrapped

class Messages(object):
    """
    Central register for messages to be stored
    """
    def __init__(self):
        super(Messages, self).__init__()
        self.message_list = {}
        self.molecules = {}
        self.atoms = {}
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
    def add_atom(self,atom):
        self.atoms[atom.get_id()] = atom

    @_all_strings
    def delete_molecule(self,id):
        pass
