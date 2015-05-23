import os

home_path = os.path.dirname(os.path.realpath(__file__))
os.system('wget -i ' + home_path + '/download_links.txt')
file_list = [file for file in os.listdir(home_path) if file.find('.sra') != -1]
for file in file_list:
	print file
	os.system('/home/mclaugr4/bio/ETSP/sratoolkit.2.3.5-2-centos_' + 
			'linux64/bin/fastq-dump.2.3.5.2 --fasta 120 ' + file)