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
    """docstring for Messages"""
    def __init__(self):
        super(Messages, self).__init__()
        self.message_list = {}

    @_all_strings
    def add_key_to_memory(self,id):
        self.message_list[id]={}

    def send_message(self,id,key,value):
        """
        Stores data centrally for other atoms
        to access
        """
        self.message_list[str(id)][str(key)] = value


    def clear_from_memory(self,id,value):
        pass

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

