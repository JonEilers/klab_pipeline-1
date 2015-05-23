import os,sys

path = './'
metagenome_path = sys.argv[1]
dir_list = os.listdir(path)
translation_path = path + 'translated_data'
if not os.path.exists(translation_path:
	os.makedirs(translation_path)
meta_list = os.listdir(metagenome_path)
for file in meta_list:
	counter = 0
	if file.find('.pep.') == -1 and file.find('.csv') == -1:
		pep_file = file.split('.')[0] + '.pep.fasta'
		os.system('/home/mclaugr4/software/bin/seqmagick convert --translate dna2protein ' +
				 download_path + file + ' ' + translation_path + pep_file
				 )
		print file, 'has been translated from nucleotides to proteins...'
		input = open(translation_path + pep_file, 'r')
		output = open(translation_path + pep_file.strip('.fasta') + '.unq.fasta', 'w')
		fix_sample_acc = []
		for line in input:
			if line.find('>') != -1:
				split_line = line.split('>')[1]
				annotationList = split_line.split(' ')

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
			counter = counter + 1
		input.close()
		output.close()
		print set(list(fix_sample_acc))
		print meta, 'has been processed to have unique read ids...'