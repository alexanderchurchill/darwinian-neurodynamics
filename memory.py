import random
class Messages(object):
	"""docstring for Messages"""
	def __init__(self):
		super(Messages, self).__init__()
		self.message_list = {}

	def add_key_to_memory(self,id):
		self.message_list[id]={}

	def send_message(self,id,key,value):
		"""
		Stores data centrally for other atoms
		to access
		"""
		self.message_list[str(id)][key] = value

	def clear_from_memory(self,id,value):
		pass
