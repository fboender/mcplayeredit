#!/usr/bin/python

#
# TODO:
# - Currently can't specify the history file.
# -  File "/home/todsah/Development/mcplayeredit/lib/icmd.py", line 97, in _help_getspecifics
#    help_short, help_desc = doc[0], '\n  '.join(doc[1:]) (EMPTY DOC STRING)

#

"""
ICmd is a wrapper library for easily creating interactive commandline programs.
You simply create a class that inherits from the ICmdBase class and create a
new ICmd instance with that class.

ICmd will automatically use readline if it is available, giving you a history
and tab-completion of commands. The ICmd class will get input from the user and
then run methods on the root class you passed to its constructor.

Example:

	class ICmdTest(ICmdBase):
		def load(self, fname):
			self.fname = fname
			print "Loading %s" % (self.fname)

		def save(self):
			fname = getattr(self, 'fname', None)
			print "Saving %s" % (fname)

		def test(self, required, optional='optional'):
			logging.info("Test: required=%s, optional=%s" % (required, optional))

	icmd = ICmd(ICmdTest)
	icmd.run()

NOTES:

	You can NOT use method decorators, as ICmd does introspection of the
	methods in the derived class.
"""

import sys
import os
import inspect
import re
import logging

# Try to load the clusterfuck that is readline. THANKS GNU!
try:
	# See if we can load PyReadline (an almost pure Python implementation of
	# readline for windows)
	import pyreadline as readline
except ImportError:
	pass

try:
	# Lets try the Unix readline version.
	import readline
except ImportError:
	pass

class ICmdBase(object):
	"""
	Base class for ICmd commandline classes. Inherit from this class to get
	default commands in your commandline application.
	"""
	def __init__(self, helptext_prefix = '', helptext_suffix = '', batch=False):
		self.helptext_prefix = helptext_prefix
		self.helptext_suffix = helptext_suffix
		self.batch = batch

	def help(self, command=None):
		"""
		Display help
		Displays all available commands or specific help for COMMAND if given.
		"""
		if command:
			# Display command-specific help
			try:
				func = getattr(self, command)
			except AttributeError, e:
				raise ICmdError(1, "No such command: '%s'. Type 'help [command]' for help." % (command))

			if not command.startswith('_') and callable(func):
				help = self._help_getspecifics(command)
				self._output("%s: %s" % (command, help[0]))
				self._output("Usage: %s\n" % (help[2]))
				for line in help[1].splitlines():
					self._output("  %s" % (line))
				self._output('')
		else:
			# Display all available commands
			self._output(self.helptext_prefix)
			for cmd in dir(self):
				if not cmd.startswith('_') and callable(getattr(self, cmd)):
					help = self._help_getspecifics(cmd)
					self._output('  %10s: %s' % (cmd, help[0]))
			self._output(self.helptext_suffix)

	def _help_getspecifics(self, command):
		help_short = ''
		help_desc = ''
		help_usage = ''

		# Get short and full descriptions from the function's docstring.
		func = getattr(self, command)
		if func.__doc__:
			for line in func.__doc__.strip().splitlines():
				if line.lower().strip().startswith('usage:'):
					help_usage = line[8:].strip()
				elif not help_short:
					help_short = line.strip()
				else:
					help_desc += "%s\n" % (line.strip())

		# Get usage from the parameters
		if not help_usage:
			args = inspect.getargspec(func)

			parcnt_max = len(args.args) - 1
			parcnt_min = len(args.args) - 1 - len(args.defaults or '')
			help_usage = command
			for i in range(1, len(args.args)):
				if i <= parcnt_min:
					help_usage += " <%s>" % (args.args[i])
				else:
					help_usage += " [%s]" % (args.args[i])

		return([help_short.strip(), help_desc.strip(), help_usage.strip()])

	def quit(self):
		"""
		Exit the program.
		Exit the program. Does not save any changes!
		"""
		raise SystemExit()

	exit = quit
	exit.__doc__ = exit.__doc__

	def _output(self, line):
		if not self.batch:
			sys.stdout.write(line + '\n')

	def _error(self, line):
		sys.stderr.write(line + '\n')

class ICmdError(Exception):
	pass

class ICmd(object):
	"""
	Interactive/Batch Commandline interface. Given a class that overloads the
	ICmdBase class, provide an interactive commandline to control that class.
	"""

	def __init__(self, rootclass, prompt='> ', histfile=os.path.join(os.environ.get('HOME', ''), '.icmd_hist'), welcometext='Type \'help\' for help.', helptext_prefix='The following commands are available:\n', helptext_suffix='\n(type \'help <command>\' for details)\n', batch=False):
		"""
		Create a new interactive commandline interface to rootclass by creating
		an instance of rootclass (your class must derive from ICmdBase). Use
		ICmd.run() or run_once() to start the commandline client. `batch`
		indicates wether to run in batch mode. If so, ICmd is silent (except
		for errors) and non-interactive; instead reading from stdin and
		executing each line as a command. It will exit after no more lines are
		available.
		"""
		self.rootclass = rootclass
		self.prompt = prompt
		self.welcometext = welcometext
		self.batch = batch
		self.histfile = histfile
		self.instclass = self.rootclass(helptext_prefix, helptext_suffix, self.batch)

		# Initialize readline, but only if we we're able to load the module.
		if 'readline' in sys.modules or 'pyreadline' in sys.modules:
			logging.info("Using readline")
			try:
				readline.read_history_file(self.histfile)
			except IOError:
				pass
			logging.info("Setting readline completer")
			readline.set_completer(self._completer)
			readline.parse_and_bind("tab: complete")

		if not self.batch:
			sys.stdout.write(welcometext + '\n')

	def dispatch(self, cmd, params=[]):
		"""
		Run `cmd` on the rootclass. `cmd` must be an existing callable in
		rootclass. Raises ICmdErrors in case of problems with the command (no
		such command, too many/few parameters).
		"""
		logging.info("Dispatching %s %s" % (cmd, str(params)))
		try:
			func = getattr(self.instclass, cmd)
			getattr(func, '__call__') # Test callability
		except AttributeError, e:
			raise ICmdError(1, "No such command: '%s'. Type 'help [command]' for help." % (cmd))

		# Introspect how many arguments the function takes and how many the
		# user gave.


		args = inspect.getargspec(func)

		parcnt_given = len(params)
		parcnt_max = len(args.args) - 1
		parcnt_min = len(args.args) - 1 - len(args.defaults or '')
		logging.info("dispatch: params: given: %i, min: %i, max: %i" % (parcnt_given, parcnt_min, parcnt_max))
		if parcnt_given < parcnt_min:
			raise ICmdError(2, 'Not enough parameters given')
		elif not args.varargs and parcnt_given > parcnt_max:
			raise ICmdError(3, 'Too many parameters given')

		return(func(*params))

	def _completer(self, text, state):
		"""
		Readline completer. Scans the Command object instance for member
		functions that match. Returns the next possible completion requested
		(state).
		"""
		logging.info("Completing '%s' '%s'" % (text, state))
		w = [cmd for cmd in dir(self.instclass) if cmd.startswith(text) and not cmd.startswith('_') and callable(getattr(self.instclass, cmd))]
		try:
			return(w[state])
		except IndexError:
			return None

	def run_once(self, catcherrors=True):
		"""
		Ask the user for a single line of input and run that command. Returns
		the returned result of the command callable (i.e. the return value of
		the function in rootclass). Multiple commands may be given by
		delimiting them with a semi-colon. In this case, a list of outputs is
		returned.
		"""
		inputline = raw_input(self.prompt)
		output = []
		if inputline:
			cmdlines = inputline.split(';') # Allow for multiple commands on one line, delimited with ';'
			for cmdline in cmdlines:
				parts = cmdline.split()
				cmd = parts.pop(0)
				params = parts
				output.append(self.dispatch(cmd, params))
			# Backwards compatible. If multiple commands where given (delimited
			# with ';'), return a list of return values from each call.
			# Otherwise, return just one return value.
			if len(output) == 1:
				return(output[0])
			else:
				return(output)
		else:
			return(False)

	def run(self, catcherrors=True):
		"""
		Continually ask the user for lines of input and run those commands.
		Catches all ICmdErrors and displays those errors. Catches
		KeyboardInterrupt and SystemExit exceptions in order to clean up
		readline. Returns True if the player quit the application by typing
		'quit' or 'exit'. Doesn't return anything (None) otherwise.
		"""
		if self.batch:
			self.prompt = ''

		try:
			while True:
				if catcherrors:
					try:
						self.run_once()
					except ICmdError, e:
						sys.stderr.write('%s\n' % (e.args[1]))
						logging.info("ICmd.run intercepted an error: %s" % (e))
					except EOFError, e:
						break
				else:
					self.run_once()
		except (SystemExit, KeyboardInterrupt):
			if 'readline' in sys.modules or 'pyreadline' in sys.modules:
				logging.info("Writing readline command history")
				readline.write_history_file(self.histfile)

		return(True)

if __name__ == "__main__":
	class ICmdTest(ICmdBase):
		def load(self, fname):
			"""
			Load a file
			Load the file indicated by FNAME.
			"""
			self.fname = fname
			print "Loading %s" % (self.fname)

		def save(self):
			"""
			Save loaded file
			Save changed made to the file loaded with the 'load' command.
			"""
			fname = getattr(self, 'fname', None)
			print "Saving %s" % (fname)

		def test(self, required, optional='optional'):
			"""
			Parameter tests
			Some parameter tests with a non-optional and optional parameter.
			Also a two-line help description.
			"""
			logging.info("Test: required=%s, optional=%s" % (required, optional))

	#logging.getLogger().level = logging.INFO
	icmd = ICmd(ICmdTest, batch=False)
	icmd.run()

	#icmd.dispatch('load', ['foo'])
	#icmd.dispatch('save')
