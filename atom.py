"""
Everything related to an atom is in here
"""
import random
class Atom(object):
    """
    The base class for an atom
    """
    def __init__(self, id, memory=None,messages=None,message_delays=None,parameters=None):
        self.id = id #count
        self.memory = memory #mm
        self.messages = messages
        self.message_delays = message_delays #messageDelays
        self.active = False
        self.active_hist = False # activeHist ....take this out probably
        self.times_tested = 0 #timesTested
        self.parameters = parameters
        self.fitness = 0 
        #!!!!! self.set_stiffness(1)
        self.timer = 0 #start
        self.timer2 = 0 #last for?
        self.type = "base"
        # register atom
        self.add_atom_to_memory()
        self.send_deactivate_message()

    def act(self):
        pass

    def mutate(self):
        pass

    def send_message(self,key,value):
        """
        Stores data centrally for other atoms
        to access
        """
        self.memory.send_message(str(self.id),key,value)

    def add_atom_to_memory(self):
        self.memory.add_key_to_memory(str(self.id))

    def send_active_message(self):
        """
        Stores data centrally for other atoms
        to access
        """
        self.send_message("Active",True)

    def send_deactivate_message(self):
        """
        Stores data centrally for other atoms
        to access
        """
        self.send_message("Active",False)

class SensorAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,id, memory=None,messages=None,message_delays=None,parameters=None,
                 sensors=None,sensory_conditions=None):
        super(SensorAtom, self).__init__(id,memory,messages,message_delays,parameters)
        self.sensors = sensors
        if self.sensors == None:
            self.sensors = []
        self.sensory_conditions = sensory_conditions
        if self.sensory_conditions == None:
            sensory_conditions = []
        self.type = "sensory"

class TransformAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,id, memory=None,messages=None,message_delays=None,parameters=None):
        super(TransformAtom, self).__init__(id,memory,messages,message_delays,parameters)
        self.type = "transform"

class MotorAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,id, memory=None,messages=None,message_delays=None,parameters=None,
                 motors=None):
        super(MotorAtom, self).__init__(id,memory,messages,message_delays,parameters)
        self.motors = motors
        self.type = "motor"

class GameAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self, arg):
        super(Game, self).__init__()
        self.arg = arg
        self.sensors = sensors
        self.sensory_conditions = []
        self.type = "game"

