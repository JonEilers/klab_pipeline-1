#!/usr/bin/env python

import os, sys

jplace_path = sys.argv[1]
jplace_split_out_path = sys.argv[2]

split_list = str(sys.argv[3]).split(',')

jplace_file_list = os.listdir(jplace_path)
# jplace_split_list = os.listdir(jplace_split_out_path)

for jplace_file in jplace_file_list:
    for index in range(0, len(split_list)):
        keep_value = split_list[index]
        guppy_cmd = 'guppy filter -Ir ' + keep_value
        for index_2 in range(0, len(split_list)):
            if index != index_2:
                remove_value = split_list[index_2]
                guppy_cmd = guppy_cmd + ' -Er ' + remove_value
        guppy_cmd = str(guppy_cmd + ' ' + os.path.join(jplace_path, jplace_file) + ' -o ' +
                        os.path.join(jplace_split_out_path,
                                     jplace_file.split('/')[-1].split('.')[0] + '.' + keep_value + '.jplace')
                        )
        print guppy_cmd
        os.system(guppy_cmd)
