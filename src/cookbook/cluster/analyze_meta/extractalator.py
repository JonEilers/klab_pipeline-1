from os import walk, makedirs
from os.path import dirname, realpath, sep, exists
from shutil import copyfile

# DEFINITIONS
def path_joiner(path1, path2):
	joined = '/'.join([path1, path2]) 
	return joined

def path_joiner(path1, path2):
	joined = '/'.join([path1, path2]) 
	return joined

def makedir(path, dir_name):
	direct = path_joiner(path,dir_name)
	if not exists(direct):
		makedirs(direct)
	return direct

def copy_file(src, dst):
	copyfile(src, dst)
	return str(dst)


# magic values
home_path = dirname(realpath(__file__))
anal_name = 'analysis'
anal_path = path_joiner(home_path,anal_name)
sub = '.jplace'
extract_name = 'place_files'
extract_path = makedir(home_path, extract_name)


for root, dir, files in walk(anal_path, topdown=True):
	max_depth = max([r.count(sep) for r,d,f in walk(anal_path, topdown=True)])
	depth = root.count(sep)
	if depth == max_depth:
		try:
			jplace_file = path_joiner(root, [j for j in files if sub in j][0])
			new_file = path_joiner(extract_path, root.split('/')[-2] + sub)
			copy_jplace = copy_file(jplace_file, new_file)
		except:
			pass # maybe add a message, but not required	
