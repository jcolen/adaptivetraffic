'''
Jonathan Colen
jcolen@uchicago.edu

road.py

Road represents an edge with two endpoints. At least one endpoint of a road must be a light
'''

class Road:
	'''
	@param length - The length of the road, in units
	@param maxspeed - The maximum speed on the road, in units/step
	@param oneway - 0 if the road is bidirectional
					1 if the road is one way from light0 to light1
					2 if the road is one way from light1 to light0
	'''
	def __init__(self, length=1, maxspeed=1, oneway=0):
		self.lights = [None] * 2
		self.length = length
		self.maxspeed = maxspeed
		self.oneway = oneway
	
	def can_enter(self, light):
		try:
			ind = self.lights.index(light)
			return self.oneway == 0 or (ind + self.oneway) % 2
		except:
			return False
	
	def enter_from(self, light):
		try:
			ind = self.lights.index(light)
			return (ind + 1) % 2
		except:
			return -1
	
	#TODO implement this
	def get_agents(self, pos1, pos2, direction):
		return []
