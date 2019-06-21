'''
Jonathan Colen
jcolen@uchicago.edu

grid.py

Grid stores the network of traffic lights and cars and allows them to act accordingly
'''
from road import Road
from light import Light, Color
from car import Car
from gridvisual import GridVisual

import csv
import time

class Grid:

	def __init__(self):
		self.cars = []
		self.lights = []
		self.roads = []

	def load_from_csv(self, light_file, road_file):
		with open(light_file, 'r') as infile:
			reader = csv.reader(infile)
			for i, row in enumerate(reader):
				if i == 0:
					continue
				self.lights.append(Light(timer=int(row[1]),	pos=[int(row[2]), int(row[3])]))
		with open(road_file, 'r') as infile:
			reader = csv.reader(infile)
			for i, row in enumerate(reader):
				if i == 0:
					continue
				self.roads.append(Road(length=int(row[1]), maxspeed=int(row[2])))
				self.roads[-1].lights[0] = self.lights[int(row[3])]
				self.roads[-1].lights[1] = self.lights[int(row[4])]
		with open(light_file, 'r') as infile:
			reader = csv.reader(infile)
			for i, row in enumerate(reader):
				if i == 0:
					continue
				for i, rd in enumerate(row[4:]):
					if not rd == '':
						self.lights[int(row[0])].roads[i] = self.roads[int(rd)]

	'''
	Update the grid by one time step, given the current state of lights and roads
	The update process looks like:
	'''
	def update(self):
		todelete = []
		for i, car in enumerate(self.cars):
			val = car.act()
			if val is None:
				todelete.append(i)

		for index in sorted(todelete, reverse=True):
			del self.cars[index]

		for light in self.lights:
			if light.timer >= 0:
				light.act()

	def print_status(self):
		for i, car in enumerate(self.cars):
			outstr = 'Car %d:\t' % i
			try:
				ind = self.roads.index(car.road)
				outstr += 'On Road %d\t' % ind
			except:
				outstr = 'Road undefined\t'
			outstr += 'Pos: %g\t' % car.position
			outstr += 'Vel: %g\t' % car.speed
			print(outstr)


if __name__ == '__main__':
	grid = Grid()

	grid.load_from_csv('grid1_lights.csv', 'grid1_roads.csv')

	#Now add cars
	grid.cars.append(Car(grid.roads[1]))
	grid.cars.append(Car(grid.roads[8]))
	grid.print_status()

	grid.lights[3].colors[0] = Color.GREEN
	grid.lights[4].colors[0] = Color.GREEN

	vis = GridVisual(grid, 20, 25)

	#Now see what happens
	for t in range(10):
		time.sleep(0.5)
		grid.update()
		grid.print_status()
		vis.update()
	
	vis.window.mainloop()
