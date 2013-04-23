class Messages(object):
	"""docstring for Messages"""
	def __init__(self):
		super(Messages, self).__init__()
		self.message_list = {}

	def send_message(self,id,key,value):
		"""
		Stores data centrally for other atoms
		to access
		"""
		self.message_list[str(id)][key] = value

	def clear_from_memory(self,id,value):
		pass
