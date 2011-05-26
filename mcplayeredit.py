#!/usr/bin/python

__NAME__ = 'MCPlayerEdit'
__AUTHOR__ = "Ferry Boender"
__VERSION__ = "%%VERSION%%"

import sys
if sys.version_info[:2] < (2, 6):
	sys.stderr.write('%s requires Python v2.6 or higher. :(\n' % (__NAME__))
	raise SystemExit()
import os
import shutil
import struct
import time
import math
import random
basepath = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])))
sys.path.insert(0, os.path.join(basepath, 'lib'))
import icmd
import nbt
import sdb
sys.path.pop(0)

welcometext = """
%s v%s by %s

Use 'load <worldname>' or 'load <path_to_level.dat>' to load a level.
Ommit the worldname to get a list of worlds. Use the 'save' command
to save changes. You MUST NOT BE PLAYING the world at the same time
as editing, or your changes will have no effect (quit to the main menu).

Type 'help' for a list of commands, 'help <command>' for detailed help.
'items' gives you a list of all available items.
""" % (__NAME__, __VERSION__, __AUTHOR__)

# Item data: ['id', 'damage', 'name', 'max_stack']
# Some items have the same ID (colored wool). They use the damage id to
# destinguish themselves from eachother. The max_stack determines the maximum
# number of the item that can be stacked in a single slot.  If the
# max_stack is 0, the item is unsafe to add to the inventory (cannot
# normally be obtained in the game).
itemsdb_data = [
	[0,    0, 'Air',                     0],
	[1,    0, 'Stone',                   64],
	[2,    0, 'Grass',                   0],
	[3,    0, 'Dirt',                    64],
	[4,    0, 'Cobblestone',             64],
	[5,    0, 'Wood',                    64],
	[6,    0, 'Sapling',                 64],
	[6,    1, 'Spruce Sapling',          64],
	[6,    2, 'Birch Sapling',           64],
	[7,    0, 'Adminium',                0],
	[8,    0, 'Water',                   0],
	[9,    0, 'Stationary water',        0],
	[10,   0, 'Lava',                    0],
	[11,   0, 'Stationary lava',         0],
	[12,   0, 'Sand',                    64],
	[13,   0, 'Gravel',                  64],
	[14,   0, 'Gold ore',                0],
	[15,   0, 'Iron ore',                0],
	[16,   0, 'Coal ore',                0],
	[17,   0, 'Log',                     64],
	[17,   1, 'Redwood',                 64],
	[17,   2, 'Birch',                   64],
	[18,   0, 'Leaves',                  0],
	[19,   0, 'Sponge',                  0],
	[20,   0, 'Glass',                   64],
	[21,   0, 'Lapis Lazuli Ore',        0],
	[22,   0, 'Lapis Lazuli Block',      0],
	[23,   0, 'Dispenser',               64],
	[24,   0, 'Sandstone',               64],
	[25,   0, 'Note Block',              64],
	[27,   0, 'Powered Rail',            64],
	[28,   0, 'Detector Rail',           64],
	[30,   0, 'Web',                     64],
	[31,   0, 'Dead Grass Shrub',        0],
	[32,   0, 'Dead Desert Shrub',       0],
	#[26,   0, 'Aqua green Cloth',       64],
	#[27,   0, 'Cyan Cloth',             64],
	#[28,   0, 'Blue Cloth',             64],
	#[29,   0, 'Purple Cloth',           64],
	#[30,   0, 'Indigo Cloth',           64],
	#[31,   0, 'Violet Cloth',           64],
	#[32,   0, 'Magenta Cloth',          64],
	#[33,   0, 'Pink Cloth',             64],
	#[34,   0, 'Black Cloth',            64],
	#[35,   0, Gray Cloth / White Cloth',64],
	[35,   0, 'White Wool',              64],
	[35,   1, 'Orange Wool',             64],
	[35,   2, 'Magenta Wool',            64],
	[35,   3, 'Light Blue Wool',         64],
	[35,   4, 'Yellow Wool',             64],
	[35,   5, 'Light Green Wool',        64],
	[35,   6, 'Pink Wool',               64],
	[35,   7, 'Gray Wool',               64],
	[35,   8, 'Light Gray Wool',         64],
	[35,   9, 'Cyan Wool',               64],
	[35,  10, 'Purple Wool',             64],
	[35,  11, 'Blue Wool',               64],
	[35,  12, 'Brown Wool',              64],
	[35,  13, 'Dark Green Wool',         64],
	[35,  14, 'Red Wool',                64],
	[35,  15, 'Black Wool',              64],
	#[36,   0, 'White Cloth',            64],
	[37,   0, 'Yellow flower',           64],
	[38,   0, 'Red rose',                64],
	[39,   0, 'Brown Mushroom',          64],
	[40,   0, 'Red Mushroom',            64],
	[41,   0, 'Gold Block',              64],
	[42,   0, 'Iron Block',              64],
	[43,   0, 'Double Stone Slab',       64],
	[43,   1, 'Double Sandstone Slab',   64],
	[43,   2, 'Double Wooden Slab',      64],
	[43,   3, 'Double Cobblestone Slab', 64],
	[44,   0, 'Stone Slab',              64],
	[44,   1, 'Sandstone Slab',          64],
	[44,   2, 'Wooden Slab',             64],
	[44,   3, 'Cobblestone Slab',        64],
	[45,   0, 'Brick',                   64],
	[46,   0, 'TNT',                     64],
	[47,   0, 'Bookcase',                64],
	[48,   0, 'Moss Stone',              64],
	[49,   0, 'Obsidian',                64],
	[50,   0, 'Torch',                   64],
	[51,   0, 'Fire',                    0],
	[52,   0, 'Mob Spawner',             0],
	[53,   0, 'Wooden Stairs',           64],
	[54,   0, 'Chest',                   64],
	[55,   0, 'Redstone Wire',           64],
	[56,   0, 'Diamond Ore',             0],
	[57,   0, 'Diamond Block',           64],
	[58,   0, 'Workbench',               64],
	[59,   0, 'Crops',                   0],
	[60,   0, 'Farmland',                0],
	[61,   0, 'Furnace',                 64],
	[62,   0, 'Burning Furnace',         0],
	[63,   0, 'Sign Post',               0],
	[64,   0, 'Wooden Door',             1],
	[65,   0, 'Ladder',                  64],
	[66,   0, 'Rail',                    64],
	[67,   0, 'Cobblestone Stairs',      64],
	[68,   0, 'Wall Sign',               0],
	[69,   0, 'Lever',                   64],
	[70,   0, 'Stone Pressure Plate',    64],
	[71,   0, 'Iron Door',               0],
	[72,   0, 'Wooden Pressure Plate',   64],
	[73,   0, 'Redstone Ore',            0],
	[74,   0, 'Glowing Redstone Ore',    0],
	[75,   0, 'Redstone torch Off',      0],
	[76,   0, 'Redstone torch',          64],
	[77,   0, 'Stone Button',            64],
	[78,   0, 'Snow',                    0],
	[79,   0, 'Ice',                     0],
	[80,   0, 'Snow Block',              64],
	[81,   0, 'Cactus',                  64],
	[82,   0, 'Clay',                    64],
	[83,   0, 'Sugar Cane',              64],
	[84,   0, 'Jukebox',                 64],
	[85,   0, 'Fence',                   64],
	[86,   0, 'Pumpkin',                 64],
	[87,   0, 'Netherrack',              64],
	[88,   0, 'Soul Sand',               64],
	[89,   0, 'Glowstone',               64],
	[90,   0, 'Portal',                  0],
	[91,   0, 'Jack-O-Lantern',          64],
	[92,   0, 'Cake Block',              0],
	[93,   0, 'Redstone Repeater Off',   0],
	[94,   0, 'Redstone Repeater On',    0],
	[95,   0, 'Locked chest',            0],
	[96,   0, 'Trapdoor',                64],
	[256,  0, 'Iron Shovel',             1],
	[257,  0, 'Iron Pickaxe',            1],
	[258,  0, 'Iron Axe',                1],
	[259,  0, 'Flint and Steel',         1],
	[260,  0, 'Apple',                   1],
	[261,  0, 'Bow',                     1],
	[262,  0, 'Arrow',                   64],
	[263,  0, 'Coal',                    64],
	[263,  1, 'Charcoal',                64],
	[264,  0, 'Diamond',                 64],
	[265,  0, 'Iron Ingot',              64],
	[266,  0, 'Gold Ingot',              64],
	[267,  0, 'Iron Sword',              64],
	[268,  0, 'Wooden Sword',            1],
	[269,  0, 'Wooden Shovel',           1],
	[270,  0, 'Wooden Pickaxe',          1],
	[271,  0, 'Wooden Axe',              1],
	[272,  0, 'Stone Sword',             1],
	[273,  0, 'Stone Shovel',            1],
	[274,  0, 'Stone Pickaxe',           1],
	[275,  0, 'Stone Axe',               1],
	[276,  0, 'Diamond Sword',           1],
	[277,  0, 'Diamond Shovel',          1],
	[278,  0, 'Diamond Pickaxe',         1],
	[279,  0, 'Diamond Axe',             1],
	[280,  0, 'Stick',                   64],
	[281,  0, 'Bowl',                    64],
	[282,  0, 'Mushroom Soup',           1],
	[283,  0, 'Gold Sword',              1],
	[284,  0, 'Gold Shovel',             1],
	[285,  0, 'Gold Pickaxe',            1],
	[286,  0, 'Gold Axe',                1],
	[287,  0, 'String',                  64],
	[288,  0, 'Feather',                 64],
	[289,  0, 'Gunpowder',               64],
	[290,  0, 'Wooden Hoe',              1],
	[291,  0, 'Stone Hoe',               1],
	[292,  0, 'Iron Hoe',                1],
	[293,  0, 'Diamond Hoe',             1],
	[294,  0, 'Gold Hoe',                1],
	[295,  0, 'Seeds',                   64],
	[296,  0, 'Wheat',                   64],
	[297,  0, 'Bread',                   1],
	[298,  0, 'Leather Helmet',          1],
	[299,  0, 'Leather Chestplate',      1],
	[300,  0, 'Leather Pants',           1],
	[301,  0, 'Leather Boots',           1],
	[302,  0, 'Chainmail Helmet',        1],
	[303,  0, 'Chainmail Chestplate',    1],
	[304,  0, 'Chainmail Pants',         1],
	[305,  0, 'Chainmail Boots',         1],
	[306,  0, 'Iron Helmet',             1],
	[307,  0, 'Iron Chestplate',         1],
	[308,  0, 'Iron Pants',              1],
	[309,  0, 'Iron Boots',              1],
	[310,  0, 'Diamond Helmet',          1],
	[311,  0, 'Diamond Chestplate',      1],
	[312,  0, 'Diamond Pants',           1],
	[313,  0, 'Diamond Boots',           1],
	[314,  0, 'Gold Helmet',             1],
	[315,  0, 'Gold Chestplate',         1],
	[316,  0, 'Gold Pants',              1],
	[317,  0, 'Gold Boots',              1],
	[318,  0, 'Flint',                   64],
	[319,  0, 'Pork',                    1],
	[320,  0, 'Grilled Pork',            1],
	[321,  0, 'Painting',                64],
	[322,  0, 'Golden apple',            1],
	[323,  0, 'Sign',                    1],
	[324,  0, 'Wooden door',             1],
	[325,  0, 'Bucket',                  1],
	[326,  0, 'Water bucket',            0],
	[327,  0, 'Lava bucket',             0],
	[328,  0, 'Mine cart',               1],
	[329,  0, 'Saddle',                  1],
	[330,  0, 'Iron door',               1],
	[331,  0, 'Redstone',                64],
	[332,  0, 'Snowball',                16],
	[333,  0, 'Boat',                    1],
	[334,  0, 'Leather',                 64],
	[335,  0, 'Milk Bucket',             0],
	[336,  0, 'Clay Brick',              64],
	[337,  0, 'Clay',                    64],
	[338,  0, 'Sugar Cane',              64],
	[339,  0, 'Paper',                   64],
	[340,  0, 'Book',                    64],
	[341,  0, 'Slime Ball',              64],
	[342,  0, 'Storage Minecart',        1],
	[343,  0, 'Powered Minecart',        1],
	[344,  0, 'Egg',                     16],
	[345,  0, 'Compass',                 64],
	[346,  0, 'Fishing Rod',             1],
	[347,  0, 'Watch',                   64],
	[348,  0, 'Glowstone Dust',          64],
	[349,  0, 'Raw Fish',                64],
	[350,  0, 'Cooked Fish',             1],
	[351,  0, 'Ink Sack',                64],
	[351,  1, 'Rose Red',                64],
	[351,  2, 'Cactus Green',            64],
	[351,  3, 'Coco Beans',              64],
	[351,  4, 'Lapis Lazuli',            64],
	[351,  5, 'Purple Dye',              64],
	[351,  6, 'Cyan Dye',                64],
	[351,  7, 'Light Gray Dye',          64],
	[351,  8, 'Gray Dye',                64],
	[351,  9, 'Pink Dye',                64],
	[351,  10, 'Lime Dye',               64],
	[351,  11, 'Dandelion Yellow',       64],
	[351,  12, 'Light Blue Dye',         64],
	[351,  13, 'Magenta Dye',            64],
	[351,  14, 'Orange Dye',             64],
	[351,  15, 'Bone Meal',              64],
	[352,  0, 'Bone',                    64],
	[353,  0, 'Sugar',                   64],
	[354,  0, 'Cake',                    1],
	[355,  0, 'Bed',                     1],
	[356,  0, 'Redstone Repeater',       64],
	[357,  0, 'Cookie',                  8],
	[358,  0, 'Map',                     1],
	[2256, 0, 'Gold Music Disc',         1],
	[2257, 0, 'Green Music Disc',        1],
]

invmap = \
	[(x, 'quick') for x in range(0, 9)] + \
	[(x, 'normal') for x in range(9, 36)] + \
	[(x, 'armor') for x in range(100, 104)]

dimensions = {
	-1: 'Nether',
	0: 'Normal',
}

defaultkits = { # Only used if kits.dat doesn't exist.
	'Diamond Miner': ( (1, 279, 0), (1, 278, 0), (1, 277, 0), (1, 293, 0) ),
	'Diamond Fighter': ( (1, 276, 0), (1, 310, 0), (1, 311, 0), (1, 313, 0), (1, 312, 0) ),
}

class ItemDB(sdb.SDB):
	def nbt_to_name(self, nbt_compound):
		item_id = nbt_compound['id'].value
		damage = nbt_compound['Damage'].value
		return(self.get_item(item_id, damage))

	def get_item(self, item_id, damage):
		item = itemdb.getx(id=item_id, damage=damage)
		if not item:
			item = itemdb.get(item_id)
		return(item)

itemdb = ItemDB(data= itemsdb_data, cols=['id', 'damage', 'name', 'max_stack'], id='id')

class MCPlayerEditError(Exception):
	pass

class MCPlayerEdit(icmd.ICmdBase):
	def __init__(self, helptext_prefix = '', helptext_suffix = '', batch=False):
		self.safe_mode = True

		# Load kits
		self.kitpath = os.path.join(confpath, 'kits.dat')
		if not os.path.exists(self.kitpath):
			self.kits = defaultkits
			self._kit_save(self.kitpath)
		else:
			self.kits = self._kit_load(self.kitpath)

		super(MCPlayerEdit, self).__init__(helptext_prefix = '', helptext_suffix = '', batch=False)

	def _kit_load(self, path):
		kits = {}
		for line in file(path):
			name, contents = line.split('\t', 1)
			kits[name] = eval(contents, {'__builtins__': None})

		# Backwards compatibility
		for name, contents in kits.items():
			if contents and len(contents[0]) == 2:
				# Convert to new format
				new_contents = []
				for c in contents:
					item = list(c)
					item.append(0)
					new_contents.append(item)
				kits[name] = new_contents
		return(kits)

	def _kit_save(self, path):
		f = file(path, 'w')
		for name, contents in self.kits.items():
			f.write('%s\t%s\n' % (name, contents))
		f.close()

	def _checkloaded(self):
		"""
		Checks if a file has already been loaded.
		"""
		if not hasattr(self, 'level'):
			raise MCPlayerEditError(1, "No file loaded yet. Use `load <filename|worldname>`.")

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

	def _checkunsafe(self):
		"""
		Check if MCPlayerEdit is in safe mode. If so, it raises an error. This
		should be called by commands which are not safe to use.
		"""
		if self.safe_mode:
			raise MCPlayerEditError(19, "MCPlayerEdit is currently in Safe mode and this command is not safe to use in Safe mode. See 'help safemode'")

	def _getinventory(self):
		inventory = [None] * 104
		for slot in self.level['Data']['Player']['Inventory']:
			inventory[slot['Slot'].value] = slot
		return(inventory)

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
			raise MCPlayerEditError(6, "Not enough empty slots found. %i needed" % (len(items)))

		i = 0
		slots = [] # int ids of slots where items where assigned
		for slot in invmap:
			item = items[i]
			if not inventory[slot[0]]:
				# Found an empty slot. Add the next item 
				newitem = nbt.TAG_Compound()
				newitem['id'] = nbt.TAG_Short(item[1])
				newitem['Damage'] = nbt.TAG_Short(item[2])
				newitem['Count'] = nbt.TAG_Byte(item[0])
				newitem['Slot'] = nbt.TAG_Byte(slot[0])
				self.level['Data']['Player']['Inventory'].append(newitem)
				slots.append(slot[0])
				i += 1
			if i == len(items):
				break
		return(slots)

	def load(self, worldname = None, *args):
		"""
		Load a world's data
		Load a world's data. You can either specify the full path to the
		level.dat file, or a world name to load that world's data.

		Example:

		> load New World
		> load /home/user/.minecraft/saves/World4/level.dat
		"""
		if not self._checkmodified():
			return(False)

		# Determine path to Minecraft directory.
		mcdir = None
		if sys.platform.startswith('darwin'):
			mcdir = '%s/Library/Application Support/minecraft/saves/' % (os.environ['HOME'], )
		elif sys.platform.startswith('win'):
			mcdir = '%s\.minecraft\saves\\' % (os.environ['APPDATA'], )
		elif sys.platform.startswith('linux'):
			mcdir = '%s/.minecraft/saves/' % (os.environ['HOME'], )

		if not worldname:
			# Show a list of available worlds.
			if not mcdir:
				raise MCPlayerEditError(2, "Unknown platform. Can't list available worlds")
			print "The following worlds are available for loading:"
			for dirname in os.listdir(mcdir):
				if not dirname.startswith('.'):
					print "  %s" % (dirname, )
			return
		else:
			# Try to load the provided world.
			if args:
				worldname = '%s %s' % (worldname, ' '.join(args))

			if mcdir:
				if worldname.endswith('level.dat'):
					worldfile = os.path.join(mcdir, worldname)
				else:
					worldfile = os.path.join(mcdir, worldname, 'level.dat')
			else:
				if worldname.endswith('level.dat'):
					worldfile = os.path.join(worldname)
				else:
					worldfile = os.path.join(worldname, 'level.dat')

			try:
				self.level = nbt.load(worldfile)
				self.worldname = worldname
				self.filename = worldfile
				self.icmd.prompt = '%s> ' % (worldname)
			except IOError, e:
				if e.errno in [2, 21]:
					raise MCPlayerEditError(3, "Invalid filename or worldname. Couldn't open '%s'." % (worldname))
					return(False)
				else:
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
			raise MCPlayerEditError(4, "Couldn't save bookmarks: %s" % (e.args[1]))

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
		slot   1 (quick inventory):  1 x Stone Shovel
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
					item = itemdb.nbt_to_name(inventory[slot[0]])
					if not item:
						print '%2i x %s (%i)' % (inventory[slot[0]]['Count'].value, 'Unknown?', inventory[slot[0]]['id'].value)
					else:
						print '%2i x %s' % (inventory[slot[0]]['Count'].value, item['name'])
				else:
					print

	def give(self, count, *args):
		"""
		Add items to the players inventory
		Usage: give [count] <item>
		Tries to add COUNT times ITEM to the player inventory. If no count is
		given, gives the maximum stack size for the item. ITEM may be an item
		ID (see the `items` command) or the name of an item. Fails if there are
		not enough empty slots in the players inventory.

		Sometimes multiple items have the same ID. If you select such an item
		by id, you will be given an additional option menu from which you can
		chose which item you want.

		If Safe mode is off (see 'help safemode'), you CAN stack unstackable
		items (64 x Diamond Pickaxe, 256 x Log), and it will work, but it might
		corrupt your game. In case of corruption, see README.txt.

		Examples:
		> give TNT
		Added 64 x TNT in slot 0

		> give 105 dirt
		Added 64 x Dirt in slot 1
		Added 41 x Dirt in slot 2

		> give 1 diamond pickaxe
		Added 1 x Diamond Pickaxe in slot 3

		> give 64 38
		Added 64 x Red rose in slot 4
		"""
		self._checkloaded()

		if not args:
			item = count
		else:
			item  = ' '.join(args)

		try:
			count = int(count)
		except ValueError:
			item = ' '.join((count,) + args)
			count = None
		except TypeError:
			# if count == None the count will later on become max_stack size.
			count = None

		# Find out which item the user is trying to add
		itemid = None
		add_item = None
		try:
			# Try to get the item by numeric ID.
			itemid = int(item)
			items = itemdb.select(lambda row: row['id'] == itemid)

			if len(items) > 1:
				# Multiple items with the same id. Allow user to select by damage
				print "\nThere are multiple items with that ID:"
				for i_item in items:
					print "%5s: %s" % (i_item['damage'], i_item['name'])
				damage = raw_input('Select a number or nothing to abort: ')
				if not damage:
					return
				d_item = itemdb.getx(id=itemid, damage=int(damage))
				if d_item:
					add_item = d_item
			else:
				add_item = itemdb.getx(id=itemid, damage=0)
		except ValueError:
			# Try to get the item by name
			rows = itemdb.select(lambda row: row['name'].lower() == item.lower())
			if rows:
				add_item = rows[0]

		if not add_item:
			raise MCPlayerEditError(6, "Unknown item '%s'. Use the `items` command for list a possible items. You may specify an ID or the item name" % (item))

		# If count not given, set to max_stack size.
		if not count:
			count = add_item['max_stack']

		# Check if the item is safe to add.
		if self.safe_mode:
			if add_item['max_stack'] < 1:
				raise MCPlayerEditError(19, "MCPlayerEdit is currently in Safe mode and this item is not safe to add. See 'help safemode'.")

		# Determine stacks to add
		if self.safe_mode:
			# Divide the count in appropriately sized (max_stack size) stacks.
			stacks = [[add_item['max_stack'], add_item['id'], add_item['damage']]] * (count / add_item['max_stack'])
			if count % add_item['max_stack'] > 0:
				stacks.append([count % add_item['max_stack'], add_item['id'], add_item['damage']])
		else:
			# Safe mode off, just add the count the user wants.
			stacks = [[count, add_item['id'], add_item['damage']], ]

		# Add stacks to the inventory.
		for stack in stacks:
			assignedslots = self._invadd((stack, ))
			self._output("Added %i x %s in slot %i" % (stack[0], add_item['name'], assignedslots[0]))

		self.modified = True

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
			for name, contents in self.kits.items():
				sys.stdout.write("  %s:\n" % (name))
				items = []
				item_count = contents[0]
				for item_count, item_id, item_damage in contents:
					item = itemdb.get_item(item_id, item_damage)
					if item:
						item_name = item['name']
						items.append( (item_count, item_name) )
				print '    %s' % (', '.join(['%i x %s' % (item[0], item[1]) for item in items]))
		else:
			self._checkloaded()

			if args:
				kit = '%s %s' % (kit, ' '.join(args))

			# Find out which kit the user is trying to add
			kitkey = None
			for k in self.kits.keys():
				if k.lower() == kit.lower():
					kitkey = k
			if not kitkey:
				raise MCPlayerEditError(7, 'No such kit name. Use the `kit` command with no parameters to list the available kits')

			kititems = self.kits[kitkey]
			self._invadd(kititems)
			self._output("Added '%s' kit to inventory." % (kitkey))

			self.modified = True

	def kitsave(self, name):
		"""
		Save current inventory as kit
		Save the current player inventory as a kit.
		"""
		self._checkloaded()

		contents = []
		for slot in self.level['Data']['Player']['Inventory']:
			contents.append( [slot['Count'].value, slot['id'].value, slot['Damage'].value] )

		self.kits[name] = contents
		self._kit_save(self.kitpath)

	def items(self, search = None):
		"""
		List item types
		List all item (blocks, tools, etc) ids and their names. These ids or
		names can be used on the `give` command. A SEARCH parameter can be
		given to limit the items listed to those in which SEARCH occurs.

		Only lists unsafe items if safemode is off (see 'help safemode')

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
		if search:
			search = search.lower()
			if self.safe_mode:
				items = itemdb.select(lambda row: search in row['name'].lower() and row['max_stack'] > 0, cmp)
			else:
				items = itemdb.select(lambda row: search in row['name'].lower(), cmp)
		else:
			if self.safe_mode:
				items = itemdb.select(lambda row: row['max_stack'] > 0)
			else:
				items = itemdb.select()

		for item in items:
			print '%5i: %s' % (item['id'], item['name'])

	def clear(self, slot):
		"""
		Clear all/a single slot(s) in the inventory
		Clear a slot in the inventory. SLOT is a slot id (see the `list`
		command). You may also specify 'all' as the slot ID to clear the entire
		inventory.
		"""
		self._checkloaded()

		inventory = self.level['Data']['Player']['Inventory']

		# Validate some input
		if slot != 'all':
			# Clear a specific slot number.
			try:
				slot = int(slot)
			except ValueError:
				raise MCPlayerEditError(8, "Invalid slot number")
			if slot < 0 or slot > 103:
				raise MCPlayerEditError(9, "Invalid slot number")

			for i in range(0, len(inventory)):
				if inventory[i]['Slot'].value == slot:
					inventory.pop(i)
					self._output("Cleared slot %i" % (slot))
					break
			else:
				raise MCPlayerEditError(10, "Slot already empty")
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
		if self.worldname:
			self.load(self.worldname)
		else:
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
				raise MCPlayerEditError(11, 'Cannot set spawn point in the %s dimension' % (dimensions[dimension]))
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
			raise MCPlayerEditError(12, "Unknown source")

		self.modified = True

	def settime(self, time):
		"""
		Set the time of day.
		Set the time of day. Possible times are: 'sunrise', 'noon', 'sunset'
		and 'midnight'.
		"""
		self._checkloaded()
		timemap = {
			'sunrise': 0,
			'noon': 6000,
			'sunset': 12000,
			'midnight': 18000,
		}
		if not time in timemap.keys():
			raise MCPlayerEditError(13, 'Invalid time of day. Valid options: %s' % (', '.join(timemap.keys())))

		self.level['Data']['Time'].value = timemap[time]
		print "Time of day set to %s" % (time)
		self.modified = True

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
				raise MCPlayerEditError(14, "No such bookmark.")

			# Warp to bookmark
			x, y, z, dimension = self.bookmarks[k]
			self.level['Data']['Player']['Dimension'].value = dimension
			self.level['Data']['Player']['Pos'][0].value = x
			self.level['Data']['Player']['Pos'][1].value = int(y) + 0.620000004768372
			self.level['Data']['Player']['Pos'][2].value = z
			self._output('Warped player position to %s' % (k))

	def warpto(self, x, y, z, dimension='Normal'):
		"""
		Move player to specific coordinates.
		Move the player to a specific set of coordinates. If no dimension is
		given, defaults to the normal dimension. Valid dimensions are 'Normal'
		and 'Nether'. 'y' is the height. y=64 is sealevel.

		CAREFUL: You can easily warp yourself into blocks, which will cause you
		to die!
		"""
		self._checkloaded()
		self._checkunsafe()

		try:
			dimension=[k for (k,v) in dimensions.items() if v.lower()==dimension.lower()][0]
		except IndexError:
			raise MCPlayerEditError(2, "No such dimension.")

		x,y,z=(float(s.rstrip(',')) for s in (x,y,z))

		self.level['Data']['Player']['Dimension'].value = dimension
		self.level['Data']['Player']['Pos'][0].value = x
		self.level['Data']['Player']['Pos'][1].value = float(int(y)) + 0.620000004768372
		self.level['Data']['Player']['Pos'][2].value = z
		self._output('Warped player position to %8f %8f %8f (%s Dimension)' % (x, y, z, dimensions[dimension]))

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

	def seed(self):
		"""
		Show the world's seed.
		Show the world's seed. It can be reused when creating a new world
		(although the spawn location can be up to 200 meters away).
		"""
		self._checkloaded()
		print "The seed for this world is:"
		print "  ", self.level['Data']['RandomSeed'].value

	def nbtdump(self, obj=None, path=''):
		"""
		Dump NBT data. (Debug information)
		Dump the level.dat's NBT data. This is primarily useful for developers.
		"""
		self._checkloaded()

		if not obj:
			obj = self.level

		if isinstance(obj, nbt.TAG_Compound):
			for name, value in obj.items():
				if isinstance(value, (nbt.TAG_Compound, nbt.TAG_List)):
					#print str.lstrip("%s.%s" % (path, name), '.')
					self.dump(value, '%s.%s' % (path, name))
				else:
					print str.lstrip("%s.%s: %s" % (path, name, value.value), '.')
		if isinstance(obj, nbt.TAG_List):
			for value in obj:
				if isinstance(value, (nbt.TAG_Compound, nbt.TAG_List)):
					self.dump(value, path)
				else:
					print str.lstrip("%s: %s" % (path, value.value), '.')

	def nbtset(self, path, value):
		"""
		Set raw NBT values.
		Directly set the value of NBT values. This is mostly useful for
		developers. You cannot currently modify lists of NBT values (the
		inventory, player position, etc).

		WARNING: This may corrupt your save!

		Examples:

		Turn on thundering:
		> nbtset Data.thundering 1

		Reset your health:
		> nbtset Data.Player.Health 20

		Set the ammount of air you've got left:
		> nbtset Data.Player.Air 300
		"""
		self._checkloaded()
		self._checkunsafe()

		try:
			obj = self.level
			for p in path.split('.'):
				obj = obj[p]
		except KeyError, e:
			raise MCPlayerEditError(17, "No such NBT tag: '%s'" % path)

		try:
			obj.value = value
		except ValueError, e:
			raise MCPlayerEditError(18, "'%s' is not a valid value for NBT tag '%s'" % (value, path))

	def rain(self, onoff, time=60):
		"""
		Turn rain/snow on/off (for a duration)
		Turn rain (snow in some biomes) on or off. Optionally specify a time
		(in seconds) for the rain/snow to last or how long it should stay off.
		The default is 60 seconds.

		Examples:

		Make it rain for an minute (real time, not game time)
		> rain on 60
		It will rain/snow for 60 seconds (real time)

		Make sure it doesn't rain for an hour (real time, not game time)
		> rain off 3600
		It will not rain/snow for 3600 seconds (real time)

		"""
		self._checkloaded()

		if onoff.lower().strip() in ['on', 'yes', '1', 'true']:
			onoff = 1
		elif onoff.lower().strip() in ['off', 'no', '0', 'false']:
			onoff = 0
		else:
			raise MCPlayerEditError(15, "Invalid value for onoff parameter. 'yes' or 'no'.")

		try:
			time = int(time)
		except ValueError:
			raise MCPlayerEditError(16, "Invalid value for time parameter. Specify a number of seconds.")

		self.level['Data']['raining'].value = onoff
		self.level['Data']['rainTime'].value = time * 20

		self._output("It will %srain/snow for %i seconds (real time)" % (['not ', ''][onoff], time))

	def thunder(self, onoff, time=60):
		"""
		Turn thunder on/off (for a duration)
		Turn thunder on or off. It needs to be raining for this to work (see
		'rain' command). Optionally specify a time (in seconds) for the
		thunderstorm to last or how long it should stay off.
		The default is 60 seconds.

		Examples:

		Make it thunder for an minute (real time, not game time)
		> thunder on 60
		It will thunder for 60 seconds (real time)

		Make sure it doesn't thunder for an hour (real time, not game time)
		> thunder off 3600
		It will not thunder for 3600 seconds (real time)

		"""
		self._checkloaded()

		if onoff.lower().strip() in ['on', 'yes', '1', 'true']:
			onoff = 1
		elif onoff.lower().strip() in ['off', 'no', '0', 'false']:
			onoff = 0
		else:
			raise MCPlayerEditError(15, "Invalid value for onoff parameter. 'yes' or 'no'.")

		try:
			time = int(time)
		except ValueError:
			raise MCPlayerEditError(16, "Invalid value for time parameter. Specify a number of seconds.")

		self.level['Data']['thundering'].value = onoff
		self.level['Data']['thunderTime'].value = time * 20

		self._output("It will %sthunder for %i seconds (real time)" % (['not ', ''][onoff], time))

	def safemode(self, onoff):
		"""
		Turn on/off safe mode
		This command turns on or off safe mode. In safe mode MCPlayerEdit will
		prevent you from doing things which are not allowed in Minecraft or
		might damage your save file. This includes:

		- adding items which can not normally be obtained in the game.
		- warping yourself to a random location (as it may warp you into rock).
		- adding a stack of items bigger than allowed normally.

		Turning safe mode off will allow you to do these things anyway (it's
		usually safe although you may die in the game)

		Examples:

		Turn off safe mode:
		> safemode off
		"""

		if onoff.lower().strip() in ['on', 'yes', '1', 'true']:
			onoff = True
		elif onoff.lower().strip() in ['off', 'no', '0', 'false']:
			onoff = False
		else:
			raise MCPlayerEditError(15, "Invalid value for onoff parameter. 'on' or 'off'.")

		self.safe_mode = onoff
		self._output("Safe mode is now %s" % (['off', 'on'][onoff]))

	def loseme(self, distance, keep_inventory=False):
		"""
		Randomly transport player.
		The loseme command will randomly transport the player DISTANCE blocks
		away in a random direction. The goal is to get back home safely. The
		inventory will be cleared, unless you specify 'yes' as the
		`keep_inventory` parameter.

		WARNING: You may end up high in the air or in the middle of rock! The
		best thing to do is find a position a little above sea-level before
		losing yourself. (your height in the map will not be changed). If you
		die immediately after warping, use the 'restore' command to get your
		restore your last position/health/inventory.

		Examples:

		Randomly transport the player 1000 blocks/meters away:
		> loseme 1000

		Randomly transport the player 200 blocks without losing inventory:
		> loseme 200 yes
		"""
		self._checkloaded()

		try:
			distance = int(distance)
		except ValueError:
			raise MCPlayerEditError(20, "Invalid value for distance: %s" % (distance))

		if not isinstance(keep_inventory, bool):
			if keep_inventory.lower().strip() in ['on', 'yes', '1', 'true']:
				keep_inventory = True
			elif keep_inventory.lower().strip() in ['off', 'no', '0', 'false']:
				keep_inventory = False
			else:
				raise MCPlayerEditError(15, "Invalid value for keep_inventory parameter. 'yes' or 'no'.")

		cx = self.level['Data']['Player']['Pos'][0].value
		cy = self.level['Data']['Player']['Pos'][1].value
		cz = self.level['Data']['Player']['Pos'][2].value

		nx = cx + distance * math.sin(random.randint(0, 360) * math.pi / 180)
		nz = cz + distance * -math.cos(random.randint(0, 360) * math.pi / 180)

		self.level['Data']['Player']['Pos'][0].value = nx
		self.level['Data']['Player']['Pos'][2].value = nz

		if not keep_inventory:
			inventory = self.level['Data']['Player']['Inventory']
			# Clear entire inventory. NBT does not support slice assignment, so
			# we need a while loop.
			while inventory:
				inventory.pop()

		self.modified = True
		self._output('You are now lost. Good luck on your journey home')

	def restore(self):
		"""
		Restore the last backup of the player data.
		MCPlayerEdit automatically creates a backup of the player data
		(level.dat) whenever you save. This command restores the last backup.
		"""
		self._checkloaded()

		if not self._checkmodified():
			return(False)

		shutil.copy(self.filename + ".bak", self.filename)
		self.reload()


	def quit(self):
		"""
		Quit
		"""
		if not self._checkmodified():
			return(False)

		super(MCPlayerEdit, self).quit()

	exit = quit

class MCPlayerCmd(icmd.ICmd):
	def __init__(self, rootclass, prompt='> ', histfile=os.path.join(os.environ.get('HOME', ''), '.icmd_hist'), welcometext='Type \'help\' for help.', helptext_prefix='The following commands are available:\n', helptext_suffix='\n(type \'help <command>\' for details)\n', batch=False):
		exit = super(MCPlayerCmd, self).__init__(rootclass, prompt=prompt, histfile=histfile, welcometext=welcometext)
		self.rootclass.icmd = self

	def _completer(self, text, state):
		"""
		Context-sensitive readline completer.
		"""
		# Get icmd module's readline buffer, instead of 'our' module's instance.
		line = icmd.readline.get_line_buffer()
		if line.startswith('give'):
			w = [item['name'] for item in itemdb.select(lambda row: row['name'].lower().startswith(text.lower()))]
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

# Create preferences directory and deduce some paths.
confpath = os.path.join(os.environ.get('HOME', ''), '.mcplayeredit')
oldconfpath = os.path.join(os.environ.get('HOME', ''), '.mcinvedit')
if sys.platform.startswith('darwin'):
	pass # FIXME
	#conffile = os.path.join(os.environ.get('HOME', ''), '.mcplayeredit')
	#oldconfpath = os.path.join(os.environ.get('APPDATA', ''), '.mcinvedit')
	#self.filename = '%s/Library/Application Support/minecraft/saves/World%i/level.dat' % (os.environ['HOME'], self.world)
elif sys.platform.startswith('win'):
	confpath = os.path.join(os.environ.get('APPDATA', ''), 'MCPlayerEdit')
	oldconfpath = os.path.join(os.environ.get('HOME', ''), '.mcinvedit')
confpath_hist = os.path.join(confpath, 'history')

if not os.path.exists(confpath):
	os.mkdir(confpath)
	# Check for old-style .mcinvedit file
	if os.path.exists(oldconfpath):
		os.rename(oldconfpath, confpath_hist)

mcplayeredit = MCPlayerCmd(MCPlayerEdit, histfile=confpath_hist, welcometext=welcometext)
mcplayeredit.run()
