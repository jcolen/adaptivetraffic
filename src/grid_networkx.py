import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import logging

from enum import Enum
from random import randint

logger = logging.getLogger('root')
FORMAT = "[%(levelname)s %(filename)s:%(lineno)3s - %(funcName)15s() ] %(message)s"
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.INFO)
logger.setLevel(logging.DEBUG)

class Color(Enum):
	RED = 0
	YELLOW = 1
	GREEN = 2
	LEFT_YELLOW = 3
	LEFT_GREEN = 4

class TrafficGrid(nx.DiGraph):

	def __init__(self):
		super(TrafficGrid, self).__init__()
		self.cars = {}

	'''
	A light is a node in the directed graph. It stores two colors which rotate on a timer
	Each light has the following attributes:
		colors: The current colors for each road direction
		timer: The number of time steps between light switches
			If timer is less than zero, then this is not a light and is just an 'empty' point
			This is necessary as all edges/roads must have two endpoints
		counter: The current count of time steps before a switch
		weight: The expected volume/throughput/importance of this node
			At one point we discussed using building height as a proxy for number of
			cars through. This will mimic that behavior
			If a car is making a randomized choice of direction, it will be weighted
			by this value.
	
	Each road specifies which "colors" entry controls its flow

	'''
	def add_light(self, idx, colors=[Color.GREEN, Color.RED], timer=5, weight=1.):
		self.add_node(idx, colors=colors, timer=timer, counter=0, weight=weight)

		#timer = -1 means always green
		if timer == -1:
			self.nodes[idx]['colors'] = [Color.GREEN, Color.GREEN]
	
	'''
	A road is an edge in the directed graph. It has the following attributes:
		length: The length of the road
		maxspeed: The speed limit of the road in units/time step
		lanes: The number of lanes the road has
		car: a list of cars located on that edge
		light_idx: The "colors" index that controls its flow
		l0:	The outgoing index for this road in the light it leaves from
		l1: The incoming index for this road in the light it goes to
	'''
	def add_road(self, idx0, idx1, light_idx, length=1, maxspeed=1, lanes=1):
		if idx0 not in self.nodes:
			logger.error('Light %d is not in the grid!')
			raise ValueError
		if idx1 not in self.nodes:
			logger.error('Light %d is not in the grid!')
			raise ValueError
		if light_idx < 0 or light_idx >= len(self.nodes[idx1]['colors']):
			logger.error('Invalid light index %d for road (%d, %d). Maximum value: %d' 
				% (light_idx, idx0, idx1, len(self.nodes[idx1]['colors'])-1))
			raise ValueError

		self.add_edge(idx0, idx1, length=length, maxspeed=maxspeed, 
						light_idx=light_idx, lanes=lanes, cars=[])
		self.edges[idx0, idx1][0] = idx0
		self.edges[idx0, idx1][1] = idx1

	'''
	A car is an entry in the cars dictionary. It has the following attributes:
		edge: The edge the car is on
		position: The position along the edge
		speed: The car's speed
		radius: The car's radius (cars have finite size)
		accel: The car's MAXIMUM acceleration
		color: The color to draw the car for visualizing
		path: A list of nodes for the car to go to
		min_length: The minimum random path length
	'''
	def add_car(self, idx0, **kwargs):
		index = kwargs.get('index', len(self.cars))
		#Cannot doubly add a car
		if 'index' in kwargs and index in self.cars:
			logger.error('Car %d has already been added!' % index)
			raise KeyError
		#Find next available index
		while index in self.cars:
			index += 1

		self.cars[index] = {}

		if 'path' in kwargs:
			self.cars[index]['path'] = tuple(kwargs['path'])
		else:
			initial_path = [idx0]
			min_length = kwargs.get('min_path_length', 3)
			if 'idx1' in kwargs:
				initial_path.append(kwargs['idx1'])
			self.cars[index]['path'] = self.generate_next_move(
				initial_path, min_length=min_length)

		self.cars[index]['edge'] = self.cars[index]['path'][:2]
		self.cars[index]['path_idx'] = 1
		self.cars[index]['position'] = min(kwargs.get('position', 0.),
			self.edges[self.cars[index]['edge']]['length'])
		self.cars[index]['speed'] = min(kwargs.get('speed', 0.), 
			self.edges[self.cars[index]['edge']]['maxspeed'])
		self.cars[index]['radius'] = kwargs.get('radius', 0.5)
		self.cars[index]['accel'] = kwargs.get('accel', 1.)
		self.cars[index]['lane'] = kwargs.get('lane', 0.)
		self.cars[index]['color'] = kwargs.get('color', 'blue')
		self.cars[index]['trip_report'] = {self.cars[index]['edge']: {
			'time': 1., 
			'avg_speed': self.cars[index]['speed'],
			'time_stopped': 1 if self.cars[index]['speed'] == 0 else 0
		}}
		
		logger.info('Car %d - Planned Path: %s' % (index, str(self.cars[index]['path'])))

		self.edges[self.cars[index]['edge']]['cars'].append(index)

	'''
	Get the average speed of cars on a given edge
	'''
	def get_average_speed(self, edge):
		if len(self.edges[edge]['cars']) == 0:
			return 0
		return np.mean([self.cars[car]['speed'] for car in self.edges[edge]['cars']])

	'''
	Randomly generate a path to follow for a car
	@param current_path The set of nodes already in the path
	@param min_length The minimum length of this path
	'''
	def generate_next_move(self, current_path, min_length=3):
		possible_edges = self.edges(current_path[-1])
		todelete = []
		total_weight = 0
		#Prune possible edges to allow only outgoing roads, and remove u-turns
		for rd in possible_edges:
			if rd[0] != current_path[-1]:
				todelete.append(rd)
				continue
			if len(current_path) > 1 and rd[1] == current_path[-2]:
				todelete.append(rd)
				continue
			total_weight += self.nodes[rd[1]]['weight']
		for rd in todelete:
			possible_edges.remove(rd)

		#A chance to just end the path if we have sufficient length
		if len(current_path) >= min_length:
			total_weight += 1

		rnd = randint(0, total_weight-1)
		current_weight = 0
		for rd in possible_edges:
			current_weight += self.nodes[rd[1]]['weight']
			#Probabilistically add next node to the path
			if rnd < current_weight:
				current_path.append(rd[1])
				return self.generate_next_move(current_path, min_length)

		#Base case, return current path
		return tuple(current_path)

	'''
	Get the light color for a car coming to an intersection from a given edge
	If the edge is coming in at direction i, the light color is colors[i%2]
	'''
	def get_light_color(self, edge):
		return self.nodes[edge[1]]['colors'][self.edges[edge]['light_idx']]

	'''
	Get the nearest agent between position x0 and x1 on a given edge
	@return Agent Index, Agent Type, Distance
	'''
	def get_nearest_agent(self, edge, x0, x1, car_idx):
		car = self.cars[car_idx]
		#Check first for nearest car on the same road
		for i in self.edges[edge]['cars']:
			if i == car_idx:
				continue
			car2 = self.cars[i]
			if car2['edge'][0] == edge[0] and car2['edge'][1] == edge[1]:
				if car2['position'] > x0 and car2['position'] <= x1 and car2['lane'] == car['lane']:
					return i, 0, car2['position']-car2['radius']-x0
		
		#Otherwise, Check the light at the end of this road
		if x1 >= self.edges[edge]['length']:
			#Stop at the light if it is red
			color = self.get_light_color(edge)
			if color == Color.RED or color == Color.YELLOW:
				return edge[1], 1, self.edges[edge]['length']-x0
			
			#Otherwise, look ahead to the next road in the car's path
			next_idx = car['path_idx']+1
			if next_idx < len(car['path']):
				next_road = car['path'][next_idx-1:next_idx+1]
				return self.get_nearest_agent(next_road, 0, x1-self.edges[edge]['length'], car_idx)

		return None, None, -1

	'''
	Get the nearest agent ahead of a given car (either a red light or another car)
	The maximum number of units to look ahead is decided by the stopping distance, calculated
	using the maximum possible speed attainable during this time step
	'''
	def get_agent_ahead(self, car_idx):
		car = self.cars[car_idx]
		maxspeed = min(car['speed'] + car['accel'], self.edges[car['edge']]['maxspeed'])
		lookahead = maxspeed + maxspeed*maxspeed / 2. / car['accel']
		front_bumper = car['position'] + car['radius']
		return self.get_nearest_agent(car['edge'], front_bumper, front_bumper+lookahead, car_idx)

	'''
	Have a car act, update it's position/speed, and enter a new road if necessary
	'''
	def act_car(self, car_idx):
		car = self.cars[car_idx]
		road = self.edges[car['edge']]

		#Handle being at the end of the road
		if car['newpos'] > road['length']:
			#Update trip report
			car['trip_report'][car['edge']]['avg_speed'] /= car['trip_report'][car['edge']]['time']

			car['newpos'] -= road['length']
			light = self.nodes[car['edge'][1]]

			#Change the car's edge, and move the car onto the new edge
			next_idx = car['path_idx']+1
			if next_idx < len(car['path']):
				newedge = car['path'][next_idx-1:next_idx+1]
				car['path_idx'] += 1
				self.edges[car['edge']]['cars'].remove(car_idx)
				self.edges[newedge]['cars'].append(car_idx)
				car['edge'] = newedge
				return self.act_car(car_idx)

			#Otherwise, we've reached the end of the car's path, delete ourselves
			return None

		car['position'] = car['newpos']
		car['speed'] = min(car['newvel'], road['maxspeed'])

		#Update trip report
		if car['edge'] in car['trip_report']:
			car['trip_report'][car['edge']]['time'] += 1.
			car['trip_report'][car['edge']]['avg_speed'] += car['speed']
			if car['speed'] == 0:
				car['trip_report'][car['edge']]['time_stopped'] += 1
		else:
			car['trip_report'][car['edge']] = {
				'time': 1.,
				'avg_speed': car['speed'],
				'time_stopped': 1 if car['speed'] == 0 else 0.
			}

		return 0

	'''
	Determine the new speed/position for a given car after one time step
	The new speed/position is calculated by finding the acceleration of the car,
	based on the nearest agent in front of it. A car interacts with another car
	via a Lennard-Jones potential, while a car will always stop at a red light
	'''
	def update_car(self, car_idx):
		car = self.cars[car_idx]

		#Start at the maximum possible acceleration for the given road
		accel = self.edges[car['edge']]['maxspeed'] - car['speed']
		
		agent, agent_type, dist = self.get_agent_ahead(car_idx)
		if agent_type == 0:	#type 0 is a car
			car2 = self.cars[agent]
			#Lennard Jones acceleration
			rmin = car['speed'] * car['speed'] / (2 * car['accel']) + car['speed']
			if dist == 0:
				accel = -car['accel']
			else:
				accel = np.power(rmin, 6) / np.power(dist, 7) - np.power(rmin, 12) / np.power(dist, 13)
			
			logger.debug('Car %d - Car %d: %g Optimal Dist: %g Accel: %g' % (car_idx, agent, dist, rmin, accel))
		elif agent_type == 1:	#type 1 is a light
			logger.debug('Car %d - Light %d: %g' % (car_idx, agent, dist))
			color = self.get_light_color(car['edge'])
			#If light is yellow, only slow down if we can stop in front of the light
			if color == Color.YELLOW and dist != 0:
				tmp_accel = car['speed'] * car['speed'] / (2 * dist)
				if tmp_accel <= car['accel']:
					accel = -tmp_accel
			#If light is red, stop in front of the light
			if color == Color.RED:
				if dist == 0:
					accel = 0
				else:
					accel = -car['speed'] * car['speed'] / (2 * dist)

		#Acceleration is capped by car's parameters
		accel = min(accel, car['accel']) if accel >= 0 else max(accel, -car['accel'])
		#accel = min(accel, car['accel']) #NOTE: Allow braking to be arbitrarily fast

		#Find new position and speed after one time step. Don't allow reversing
		car['newpos'] = max(car['position'] + car['speed'] + 0.5 * accel, car['position'])
		car['newvel'] = max(car['speed'] + accel, 0)

	'''
	Update a light. Increment the counter and switch from red to green if necessary
	'''
	def update_light(self, idx):
		light = self.nodes[idx]	
		if light['timer'] < 0:
			return
		light['counter'] += 1
		if light['counter'] == light['timer']:
			for i in range(len(light['colors'])):
				if light['colors'][i] == Color.GREEN:
					light['colors'][i] = Color.YELLOW
			light['counter'] = -1
		elif light['counter'] == 0:
			for i in range(len(light['colors'])):
				if light['colors'][i] == Color.YELLOW:
					light['colors'][i] = Color.RED
				elif light['colors'][i] == Color.RED:
					light['colors'][i] = Color.GREEN

	'''
	Update all cars and lights

	Note: car update was split into two steps. Otherwise, there might be propagation errors, as
	a car might be calculating its new position based on a car ahead of its position at the next
	time step
	'''
	def update(self):
		#First, have cars determine their new positions/velocities
		for i in self.cars:
			self.update_car(i)

		#Next, actually update all of the positions/velocities
		todelete = []
		for i in self.cars:
			val = self.act_car(i)
			if val is None:
				todelete.append(i)

		#Delete cars as necessary
		for i in todelete:
			self.edges[self.cars[i]['edge']]['cars'].remove(i)
			self.print_trip_report(i)
			del self.cars[i]

		#Update all lights
		for i in self.nodes:
			self.update_light(i)
			light = self.nodes[i]
	
	'''
	Print the trip report of a car before deleting it
	'''
	def print_trip_report(self, idx):
		total_time = 0.
		avg_speed = 0.
		total_stopped = 0.

		logger.info('Trip Report for Car %d' % idx)
		report = self.cars[idx]['trip_report']
		for rd in report:
			total_time += report[rd]['time']
			avg_speed += report[rd]['time'] * report[rd]['avg_speed']
			total_stopped += report[rd]['time_stopped']
			logger.info('\tRoad (%d, %d) - Time: %g Avg. Speed: %g Stopped: %g' % 
				(rd[0], rd[1], report[rd]['time'], report[rd]['avg_speed'], report[rd]['time_stopped']))
		logger.info('\tTotal - Time: %g Avg. Speed; %g Stopped %g' % (total_time, avg_speed, total_stopped))

	'''
	Print the status of each car/light
	'''
	def print_status(self):
		for node in self.nodes:
			if self.nodes[node]['timer'] < 0:
				continue
			outstr = 'Light %d\t' % node
			outstr += 'Colors: %s' % self.nodes[node]['colors']
			logger.info(outstr)
		for road in self.edges:
			if len(self.edges[road]['cars']) == 0:
				continue
			logger.info('On Road %s\tAverage Speed: %g' % (str(road), self.get_average_speed(road)))
			for i in self.edges[road]['cars']:
				car = self.cars[i]
				outstr = '\tCar %d\t' % i
				outstr += 'Lane: %d\t' % car['lane']
				outstr += 'Pos: %g\t' % car['position']
				outstr += 'Vel: %g' % car['speed']
				logger.info(outstr)

'''
GridDrawer is a way to visualize a Traffic grid and all cars on that grid
It is a simple extension of the matplotlib drawing module in NetworkX
'''
class GridDrawer:
	
	def __init__(self, grid):
		self.grid = grid
		self.ax = plt.gca()
		self.layout = None
		self.edge_info = {}

	'''
	Draw lights to include both light colors
	'''
	def draw_lights(self):
		nodelist = list(self.grid)
		if not nodelist or len(nodelist) == 0:
			return None

		node_size=300
		for light in nodelist:
			xy = self.layout[light]
			for i, color in enumerate(self.grid.nodes[light]['colors']):
				marker = mpl.markers.MarkerStyle(marker='o', fillstyle='left' if i == 0 else 'right')
				if color == Color.GREEN:
					mk = self.ax.scatter(xy[0], xy[1], s=node_size, c='green', marker=marker)
				elif color == Color.YELLOW:
					mk = self.ax.scatter(xy[0], xy[1], s=node_size, c='yellow', marker=marker)
				elif color == Color.RED:
					mk = self.ax.scatter(xy[0], xy[1], s=node_size, c='red', marker=marker)
				mk.set_zorder(2)	#Put lights in front of edges

	'''
	Draw cars on each road
	'''
	def draw_cars(self):
		#Need to find positions of each car on the self.grid
		car_width = 0.2
		for edge in self.grid.edges:
			edge_info = self.edge_info[edge]
			for i in self.grid.edges[edge]['cars']:
				car = self.grid.cars[i]
				edge_info = self.edge_info[car['edge']]
				center = self.layout[car['edge'][0]] + car['position'] * edge_info['vect']
				center += edge_info['perp'] * (car_width * car['lane'] + 0.5 * car_width)
				wh = np.array([car['radius'] * 2, car_width]) * edge_info['leng']
				bottom_left = center - 0.5 * wh
				self.ax.add_patch(mpl.patches.Rectangle(
					bottom_left,
					wh[0],
					wh[1],
					zorder=3,
					angle=edge_info['angle'],
					facecolor=car['color'],
					edgecolor='black'))

	'''
	Generate the layout and calculate direction information about each edge
	This way, we don't have to recalculate things at each time step
	'''
	def generate_layout(self):
		#self.layout = nx.drawing.self.layout.planar_layout(self.grid)
		#self.layout = nx.drawing.spring_layout(self.grid)
		self.layout = nx.spectral_layout(self.grid, weight='length')
	
		self.edge_info = {}
		for edge in self.grid.edges:
			self.edge_info[edge] = {}
			pos0, pos1 = self.layout[edge[0]], self.layout[edge[1]]
			self.edge_info[edge]['vect'] = (pos1 - pos0) / self.grid.edges[edge]['length']
			self.edge_info[edge]['leng'] = np.linalg.norm(self.edge_info[edge]['vect'])
			self.edge_info[edge]['perp'] = np.array(
				[self.edge_info[edge]['vect'][1], -self.edge_info[edge]['vect'][0]])
			self.edge_info[edge]['angle'] = np.degrees(np.arctan2(
				self.edge_info[edge]['vect'][1], self.edge_info[edge]['vect'][0]))

	'''
	Draw the state of the traffic grid at a certain time step
	'''
	def draw(self):
		self.ax.clear()
		self.ax.set_axis_off()

		if self.layout is None:
			self.generate_layout()
		
		nx.draw_networkx_edges(self.grid, self.layout, arrows=True)
		self.draw_lights()
		self.draw_cars()
		nx.draw_networkx_labels(self.grid, self.layout)

#Simulate basic one way road with a light
if __name__=='__main__':
	grid = TrafficGrid()

	grid.add_light(0, timer=-1)
	grid.add_light(1, colors=[Color.RED, Color.GREEN], timer=10)
	grid.add_light(2, timer=-1)

	grid.add_road(0, 1, 0, length=20, maxspeed=5, lanes=2)
	grid.add_road(1, 2, 0, length=20, maxspeed=5, lanes=2)

	
	grid.add_car(0, idx1=1, speed=1.)
	grid.add_car(0, idx1=1, speed=1., position=1.5)
	grid.add_car(0, idx1=1, speed=1., position=3.)
	grid.add_car(0, idx1=1, speed=1., position=4.5)
	grid.add_car(0, idx1=1, speed=1., position=6.)
	grid.add_car(0, idx1=1, lane=1)

	drawer = GridDrawer(grid=grid)
	drawer.draw()
	grid.print_status()

	for t in range(25):
		grid.update()
		grid.print_status()
		drawer.draw()
		plt.pause(0.2)
	
	plt.show()
