import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import time
from enum import Enum
from random import randint

class Color(Enum):
	RED = 0
	GREEN = 1

class Car:
	
	def __init__(self, edge, **kwargs):
		self.edge = edge

		self.position = kwargs.get('position', 0.)
		self.speed = kwargs.get('speed', 0.)
		self.radius = kwargs.get('radius', 1.)
		self.accel = kwargs.get('accel', 1.)

class Grid_Graph(nx.DiGraph):

	def __init__(self):
		super(Grid_Graph, self).__init__()
		self.cars = []

	'''
	A light is a node in the directed graph. It stores two colors which rotate on a timer
	Each light has the following attributes:
		colors: The current colors for each road direction
		timer: The number of time steps between light switches
			If timer is less than zero, then this is not a light and is just an 'empty' point
			This is necessary as all edges/roads must have two endpoints
		counter: The current count of time steps before a switch
		inc_idxs: A list of which indices are filled for incoming roads
		out_idxs: A list of which indices are filled for outgoing roads
	
	The 'indices' for incoming or outgoing roads refer to the direction of that road
	relative to the light. This is important for left/right turns and determining which 
	road is directed by which light. The indices are as follows:

		  0

	 3	LIGHT  1

		  2

	So indices 0/2 are controlled by one light, and 1/3 are controlled by the other. In
	general, the road at index i is controlled by colors[i%2]
	'''
	def add_light(self, idx, colors=[Color.RED, Color.RED], timer=5):
		self.add_node(idx, colors=colors, timer=timer, counter=0, inc_idxs=[], out_idxs=[])
	
	'''
	A road is an edge in the directed graph. It has the following attributes:
		length: The length of the road
		maxspeed: The speed limit of the road in units/time step
		l0:	The outgoing index for this road in the light it leaves from
		l1: The incoming index for this road in the light it goes to
	'''
	def add_road(self, idx0, idx1, light0_index, light1_index, length=1, maxspeed=1):
		self.add_edge(idx0, idx1, length=length, maxspeed=maxspeed, 
						l0=light0_index, l1=light1_index)
		self.edges[idx0, idx1][0] = idx0
		self.edges[idx0, idx1][1] = idx1
		self.nodes[idx0]['out_idxs'].append(light0_index)
		self.nodes[idx1]['inc_idxs'].append(light1_index)

	def add_car(self, idx0, idx1, **kwargs):
		self.cars.append(Car(self.edges[idx0, idx1], **kwargs))

	def get_light_color(self, agent):
		return Color.RED
	
	def get_allowed_roads(self, edge):
		roads = []
		light = edge[1]
		for rd in self.edges(light):
			#Only turn onto outgoing roads
			if rd[0] != light:
				continue
			#No U-turns
			if rd[1] == edge[0]:
				continue
			roads.append(rd)
	
		return roads

	def get_agents(self, car):
		#The number of units to look ahead is decided by the stopping distnace
		front_bumper = car.position + car.radius
		lookahead = car.speed + car.speed * car.speed / 2. / car.accel

		return []

	def act_car(self, car, newpos, newvel):
		if newpos > car.edge['length']:
			newpos -= car.edge['length']
			light = self.nodes[car.edge[1]]
			#Delete ourselves if we are off the grid
			if light['timer'] < 0:
				return None
			allowed = self.get_allowed_roads(car.edge)
			#This is a bug - delete car if this happens
			if len(allowed) == 0:
				print('At an intersection with no options')
				return None
			newedge = allowed[randint(0, len(allowed) - 1)]
			car.edge = self.edges[newedge[0], newedge[1]]
			return self.act_car(car, newpos, newvel)

		car.position = newpos
		car.speed = newvel
		return 0

	def update_car(self, car):
		#Start at the maximum possible acceleration for the car and the given road
		accel = min(car.accel, car.edge['maxspeed'] - car.speed)
		
		agents = self.get_agents(car)
		for agent in agents:
			if isinstance(agent, Car):
				#Accelerate to car ahead's speed
				accel = min(accel, agent.speed - car.speed)
			else:
				#If light is red, set to max possible deceleration
				if self.get_light_color(agent) == Color.RED:
					accel = -min(car.accel, car.speed)

		#Find new position and speed after one time step
		newpos = car.position + car.speed + 0.5 * accel
		newvel = car.speed + accel

		return self.act_car(car, newpos, newvel)

	def update(self):
		todelete = []
		for i, car in enumerate(self.cars):
			val = self.update_car(car)
			if val is None:
				todelete.append(i)

		for i in sorted(todelete, reverse=True):
			del self.cars[i]

		for i in self.nodes:
			light = self.nodes[i]
			if light['timer'] < 0:
				continue
			light['counter'] += 1
			if light['counter'] == light['timer']:
				for i in range(len(light['colors'])):
					light['colors'][i] = Color.RED if light['colors'][i] == Color.GREEN else Color.GREEN
					light['counter'] = 0
		
	def print_status(self):
		for i, car in enumerate(self.cars):
			outstr = 'Car %d\t' % i
			outstr += 'On edge (%d, %d)\t' % (car.edge[0], car.edge[1])
			outstr += 'Pos: %g\t' % car.position
			outstr += 'Vel: %g' % car.speed
			print(outstr)
	
	def draw_lights(self, ax, layout):
		nodelist = list(self)
		if not nodelist or len(nodelist) == 0:
			return None

		node_size=300
		for light in nodelist:
			xy = layout[light]
			if self.nodes[light]['timer'] < 0:
				mk = ax.scatter(xy[0], xy[1], s=node_size, c='gray')
				mk.set_zorder(2)
				continue
			for i, color in enumerate(self.nodes[light]['colors']):
				marker = mpl.markers.MarkerStyle(marker='o', fillstyle='left' if i == 0 else 'right')
				if color == Color.GREEN:
					mk = ax.scatter(xy[0], xy[1], s=node_size, c='green', marker=marker)
				elif color == Color.RED:
					mk = ax.scatter(xy[0], xy[1], s=node_size, c='red', marker=marker)
				mk.set_zorder(2)

	def draw_cars(self, ax, layout):
		#Need to find positions of each car on the grid
		xy = np.zeros([len(self.cars), 2])
		for i, car in enumerate(self.cars):
			pos0, pos1 = layout[car.edge[0]], layout[car.edge[1]]
			dist = car.position / car.edge['length']
			xy[i, :] = pos0 + (pos1 - pos0) * dist
		ax.scatter(xy[:, 0], xy[:, 1], color='blue')

	def draw(self):
		ax = plt.gca()
		ax.clear()
		ax.set_axis_off()

		layout = nx.drawing.layout.planar_layout(self)
		nx.draw_networkx_edges(self, layout, arrows=True)
		self.draw_lights(ax, layout)
		self.draw_cars(ax, layout)
		nx.draw_networkx_labels(self, layout)

if __name__=='__main__':
	grid = Grid_Graph()

	#TODO Add loading from text (JSON, probably)

	grid.add_light(0, timer=-1)
	grid.add_light(1, colors=[Color.GREEN, Color.RED])
	grid.add_light(2, colors=[Color.GREEN, Color.RED])
	grid.add_light(3, timer=-1)

	grid.add_road(0, 1, 2, 0, length=5)
	grid.add_road(1, 0, 0, 2, length=5)
	grid.add_road(1, 2, 2, 0, length=10)
	grid.add_road(2, 1, 0, 2, length=10)
	grid.add_road(2, 3, 2, 0, length=5)
	grid.add_road(3, 2, 0, 2, length=5)

	grid.add_car(0, 1)
	
	grid.draw()

	for t in range(10):
		grid.update()
		grid.print_status()
		grid.draw()
		plt.pause(0.5)
	
	plt.show()
