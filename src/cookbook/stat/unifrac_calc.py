import subprocess
from os import path, listdir
import sys


def run_unifrac(jplace_list, out_dir):
	subprocess.check_output(
		'guppy', 'unifrac', '--csv', '--out-dir', out_dir, ' '.join(jplace_list)
		)


j_dir = sys.argv[1]
j_file_list = listdir(j_dir)
j_dict = {}
for j_file in j_file_list:
	