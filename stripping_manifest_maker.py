
import cmd

PLATFORMS = ( "x86-win32", "x86_64-win32", "x86_64-osx", "x86_64-linux", "js-web", "armv7-android", "armv7-ios", "arm64-ios" )
WINPLATFORMS = { "x86-win32": "x86-win32", "x86_64-win32": "x86_64-win32" }
TAB = "    " # use tabs initially, then go through and replace them all with four spaces
OPENER = "platforms:" # file opening line (after any title or comments)
PLAT_OPEN = "\t\tcontext:\n" # opening line for each platform
DEFAULT_PATH = "my_test.appmanifest"

OPTIONS = {
	"physics": { "excludeLibs": ["BulletDynamics", "BulletCollision", "LinearMath", "Box2D", "physics"], "excludeSymbols": [], "libs": ["physics_null"] },
	"record": { "excludeLibs": ["record", "vpx"], "excludeSymbols": [], "libs": ["record_null"] },
	"profiler": { "excludeLibs": ["profilerext"], "excludeSymbols": ["ProfilerExt"], "libs": [] },
	"facebook": { "excludeLibs": [], "excludeSymbols": ["FacebookExt"], "libs": [] },
	"release": { "excludeLibs": ["engine"], "excludeSymbols": [], "libs": ["engine_release"] },
	"headless": { # includes recorder
		"excludeLibs": ["graphics", "sound", "record", "vpx", "tremolo", "hid"],
		"excludeSymbols": ["DefaultSoundDevice", "AudioDecoderWav", "AudioDecoderStbVorbis", "AudioDecoderTremolo"],
		"libs": ["graphics_null", "sound_null", "record_null", "hid_null"]
	}
}

options = [] # list of currently enabled options

def find(l, v):
	for i in range(len(l)):
		if l[i] == v:
			return i

def assemble_data(options):
	# options is a list of string options to use
	# Turn list of option names into lists of excludeLibs, excludeSymbols, and libs
	data = { "excludeLibs": [], "excludeSymbols": [], "libs": [] }
	for opt in options:
		# for each listed option, get its excludeLibs, excludeSymbols, and libs from 'OPTIONS' and add them to 'data'
		if opt in OPTIONS:
			optionData = OPTIONS[opt]
			for listType in optionData.keys(): # listType = "excludeLibs", "excludeSymbols", or "libs"
				for i in range(len(optionData[listType])):
					flag = optionData[listType][i]
					fs = '"%s", ' % (flag)
					if find(data[listType], fs) is None: # don't make duplicates
						# format flag with quotes, comma, and space, and add to list
						data[listType].append(fs)
		else:
			print("ERROR - assemble_data - invalid option: " + opt)
	return data

# All platforms except windows use the exact same flags.
# On windows there are basically the same, but with some "lib"s added
def windowsify_flags(flaglist, flagtype):
	if flagtype == "excludeSymbols": # "excludeSymbols" are unchanged
		return flaglist
	else:
		f = flaglist[0:len(flaglist)] # copy flaglist
		for i in range(len(f)):
			v = f[i].replace('"', '"lib', 1) # add '"lib' to front in place of '"'
			if flagtype == "libs":
				v = v[:-3] + '.lib", ' # add '.lib", ' to end in place of '", '
			f[i] = v
		return f

def make_manifest(options):
	data = assemble_data(options)
	filestr = OPENER
	for platstring in PLATFORMS:
		pstr = '\t%s:\n%s' % (platstring, PLAT_OPEN)
		for flagtype in ("excludeLibs", "excludeSymbols", "libs"):
			f = data[flagtype]
			if platstring in WINPLATFORMS:
				f = windowsify_flags(data[flagtype], flagtype)
			flaglist = "".join(f) # concatenate list of flag strings
			flaglist = flaglist[0:-2] # remove trailing comma and space
			pstr = "%s\t\t\t%s: [%s]\n" % (pstr, flagtype, flaglist) # add in line for this flag type
		filestr = filestr + "\n" + pstr # add platform string to file string, with newline before it
	filestr = filestr.replace("\t", TAB) # replace all tab characters with four spaces
	return filestr

def write_file(path, filestr):
	f = open(path, "w")
	f.write(filestr)
	f.close()
	print("...manifest file written.")

class ManifestMaker(cmd.Cmd):

	intro = "Welcome to Ross's appmanifest Maker \n\t type 'help' for a list of commands. \n\t press Ctrl-z or type 'quit' to quit."
	prompt = "(Manifest Maker): "
	ruler = "-"

	def do_options(self, line):
		"""options():
    Prints a list of available options."""
		print("The available options are: ")
		for opt in OPTIONS.keys():
			print("\t" + opt)

	def do_show_enabled(self, line):
		"""show_enabled():
    Prints the list of currently enabled options."""
		print("The currently enabled options are: ")
		if options:
			for opt in options:
				print("\t" + opt)
		else:
			print("No options are currently enabled.")

	def do_enable_option(self, opts):
		"""enable_option(option):
    Adds the specified option(s) to the list of enabled options.
    Separate multiple options with a comma and a space.
    See the 'options' command for a list of available options."""
		optlist = opts.split(", ")
		for o in optlist:
			if o in OPTIONS:
				if find(options, o) is None:
					options.append(o)
					print("...option '%s' enabled" % (o))
				else:
					print("...option '%s' is already enabled" % (o))
			else:
				print("...invalid option: " + o)
		print("Enabled options are now: ", options)

	def do_disable_option(self, opts):
		"""disable_option(option):
    Removes the specified option(s) from the list of enabled options.
    Separate multiple options with a comma and a space.
    See the 'options' command for a list of available options."""
		optlist = opts.split(", ")
		for o in optlist:
			if o in OPTIONS:
				if find(options, o) is not None:
					options.remove(o)
					print("...option %s removed." % (o))
				else:
					print("...option '%s' is not enabled" % (o))
			else:
				print("...invalid option: " + o)
		print("Enabled options are now: ", o)


	def do_make_manifest(self, line):
		"""make_manifest([filepath]):
    Makes an appmanifest with the currently enabled options.
    Specify a filename/path for the file, or it will use a preset default path."""
		path = DEFAULT_PATH
		if line:
			path = line
			print("...using specified path: " + line)
		else:
			print("...no path specified, using default path: " + DEFAULT_PATH)
		write_file(path, make_manifest(options))

	def do_exit(self, line):
		return True

	def do_quit(self, line):
		return True

	def do_EOF(self, line):
		return True

if __name__ == '__main__':
	ManifestMaker().cmdloop()