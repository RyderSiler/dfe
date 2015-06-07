from pygame import *
from func import *
from Character import *
from Room import *
from Bomb import *
from time import time as cTime
import random

class Game:
	floor = {}
	floorIndex = 0
	currentRoom = (0,0)
	animatingRooms = []
	def __init__(self, characterType, seed):
		self.surface = surface
		self.characterType = characterType
		self.seed = seed

		random.seed(self.seed)

	def setup(self):
		floor = loadFloor("basement.xml", self.floorIndex, randint(8, 12), self.sounds, self.textures)
		adjecent = [-1,0], [0, 1], [1, 0], [0, -1]
		doorPoss = [[13, 3], [6,7], [-1,3], [6,-1]]

		for coord in floor:
			for i in range(len(adjecent)):
				diffX = adjecent[i][0]
				diffY = adjecent[i][1]

				coordX = coord[0]
				coordY = coord[1]

				try:
					room = floor[(diffX + coordX, diffY + coordY)]
					if room.variant != 0:
						room.addDoor(doorPoss[i], room.variant, True)
					else:
						room.addDoor(doorPoss[i], floor[coord].variant, True)
				except:
					pass

		self.floor = floor

	def updateMinimap(self, currentRoom):
		self.minimap.fill((0,0,0,0))
		self.minimap.blit(self.textures["map"]["background"], (0, 0))
		for room in self.floor:
			self.floor[room].renderMap(self.minimap, currentRoom, False)
		for room in self.floor:
			self.floor[room].renderMap(self.minimap, currentRoom, True)

	def run(self, screen, sounds, textures, fonts, joystick=None):
		animatingRooms = self.animatingRooms
		currentRoom = self.currentRoom

		self.sounds = sounds
		self.textures = textures
		self.setup()

		floor = self.floor
		floorIndex = self.floorIndex
		clock = time.Clock()

		self.minimap = Surface((textures["map"]["background"].get_width(), textures["map"]["background"].get_height())).convert_alpha()
		self.updateMinimap(currentRoom)
		self.minimap.set_clip(Rect(4, 4, 100, 86))
		mWidth = self.minimap.get_width()
		mHeight = self.minimap.get_height()
		
		posMoves = [[1, 0], [0, 1], [-1, 0], [0, -1]]
		self.isaac = isaac = Character(self.characterType, (WIDTH//2, (HEIGHT//4)*3), [[115, 100, 119, 97], [274, 275, 273, 276]], textures, sounds, fonts)

		floor[currentRoom].entered = True

		for m in posMoves:
			mx, my = m
			x, y = currentRoom
			newPos = (mx+x, my+y)

			try:
				floor[newPos].seen = True
			except:
				pass


		self.updateMinimap(currentRoom)

		running = True
		while running:

			currTime = cTime()
			k = key.get_pressed() # Current down keys

			for e in event.get():
				if e.type == QUIT or k[K_ESCAPE]: 
					running = False

				elif e.type == KEYDOWN:
					isaac.moving(e.key, True, False)
					if e.unicode == "p":
						isaac.hurt(1, currTime)
					elif e.unicode == "e":
						if isaac.pickups[1].use(1):
							floor[currentRoom].other.append(Bomb(floor[currentRoom], 0, ((isaac.x-GRIDX)/GRATIO, (isaac.y-GRIDY)/GRATIO), [sounds["explosion"]], textures["bombs"], explode=True))
					elif e.unicode == "t":
						isaac.pickups[1].add(3)
					elif e.unicode == "h":
						isaac.hurt(1, 0, 0, currTime)
					elif e.unicode == "m":
						print(self.seed)

				elif e.type == KEYUP:
					isaac.moving(e.key, False, False)

			if len(animatingRooms) > 0:
				for r in animatingRooms[:]:
					r.render(screen, isaac, currTime)
					if not r.animating:
						animatingRooms.remove(r)
			else:
				screen.fill((0,0,0))
				move = floor[currentRoom].render(screen, isaac, currTime)
				if move[0] != 0 or move[1] != 0:
					old = tuple(currentRoom[:])

					currentRoom = (move[0]+currentRoom[0], move[1]+currentRoom[1])
					try:
						floor[currentRoom].animateIn(move)
						floor[old].animateOut(move)

						animatingRooms.append(floor[currentRoom])
						animatingRooms.append(floor[old])

						isaac.x += 650*(-move[0])
						isaac.y += 338*(move[1])

						isaac.clearTears()

						floor[currentRoom].entered = True

						for m in posMoves:
							mx, my = m
							x, y = currentRoom
							newPos = (mx+x, my+y)

							try:
								floor[newPos].seen = True
							except:
								pass

						self.updateMinimap(currentRoom)

					except:
						currentRoom = old

			# DRAW MAP
			screen.blit(self.minimap, (MAPX-mWidth//2, MAPY-mHeight//2))

			if joystick != None:
				joystick.update()

			if isaac.dead:
				running = False

			display.flip()
			clock.tick(60)