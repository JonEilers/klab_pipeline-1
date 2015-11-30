#! /usr/bin/env python
'''
### LINGEAGE ###
The main input of this script are jplace files from the
Phylogenetic Analysis Framework (PAF) developed by
Erick Matsen and Robin Kodner.

Purpose:
To add taxonomic information to the placements which is
otherwise not able to be appended or used by the PAF.

Creatior: Ryan J. McLaughlin
Last Updated: 12/10/2014

Required input files:
	1. jplace files from the PAF
	2. guppy executable [http://matsen.fhcrc.org/pplacer/builds/pplacer-v1.1-Linux.tar.gz]
	3. NCBI Taxonomy DB dump [ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz]
	Note: The script should identify missing files and attempt to automatically
		downloac them from online resouncres.

Output:
	Currently lineage outputs a comma-sepatated variable (.csv)
	file, which contains either "confident", "unknown", or "junk"
	placements.
'''

from os import listdir, system, walk, popen
from os.path import dirname, realpath, join
from fnmatch import filter

import argparse

import sys


def is_guppy(lin_work_path):
    # check to be sure the guppy executable is in the lineage working directory
    guppy_path = False
    for root, dirs, files in walk(lin_work_path):
        for file in filter(files, 'guppy'):
            guppy_path = join(root, file)
    # download guppy to lineage_work directory
    if guppy_path == False:
        print 'guppy was not found, a copy will be downloaded...'
        # download a version of guppy
        system('wget -O ' + lin_work_path +
               'pplacer-v1.1-Linux.tar.gz ' +
               'http://matsen.fhcrc.org/pplacer/builds/pplacer-v1.1-Linux.tar.gz'
               )
        system('tar -zxvf ' +
               lin_work_path +
               'pplacer-v1.1-Linux.tar.gz -C ' +
               lin_work_path +
               ' pplacer-v1.1.alpha16-1-gf748c91-Linux-3.2.0'
               )
        for root, dirs, files in walk(lin_work_path):
            for file in filter(files, 'guppy'):
                guppy_path = join(root, file)
        return guppy_path

    else:
        return guppy_path


def jplace_2_csv(jfile, lin_work_path):
    '''
    very simple, converts jplace files into csv
    uses the guppy to_csv command, but allows for conversion
    with worrying about where a file has placements or not
    RETURNS a list where each value is a line of the csv output
    '''
    guppy_path = is_guppy(lin_work_path)
    # run guppy command on jplace
    convert2csv = popen(guppy_path + ' to_csv ' + jfile).read().split('\n')
    if len(convert2csv) == 1:
        print (jfile, 'Does not have placements and will not be added to the output files...')
    return convert2csv


def set_lin_work_path(workdir):
    '''
    make sure there is a '[CWD]/lineage_work/' directory to
    store all lineage output
    '''
    lin_work_dir_name = 'lineage_work'
    if listdir(workdir).count(lin_work_dir_name) == 0:
        print 'The', lin_work_dir_name, 'directory is required and will be created...'
        system('mkdir ' + workdir + '/' + lin_work_dir_name)
        lin_work_path = workdir + '/' + lin_work_dir_name + '/'
    else:
        lin_work_path = workdir + '/' + lin_work_dir_name + '/'
    return lin_work_path


def make_jfile_list(jdir, jfile):
    '''
    creates a file list from the commands supplied by the user.
    '''
    jfile_list = []
    # If user specifies a file directory for the input .jplace.csv files
    if jdir != False:
        for root, dirs, files in walk(jdir, topdown=True):
            for file in files:
                if file.split('.')[-1].find('jplace') != -1:
                    jfile_list.append(root + '/' + file)
    # If the user only has one file to run
    elif jfile != False:
        if jfile.split('.')[-1].find('jplace') != -1:
            jfile_list = [jfile]

    if len(jfile_list) < 1 or jfile_list == []:
        sys.exit('You did not supply files which can be run through this script...\n'
                 + 'Files must be \".jplace\" files output from the PAF pipeline...\n'
                 )

    return jfile_list


def update_tax(update, lin_work_path):
    '''
    Download and extract the taxdump archive from NCBI Taxonomy FTP, if needed.
    If anything is missing, they are found and placed in the correct location.
    RETURNS the update variable, if something was missing then other files
    might also be missing.
    '''
    if (listdir(lin_work_path).count('names.dmp') == 0
        or listdir(lin_work_path).count('nodes.dmp') == 0
        or listdir(lin_work_path).count('merged.dmp') == 0
        or listdir(lin_work_path).count('delnodes.dmp') == 0
        or update == True):
        if update == True:
            print 'The NCBI Taxonomy archive will be updated...'
            system('wget -O ' + lin_work_path +
                   'taxdump.tar.gz ' +
                   'ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz'
                   )
            system('tar -zxvf ' +
                   lin_work_path +
                   'taxdump.tar.gz -C ' +
                   lin_work_path +
                   ' nodes.dmp names.dmp merged.dmp delnodes.dmp'
                   )
        elif listdir(lin_work_path).count('taxdump.tar.gz') == 0:
            print 'The NCDI Taxonomy archive has not been found, it will be downloaded...'
            system('wget -O ' + lin_work_path +
                   'taxdump.tar.gz ' +
                   'ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz'
                   )
            system('tar -zxvf ' + lin_work_path +
                   'taxdump.tar.gz -C ' + lin_work_path +
                   ' nodes.dmp names.dmp merged.dmp delnodes.dmp'
                   )
            update = True
        elif listdir(lin_work_path).count('taxdump.tar.gz') == 1:
            print 'The NCBI Taxonomy archive is present but not extracted, it will be extacted...'
            system('tar -zxvf ' + lin_work_path +
                   'taxdump.tar.gz -C ' + lin_work_path +
                   ' nodes.dmp names.dmp merged.dmp delnodes.dmp'
                   )
            update = True
    return update


def get_nodes(update, lin_work_path):
    if update == True:
        '''
        Extract all the nodes and their parent nodes from the nodes.dmp
        The nodes and parent nodes populate a dictionary object
        nodes are the dictionary keys and parent nodes are the values of the dictionary
        A "node" is also called a "taxon ID" or "taxid"
        '''
        nodes = lin_work_path + 'nodes.dmp'
        input = open(nodes, 'r')
        tax_dict = {}
        for line in input:
            split_line = line.split('\t|\t')
            taxid = int(split_line[0])
            parent_taxid = int(split_line[1])
            tax_dict[taxid] = parent_taxid
        input.close()
        '''
        Using the tax_dict created above
        A tab-delimited file is created containing a full lineage for each node
        The first value of each line is the node and each value
        following that node is the parent node of the preceding value
        Essentially each line tracks from a node to the highest level, 'root'
        Again, these are also known as "taxon IDs" or "taxids"
        '''
        output = open(lin_work_path + 'full_lineage.txt', 'w')
        for k, v in tax_dict.iteritems():
            full_lineage = []
            taxid = int(k)
            parent = int(v)
            full_lineage.append(str(taxid))
            if taxid == parent:
                output.write('\t'.join(full_lineage) + '\n')
            else:
                done = False
                while done == False:
                    if tax_dict.has_key(parent) == True and done == False:
                        full_lineage.append(str(parent))
                        taxid = parent
                        parent = tax_dict[parent]
                    if taxid == parent:
                        done = True
            output.write('\t'.join(full_lineage) + '\n')
        output.close()


def get_names(update, lin_work_path):
    if update == True:
        # Extracts
        file = lin_work_path + 'names.dmp'
        input = open(file, 'r')
        file2 = lin_work_path + 'scientific_names.txt'
        output = open(file2, 'w')
        name_dict = {}
        for line in input:
            line = line.strip('\t|\n')
            split_line = line.split('\t|\t')
            taxid = int(split_line[0])
            name_txt = split_line[1]
            if name_txt.find(',') != -1:
                name_txt = name_txt.replace(',', '/')
            unique_name = split_line[2]
            name_class = split_line[3]
            if name_class == "scientific name":
                name_dict[taxid] = name_txt
                output.write(str(taxid) + '\t' + name_txt + '\n')
        input.close()
        output.close()

    elif update == False:
        file = lin_work_path + 'scientific_names.txt'
        input = open(file, 'r')
        name_dict = {}
        for line in input:
            line = line.strip('\n')
            split_line = line.split('\t')
            taxid = int(split_line[0])
            name_txt = split_line[1]
            name_dict[taxid] = name_txt
        input.close()

    return name_dict


def get_merged(lin_work_path):
    file = lin_work_path + 'merged.dmp'
    input = open(file, 'r')
    merged_dict = {}
    for line in input:
        line = line.strip('\t|\n')
        split_line = line.split('\t|\t')
        old_taxid = int(split_line[0])
        merged_taxid = int(split_line[1])
        merged_dict[old_taxid] = merged_taxid
    input.close()

    return merged_dict


def get_delnodes(lin_work_path):
    file = lin_work_path + 'delnodes.dmp'
    input = open(file, 'r')
    deleted_list = []
    for line in input:
        line = line.split('\t|\n')
        deleted_taxid = int(line[0])
        deleted_list.append(deleted_taxid)

    return deleted_list


def taxon_map(update, lin_work_path):
    if update == True:
        file = lin_work_path + 'full_lineage.txt'
        input = open(file, 'r')
        file2 = lin_work_path + 'domain_map.txt'
        output = open(file2, 'w')
        taxon_dict = {}
        for line in input:
            split_line = line.strip('\n').split('\t')
            if len(split_line) > 2:
                taxid = int(split_line[0])
                tax_list = []
                domain = int(split_line[-3])
                if split_line[-2] == '10239':
                    domain = int(split_line[-2])
                tax_list.append(str(domain))
                if len(split_line) > 3:
                    phylum = int(split_line[-4])
                    tax_list.append(str(phylum))
                if len(split_line) > 4:
                    Class = int(split_line[-5])
                    tax_list.append(str(Class))
                if len(tax_list) != 3:
                    while len(tax_list) != 3:
                        tax_list.append('-1')
                taxon_dict[taxid] = tax_list
                output.write(str(taxid) + '\t' + '\t'.join(tax_list) + '\n')

        input.close()
        output.close()
    elif update == False:
        file = lin_work_path + 'domain_map.txt'
        input = open(file, 'r')
        taxon_dict = {}
        for line in input:
            split_line = line.split('\t')
            taxid = int(split_line[0])
            domain = int(split_line[1])
            phylum = int(split_line[2])
            Class = int(split_line[3])
            taxon_dict[taxid] = [domain, phylum, Class]
        input.close()

    return taxon_dict


def add_lineage(jfile, name_dict, merged_dict, deleted_list, taxon_dict, lin_work_path):
    # convert the jplace into a list file
    csv_line_list = jplace_2_csv(jfile, lin_work_path)
    data_dictionary = {}
    input_list = []
    junk_list = []
    header = []
    # add each value from the csv list, after spliting them by comma
    for line in csv_line_list:
        line = line.strip('\r')
        line = line.strip('\n')
        if line != '':
            split_line = line.split(',')
            input_list.append(split_line)
    name_count = 0
    for split_line in input_list:
        if input_list.index(split_line) == 0 or split_line[0] == 'origin':
            split_line.append('domain_id')
            split_line.append('domain_name')
            split_line.append('division_id')
            split_line.append('division_name')
            split_line.append('class_id')
            split_line.append('class_name')
            class_index = split_line.index('classification')
            split_line.insert(class_index + 1, 'scientific_name')
            weight_index = split_line.index('like_weight_ratio')
            header = split_line
        elif split_line[0] != "origin":
            name = split_line[header.index('name')]
            classification = split_line[class_index]
            last_row = input_list[input_list.index(split_line) - 1]
            last_classification = last_row[class_index]
            if last_classification.isdigit() == True:
                last_classification = int(last_classification)
            last_name = last_row[header.index('name')]
            if name == last_name and classification.isdigit() == True:
                name_count += 1
                first_row = input_list[input_list.index(split_line) - name_count]
                first_name = first_row[1]
                weight_ratio = split_line[weight_index]
                first_weight_ratio = first_row[weight_index]
                if float(first_weight_ratio) - float(weight_ratio) > 0.05:
                    classification = 'Omit this row due to weight ratio!'
            else:
                name_count = 0
            if classification.isdigit() == True:
                if deleted_list.count(int(classification)) != 0:
                    classification = 'Omit this row due to deleted taxid!'
            if classification.isdigit() == True:
                classification = int(classification)
                if classification in merged_dict.keys():
                    classification = merged_dict[classification]
                if (taxon_dict.has_key(classification) == True
                    and name_dict.has_key(classification) == True
                    ):
                    split_line.insert(class_index + 1, str(name_dict[classification]))
                    for each in list(taxon_dict[classification]):
                        split_line.append(str(each))
                        if each in name_dict.keys():
                            split_line.append(str(name_dict[int(each)]))
                        else:
                            split_line.append(str('NULL'))
                if (name_dict.has_key(last_classification) == True
                    and name_dict.has_key(classification) == True
                    ):
                    if name_dict[classification] != name_dict[last_classification]:
                        if data_dictionary.has_key(name) == False:
                            data_dictionary[name] = []
                            data_dictionary[name].append(split_line)
                        else:
                            data_dictionary[name].append(split_line)
                elif last_classification == 'classification':
                    if data_dictionary.has_key(name) == False:
                        data_dictionary[name] = []
                        data_dictionary[name].append(split_line)
                    else:
                        data_dictionary[name].append(split_line)
            else:
                junk_list.append(split_line)

    return header, data_dictionary, junk_list


def main(workdir, jdir, jfile, update):
    # Establish Path Variables
    lin_work_path = set_lin_work_path(workdir)

    # updates NCBI Taxonomy ref data if specified
    update = update_tax(update, lin_work_path)

    # creates jplace file list to parse through
    jfile_list = make_jfile_list(jdir, jfile)

    # Make sure the required supplimentary files are present
    # Note: if you get an Error, add '--update' to the command
    # this will update all files needed for the lineage run
    get_nodes(update, lin_work_path)
    name_dict = get_names(update, lin_work_path)
    taxon_dict = taxon_map(update, lin_work_path)
    # Dicitonary of all merged taxids
    merged_dict = get_merged(lin_work_path)

    # List of all deleted taxids
    deleted_list = get_delnodes(lin_work_path)

    confident_dict = {}
    unknown_dict = {}
    junk_list = []

    # Send all jplace files in the file list through
    # the lineage addition function.
    one_header = False
    for jfile in jfile_list:
        jplace_add_lineage = add_lineage(jfile, name_dict,
                                         merged_dict, deleted_list, taxon_dict, lin_work_path
                                         )
        header = jplace_add_lineage[0]
        data_dictionary = jplace_add_lineage[1]
        junk_data = jplace_add_lineage[2]
        # add the header info to the confident and unknown files
        if one_header == False:
            unknown_dict['header'] = header
            confident_dict['header'] = header
            junk_list.append(','.join(header) + '\n')
        one_header = True
        # Save the confident, unknown, and junk
        # to their respective files.
        for junk_line in junk_data:
            junk_list.append(','.join(junk_line) + '\n')
        for name, lineList in data_dictionary.iteritems():
            if len(lineList) > 1:
                # print lineList
                for split_line in lineList:
                    read_name = split_line[1]
                    if read_name in unknown_dict.keys():
                        unknown_dict[read_name].append(split_line)
                    else:
                        unknown_dict[read_name] = [split_line]
            else:
                for split_line in lineList:
                    read_name = split_line[1]
                    mlwr = split_line[4]
                    taxid = split_line[10]
                    if taxid == '131567':
                        split_line.append('cellular_organism')
                        split_line.append(taxid)
                        split_line.append('cellular_organism')
                    elif taxid == '10239':
                        split_line.append('viruses')
                        split_line.append(taxid)
                        split_line.append('viruses')
                    elif taxid == '1':
                        split_line.append('root')
                        split_line.append(taxid)
                        split_line.append('root')
                    # If a read name was placed in more than one gene
                    # choose the best placement based on MLWR score
                    if read_name in confident_dict.keys():
                        if float(mlwr) > float(confident_dict[read_name][4]):
                            confident_dict[read_name] = split_line
                    else:
                        confident_dict[read_name] = split_line
                countLine = len(split_line)

    # Save Confident data
    confident = lin_work_path + 'Confident_scores.csv'
    confident_output = open(confident, 'w')
    confident_output.write(','.join(confident_dict['header']) + '\n')
    del confident_dict['header']
    print len(confident_dict), ' reads in confident...'
    for name, line_list in confident_dict.iteritems():
        line = ','.join(line_list) + '\n'
        confident_output.write(line)
    confident_output.close()

    # Save Junk data
    junk = lin_work_path + 'junk.csv'
    print len(junk_list), ' reads in junk...'
    junk_output = open(junk, 'w')
    junk_output.write(''.join(junk_list))
    junk_output.close()


    # Manipulate unknown data to parse out possible taxa annotations
    unknown = lin_work_path + 'unknown.csv'
    unknown_output = open(unknown, 'w')
    unknown_output.write(','.join(unknown_dict['header']) + '\n')
    del unknown_dict['header']
    print len(unknown_dict), ' reads in unknown...'
    for name, line_list in unknown_dict.iteritems():
        # Dealing with unknowns#
        know_name = True
        domain_name = True
        last_name = False
        last_domain = False
        outline = line_list[0]
        for split_line in line_list:
            if len(split_line) == 11:
                taxid = split_line[10]
                if taxid == '131567':
                    split_line.append('cellular_organism')
                    split_line.append(taxid)
                    split_line.append('cellular_organism')
                elif taxid == '10239':
                    split_line.append('viruses')
                    split_line.append(taxid)
                    split_line.append('viruses')
                elif taxid == '1':
                    split_line.append('root')
                    split_line.append(taxid)
                    split_line.append('root')
                outline = split_line
            if isinstance(split_line, list):
                if len(split_line) != 0:
                    try:
                        if know_name == True:
                            if split_line[11] == last_name or last_name == False:
                                know_name = True
                                last_name = split_line[11]
                            else:
                                know_name = False
                        if domain_name == True:
                            try:
                                if split_line[13] == last_domain or last_domain == False:
                                    domain_name = True
                                    last_domain = split_line[13]
                                else:
                                    domain_name = False
                            except:
                                print split_line
                    except:
                        print split_line, len(split_line)
        if know_name == False:
            if len(outline) == 19:
                outline.pop(-1)
            outline[10] = 'unknown'
            outline[11] = 'unknown'

        if domain_name == False:
            if len(outline) == 19:
                outline.pop(-1)
            try:
                outline[12] = 'unknown'
                outline[13] = 'unknown'
            except:
                print outline
            outline.extend([str('-1'), 'NULL', str('-1'), 'NULL'])
        unknown_output.write(','.join(outline) + '\n')
    unknown_output.close()


if __name__ == '__main__':
    # collect arguments from commandline
    parser = argparse.ArgumentParser(description='Welcome to Lineage! Get your jplace files ready for processing!')
    parser.add_argument('-w', '--workdir', help='path to working directory. [default = CWD]',
                        required=False, default=dirname(realpath(__file__))
                        )
    parser.add_argument('-d', '--jdir', help='path to input jplace directory. [default = False]',
                        required=False, default=False
                        )
    parser.add_argument('-f', '--jfile', help='path to single input jplace file. [default = False]',
                        required=False, default=False
                        )
    parser.add_argument('-u', '--update',
                        help='set to True to update NCBI Taxonomy reference information before run. [default = False]',
                        required=False, default=False
                        )
    args = vars(parser.parse_args())
    # check to make sure that enough arguments were passed before proceeding
    if len(sys.argv) < 2:
        sys.exit("Missing flags, type \"--help\" for assistance...")
    main(args['workdir'], args['jdir'], args['jfile'], args['update'])
