'''
Jonathan Colen
jcolen@uchicago.edu

road.py

Road represents an edge with two endpoints. At least one endpoint of a road must be a light

All roads represent one directed edge in the directed graph representing the road network. 
Roads are oneway, so a two-way road must be represented by two roads between the same lights
in opposite directions

Roads store references to two lights in an array [light0, light1]. Cars travel from light0
to light1 on the road.
'''

class Road:
	'''
	@param length - The length of the road, in units
	@param maxspeed - The maximum speed on the road, in units/step
	'''
	def __init__(self, length=1, maxspeed=1, pos0=[None, None], pos1=[None, None]):
		self.lights = [None] * 2
		self.length = length
		self.maxspeed = maxspeed
		self.x0, self.y0 = pos0[0], pos0[1]
		self.x1, self.y1 = pos1[0], pos1[1]

	#TODO implement this
	def get_agents(self, pos1, pos2):
		return []
