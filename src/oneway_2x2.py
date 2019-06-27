from grid_networkx import TrafficGrid, GridDrawer, Color, logger
import matplotlib.pyplot as plt

logger.setLevel('INFO')

#Simulate a 2x2 grid of lights in a one-way pattern
if __name__=='__main__':
	grid = TrafficGrid()

	#Row 0
	grid.add_light(0, timer=-1)
	grid.add_light(1, timer=-1)
	
	#Row 1
	grid.add_light(2, timer=-1)
	grid.add_light(3, colors=[Color.GREEN, Color.RED], timer=5)
	grid.add_light(4, colors=[Color.GREEN, Color.RED], timer=5)
	grid.add_light(5, timer=-1)
	
	#Row 2
	grid.add_light(6, timer=-1)
	grid.add_light(7, colors=[Color.GREEN, Color.RED], timer=5)
	grid.add_light(8, colors=[Color.GREEN, Color.RED], timer=5)
	grid.add_light(9, timer=-1)

	#Row 3
	grid.add_light(10, timer=-1)
	grid.add_light(11, timer=-1)

	#Vertical roads
	grid.add_road(0, 3, 0, length=10, maxspeed=2)
	grid.add_road(3, 7, 0, length=10, maxspeed=2)
	grid.add_road(7, 10, 0, length=10, maxspeed=2)
	
	grid.add_road(11, 8, 0, length=10, maxspeed=2)
	grid.add_road(8, 4, 0, length=10, maxspeed=2)
	grid.add_road(4, 1, 0, length=10, maxspeed=2)

	#Horizontal Roads
	grid.add_road(2, 3, 1, length=10, maxspeed=2)
	grid.add_road(3, 4, 1, length=10, maxspeed=2)
	grid.add_road(4, 5, 1, length=10, maxspeed=2)

	grid.add_road(9, 8, 1, length=10, maxspeed=2)
	grid.add_road(8, 7, 1, length=10, maxspeed=2)
	grid.add_road(7, 6, 1, length=10, maxspeed=2)

	grid.add_car(0, 3)
	grid.add_car(3, 7)
	grid.add_car(2, 3)
	grid.add_car(3, 4)

	drawer = GridDrawer(grid=grid)
	drawer.draw()
	grid.print_status()

	for t in range(5):
		grid.update()
		grid.print_status()
		drawer.draw()
		plt.pause(0.5)

	plt.show()
