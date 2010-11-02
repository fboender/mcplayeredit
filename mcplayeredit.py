#!/usr/bin/python

#
# Todo:
# - MCPlayerEditError errno's are not correct.
# - MacOSX windows support (tab completion)
# - give/kit will put items in armor slots even if they're not supposed to go there.
# - Watch level.dat for changes?

__NAME__    = 'MCPlayerEdit'
__AUTHOR__  = "Ferry Boender"
__VERSION__ = (0, 5)

import sys
if sys.version_info[:2] < (2, 6):
	sys.stderr.write('%s requires Python v2.6 or higher. :(\n' % (__NAME__))
	raise SystemExit()
import os
import shutil
import struct
import time
basepath = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])))
sys.path.insert(0, os.path.join(basepath, 'lib'))
import icmd
import nbt
sys.path.pop(0)

items = {
	0    : 'Air',
	1    : 'Stone',
	2    : 'Grass',
	3    : 'Dirt',
	4    : 'Cobblestone',
	5    : 'Wood',
	6    : 'Sapling',
	7    : 'Adminium',
	8    : 'Water',
	9    : 'Stationary water',
	10   : 'Lava',
	11   : 'Stationary lava',
	12   : 'Sand',
	13   : 'Gravel',
	14   : 'Gold ore',
	15   : 'Iron ore',
	16   : 'Coal ore',
	17   : 'Log',
	18   : 'Leaves',
	19   : 'Sponge',
	20   : 'Glass',
	21   : 'Red Cloth',
	22   : 'Orange Cloth',
	23   : 'Yellow Cloth',
	24   : 'Lime Cloth',
	25   : 'Green Cloth',
	26   : 'Aqua green Cloth',
	27   : 'Cyan Cloth',
	28   : 'Blue Cloth',
	29   : 'Purple Cloth',
	30   : 'Indigo Cloth',
	31   : 'Violet Cloth',
	32   : 'Magenta Cloth',
	33   : 'Pink Cloth',
	34   : 'Black Cloth',
	#35  : 'Gray Cloth / White Cloth',
	35   : 'Wool',
	36   : 'White Cloth',
	37   : 'Yellow flower',
	38   : 'Red rose',
	39   : 'Brown Mushroom',
	40   : 'Red Mushroom',
	41   : 'Gold Block',
	42   : 'Iron Block',
	43   : 'Double Step',
	44   : 'Step',
	45   : 'Brick',
	46   : 'TNT',
	47   : 'Bookcase',
	48   : 'Mossy Cobblestone',
	49   : 'Obsidian',
	50   : 'Torch',
	51   : 'Fire',
	52   : 'Mob Spawner',
	53   : 'Wooden Stairs',
	54   : 'Chest',
	55   : 'Redstone Wire',
	56   : 'Diamond Ore',
	57   : 'Diamond Block',
	58   : 'Workbench',
	59   : 'Crops',
	60   : 'Soil',
	61   : 'Furnace',
	62   : 'Burning Furnace',
	63   : 'Sign Post',
	64   : 'Wooden Door',
	65   : 'Ladder',
	66   : 'Minecart Tracks',
	67   : 'Cobblestone Stairs',
	68   : 'Wall Sign',
	69   : 'Lever',
	70   : 'Stone Pressure Plate',
	71   : 'Iron Door',
	72   : 'Wooden Pressure Plate',
	73   : 'Redstone Ore',
	74   : 'Glowing Redstone Ore',
	75   : 'Redstone torch Off',
	76   : 'Redstone torch On',
	77   : 'Stone Button',
	78   : 'Snow',
	79   : 'Ice',
	80   : 'Snow Block',
	81   : 'Cactus',
	82   : 'Clay',
	83   : 'Reed',
	84   : 'Jukebox',
	85   : 'Fence',
	86   : 'Pumpkin',
	87   : 'Bloodstone',
	88   : 'Slow Sand',
	89   : 'Lightstone',
	90   : 'Portal',
	91   : 'Jack-O-Lantern',
	256  : 'Iron Spade',
	257  : 'Iron Pickaxe',
	258  : 'Iron Axe',
	259  : 'Flint and Steel',
	260  : 'Apple',
	261  : 'Bow',
	262  : 'Arrow',
	263  : 'Coal',
	264  : 'Diamond',
	265  : 'Iron Ingot',
	266  : 'Gold Ingot',
	267  : 'Iron Sword',
	268  : 'Wooden Sword',
	269  : 'Wooden Spade',
	270  : 'Wooden Pickaxe',
	271  : 'Wooden Axe',
	272  : 'Stone Sword',
	273  : 'Stone Spade',
	274  : 'Stone Pickaxe',
	275  : 'Stone Axe',
	276  : 'Diamond Sword',
	277  : 'Diamond Spade',
	278  : 'Diamond Pickaxe',
	279  : 'Diamond Axe',
	280  : 'Stick',
	281  : 'Bowl',
	282  : 'Mushroom Soup',
	283  : 'Gold Sword',
	284  : 'Gold Spade',
	285  : 'Gold Pickaxe',
	286  : 'Gold Axe',
	287  : 'String',
	288  : 'Feather',
	289  : 'Gunpowder',
	290  : 'Wooden Hoe',
	291  : 'Stone Hoe',
	292  : 'Iron Hoe',
	293  : 'Diamond Hoe',
	294  : 'Gold Hoe',
	295  : 'Seeds',
	296  : 'Wheat',
	297  : 'Bread',
	298  : 'Leather Helmet',
	299  : 'Leather Chestplate',
	300  : 'Leather Pants',
	301  : 'Leather Boots',
	302  : 'Chainmail Helmet',
	303  : 'Chainmail Chestplate',
	304  : 'Chainmail Pants',
	305  : 'Chainmail Boots',
	306  : 'Iron Helmet',
	307  : 'Iron Chestplate',
	308  : 'Iron Pants',
	309  : 'Iron Boots',
	310  : 'Diamond Helmet',
	311  : 'Diamond Chestplate',
	312  : 'Diamond Pants',
	313  : 'Diamond Boots',
	314  : 'Gold Helmet',
	315  : 'Gold Chestplate',
	316  : 'Gold Pants',
	317  : 'Gold Boots',
	318  : 'Flint',
	319  : 'Pork',
	320  : 'Grilled Pork',
	321  : 'Paintings',
	322  : 'Golden apple',
	323  : 'Sign',
	324  : 'Wooden door',
	325  : 'Bucket',
	326  : 'Water bucket',
	327  : 'Lava bucket',
	328  : 'Mine cart',
	329  : 'Saddle',
	330  : 'Iron door',
	331  : 'Redstone',
	332  : 'Snowball',
	333  : 'Boat',
	334  : 'Leather',
	335  : 'Milk Bucket',
	336  : 'Clay Brick',
	337  : 'Clay Balls',
	338  : 'Reed',
	339  : 'Paper',
	340  : 'Book',
	341  : 'Slime Ball',
	342  : 'Storage Minecart',
	343  : 'Powered Minecart',
	344  : 'Egg',
	345  : 'Compass',
	346  : 'Fishing Rod',
	347  : 'Watch',
	348  : 'Gold Dust',
	349  : 'Raw Fish',
	350  : 'Cooked Fish',
	2256 : 'Gold Record',
	2257 : 'Green Record',
}

invmap = \
	[(x, 'quick') for x in range(0,9)] + \
	[(x, 'normal') for x in range(9, 36)] + \
	[(x, 'armor') for x in range(100, 104)]

kits = {
	'Diamond Miner': ( (1, 279), (1, 278), (1, 277), (1, 293) ),
	'Diamond Fighter': ( (1, 276), (1, 310), (1, 311), (1, 313), (1, 312) ),
}

dimensions = {
	-1: 'Nether',
	0: 'Normal',
}

class MCPlayerEditError(Exception):
	pass

class MCPlayerEdit(icmd.ICmdBase):

	def _checkloaded(self):
		"""
		Checks if a file has already been loaded.
		"""
		if not hasattr(self, 'level'):
			raise MCPlayerEditError(1, "No file loaded yet. Use `load <filename|worldnumber>`.")

	def _checkmodified(self):
		"""
		Check if the user has made modifications to the inventory/data. If
		there are changes, ask the user if he wants to continue. Returns True
		if the caller function can continue with the operation, false if the
		user wants to abort the operation.
		"""
		if hasattr(self, 'modified') and self.modified:
			reply = raw_input('You have unsaved changes. Continue without saving? [y/N] ')
			if not reply.lower().startswith('y'):
				return(False) # Do not perform operation
			else:
				return(True) # Perform operation, user is okay with loosing modifications
		else:
			return(True) # Perform operation, user has no modifications

	def _getinventory(self):
		inventory = [None] * 104
		for slot in self.level['Data']['Player']['Inventory']:
			inventory[slot['Slot'].value] = slot
		return(inventory)

	def load(self, filename, *args):
		"""
		Load a player's data
		Load a player's data. You can either specify the full path to the
		level.dat file, or a world number to load that world's data.

		Example:

		> load 4
		> load /home/user/.minecraft/saves/World4/level.dat

		Both commands will load World4's information.
		"""
		if not self._checkmodified():
			return(False)

		if args:
			filename = '%s %s' % (filename, ' '.join(args))

		try:
			# Try to load a world by number.
			self.world = int(filename)
			if sys.platform.startswith('darwin'):
				self.filename = '%s/Library/Application Support/minecraft/saves/World%i/level.dat' % (os.environ['HOME'], self.world)
			elif sys.platform.startswith('win'):
				self.filename = '%s\.minecraft\saves\World%i\level.dat' % (os.environ['APPDATA'], self.world)
			elif sys.platform.startswith('linux'):
				self.filename = '%s/.minecraft/saves/World%i/level.dat' % (os.environ['HOME'], self.world)
			else:
				raise MCPlayerEditError(3, "Unknown platform. Can't load by world number. Please specify full path")
			if hasattr(self, 'world'):
				self.icmd.prompt = 'World %i> ' % (self.world)
		except ValueError:
			# Try to load world by full path
			self.filename = filename

		try:
			self.level = nbt.load(self.filename)
		except IOError, e:
			if e.errno == 2:
				raise MCPlayerEditError(4, "Invalid filename or worldnumber. Couldn't open '%s'." % (self.filename))
				del self.filename
				return(False)
			else:
				del self.filename
				raise e

		# Load the bookmarks, if any
		self.bookmarks = {}
		try:
			for line in file(self.filename + '.bookmarks'):
				if line.strip():
					# Check for pre-halloween update format
					lastfield = line.split(' ')[-1]
					if not '.' in lastfield:
						# New format
						name, x, y, z, dimension = line.strip().rsplit(' ', 4)
					else:
						# Old format
						dimension = 0
						name, x, y, z = line.strip().rsplit(' ', 3)

					self.bookmarks[name] = (float(x), float(y), float(z), int(dimension))
		except IOError:
			pass

		self.modified = False
		self._output("Loaded.")

	def save(self):
		"""
		Save modifications to player data
		Save any modifications made to the world loaded with the `load`
		command.
		"""
		self._checkloaded()

		# Make a backup
		shutil.copy(self.filename, self.filename + '.bak')

		# Save modifications to level.dat
		self.level.save(self.filename)

		# Save the bookmarks
		try:
			f = file(self.filename + '.bookmarks', 'w')
			for bookmark in self.bookmarks.items():
				name = bookmark[0]
				x, y, z, dimension = bookmark[1]
				f.write('%s %f %f %f %i\n' % (name, x, y, z, dimension))
			f.close()
		except IOError, e:
			raise MCPlayerEditError(5, "Couldn't save bookmarks: %s" % (e.args[1]))

		self.modified = False
		self._output("Saved. Backup created (%s)" % (self.filename + '.bak'))

	def list(self, type = 'all'):
		"""
		List the players current inventory
		List the players current inventory. `type` can be 'quick', 'normal' or
		'armor' to list the quick inventory, normal inventory and armor
		inventory. 'all' will list your entire inventory, which is also the
		default if no `type` is specified.

		Examples:

		> list
		--entire inventory--
		> list quick
		slot   0 (quick inventory):  1 x Stone Pickaxe
		slot   1 (quick inventory):  1 x Stone Spade
		slot   2 (quick inventory): 42 x Dirt
		...
		"""
		self._checkloaded()

		inventory = [None] * 104
		for slot in self.level['Data']['Player']['Inventory']:
			inventory[slot['Slot'].value] = slot

		for slot in invmap:
			if slot[1] == type or type == 'all':
				print 'slot %3i (%6s inventory):' % (slot[0], slot[1]),
				if inventory[slot[0]]:
					print '%2i x %s' % (inventory[slot[0]]['Count'].value, items[inventory[slot[0]]['id'].value])
				else:
					print

	def give(self, count, *args):
		"""
		Add items to the players inventory
		Usage: give [count] <item>
		Tries to add COUNT times ITEM to the player inventory. COUNT must be in
		the range 1-64. If no count is given, gives one item. ITEM may be an
		item ID (see the `items` command) or the name of an item. Fails if
		there are no empty slots in the players inventory.

		You CAN stack unstackable items (64 x Diamond Pickaxe), and it will
		work, but it might corrupt your game. NO GAME-LOGIC IS CHECKED WHEN
		GIVING ITEMS! In case of corruption, see README.txt.

		Examples:
		> give 64 TNT
		Added 64 x TNT in slot 13
		> give 1 diamond pickaxe
		Added 1 x Diamond Pickaxe in slot 14
		> give 64 2256
		Added 64 x Gold Record in slot 15
		"""
		self._checkloaded()

		item = ' '.join(args)
		if not item:
			item = count
			count = 1

		# Validate some input
		try:
			count = int(count)
		except ValueError:
			item = ' '.join((count,) + args)
			count = 1
		if count < 1 or count > 64:
			raise MCPlayerEditError(2, 'Invalid count number. Must be in range 1 - 64')

		# Find out which item the user is trying to add
		itemid = None
		try:
			itemid = int(item)
		except ValueError:
			for i in items.items():
				if i[1].lower() == item.lower():
					itemid = i[0]
					break
		if not itemid or itemid not in items:
			raise MCPlayerEditError(2, "Unknown item '%s'. Use the `items` command for list a possible items. You may specify an ID or the item name" % (item))

		assignedslots = self._invadd([(count, itemid)])
		self._output("Added %i x %s in slot %i" % (count, items[itemid], assignedslots[0]))

		self.modified = True

	def _invadd(self, items):
		"""
		Add ITEMS to the users inventory. ITEMS is a list where each member is
		a list of two values: (count, itemid). Raises MCPlayerEditError if not
		enough slots are available. Returns a list of slots in which the items
		were added.
		"""
		inventory = self._getinventory()

		# Check available slots
		cnt = 0
		for slot in invmap:
			if not inventory[slot[0]]:
				cnt += 1
		if cnt < len(items):
			raise MCPlayerEditError(2, "Not enough empty slots found. %i needed" % (len(items)))

		i = 0
		slots = [] # int ids of slots where items where assigned
		for slot in invmap:
			item = items[i]
			if not inventory[slot[0]]:
				# Found an empty slot. Add the next item 
				newitem = nbt.TAG_Compound()
				newitem['id'] = nbt.TAG_Short(item[1])
				newitem['Damage'] = nbt.TAG_Short(0)
				newitem['Count'] = nbt.TAG_Byte(item[0])
				newitem['Slot'] = nbt.TAG_Byte(slot[0])
				self.level['Data']['Player']['Inventory'].append(newitem)
				slots.append(slot[0])
				i += 1
			if i == len(items):
				break
		return(slots)

	def kit(self, kit = None, *args):
		"""
		Add a collection of items to the user's inventory
		The kit command adds a whole kit of items to the user's inventory. The
		inventory must have enough empty slots for all the items.

		Examples:
		> kit Diamond Miner
		Added 'Diamond Miner' kit to inventory.
		"""
		if not kit:
			sys.stdout.write("The following kits are available:\n")
			for name, contents in kits.items():
				sys.stdout.write("  %s:\n" % (name))
				print '    %s' % (', '.join(['%i x %s' % (c[0], items[c[1]]) for c in contents]))
		else:
			self._checkloaded()

			if args:
				kit = '%s %s' % (kit, ' '.join(args))

			# Find out which kit the user is trying to add
			kitkey = None
			for k in kits.keys():
				if k.lower() == kit.lower():
					kitkey = k
			if not kitkey:
				raise MCPlayerEditError(2, 'No such kit name. Use the `kit` command with no parameters to list the available kits')

			kititems = kits[kitkey]
			self._invadd(kititems)
			self._output("Added '%s' kit to inventory." % (kitkey))

			self.modified = True

	def items(self, search = None):
		"""
		List item types
		List all item (blocks, tools, etc) ids and their names. These ids or
		names can be used on the `give` command. A SEARCH parameter can be
		given to limit the items listed to those in which SEARCH occurs.

		Examples:
		> items diamond
		264: Diamond
		279: Diamond Axe
		57: Diamond Block
		313: Diamond Boots
		...
		> items ingot
		266: Gold Ingot
		265: Iron Ingot
		"""
		sitems = [(item[1], item[0]) for item in items.items()]
		sitems.sort()
		for item in sitems:
			if not search or (search and search.lower() in item[0].lower()):
				print '%5i: %s' % (item[1], item[0])

	def clear(self, slot):
		"""
		Clear a slot in the inventory
		Clear a slot in the inventory. SLOT is a slot id (see the `list`
		command). You may also specify 'all' as the slot ID to clear the entire
		inventory.
		"""
		self._checkloaded()

		# Validate some input
		inventory = self.level['Data']['Player']['Inventory']

		if slot != 'all':
			# Clear a specific slot number.
			try:
				slot = int(slot)
			except ValueError:
				raise MCPlayerEditError(2, "Invalid slot number")
			if slot < 0 or slot > 103:
				raise MCPlayerEditError(2, "Invalid slot number")

			for i in range(0, len(inventory)):
				if inventory[i]['Slot'].value == slot:
					inventory.pop(i)
					self._output("Cleared slot %i" % (slot))
					break
			else:
				raise MCPlayerEditError(2, "Slot already empty")
		else:
			# Clear entire inventory. NBT does not support slice assignment, so
			# we need a while loop.
			while inventory:
				inventory.pop()
			self._output("Inventory cleared")

		self.modified = True

	def reload(self):
		"""
		Discard modifications and reload player data
		Discards the modifications made to the player data and reloads it.
		"""
		self._checkloaded()
		self.load(self.filename)

	def position(self):
		"""
		Display player/spawn position
		Displays the players current position (X, Y, Z and current spawnpoint
		position.

		X is smaller than 0 for North, larger than 0 for South.
		Y is the height. 0 is the bottom, 64 is sealevel, 128 is the ceiling.
		Z is smaller than 0 for East, larger than 0 for West.
		"""
		self._checkloaded()
		print self.level['Data']
		print "Spawn position : X, Y, Z: %i, %i, %i" % (
			self.level['Data']['SpawnX'].value,
			self.level['Data']['SpawnY'].value,
			self.level['Data']['SpawnZ'].value)
		print "Player position: Dimension, X, Y, Z: %s, %f, %f, %f" % (
			dimensions[self.level['Data']['Player']['Dimension'].value],
			self.level['Data']['Player']['Pos'][0].value,
			self.level['Data']['Player']['Pos'][1].value,
			self.level['Data']['Player']['Pos'][2].value)

	def move(self, source):
		"""
		Move player or spawnpoint
		Move the SOURCE ('player' or 'spawn') to the other position ('spawn' or
		'player'). Spawnpoints can not be moved to other dimensions.

		Examples:

		Move spawnpoint to the player's current position:
		> move spawn

		Move the player to his/her spawnpoint:
		> move player
		"""
		self._checkloaded()
		if source.lower() == 'spawn':
			dimension = self.level['Data']['Player']['Dimension'].value
			if dimension != 0:
				raise MCPlayerEditError(2, 'Cannot set spawn point in the %s dimension' % (dimensions[dimension]))
			self.level['Data']['SpawnX'].value = int(self.level['Data']['Player']['Pos'][0].value)
			self.level['Data']['SpawnY'].value = int(self.level['Data']['Player']['Pos'][1].value - 3)
			self.level['Data']['SpawnZ'].value = int(self.level['Data']['Player']['Pos'][2].value)
			self._output("Moved spawnpoint to current player position")
		elif source.lower() == 'player':
			self.level['Data']['Player']['Dimension'].value = 0
			self.level['Data']['Player']['Pos'][0].value = self.level['Data']['SpawnX'].value + 0.5
			self.level['Data']['Player']['Pos'][1].value = self.level['Data']['SpawnY'].value + 3.620000004768372
			self.level['Data']['Player']['Pos'][2].value = self.level['Data']['SpawnZ'].value + 0.5
			self._output("Moved current player position to spawnpoint")
		else:
			raise MCPlayerEditError(2, "Unknown source")

		self.modified = True

	def settime(self, time):
		"""
		Set the time of day.
		"""
		self._checkloaded()
		timemap = {
			'sunrise': 0,
			'noon': 6000,
			'sunset': 12000,
			'midnight': 18000,
		}
		if not time in timemap.keys():
			raise MCPlayerEditError(2, 'Invalid time of day. Valid options: %s' % (', '.join(timemap.keys())))

		self.level['Data']['Time'].value = timemap[time]
		self.modified = True

	#
	# Winter mode is no longer available after the Halloween update. :(
	#
	#def winter(self, onoff=None):
	#	"""
	#	Display/change winter mode
	#	Display or change the map to summer/winter mode. Winter mode will have
	#	snow. ONOFF can be either 'on' or 'off'. If obmitted, displays the
	#	current setting.
	#	"""
	#	self._checkloaded()
	#	if not onoff:
	#		print "Winter mode: %s" % (('off', 'on')[self.level['Data']['SnowCovered'].value])
	#	elif onoff.lower() == 'off':
	#		self.level['Data']['SnowCovered'].value = 0
	#		self.modified = True
	#	elif onoff.lower() == 'on':
	#		self.level['Data']['SnowCovered'].value = 1
	#		self.modified = True

	def bookmark(self, bookmark, *args):
		"""
		Create bookmark for later warping
		Creates a bookmark named BOOKMARK at the current player's position and
		dimension. If a bookmark with that name already exists, it is
		overwritten. The player can later warp to that bookmark using the
		`warp` command.
		"""
		self._checkloaded()

		if args:
			bookmark = '%s %s' % (bookmark, ' '.join(args))

		self.bookmarks[bookmark] = (
			self.level['Data']['Player']['Pos'][0].value,
			self.level['Data']['Player']['Pos'][1].value,
			self.level['Data']['Player']['Pos'][2].value,
			self.level['Data']['Player']['Dimension'].value,
		)
		self._output("Bookmark '%s' created." % (bookmark))

	def warp(self, bookmark = None, *args):
		"""
		Move player to bookmarked point
		Moves the player to a bookmarked point set with the `bookmark` command.
		If no BOOKMARK is given, list the current bookmarks. You CAN warp
		between dimensions.
		"""
		self._checkloaded()
		if not bookmark:
			# List bookmarks
			print "The following bookmarks have been set:"
			for bookmark in self.bookmarks.items():
				name = bookmark[0]
				x, y, z, dimension = bookmark[1]
				print "  %-20s: %8f %8f %8f (%s Dimension)" % (name, x, y, z, dimensions[dimension])
		else:
			if args:
				bookmark = '%s %s' % (bookmark, ' '.join(args))

			try:
				i = [b.lower() for b in self.bookmarks.keys()].index(bookmark.lower())
				k = self.bookmarks.keys()[i]
			except ValueError:
				raise MCPlayerEditError(2, "No such bookmark.")

			# Warp to bookmark
			x, y, z, dimension = self.bookmarks[k]
			self.level['Data']['Player']['Dimension'].value = dimension
			self.level['Data']['Player']['Pos'][0].value = x
			self.level['Data']['Player']['Pos'][1].value = int(y) + 0.620000004768372
			self.level['Data']['Player']['Pos'][2].value = z
			self._output('Warped player position to %s' % (k))

	def trackinv(self):
		"""
		Restore inventory after dying
		This command will track your inventory while you are playing. In the
		event of an untimely failure to continue living, it will save the
		inventory you had when you died. If you respawn and then quit playing
		the level, you can press Ctrl-C in MCPlayerEdit and choose to restore
		your inventory.
		"""
		self._checkloaded()
		self._output("Tracking inventory. Press Ctrl-c to stop.")

		playerdied = False
		inventory = []
		try:
			while True:
				time.sleep(1)
				level = nbt.load(self.filename)

				# Check if the player died. If so, save the inventory
				if not playerdied and level['Data']['Player']['Health'].value == 0:
					playerdied = True
					inventory[:] = [] # Clear previous inventory
					for slot in level['Data']['Player']['Inventory']:
						inventory.append((slot['Count'].value, slot['id'].value))
					print "Player died"
		except KeyboardInterrupt:
			if playerdied:
				print "\nOh dear, it seems you have died. If you have respawned and "
				print "quit to the main title, you can restore your inventory now."
				reply = raw_input('Would you like to restore your inventory? [Y/n]')
				if not reply.lower().startswith('n'):
					self.reload()
					self.clear('all')
					self._invadd(inventory)
					self.save()
					print "Inventory restored"
		self._output("\nNo longer tracking inventory.")

	def quit(self):
		"""
		Quit
		"""
		if not self._checkmodified():
			return(False)

		super(MCPlayerEdit, self).quit()

	exit = quit

class MCPlayerCmd(icmd.ICmd):
	def __init__(self, rootclass, prompt='> ', welcometext='Type \'help\' for help.', helptext_prefix='The following commands are available:\n', helptext_suffix='\n(type \'help <command>\' for details)\n', batch=False):
		exit = super(MCPlayerCmd, self).__init__(rootclass, prompt=prompt, welcometext=welcometext)
		self.rootclass.icmd = self

	def _completer(self, text, state):
		"""
		Context-sensitive readline completer.
		"""
		# Get icmd module's readline buffer, instead of 'our' module's instance.
		line = icmd.readline.get_line_buffer()
		if line.startswith('give'):
			w = [item for item in items.values() if item.lower().startswith(text.lower())]
		elif line.startswith('kit'):
			w = [key for key in kits.keys() if key.lower().startswith(text.lower())]
		elif line.startswith('list'):
			w = [l for l in ('all', 'quick', 'normal', 'armor') if l.startswith(text)]
		elif line.startswith('move'):
			w = [l for l in ('player', 'spawn') if l.startswith(text)]
		elif line.startswith('settime'):
			w = [l for l in ('sunrise', 'noon', 'sunset', 'midnight') if l.startswith(text)]
		else:
			w = [cmd for cmd in dir(self.instclass) if cmd.startswith(text) and not cmd.startswith('_') and callable(getattr(self.instclass, cmd))]

		try:
			return(w[state] + ' ')
		except IndexError:
			return None

	def run(self, catcherrors=True):
		exit = None
		while True:
			try:
				exit = super(MCPlayerCmd, self).run()
			except MCPlayerEditError, e:
				sys.stderr.write(e.args[1] + '\n')

			if exit:
				break

welcometext = """
%s v%i.%i by %s

Use 'load <worldnr>' or 'load <path_to_level.dat>' to load a level.
Type 'help' for a list of commands, 'help <command>' for detailed help.
'items' gives you a list of all available items.
""" % (__NAME__, __VERSION__[0], __VERSION__[1], __AUTHOR__)

mcplayeredit = MCPlayerCmd(MCPlayerEdit, welcometext=welcometext)
mcplayeredit.run()
