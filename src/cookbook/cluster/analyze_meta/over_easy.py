import sys
from os import listdir, makedirs, chdir, chmod, walk, stat
from os.path import exists, dirname, realpath
from shutil import copy
from subprocess import Popen
import stat as Stat


def makedir(path, dir_name):
	direct = '/'.join([path,dir_name])
	if not exists(direct):
		makedirs(direct)
	return direct

def path_joiner(path1, path2):
	joined = '/'.join([path1, path2]) 
	return joined

def mod_shell(arg_dict, src, dest):
	with open(src,'r') as o:
		data = o.readlines()
	new_list = []
	for line in data:
		line = line.rsplit('\n',1)[0]
		if line in arg_dict.keys():
			new_line = ''.join([line,'=','\"',arg_dict[line],'\"'])
			new_list.append(new_line)
		else:
			new_list.append(line)
	with open(dest,'w') as r:
		r.write('\n'.join(new_list))
	st = stat(dest)
	chmod(dest, st.st_mode | Stat.S_IEXEC)

def condor_sub(cmd_list):
	for cmd in cmd_list:
		chdir(cmd[1].rsplit('/',1)[0])
		print cmd
		proc = Popen(' '.join(cmd), shell=True, stdin=None,
			stdout=None, stderr=None, close_fds=True)
		chdir(home_path)

# magic values
home_path = dirname(realpath(__file__))
fasta_path = path_joiner(home_path,'preprocessing')
MN_sub = 'make_nest_HTC.sub.temp'
MN_shell = 'make_nest_HTC.sh.temp'
refpkg_dir = path_joiner(home_path,'silva500_taxpkgs')

# create analysis directory
anal_name = 'silva500_analysis'
anal_path = makedir(home_path, anal_name)

# list all fasta files for analysis
fasta_list = [f for f in listdir(fasta_path) if f.find('.fasta') != -1
	]
con_list = []
for fasta in fasta_list:
	fa_path = path_joiner(fasta_path, fasta)
	run_name = fasta.split('.')[0]
	run_path = makedir(anal_path, run_name)
	MN_sub_dest = path_joiner(run_path, MN_sub.rsplit('.',1)[0])
	MN_shell_dest = path_joiner(run_path, MN_shell.rsplit('.',1)[0]) 
	copy(MN_sub, MN_sub_dest)
	run_dict = {'REFPKG_DIR':refpkg_dir, 'FASTA_FILE_PATH':fa_path, 'RUNDIR':run_path}
	mod_shell(run_dict, MN_shell, MN_shell_dest)
	con_cmd = ['condor_submit', MN_sub_dest]
	print MN_sub_dest
	con_list.append(con_cmd)

#condor_sub(con_list)