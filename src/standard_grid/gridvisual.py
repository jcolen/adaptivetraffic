'''
Jonathan Colen
jcolen@uchicago.edu

gridvisual.py

Tkinter Visualization of traffic grids
'''

import Tkinter
from light import Color

class GridVisual:
	def __init__(self, grid, xmax, ymax):
		self.grid = grid
		self.xmax, self.ymax = xmax, ymax

		self.window = Tkinter.Tk()
		self.canvas = Tkinter.Canvas(self.window, bg='white', height=300, width=300)
		
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
			if light.timer < 0:
				self.canvas.create_oval(x-10, y-10, x+10, y+10, fill='gray')
				continue
			for i, c in enumerate(light.colors):
				if c == Color.RED:
					self.canvas.create_oval(x-i*10, y-5, x-i*10+10, y+5, fill='red')
				elif c == Color.GREEN:
					self.canvas.create_oval(x-i*10, y-5, x-i*10+10, y+5, fill='green')

		for road in self.grid.roads:
			x0 = road.lights[0].x * x_conversion_factor
			y0 = road.lights[0].y * y_conversion_factor
			x1 = road.lights[1].x * x_conversion_factor
			y1 = road.lights[1].y * y_conversion_factor
			self.canvas.create_line(x0, y0, x1, y1, arrow=Tkinter.LAST)
		
		for car in self.grid.cars:
			x = (car.road.lights[1].x - car.road.lights[0].x) * car.position / car.road.length + car.road.lights[0].x
			y = (car.road.lights[1].y - car.road.lights[0].y) * car.position / car.road.length + car.road.lights[0].y
			x *= x_conversion_factor
			y *= y_conversion_factor
			self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="black")
		self.canvas.update()
