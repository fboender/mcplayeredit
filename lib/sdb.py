# Copyright (c) 2010 Ferry Boender
# 
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

__VERSION__ = (0, 1)

class SDB(object):
	"""
	SimpleDB

	Examples:
	>>> data = [
	...   ['tom', 18, 'Student'],
	...   ['dick', 65, 'Retired'],
	...   ['harry', 30, 'Unemployed'],
	...   ['seymore', 20, 'Student'],
	... ]
	>>> sdb = SDB(data=data, cols=['name', 'age', 'occupation'], id='name')

	# Select by ID
	>>> sdb.get('tom')
	{'age': 18, 'name': 'tom', 'occupation': 'Student'}

	# Select all rows where occupation is 'Student'
	>>> sdb.select(lambda row: row['occupation'] == 'Student')
	[{'age': 18, 'name': 'tom', 'occupation': 'Student'}, {'age': 20, 'name': 'seymore', 'occupation': 'Student'}]

	# Select all rows where age < 65. Sort by age
	>>> sdb.select(lambda row: row['age'] < 65, lambda a, b: cmp(a['age'], b['age']))
	[{'age': 18, 'name': 'tom', 'occupation': 'Student'}, {'age': 20, 'name': 'seymore', 'occupation': 'Student'}, {'age': 30, 'name': 'harry', 'occupation': 'Unemployed'}]

	# Save
	>>> sdb.save('occup.dat')

	# Load from file
	>>> sdb = SDB(path='occup.dat', cols=['name', 'age', 'occupation'], id='name', col_types=[str, int, str])
	>>> for row in sdb:
	...   print row
	{'age': 18, 'name': 'tom', 'occupation': 'Student'}
	{'age': 65, 'name': 'dick', 'occupation': 'Retired'}
	{'age': 30, 'name': 'harry', 'occupation': 'Unemployed'}
	{'age': 20, 'name': 'seymore', 'occupation': 'Student'}

	# Insert
	>>> sdb.insert(['claus', 350, 'Jolly man'])

	# Select all rows where age > 60 and name contains 't'.
	>>> sdb.select(lambda row: row['age'] > 60 or 't' in row['name'])
	[{'age': 18, 'name': 'tom', 'occupation': 'Student'}, {'age': 65, 'name': 'dick', 'occupation': 'Retired'}, {'age': 350, 'name': 'claus', 'occupation': 'Jolly man'}]

	# Update all rows where name == 'tom', set age to 20 and occupation to 'Junior Developer'
	>>> sdb.update({'age': 20, 'occupation': 'Junior Developer'}, lambda row: row['name'] == 'tom')

	# Select a single row by ID
	>>> sdb.get('tom')
	{'age': 20, 'name': 'tom', 'occupation': 'Junior Developer'}

	# Select a single row by muliple fields (values must exactly match)
	>>> sdb.getx(name='seymore', occupation='Student')
	{'age': 20, 'name': 'seymore', 'occupation': 'Student'}

	# Delete all rows where age < 30
	>>> sdb.delete(lambda row: row['age'] < 30)

	# Select all rows
	>>> sdb.select()
	[{'age': 65, 'name': 'dick', 'occupation': 'Retired'}, {'age': 30, 'name': 'harry', 'occupation': 'Unemployed'}, {'age': 350, 'name': 'claus', 'occupation': 'Jolly man'}]

	# Cleanup
	>>> os.unlink('occup.dat')
	"""
	def __init__(self, path=None, data=None, sep=',', id=None, cols=[], col_types=None):
		self.path = path
		self.sep = sep
		self.cols = cols
		self.id = id
		self.col_types = col_types

		self.data = []
		self.id_key = None

		# If user specified data as a parameter, set it. Otherwise, if the user
		# specified a path to a file, read data from that file.
		if data:
			self.data = data
		elif path:
			self.load(path)
		else:
			self.data = []

		# Resolve the id
		if id:
			try:
				self.id_index = self.cols.index(id)
			except ValueError:
				self.id_index = id
		else:
			self.id = 0
			self.id_index = 0

	def load(self, path):
		"""
		Load data from a file. Uses `self.sep` and `self.col_types`.
		"""
		self.data = []
		with open(path) as f:
			for line in f:
				cols = line.rstrip().split(self.sep)
				if self.col_types:
					self.data.append([f(x) for f, x in zip(self.col_types, cols)])
				else:
					self.data.append(cols)

	def save(self, path=None):
		"""
		Save data to a file. Uses `self.sep` and `self.col_types`.
		"""
		if not path:
			path = self.path
		else:
			self.path = path

		if not path:
			raise IOError("Invalid filename '%s'" % (path))

		with file(path, 'w') as f:
			for row in self.data:
				f.write(self.sep.join([str(col) for col in row]) + '\n')

	def get(self, id):
		"""
		Get a row by its id (`self.id`)
		"""
		for row in self.data:
			if row[self.id_index] == id:
				return(self._make_drow(row))

	def getx(self, **kwargs):
		"""
		Get a row by multiple columns
		"""
		for row in self.data:
			match = True
			for colname, value in kwargs.items():
				if row[self.cols.index(colname)] != value:
					match = False
			if match:
				return(self._make_drow(row))

	def select(self, select_cb=None, sort_cb=None):
		"""
		Select data using a callback function `select_cb` which should return
		True or False if the row should be included in the results. `sort_cb`
		can be used as a sorting callback. See help documentation for the SDB
		class for examples.
		"""
		results = []
		for row in self.data:
			drow = self._make_drow(row)
			if not select_cb or select_cb(drow):
				results.append(drow)
		if sort_cb:
			results.sort(sort_cb)
		return(results)

	def insert(self, values):
		self.data.append(values)

	def update(self, values, select_cb):
		for i in range(0, len(self.data)):
			row = self.data[i]
			drow = self._make_drow(row)
			if select_cb(drow):
				for key, value in values.items():
					if self.cols:
						row[self.cols.index(key)] = value
					else:
						row[key] = value

	def delete(self, select_cb):
		for i in range(len(self.data), 0, -1):
			if select_cb(self._make_drow(self.data[i-1])):
				self.data.pop(i-1)

	def _make_drow(self, row):
		"""
		Turn a row into a dictionary mapping if column names are available.
		"""
		if self.cols:
			return(dict(zip(self.cols, row)))
		else:
			return(row)

	def __iter__(self):
		for row in self.data:
			yield self._make_drow(row)

if __name__ == '__main__':
	import doctest, os
	doctest.testmod()
