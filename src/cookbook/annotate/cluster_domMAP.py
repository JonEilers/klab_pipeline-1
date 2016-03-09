#!/usr/bin/env python

from os import walk, listdir, path
import sys
from subprocess import call, Popen

def slice_it(script_cmd_list, file_number):
    sub_lists = []
    start = 0
    for i in xrange(file_number):
        stop = start + len(script_cmd_list[i::file_number])
        sub_lists.append(script_cmd_list[start:stop])
        start = stop
    return (sub_lists)


working_dir = sys.argv[1]
jplace_dir = sys.argv[2]
conf_file = sys.argv[3]

HTC_file_path = path.join(working_dir, 'HTC_batch')
dir_out = working_dir

# Create HTC file directory
supplementary_file_list = listdir(working_dir)
if supplementary_file_list.count('HTC_batch') == 0:
    call(['mkdir', path.join(working_dir, 'HTC_batch')])
batch_dir = path.join(working_dir, 'HTC_batch')
# Create SBE HTC BATCH scripts from the jplace file list
jplace_file_list = [path.join(root, jfile) for root, dirs, jfiles in walk(jplace_dir)
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
    file_name = path.join(batch_dir, 'HTC_' + str(sub_lists.index(script_cmd_list)))
    with open(file_name, 'w') as o:
        o.write('\n'.join(script_cmd_list))
'''
HTC_file_list = listdir(HTC_file_path)
for HTC_file in HTC_file_list:
    if HTC_file.find('.sh') != -1:
        proc = Popen(' '.join(['condor_run', path.join(HTC_file_path, HTC_file)]), shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
        print HTC_file, 'has been sent to the cluster...'
'''