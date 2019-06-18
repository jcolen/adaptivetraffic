'''
Jonathan Colen
jcolen@uchicago.edu

light.py

Light represents a single traffic light. A light can connect at least two and up to 
8 roads. 

The roads connected to a given light are at right angles to each other. They are stored in a list
where the indices correspond to the diagram below:

			 0 4 

	  3 7	LIGHT   1 5

			 2 6

Here, the first index represents roads heading towards the light, and the second index
represents roads traveling away from the light.

So for example, if the state of the light is green, a car can go from 0 to 6 or 7. We will add left turns and U turns later in some probabilistic model.

More generally, a car at position n can go from position n to position (n + 2) % 4 + 4 or (n + 3) % 4 + 4

The state of the light is stored as an array of two numbers. We will eventually figure out behavior for 
yellow lights. 

[Color02, Color13] - Color02 corresponds to the 02 direction and Color13 corresponds to the 13 direction.
It is never possible for Color02 and Color13 to both be GREEN. 
'''
from enum import Enum

class Color(Enum):
	RED = 0
	GREEN = 1

class Light:
	'''
	@param timer - Switch the lights after this many steps
	'''
	def __init__(self, timer=5, pos=[None, None]):
		self.roads = [None] * 8
		self.color = [Color.RED, Color.RED]
		self.timer = timer
		self.counter = 0
		self.x, self.y = pos[0], pos[1]

	def get_light_color(self, road):
		try:
			ind = self.roads.index(road)
			return self.color(ind % 2)
		except:
			return Color.RED

	def get_allowed_roads(self, road):
		try:
			ind = self.roads.index(road)
			color = self.color[ind % 2]
			if color == Color.RED:
				return []
			roads = []
			for rd in [self.roads[(ind+2)%4+4], self.roads[(ind+3)%4+4]]:
				if rd is not None:
					roads.append(rd)
			return roads
		except:
			return []
	
	def act(self):
		self.counter += 1
		if self.counter == self.timer:
			for i in range(len(self.color)):
				self.color[i] = Color.RED if self.color[i] == Color.GREEN else Color.GREEN
			self.counter = 0
