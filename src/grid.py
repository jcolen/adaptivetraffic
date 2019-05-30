'''
Jonathan Colen
jcolen@uchicago.edu

grid.py

Grid stores the network of traffic lights and cars and allows them to act accordingly
'''
from road import Road
from light import Light, Color
from car import Car

class Grid:

	def __init__(self):
		self.cars = []
		self.lights = []
		self.roads = []
	
	'''
	Check that all lights have at least two connected roads and all roads have at least
	one connected light.
	'''
	def validate_grid(self):
		for light in self.lights:
			if sum(x is not None for x in light.roads) < 2:
				return False
		for road in self.roads:
			if sum(x is not None for x in road.lights) < 1:
				return False
		return True

	'''
	Update the grid by one time step, given the current state of lights and roads
	The update process looks like:
	'''
	def update(self):
		for car in self.cars:
			car.act()
		for light in self.lights:
			light.act()

	def print_status(self):
		for i, car in enumerate(self.cars):
			outstr = 'Car %d:\t' % i
			try:
				ind = self.roads.index(car.road)
				outstr += 'On Road %d\t' % ind
			except:
				outstr = 'Road undefined\t'
			outstr += 'Dir: %d\t' % car.direction
			outstr += 'Pos: %g\t' % car.position
			outstr += 'Vel: %g\t' % car.speed
			print(outstr)

if __name__ == '__main__':
	grid = Grid()

	#TODO implement loading from text

	#Construct 3 roads, connected by two lights, in a straight line
	grid.roads.append(Road(length=5, maxspeed=2, oneway=0))
	grid.roads.append(Road(length=10, maxspeed=2, oneway=0))
	grid.roads.append(Road(length=5, maxspeed=2, oneway=0))

	grid.lights.append(Light(timer=5))
	grid.lights.append(Light(timer=5))

	#Connect roads to lights
	grid.roads[0].lights[1] = grid.lights[0]
	grid.roads[1].lights[0] = grid.lights[0]
	grid.roads[1].lights[1] = grid.lights[1]
	grid.roads[2].lights[0] = grid.lights[1]

	#Connect lights to roads
	grid.lights[0].roads[0] = grid.roads[0]
	grid.lights[0].roads[2] = grid.roads[1]
	grid.lights[1].roads[0] = grid.roads[1]
	grid.lights[1].roads[2] = grid.roads[2]

	print(grid.validate_grid())

	#Now add cars
	grid.cars.append(Car(grid.roads[0], 1))
	grid.cars.append(Car(grid.roads[2], 0))
	grid.print_status()

	grid.lights[0].color[0] = Color.GREEN
	grid.lights[1].color[0] = Color.GREEN

	#Now see what happens
	for t in range(5):
		grid.update()
		grid.print_status()
