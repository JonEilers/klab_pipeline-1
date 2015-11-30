import os

from qsub import Qsub


def slice_it(script_cmd_list, file_number):
    sub_lists = []
    start = 0
    for i in xrange(file_number):
        stop = start + len(script_cmd_list[i::file_number])
        sub_lists.append(script_cmd_list[start:stop])
        start = stop
    return (sub_lists)


homepath = os.path.dirname(os.path.realpath(__file__))
working_dir = homepath + '/data/ETSP_COG_SSU/'
qsub_file_path = working_dir + 'qsub_batch/'
jplace_dir = working_dir + 'jplace_split/'
dir_out = working_dir
conf_file = working_dir + 'lineage_2.0/COG_SSU_placements_with_lineage.tsv'
unkn_file = ''

# Create qsub file directory
supplementary_file_list = os.listdir(working_dir)
if supplementary_file_list.count('qsub_batch') == 0:
    os.system('mkdir ' + working_dir + 'qsub_batch')
# Create SBE QSUB BATCH scripts from the jplace file list
jplace_file_list = [root + jfile for root, dirs, jfiles in os.walk(jplace_dir)
                    for jfile in jfiles if jfile.split('.')[-1].find('jplace') != -1]
# and root == jplace_dir]
script_cmd_list = []
file_number = 200
for jfile in jplace_file_list:
    script_cmd = ' '.join(['python', homepath + '/domMAP.py', '--file', jfile,
                           '--dir-out', dir_out, '--lineage', conf_file
                           ])
    script_cmd_list.append(script_cmd)
# break the script commands into [file_number] of qsub scripts
sub_lists = slice_it(script_cmd_list, file_number)
for script_cmd_list in sub_lists:
    file_name = 'qsub_' + str(sub_lists.index(script_cmd_list))
    qsub_file = Qsub(qsub_file_path, script_cmd_list, file_name)
    print qsub_file.Batch_builder()

qsub_file_list = os.listdir(qsub_file_path)
for qsub_file in qsub_file_list:
    if qsub_file.find('.sh') != -1:
        os.system('qsub ' + qsub_file_path + qsub_file)
        print qsub_file, 'has been sent to the cluster...'
