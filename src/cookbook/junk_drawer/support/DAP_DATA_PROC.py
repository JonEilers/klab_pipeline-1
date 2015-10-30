# This is a class built to house the functions needed to analyze the PAF output
import os
import json


class jplaceDDP:
    def __init__(self, jplaceFILE):
        self.jplaceFILE = jplaceFILE

    def jplace2csv(self):
        """
        very simple, converts jplace files into csv
        uses the guppy to_csv command, but allows for conversion
        with worrying about where a file has placements or not
        RETURNS a list where each value is a line of the csv output
        """
        convert2csv = os.popen('guppy to_csv ' + self.jplaceFILE).read().split('\n')
        if len(convert2csv) == 1:
            print (self.jplaceFILE, 'Does not have placements and will not be added to the output files...')
        return convert2csv

    def emptyjplace(self):
        """
        Checks to see if a jplace file has placements
        RETURNS True if is does, and False if it doesn't
        """
        # open file and load as a json
        jplace_data = open(self.jplaceFILE)
        data = json.load(jplace_data)
        jplace_data.close()
        placements = data['placements']
        if not placements:
            return False
        else:
            return len(placements)


class Qsub:
    def __init__(self, qsub_file_path, script_list, link):
        self.qsub_file_path = qsub_file_path
        self.script_list = script_list
        self.link = link

    def Batch_builder(self):
        """
        builds shell [.sh] scripts which can then be sent through the SGE
        to be run on the cluster
        RETURNS a string confirming that the submission occured.
        """
        qsub_parameters = '#!/bin/sh\n#$ -m be\n#$ -o ' + self.qsub_file_path + 'output.txt\n#$ -e ' + self.qsub_file_path + 'error.txt\n\n'
        output = open(self.qsub_file_path + self.link.split('/')[-1] + '.sh', 'w')
        output.write(qsub_parameters)
        for script in self.script_list:
            output.write('python ' + script + ' ' + self.link + '\n')
        output.close()
        return_string = 'The  batch script for ' + self.link.split('/')[-1] + ' has been created...'
        return return_string


class translateTool:
    def __init__(self, fastaFILE):
        self.fastaFILE = fastaFILE

    def dna2protein(self):
        """
        I just moved this into this class, it needs to be rebuilt...
        Be sure to use the fullpath to the fastaFILE.
        RETURNS a string that either it worked or it did not.
        """

        # Convert the files and add sample accessions if they exist
        try:
            os.system(
                'seqmagick convert --translate dna2protein ' + self.fastaFILE + ' ' + self.fastaFILE + '.pep.fasta')
            return_string = self.fastaFILE + ' has been translated and saved to: ' + self.fastaFILE + '.pep.fasta'
        except RuntimeError:
            return_string = self.fastaFILE + ' is not the correct format...'
        return return_string


class sample_acc:
    # STILL WORKING ON THIS ONE
    def __init__(self, fastaFILE, metaFILE):
        self.fastaFILE = fastaFILE
        self.metaFILE = metaFILE

    def add_sample_acc(self):

        """
        The metadata file should have the exact same name as the fasta
        EXCEPT it should be a .csv instead of .fasta,i.e, [fasta_file].fasta and [meta_file].csv
        [fasta_file] == [meta_file]
        If you don't have a metadata file, just put None into the path2meta variable
        """
        # Collect the sample accessions from the metadata file
        sample_accList = []
        input = open(self.metaFILE, 'r')
        sample_accList = []
        for line in input:
            split_line = line.split(',')
            sample_accList.append(split_line[0].strip('\"'))
        input.close()

        # Append the metadata sample accessions to the name of each read
        input = open(self.fastaFILE, 'r')
        output = open(self.fastaFILE.strip('.fasta') + '.unq.fasta', 'w')
        fix_sample_acc = []
        # counter is used to add a random variable to each name to ensure they are unique
        counter = 0
        for line in input:
            if line.find('>') != -1:
                split_line = line.split('>')[1]
                annotationList = split_line.split(' ')
                sample_acc = -1
                for part in annotationList:
                    if part.find('=') != -1:
                        if sample_accList.count(part.split('=')[1].strip('\"')) != 0:
                            sample_acc = part.split('=')[1].strip('\"')
                        elif part.find('sample_id') != -1:
                            sample_acc = part.split('=')[1].strip('\"')
                            fix_sample_acc.append(part.split('=')[1].strip('\"'))
                if sample_acc == -1:
                    sample_acc = file.split('.')[0]
                new_line = '>' + sample_acc + '.' + str(counter) + '.' + split_line
                output.write(new_line)
            else:
                output.write(line)
            counter += 1
        input.close()
        output.close()
        # print set(list(fix_sample_acc))
        return meta, 'has been processed to have unique read ids...'
