"""
Everything related to an atom is in here
"""

import random

######################
# decorators
######################

def _check_active_timer(f):
    """
    This is a decorator to make sure
    the should still be active
    """
    def wrapped(self,*args):
        if (self.parameters["time_active"] is not "always"
            and self.time_active >= self.parameters["time_active"]
            ):
            self.deactivate()
            self.active = False
            self.time_delayed = 0
            self.time_active = 0
        else:
            return f(self,*args)
    return wrapped

######################
# Base atom classes
######################

class Atom(object):
    """
    The base class for an atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None):
        self.memory = memory #mm
        self.messages = messages
        self.message_delays = message_delays #messageDelays
        self.active = False
        self.active_hist = False # activeHist ....take this out probably
        self.times_tested = 0 #timesTested
        self.fitness = 0 
        #!!!!! self.set_stiffness(1)
        self.time_delayed = 0 #start
        self.time_active = 0 #last for?
        self.id = self.create_id()#count
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

    def create_id(self):
        id = "a-{0}".format(random.randint(1,5000))
        while id in self.memory.atoms:
            id = "a-{0}".format(random.randint(1,5000))
        return id

    def get_id(self):
        return self.id

    def deactivate(self):
        self.active = False
        self.time_delayed = 0
        self.time_active = 0
        self.memory.clear_all_from_memory(self.id)
        self.send_deactivate_message()

    def activate(self):
        self.active = True
        self.send_active_message()

    def conditional_activate(self):
        if self.messages is not None:
            for index, atom_id in enumerate(self.messages):
                if self.memory.get_message(atom_id,"active") and self.active is False: 
                    #Incremement timer
                    self.time_delayed += 1
                    if self.time_delayed >= self.message_delays[index]:
                        self.activate()

class SensorAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 sensors=None,sensory_conditions=None):
        super(SensorAtom, self).__init__(memory=memory,messages=messages,
                                    message_delays=message_delays
                                    )
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
        self.get_sensor_input()
        self.send_message("output",[sensor for sensor in self.sensor_input])

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
    def __init__(self,memory=None,messages=None,message_delays=None,parameters=None):
        super(TransformAtom, self).__init__(memory,messages,message_delays)
        self.type = "transform"
        self.parameters = parameters

    @_check_active_timer
    def act(self):
        self.time_active += 1
        inp = []
        output = []
        for m in self.messages:
            inp.append(self.memory.get_message(m,'output'))
        output = inp
        self.send_message("output",inp)

class MotorAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,parameters=None,
                 motors=None):
        super(MotorAtom, self).__init__(memory,messages,message_delays)
        self.motors = motors
        self.parameters = parameters
        self.type = "motor"

    def act(self):
        self.motion()

    def motion(self):
        pass

class GameAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None):
        super(GameAtom, self).__init__(memory=memory,messages=messages,message_delays=message_delays)
        self.type = "game"
        self.state = []

    def get_fitness(self):
        pass

    def clear_game_history(self):
        self.state = []


######################
# Nao Atoms
######################

class NaoSensorAtom(SensorAtom):
    """
    The base class for a Nao specific sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 sensors=None,sensory_conditions=None,nao_memory=None):
        super(NaoSensorAtom, self).__init__(
                                    memory=memory,messages=messages,message_delays=message_delays,
                                    sensors=sensors,sensory_conditions=sensory_conditions
                                    )
        self.nao_memory = nao_memory
    def get_sensor_input(self):
        # print "in NaoSensorAtom"
        self.sensor_input = []
        for s in self.sensors:
            self.sensor_input.append(self.nao_memory.getSensorValue(s))
            print self.sensor_input

class NaoMotorAtom(MotorAtom):
    """
    The base class for a Nao specific sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,parameters=None,
                 motors=None,nao_motion=None,nao_memory=None):
        super(NaoMotorAtom, self).__init__(
                                    memory=memory,messages=messages,
                                    message_delays=message_delays,parameters=parameters,
                                    motors=motors
                                    )
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion

    def send_motors_message(self,motors,angles):
        self.send_message("motors",motors)
        self.send_message("angles",angles)

    @_check_active_timer
    def motion(self):
        self.time_active += 1
        angles = []
        names = []

        for index, i in enumerate(self.motors):
            name = self.nao_memory.getMotorName(i)
            if name in names:
                continue
            print "name:",name
            names.append(name)
            angles.append(self.get_safe_angles(name,self.parameters["motor_parameters"][index]))
        self.nao_motion.motion.setAngles(names,angles,1)
        self.send_motors_message(self.motors,angles)

    def get_safe_angles(self,name,angle):
        limits = self.nao_motion.motion.getLimits(name)
        lo = limits[0][0]
        hi = limits[0][1]
        if angle < lo:
            angle = float(lo)
        elif angle > hi:
            angle = float(hi)
        return angle

class NaoMaxSensorGame(GameAtom):
    """A simple NAO game"""
    def __init__(self,memory=None,messages=None,message_delays=None):
        super(NaoMaxSensorGame, self).__init__(
            memory=memory,messages=messages,message_delays=message_delays
            )

    def act(self):
        inp = []
        output = []
        for m in self.messages:
            inp.append(self.memory.get_message(m,'output'))
        print "adding {0} to state".format(inp)
        self.state += inp

    def get_fitness(self):
        fitness = 0
        for time_step in self.state:
            for record in time_step:
                for data in record:
                    fitness += data
        return fitness


        
