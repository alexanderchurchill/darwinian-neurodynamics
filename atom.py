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
        # register atom:
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
        self.memory.send_message(self.id,key,value)

    def add_atom_to_memory(self):
        self.memory.add_key_to_memory(self.id)

    def send_active_message(self):
        """
        Stores data centrally for other atoms
        to access
        """
        self.send_message("active",True)

    def send_deactivate_message(self):
        """
        Stores data centrally for other atoms
        to access
        """
        self.send_message("active",False)

    def get_id(self):
        return self.id

    def activate(self):
        self.active = True
        self.send_active_message()

    def conditional_activate(self):
        if self.messages is not None:
            for index, atom_id in enumerate(self.messages):
                if self.memory.get_message(atom_id,"active") and self.active is False: 
                    #Incremement timer
                    self.timer += 1
                    if self.timer == self.message_delays[index]:
                        self.activate()

class SensorAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,id, memory=None,messages=None,message_delays=None,parameters=None,
                 sensors=None,sensory_conditions=None):
        super(SensorAtom, self).__init__(id,memory=memory,messages=messages,message_delays=message_delays,parameters=parameters)
        self.sensors = sensors
        if self.sensors == None:
            self.sensors = []
        self.sensory_conditions = sensory_conditions
        if self.sensory_conditions == None:
            sensory_conditions = []
        self.sensor_input = None
        self.type = "sensory"

    def act(self):
        self.times_tested = self.times_tested+1
        self.send_message([sensor for sensor in self.sensors])

    def activate(self):
        self.get_sensor_input()
        conditions_met = True
        for sensor,condition in zip(self.sensor_input,self.sensory_conditions):
            if sensor < condition:
                conditions_met = False
        if conditions_met:
            Atom.activate(self)
    def get_sensor_input(self):
        pass
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


# NAO Classes
class NaoSensorAtom(SensorAtom):
    """
    The base class for a Nao specific sensor atom
    """
    def __init__(self,id, memory=None,messages=None,message_delays=None,parameters=None,
                 sensors=None,sensory_conditions=None,nao_memory=None):
        super(NaoSensorAtom, self).__init__(id,memory=memory,messages=messages,message_delays=message_delays,parameters=parameters,sensors=sensors,sensory_conditions=sensory_conditions)
        self.nao_memory = nao_memory
    def get_sensor_input(self):
        # print "in NaoSensorAtom"
        self.sensor_input = []
        for s in self.sensors:
            self.sensor_input.append(self.nao_memory.getSensorValue(s))
            print self.sensor_input
