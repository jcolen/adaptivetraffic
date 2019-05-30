'''
Jonathan Colen
jcolen@uchicago.edu

light.py

Light represents a single traffic light. A light can connect at least two and up to 
4 roads. 

The roads connected to a given light are at right angles to each other. They are stored in a list
where the indices correspond to the diagram below:

			  0

		3	LIGHT   1

			  2

So for example, if the state of the light is green, a car can go from 3 to 1 or 2. We will add
left turns and U turns in later. 

More generally, a car at position n can go from position n to position (n + 2) % 2 or position (n + 3) % 2

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
	def __init__(self, timer=5):
		self.roads = [None] * 4
		self.color = [Color.RED, Color.RED]
		self.timer = timer
		self.counter = 0

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
			for i, rd in enumerate(self.roads):
				if rd is None or rd is road or i == (ind + 1) % 2:
					continue
				if rd.can_enter(self):
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
