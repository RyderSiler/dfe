from pygame import *
from time import time as cTime
from random import randint
from math import *
from Explosion import *
from Animation import *

class Bomb:
	"""Droppable bomb class"""

	collideable = False
	pickedUp = False
	exploded = False
	fuse = 2

	def __init__(self, parent, variant, xy, sounds, textures, explode=False):
		self.variant = variant
		self.x = xy[0]
		self.y = xy[1]
		self.sounds = sounds
		self.textures = textures
		self.parent = parent

		self.bounds = Rect(GRIDX+GRATIO*self.x,GRIDY+GRATIO*self.y, 32, 64)

		self.shouldExplode = explode
		self.placed = cTime()

		self.anim = Animation([textures[0].subsurface(0,0,64,64)], .2)

	def explode(self, objects):
		self.exploded = True
		self.anim = Explosion(0, (self.x, self.y), self.sounds[0], self.textures[1])
		self.parent.backdrop.blit(self.textures[2].subsurface(192*randint(0,1), 128*randint(0,1), 192, 128), ((GRIDX + GRATIO*self.x) - 128, (GRIDY + GRATIO*self.y) - 32))
		for ob in objects:
			if sqrt((ob.x-self.x)**2 + (ob.y-self.y)**2) < 2:
				ob.destroy()

	def pickup(self):
		if not self.shouldExplode:
			self.pickedUp = True
			self.sounds[0].play()


	def render(self, surface, time, objects, ox=0, oy=0):
		if self.pickedUp:
			return False

		if not self.shouldExplode:
			surface.blit(self.anim.render(time), ((GRIDX + GRATIO*self.x) - self.anim.width//2+ox, (GRIDY + GRATIO*self.y) - self.anim.height//2+oy))
			return True

		if not self.exploded:
			frame = self.anim.render(time)
			surface.blit(frame, ((GRIDX + GRATIO*self.x) - self.anim.width//2+ox, (GRIDY + GRATIO*self.y) - self.anim.height//2+oy))

			if time-self.placed >= self.fuse:
				self.explode(objects)
			return True
		else:
			return self.anim.render(surface, time)

