"""
Everything related to an atom is in here
"""

import random,copy,string

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
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        self.memory = memory #mm
        self.messages = messages
        self.message_delays = message_delays #messageDelays
        self.active = False
        self.active_hist = False # activeHist ....take this out probably
        self.times_tested = 0 #timesTested
        self.fitness = 0 
        self.time_delayed = 0
        self.time_active = 0
        if id == None:
            self.id = self.create_id()
        else:
            self.id = id
        self.type = "base"
        self.json = {}
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
        id = "a-{0}-{1}".format(random.randint(1,5000),self._rand_char())
        while id in self.memory.atoms:
            id = "a-{0}-{1}".format(random.randint(1,5000),self._rand_char())
        return id

    def get_id(self):
        return self.id

    def deactivate(self):
        self.active = False
        self.time_delayed = 0
        self.time_active = 0
        # self.memory.clear_all_from_memory(self.id)
        self.send_deactivate_message()

    def activate(self):
        self.active = True
        self.send_active_message()

    def conditional_activate(self):
        any_parent_active = False
        if self.messages is not None:
            for index, atom_id in enumerate(self.messages):
                if self.memory.get_message(atom_id,"active"):
                    if self.active is False:
                        if self.time_delayed >= self.message_delays[index]:
                            self.activate()
                        #Incremement timer
                        self.time_delayed += 1
        if self.time_delayed > 0:
            self.time_delayed += 1
        # if any_parent_active == False:
        #     self.time_delayed = 0

    def can_connect_to(self):
        return []
    def _rand_char(self):
        return ""+random.choice(string.letters)+random.choice(string.letters)

    def to_json(self):
        for variable in ["id","message_delays","type","time_active"]:
            self.json[variable] = self.__getattribute__(variable)
        self.json["class"]=self.__class__.__name__

    def get_json(self):
        # save to json
        self.to_json()
        return self.json

    def __str__(self):
        return str(self.get_id())

class SensorAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,
                 sensors=None,sensory_conditions=None,parameters=None,id=None):
        super(SensorAtom, self).__init__(memory=memory,messages=messages,
                                    message_delays=message_delays,id=id
                                    )
        self.sensors = sensors
        if self.sensors == None:
            self.sensors = []
        self.sensory_conditions = sensory_conditions
        if self.sensory_conditions == None:
            sensory_conditions = []
        self.sensor_input = None
        self.type = "sensory"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters

    @_check_active_timer
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

    def can_connect_to(self):
        return ["sensory","motor","transform"]

    def to_json(self):
        Atom.to_json(self)
        for variable in ["sensors","sensory_conditions"]:
            self.json[variable] = self.__getattribute__(variable)


class TransformAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,parameters=None,id=None):
        super(TransformAtom, self).__init__(memory,messages,message_delays,id=id)
        self.type = "transform"
        if parameters == None:
            self.parameters = {}
        else:
            self.parameters = parameters

    @_check_active_timer
    def act(self):
        self.time_active += 1
        inp = self.get_input()
        output = inp
        self.send_message("output",inp)

    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in self.messages:
            inp+=self.memory.get_message(m,'output')
        return inp

    def duplicate(self):
        new_atom = TransformAtom(memory=self.memory,
                                messages=[],
                                message_delays=copy.deepcopy(self.message_delays),
                                parameters=copy.deepcopy(self.parameters)
                                )
        return new_atom

    def print_atom(self):
        output=""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

    def can_connect_to(self):
        return ["sensory"]

    def to_json(self):
        Atom.to_json(self)
        for variable in ["parameters"]:
            self.json[variable] = self.__getattribute__(variable)

class LinearTransformAtom(TransformAtom):
    """
    Atom used to transform sensor input to output
    """
    def __init__(self,memory=None,messages=None,message_delays=None,parameters=None,id=None,n=5):
        super(LinearTransformAtom, self).__init__(memory,messages,message_delays,id=id)
        self.n  = n #size of matrix
        self.t_matrix = [] #creates nxn matrix (with an extra bias)
        for i in range(0,self.n+1):
            self.t_matrix.append([])
            for j in range(0,5):
                self.t_matrix[i] += [0]
        self.init_t_matrix()
        self.parameters = parameters

    @_check_active_timer
    def act(self):
        self.time_active += 1
        inp = self.get_input()
        output = self.get_output(inp,5)
        self.send_message("output",output)


    def init_t_matrix(self):
        for m,row in enumerate(self.t_matrix):
            for n,cell in enumerate(row):
                self.t_matrix[m][n]=random.gauss(0,1)
                if self.t_matrix[m][n] > 1:
                    self.t_matrix[m][n] = 1
                elif self.t_matrix[m][n] < -1:
                    self.t_matrix[m][n] = -1

    def init_test_matrix(self):
        for i,row in enumerate(self.t_matrix):
            for j,column in enumerate(row):
                self.t_matrix[i][j] = i

    def get_t_matrix(self):
        return self.t_matrix

    def set_t_matrix(self):
        self.t_matrix = t_matrix

    def get_output(self,input,len_output):
        """
        takes an input vector (of max length n)
        and produces an output vector (of max length n)
        """
        print "get_output: input: ",input
        input_bias = input + [1]
        print "get_output: input_bias: ",input_bias
        if len_output > self.n:
            len_output = self.n
        output = [0]*len_output
        for column in range(0,len_output):
            for i,inp in enumerate(input_bias):
                output[column] += self.t_matrix[i][column]*inp
        print "input:",input
        print "transformed output:",output
        return output

    def duplicate(self):
        new_atom = LinearTransformAtom(memory=self.memory,
                                messages=[],
                                message_delays=copy.deepcopy(self.message_delays),
                                parameters=copy.deepcopy(self.parameters),
                                )
        new_atom.set_t_matrix(copy.deepcopy(self.get_t_matrix))
        return new_atom



class MotorAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,parameters=None,
                 motors=None,id=None):
        super(MotorAtom, self).__init__(memory,messages,message_delays,id=id)
        self.motors = motors
        self.parameters = parameters
        self.type = "motor"

    def act(self):
        self.motion()

    def motion(self):
        pass

    def can_connect_to(self):
        return ["transform","motor"]

    def to_json(self):
        Atom.to_json(self)
        for variable in ["motors","parameters"]:
            self.json[variable] = self.__getattribute__(variable)


class GameAtom(Atom):
    """
    The base class for a sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        super(GameAtom, self).__init__(memory=memory,messages=messages,message_delays=message_delays,
            id=id)
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
                 sensors=None,sensory_conditions=None,
                 parameters=None,nao_memory=None,id=None):
        super(NaoSensorAtom, self).__init__(
                                    memory=memory,messages=messages,message_delays=message_delays,
                                    sensors=sensors,sensory_conditions=sensory_conditions,parameters=parameters,id=id
                                    )
        self.nao_memory = nao_memory
    def get_sensor_input(self):
        self.sensor_input = []
        for s in self.sensors:
            self.sensor_input.append(self.nao_memory.getSensorValue(s))

    def duplicate(self):
        new_atom = NaoSensorAtom(memory=self.memory,
                                messages=[],
                                message_delays=copy.deepcopy(self.message_delays),
                                sensors=copy.deepcopy(self.sensors),
                                sensory_conditions=copy.deepcopy(self.sensory_conditions),
                                nao_memory=self.nao_memory
                                )
        return new_atom

    def print_atom(self):
        output = ""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "sensors: {0}\n".format(self.sensors)
        output += "sensory_conditions: {0}\n".format(self.sensory_conditions)
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

class NaoMotorAtom(MotorAtom):
    """
    The base class for a Nao specific sensor atom
    """
    def __init__(self,memory=None,messages=None,message_delays=None,parameters=None,
                 motors=None,nao_motion=None,nao_memory=None,use_input=False,id=None):
        super(NaoMotorAtom, self).__init__(
                                    memory=memory,messages=messages,
                                    message_delays=message_delays,parameters=parameters,
                                    motors=motors,id=id
                                    )
        self.nao_memory = nao_memory
        self.nao_motion = nao_motion
        self.use_input = use_input

    def send_motors_message(self,motors,input,angles):
        self.send_message("motors",motors)
        self.send_message("output",input)
        self.send_message("angles",angles)

    @_check_active_timer
    def motion(self):
        self.time_active += 1
        safe_angles = []
        names = []
        if self.use_input:
            # here we are using input from another atom, e.g. transfer atom
            angles = self.get_input()
        else:
            angles = self.parameters["motor_parameters"]
        for index, i in enumerate(self.motors):
            name = self.nao_memory.getMotorName(i)
            names.append(name)
            safe_angles.append(self.get_safe_angles(name,angles[index]))
        self.nao_motion.motion.setAngles(names,safe_angles,1)
        # print "moving:\nnames:{0}\nangles:{1}".format(names,angles)
        self.send_motors_message(self.motors,angles,safe_angles)

    def get_safe_angles(self,name,angle):
        limits = self.nao_motion.motion.getLimits(name)
        lo = limits[0][0]
        hi = limits[0][1]
        if angle < lo:
            angle = float(lo)
        elif angle > hi:
            angle = float(hi)
        return angle

    def mutate_motors(self,mutation_rate):
        for i,motor in enumerate(self.motors):
            if random.random() < mutation_rate:
                self.motors[i] = self.get_unique_rand_motor()

    def mutate_angles(self,mutation_rate):
        angles = self.parameters["motor_parameters"]
        for i,angle in enumerate(angles):
            if random.random() < mutation_rate:
                angle = 0.5*(random.random()-0.5) + angle
            self.parameters["motor_parameters"][i] = angle

    def mutate_delays(self,mutation_rate):
        if random.random() < mutation_rate:
            self.parameters["time_active"] += random.randint(-2,2)
        if self.parameters["time_active"] < 1:
            self.parameters["time_active"] = 1
        elif self.parameters["time_active"] > 100:
            self.parameters["time_active"] = 100

        for i,delay in enumerate(self.message_delays):
            if random.random() < mutation_rate:
                self.message_delays[i]+= random.randint(-2,2)

    def mutate(self):
        self.mutate_delays(0.05)
        self.mutate_motors(0.05)
        self.mutate_angles(0.05)

    def get_unique_rand_motor(self):
        motor = self.nao_memory.getRandomMotor()
        while motor in self.motors:
            motor = self.nao_memory.getRandomMotor()
        return motor
###############################Deprecate this:
    def get_input(self):
        """
        Reads the output messages sent by the atoms
        connected to this one
        """
        inp = []
        for m in self.messages:
            inp+=self.memory.get_message(m,'output')
        return inp


    def print_atom(self):
        output = ""
        output += "id: {0}\n".format(self.get_id())
        output += "type: {0}\n".format(self.type)
        output += "time_active: {0}\n".format(self.parameters["time_active"])
        output += "motors: {0}\n".format(self.motors)
        output += "motor_angles: {0}\n".format(self.parameters["motor_parameters"])
        output += "messages: {0}\n".format(self.messages)
        output += "message_delays: {0}\n".format(self.message_delays)
        return output

    def duplicate(self):
        new_atom = NaoMotorAtom(memory=self.memory,messages=[],
                                message_delays=copy.deepcopy(self.message_delays),
                                parameters = copy.deepcopy(self.parameters),
                                motors=copy.deepcopy(self.motors),
                                nao_motion=self.nao_motion,
                                nao_memory=self.nao_memory,
                                use_input= self.use_input
                                )
        return new_atom

class NaoMaxSensorGame(GameAtom):
    """A simple NAO game"""
    def __init__(self,memory=None,messages=None,message_delays=None,id=None):
        super(NaoMaxSensorGame, self).__init__(
            memory=memory,messages=messages,message_delays=message_delays,id=id
            )

    def act(self):
        inp = []
        output = []
        for m in self.messages:
            inp.append(self.memory.get_message(m,'output'))
        print "game_inp:",inp
        self.state.append(inp)
        print "game_state:",self.state

    def get_fitness(self):
        fitness = 0
        for time_step in self.state:
            for record in time_step:
                for data in record:
                    fitness += data
        return fitness
        
