
class Qsub:
	def __init__(self,qsub_file_path, script_cmd_list, file_name):
		self.qsub_file_path = qsub_file_path
		self.script_cmd_list = script_cmd_list
		self.file_name = file_name
	def Batch_builder(self):
		qsub_parameters = '#!/bin/sh\n#$ -m be\n#$ -o ' + self.qsub_file_path + 'output.txt\n#$ -e ' + self.qsub_file_path + 'error.txt\n\n'
		output = open(self.qsub_file_path + str(self.file_name) + '.sh', 'w')
		output.write(qsub_parameters)
		output.write('\n'.join(self.script_cmd_list) + '\n')
		output.close()
		return_string = 'The  batch script for ' + str(self.file_name) + ' has been created...'
		return return_string
