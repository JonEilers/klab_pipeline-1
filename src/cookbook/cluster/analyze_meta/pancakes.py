from os import walk, path, chdir, environ
import json
from shutil import copyfile
from subprocess import Popen
from time import sleep 

search_place = '/home/mclaugr4/open2all/search_place.sh'
search_name = search_place.rsplit('/', 1)[1]
htc_sub = '/home/mclaugr4/open2all/search_place.sub'
htc_name = htc_sub.rsplit('/', 1)[1]
home_path = path.dirname(path.realpath(__file__))
my_env = environ.copy()

for root, dirs, files in walk('silva50_analysis'): # This is a magic value
	for file in files:
		if 'control.json' in file:
			full_root = path.abspath(root)
			full_json = path.join(root, file)
			with open(full_json, 'r') as control_data:
				data = json.load(control_data)
			new_search = path.join(root, search_name)
			with open(new_search, 'w') as o:
				with open(search_place, 'r') as r:
					for line in r:
						o.write(line.replace('{refpkg}', data['refpkg']).replace('{title}', data['title']))
			copyfile(htc_sub, path.join(root, htc_name))
			chdir(full_root)
			sleep(1)
			perms = Popen(' '.join(['chmod', '-R', '777', full_root]), shell=True)
			proc = Popen(' '.join(['condor_submit', path.join(full_root, htc_name)]), shell=True, env=my_env)
			sleep(1)
			chdir(home_path)
			sleep(1)
