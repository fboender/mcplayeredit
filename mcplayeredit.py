#!/usr/bin/python

#
# Todo:
# - autocomplete needs work
#   * Values with spaces are not quoted/escaped properly. 
#   * Autocomplete on mac
#   * completing 'kit' doesn't show 'kitsave'.
# - MacOSX windows support (tab completion)
# - give/kit will put items in armor slots even if they're not supposed to go
#   there.
# - Safe mode: Users can't do things using MCPlayerEdit which they can't do in the game:
#   * Add more than 1 tool/etc in a slot.
#   * Add non-armor in an armor slot.
#   * Give coloured cloth and other invalid items.
# - Watch level.dat for changes?
# - Detect lock? (Is this even possible?)
# - Confirm method.

__NAME__    = 'MCPlayerEdit'
__AUTHOR__  = "Ferry Boender"
__VERSION__ = (0, 8)

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
import sdb
sys.path.pop(0)

welcometext = """
%s v%i.%i by %s

Use 'load <worldnr>' or 'load <path_to_level.dat>' to load a level.
Type 'help' for a list of commands, 'help <command>' for detailed help.
'items' gives you a list of all available items.
""" % (__NAME__, __VERSION__[0], __VERSION__[1], __AUTHOR__)

itemsdb_data = [
	[0,    0, 'Air'],
	[1,    0, 'Stone'],
	[2,    0, 'Grass'],
	[3,    0, 'Dirt'],
	[4,    0, 'Cobblestone'],
	[5,    0, 'Wood'],
	[6,    0, 'Sapling'],
	[7,    0, 'Adminium'],
	[8,    0, 'Water'],
	[9,    0, 'Stationary water'],
	[10,   0, 'Lava'],
	[11,   0, 'Stationary lava'],
	[12,   0, 'Sand'],
	[13,   0, 'Gravel'],
	[14,   0, 'Gold ore'],
	[15,   0, 'Iron ore'],
	[16,   0, 'Coal ore'],
	[17,   0, 'Log'],
	[17,   1, 'Redwood'],
	[17,   2, 'Birch'],
	[18,   0, 'Leaves'],
	[19,   0, 'Sponge'],
	[20,   0, 'Glass'],
	[21,   0, 'Lapis Lazuli Ore'],
	[22,   0, 'Lapis Lazuli Block'],
	[23,   0, 'Dispenser'],
	[24,   0, 'Sandstone'],
	[25,   0, 'Note Block'],
	#[26,   0, 'Aqua green Cloth'],
	#[27,   0, 'Cyan Cloth'],
	#[28,   0, 'Blue Cloth'],
	#[29,   0, 'Purple Cloth'],
	#[30,   0, 'Indigo Cloth'],
	#[31,   0, 'Violet Cloth'],
	#[32,   0, 'Magenta Cloth'],
	#[33,   0, 'Pink Cloth'],
	#[34,   0, 'Black Cloth'],
	#[35,   0, Gray Cloth / White Cloth'],
	[35,   0, 'White Wool'],
	[35,   1, 'Orange Wool'],
	[35,   2, 'Magenta Wool'],
	[35,   3, 'Light Blue Wool'],
	[35,   4, 'Yellow Wool'],
	[35,   5, 'Light Green Wool'],
	[35,   6, 'Pink Wool'],
	[35,   7, 'Gray Wool'],
	[35,   8, 'Light Gray Wool'],
	[35,   9, 'Cyan Wool'],
	[35,  10, 'Purple Wool'],
	[35,  11, 'Blue Wool'],
	[35,  12, 'Brown Wool'],
	[35,  13, 'Dark Green Wool'],
	[35,  14, 'Red Wool'],
	[35,  15, 'Black Wool'],
	#[36,   0, 'White Cloth'],
	[37,   0, 'Yellow flower'],
	[38,   0, 'Red rose'],
	[39,   0, 'Brown Mushroom'],
	[40,   0, 'Red Mushroom'],
	[41,   0, 'Gold Block'],
	[42,   0, 'Iron Block'],
	[43,   0, 'Double Stone Slab'],
	[44,   0, 'Stone Slab'],
	[45,   0, 'Brick'],
	[46,   0, 'TNT'],
	[47,   0, 'Bookcase'],
	[48,   0, 'Moss Stone'],
	[49,   0, 'Obsidian'],
	[50,   0, 'Torch'],
	[51,   0, 'Fire'],
	[52,   0, 'Mob Spawner'],
	[53,   0, 'Wooden Stairs'],
	[54,   0, 'Chest'],
	[55,   0, 'Redstone Wire'],
	[56,   0, 'Diamond Ore'],
	[57,   0, 'Diamond Block'],
	[58,   0, 'Workbench'],
	[59,   0, 'Crops'],
	[60,   0, 'Soil'],
	[61,   0, 'Furnace'],
	[62,   0, 'Burning Furnace'],
	[63,   0, 'Sign Post'],
	[64,   0, 'Wooden Door'],
	[65,   0, 'Ladder'],
	[66,   0, 'Minecart Tracks'],
	[67,   0, 'Cobblestone Stairs'],
	[68,   0, 'Wall Sign'],
	[69,   0, 'Lever'],
	[70,   0, 'Stone Pressure Plate'],
	[71,   0, 'Iron Door'],
	[72,   0, 'Wooden Pressure Plate'],
	[73,   0, 'Redstone Ore'],
	[74,   0, 'Glowing Redstone Ore'],
	[75,   0, 'Redstone torch Off'],
	[76,   0, 'Redstone torch On'],
	[77,   0, 'Stone Button'],
	[78,   0, 'Snow'],
	[79,   0, 'Ice'],
	[80,   0, 'Snow Block'],
	[81,   0, 'Cactus'],
	[82,   0, 'Clay'],
	[83,   0, 'Sugar Cane'],
	[84,   0, 'Jukebox'],
	[85,   0, 'Fence'],
	[86,   0, 'Pumpkin'],
	[87,   0, 'Netherrack'],
	[88,   0, 'Soul Sand'],
	[89,   0, 'Glowstone'],
	[90,   0, 'Portal'],
	[91,   0, 'Jack-O-Lantern'],
	[92,   0, 'Cake Block'],
	[256,  0, 'Iron Spade'],
	[257,  0, 'Iron Pickaxe'],
	[258,  0, 'Iron Axe'],
	[259,  0, 'Flint and Steel'],
	[260,  0, 'Apple'],
	[261,  0, 'Bow'],
	[262,  0, 'Arrow'],
	[263,  0, 'Coal'],
	[263,  1, 'Charcoal'],
	[264,  0, 'Diamond'],
	[265,  0, 'Iron Ingot'],
	[266,  0, 'Gold Ingot'],
	[267,  0, 'Iron Sword'],
	[268,  0, 'Wooden Sword'],
	[269,  0, 'Wooden Spade'],
	[270,  0, 'Wooden Pickaxe'],
	[271,  0, 'Wooden Axe'],
	[272,  0, 'Stone Sword'],
	[273,  0, 'Stone Spade'],
	[274,  0, 'Stone Pickaxe'],
	[275,  0, 'Stone Axe'],
	[276,  0, 'Diamond Sword'],
	[277,  0, 'Diamond Spade'],
	[278,  0, 'Diamond Pickaxe'],
	[279,  0, 'Diamond Axe'],
	[280,  0, 'Stick'],
	[281,  0, 'Bowl'],
	[282,  0, 'Mushroom Soup'],
	[283,  0, 'Gold Sword'],
	[284,  0, 'Gold Spade'],
	[285,  0, 'Gold Pickaxe'],
	[286,  0, 'Gold Axe'],
	[287,  0, 'String'],
	[288,  0, 'Feather'],
	[289,  0, 'Gunpowder'],
	[290,  0, 'Wooden Hoe'],
	[291,  0, 'Stone Hoe'],
	[292,  0, 'Iron Hoe'],
	[293,  0, 'Diamond Hoe'],
	[294,  0, 'Gold Hoe'],
	[295,  0, 'Seeds'],
	[296,  0, 'Wheat'],
	[297,  0, 'Bread'],
	[298,  0, 'Leather Helmet'],
	[299,  0, 'Leather Chestplate'],
	[300,  0, 'Leather Pants'],
	[301,  0, 'Leather Boots'],
	[302,  0, 'Chainmail Helmet'],
	[303,  0, 'Chainmail Chestplate'],
	[304,  0, 'Chainmail Pants'],
	[305,  0, 'Chainmail Boots'],
	[306,  0, 'Iron Helmet'],
	[307,  0, 'Iron Chestplate'],
	[308,  0, 'Iron Pants'],
	[309,  0, 'Iron Boots'],
	[310,  0, 'Diamond Helmet'],
	[311,  0, 'Diamond Chestplate'],
	[312,  0, 'Diamond Pants'],
	[313,  0, 'Diamond Boots'],
	[314,  0, 'Gold Helmet'],
	[315,  0, 'Gold Chestplate'],
	[316,  0, 'Gold Pants'],
	[317,  0, 'Gold Boots'],
	[318,  0, 'Flint'],
	[319,  0, 'Pork'],
	[320,  0, 'Grilled Pork'],
	[321,  0, 'Paintings'],
	[322,  0, 'Golden apple'],
	[323,  0, 'Sign'],
	[324,  0, 'Wooden door'],
	[325,  0, 'Bucket'],
	[326,  0, 'Water bucket'],
	[327,  0, 'Lava bucket'],
	[328,  0, 'Mine cart'],
	[329,  0, 'Saddle'],
	[330,  0, 'Iron door'],
	[331,  0, 'Redstone'],
	[332,  0, 'Snowball'],
	[333,  0, 'Boat'],
	[334,  0, 'Leather'],
	[335,  0, 'Milk Bucket'],
	[336,  0, 'Clay Brick'],
	[337,  0, 'Clay Balls'],
	[338,  0, 'Sugar Cane'],
	[339,  0, 'Paper'],
	[340,  0, 'Book'],
	[341,  0, 'Slime Ball'],
	[342,  0, 'Storage Minecart'],
	[343,  0, 'Powered Minecart'],
	[344,  0, 'Egg'],
	[345,  0, 'Compass'],
	[346,  0, 'Fishing Rod'],
	[347,  0, 'Watch'],
	[348,  0, 'Glowstone Dust'],
	[349,  0, 'Raw Fish'],
	[350,  0, 'Cooked Fish'],
	[351,  0, 'Ink Sack'],
	[351,  1, 'Rose Red'],
	[351,  2, 'Cactus Green'],
	[351,  3, 'Coco Beans'],
	[351,  4, 'Lapis Lazuli'],
	[351,  5, 'Purple Dye'],
	[351,  6, 'Cyan Dye'],
	[351,  7, 'Light Gray Dye'],
	[351,  8, 'Gray Dye'],
	[351,  9, 'Pink Dye'],
	[351,  10, 'Lime Dye'],
	[351,  11, 'Dandelion Yellow'],
	[351,  12, 'Light Blue Dye'],
	[351,  13, 'Magenta Dye'],
	[351,  14, 'Orange Dye'],
	[351,  15, 'Bone Meal'],
	[352,  0, 'Bone'],
	[353,  0, 'Sugar'],
	[354,  0, 'Cake'],
	[2256, 0, 'Gold Music Disc'],
	[2257, 0, 'Green Music Disc'],
]

invmap = \
	[(x, 'quick') for x in range(0,9)] + \
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

itemdb = ItemDB(data= itemsdb_data, cols=['id', 'damage', 'name'], id='id')

class MCPlayerEditError(Exception):
	pass

class MCPlayerEdit(icmd.ICmdBase):
	def __init__(self, helptext_prefix = '', helptext_suffix = '', batch=False):
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
				raise MCPlayerEditError(2, "Unknown platform. Can't load by world number. Please specify full path")
			if hasattr(self, 'world'):
				self.icmd.prompt = 'World %i> ' % (self.world)
		except ValueError:
			# Try to load world by full path
			self.filename = filename

		try:
			self.level = nbt.load(self.filename)
		except IOError, e:
			if e.errno == 2:
				raise MCPlayerEditError(3, "Invalid filename or worldnumber. Couldn't open '%s'." % (self.filename))
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
					item = itemdb.nbt_to_name(inventory[slot[0]])
					if not item:
						print '%2i x %s' % (inventory[slot[0]]['Count'].value, 'Unknown?')
					else:
						print '%2i x %s' % (inventory[slot[0]]['Count'].value, item['name'])
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

		Sometimes multiple items have the same ID. If you select such an item
		by id, you will be given an additional option menu from which you can
		chose which item you want.

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
			raise MCPlayerEditError(5, 'Invalid count number. Must be in range 1 - 64')

		# Find out which item the user is trying to add
		itemid = None
		add_item = None
		try:
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
			rows = itemdb.select(lambda row: row['name'].lower() == item.lower())
			if rows:
				add_item = rows[0]

		if not add_item:
			raise MCPlayerEditError(6, "Unknown item '%s'. Use the `items` command for list a possible items. You may specify an ID or the item name" % (item))

		assignedslots = self._invadd([(count, add_item['id'], add_item['damage'])])
		self._output("Added %i x %s in slot %i" % (count, add_item['name'], assignedslots[0]))

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
			items = itemdb.select(lambda row: search in row['name'].lower(), cmp)
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
		given, defaults to the normal dimension. 'y' is the height. 
		
		CAREFUL: You can easily warp yourself into blocks, which will cause you
		to die!
		"""
		self._checkloaded()

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
