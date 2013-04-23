"""
Everything related to an atom is in here
"""

class Atom(object):
	"""
	The base class for an atom
	"""
	def __init__(self, arg):
		self.id = None #count
	    self.memory = None #mm
	    self.messages = None
	    self.message_delays = message_delays #messageDelays
	    ######
	    # do put in memory:
	    #self.mm.putMemory(self.id, [0,0,0]) #0 in first position = inactive, 1 in first position = active.
	    ######
	    self.active = False
	    self.active_hist = False # activeHist ....take this out probably
	    self.times_tested = 0 #timesTested
	    self.parameters = parameters
	    self.fitness = 0 
	    # self.set_stiffness(1)
	    self.timer = 0 #start
	    self.timer2 = 0 #last for?
	    self.type = "base"

    def act(self):
    	pass

	def mutate(self):
		pass

	def conditional_activate(self):
		"""
		previous: conditionalActivate
		"""
		pass

class SensorAtom(Atom):
	"""
	The base class for a sensor atom
	"""
	def __init__(self,sensors,sensory_conditions=None):
		super(Sensor, self).__init__()
		self.arg = arg
    	self.sensors = sensors
    	self.sensory_conditions = []
    	self.type = "sensory"

class MotorAtom(Atom):
	"""
	The base class for a sensor atom
	"""
	def __init__(self):
		super(Motor, self).__init__()
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

