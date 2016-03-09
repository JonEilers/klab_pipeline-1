import os
import sys
from cookbook.junk_drawer.HTC import HTC


def slice_it(script_cmd_list, file_number):
    sub_lists = []
    start = 0
    for i in xrange(file_number):
        stop = start + len(script_cmd_list[i::file_number])
        sub_lists.append(script_cmd_list[start:stop])
        start = stop
    return (sub_lists)


homepath = os.path.dirname(os.path.realpath(__file__))
working_dir = sys.argv[1]
HTC_file_path = os.path.join(working_dir, 'HTC_batch')
jplace_dir = os.path.join(working_dir, 'jplace_files')
dir_out = working_dir
conf_file = os.path.join(working_dir, 'COG_SSU_placements_with_lineage.tsv')

# Create HTC file directory
supplementary_file_list = os.listdir(working_dir)
if supplementary_file_list.count('HTC_batch') == 0:
    os.system('mkdir ' + working_dir + 'HTC_batch')
# Create SBE HTC BATCH scripts from the jplace file list
jplace_file_list = [root + jfile for root, dirs, jfiles in os.walk(jplace_dir)
                    for jfile in jfiles if jfile.split('.')[-1].find('jplace') != -1]
script_cmd_list = []
file_number = 200
for jfile in jplace_file_list:
    script_cmd = ' '.join(['domMAP.py', '--file', jfile,
                           '--dir-out', dir_out, '--lineage', conf_file
                           ])
    script_cmd_list.append(script_cmd)
# break the script commands into [file_number] of HTC scripts
sub_lists = slice_it(script_cmd_list, file_number)
for script_cmd_list in sub_lists:
    file_name = 'HTC_' + str(sub_lists.index(script_cmd_list))
    with open(file_name, 'w') as o:
        o.write('\n'.join(script_cmd_list))

HTC_file_list = os.listdir(HTC_file_path)
for HTC_file in HTC_file_list:
    if HTC_file.find('.sh') != -1:
        proc = Popen(' '.join(['condor_run', path.join(HTC_file_path, HTC_file)]), shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        print HTC_file, 'has been sent to the cluster...'
