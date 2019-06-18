'''
Jonathan Colen
jcolen@uchicago.edu

grid.py

Grid stores the network of traffic lights and cars and allows them to act accordingly
'''
from road import Road
from light import Light, Color
from car import Car

import Tkinter
import time 

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
			outstr += 'Pos: %g\t' % car.position
			outstr += 'Vel: %g\t' % car.speed
			print(outstr)

class GridVisual:
	def __init__(self, grid, xmax, ymax):
		self.grid = grid
		self.xmax, self.ymax = xmax, ymax

		self.window = Tkinter.Tk()
		self.canvas = Tkinter.Canvas(self.window, bg='white', height=300, width=300)
		print(self.canvas.winfo_width())
		print(self.canvas.winfo_height())
		
		self.canvas.pack(fill=Tkinter.BOTH, expand=Tkinter.YES)
		self.canvas.update()

		self.update()

	
	def update(self):
		self.canvas.delete('all')

		x_conversion_factor = self.canvas.winfo_width() / float(self.xmax)
		y_conversion_factor = self.canvas.winfo_height() / float(self.ymax)

		for light in self.grid.lights:
			#First, calculate coordinates
			x = light.x * x_conversion_factor
			y = light.y * y_conversion_factor
			for i, c in enumerate(light.color):
				if c == Color.RED:
					self.canvas.create_oval(x-i*10, y-5, x-i*10+10, y+5, fill='red')
				elif c == Color.GREEN:
					self.canvas.create_oval(x-i*10, y-5, x-i*10+10, y+5, fill='green')

		for road in self.grid.roads:
			x0 = road.x0 * x_conversion_factor
			y0 = road.y0 * y_conversion_factor
			x1 = road.x1 * x_conversion_factor
			y1 = road.y1 * y_conversion_factor
			self.canvas.create_line(x0, y0, x1, y1, arrow=Tkinter.LAST)
		
		for car in self.grid.cars:
			x = (car.road.x1 - car.road.x0) * car.position / car.road.length + car.road.x0
			y = (car.road.y1 - car.road.y0) * car.position / car.road.length + car.road.y0
			x *= x_conversion_factor
			y *= y_conversion_factor
			self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="black")
		self.canvas.update()

if __name__ == '__main__':
	grid = Grid()

	#TODO implement loading from text

	#Construct 3 roads, connected by two lights, in a straight line
	grid.lights.append(Light(timer=5, pos=[10, 5]))
	grid.lights.append(Light(timer=5, pos=[10, 15]))
	
	grid.roads.append(Road(length=5, maxspeed=2, pos0=[10, 0], pos1=[10, 5]))
	grid.roads.append(Road(length=5, maxspeed=2, pos0=[10, 5], pos1=[10, 0]))
	grid.roads.append(Road(length=10, maxspeed=2, pos0=[10, 5], pos1=[10, 15]))
	grid.roads.append(Road(length=10, maxspeed=2, pos0=[10, 15], pos1=[10, 5]))
	grid.roads.append(Road(length=5, maxspeed=2, pos0=[10, 15], pos1=[10, 20]))
	grid.roads.append(Road(length=5, maxspeed=2, pos0=[10, 20], pos1=[10, 15]))

	#Connect roads to lights
	grid.roads[0].lights[1] = grid.lights[0]
	grid.roads[1].lights[0] = grid.lights[0]
	
	grid.roads[2].lights[0] = grid.lights[0]
	grid.roads[2].lights[1] = grid.lights[1]
	grid.roads[3].lights[0] = grid.lights[1]
	grid.roads[3].lights[1] = grid.lights[0]
	
	grid.roads[4].lights[0] = grid.lights[1]
	grid.roads[5].lights[1] = grid.lights[1]

	#Connect lights to roads
	grid.lights[0].roads[0] = grid.roads[0]
	grid.lights[0].roads[2] = grid.roads[3]
	grid.lights[0].roads[4] = grid.roads[1]
	grid.lights[0].roads[6] = grid.roads[2]
	grid.lights[1].roads[0] = grid.roads[2]
	grid.lights[1].roads[2] = grid.roads[5]
	grid.lights[1].roads[4] = grid.roads[3]
	grid.lights[1].roads[6] = grid.roads[4]

	print(grid.validate_grid())

	#Now add cars
	grid.cars.append(Car(grid.roads[0]))
	grid.cars.append(Car(grid.roads[5]))
	grid.print_status()

	grid.lights[0].color[0] = Color.GREEN
	grid.lights[1].color[0] = Color.GREEN

	vis = GridVisual(grid, 20, 20)

	#Now see what happens
	for t in range(10):
		time.sleep(0.5)
		grid.update()
		grid.print_status()
		vis.update()
	
	vis.window.mainloop()
