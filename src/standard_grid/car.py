'''
Jonathan Colen
jcolen@uchicago.edu

car.py

A Car is an agent in our traffic network. Cars will be modeled as circles which
travel at a given direction with a given speed

This will eventually have to be updated in order for cars to keep track of their paths
'''

from light import Light, Color
from road import Road
from random import randint

class Car:
	'''
	@param road - The road the car is on
	@param position - The position of the car along the road
	@param speed - the speed of the car along the road in (units/step)
	@param radius - The size of the car
	@param accel - The acceleration of the car, in units/step^2
	'''
	def __init__(self, road, position=0., speed=0., radius=1., accel=1.):
		self.road = road
		
		self.position = position
		self.speed = speed
		self.radius = radius
		self.accel = accel
	
	def update(self, newpos, newvel):
		#print('Attempting to update: Pos %g Vel %g' % (newpos, newvel))
		#Check whether we need to move to a new road
		if newpos > self.road.length:
			newpos -= self.road.length
			light = self.road.lights[1]
			#Delete ourselves if we are off the grid
			if light is None or light.timer < 0:
				return None
			allowed = light.get_allowed_roads(self.road)
			#Delete ourselves, since this is a bug in the system
			if len(allowed) == 0:
				print('At an intersection with no options')
				return None
			self.road = allowed[randint(0, len(allowed)-1)]
			
			#Recur to the next road
			return self.update(newpos, newvel)

		self.position = newpos
		self.speed = newvel
		return 0

	'''
	A car acts by looking ahead and responding to what it sees
	How this works:
		A car moving at a given speed must look ahead a set number of units
		If the car sees a RED light - it immediately slows down
		If the car sees another car - it accelerates in order to match that car's speed in one step,
			or at the car's 'accel' parameter, whichever is smaller
		If the car reaches the end of a road:
			Eventually the car will have a route to follow
			For now, assume all cars will continue straight or turn right if straight is not an option
			Transition to the next allowed road in the light
		@return None if the car needs to be deleted
	'''
	def act(self):
		#The number of units to look ahead is decided by the stopping distance
		front_bumper = self.position + self.radius
		lookahead = self.speed + self.speed * self.speed / 2. / self.accel

		#Start at the maximum possible acceleration for the car and the given road
		accel = min(self.accel, self.road.maxspeed - self.speed)

		agents = self.road.get_agents(front_bumper, front_bumper + lookahead)
		for agent in agents:
			if isinstance(agent, Car):
				#accelerate to match that car's speed
				accel = min(accel, agent.speed - self.speed)
			if isinstance(agent, Light):
				if agent.get_light_color(self.road) == Color.RED:
					accel = -min(self.accel, self.speed)	#Set to maximum possible deceleration

		#Now, find the new position and new speed after one time step
		newpos = self.position + self.speed + 0.5 * accel
		newvel = self.speed + accel

		return self.update(newpos, newvel)

