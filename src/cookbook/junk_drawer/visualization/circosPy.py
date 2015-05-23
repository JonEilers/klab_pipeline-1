import os,sys
import itertools

path = './'

file_list = os.listdir(path)
color_dictionary = {'coastal_1_8':'chr1','coastal_8_3':'chr2','coastal_3_20':'chr3','DCM_1_8':'chr4','DCM_8_3':'chr5','DCM_3_20':'chr6','surface_1_8':'chr14','surface_8_3':'chr15','surface_3_20':'chr17','upwelling_1_8':'chr10','upwelling_8_3':'chr11','upwelling_3_20':'chr12'}
cyto_list = ['gpos100','gpos75','gpos66','gpos50','gpos33','gpos25','gvar','gneg','acen','stalk']
lib_change_key = {'Ecoastal18':'Eupwelling18','Ecoastal320':'Eupwelling320','Ecoastal83':'Eupwelling83','Eupwelling18':'Esurface18','Eupwelling320':'Esurface320','Eupwelling83':'Esurface83','Esurface18':'EDCM18','Esurface320':'EDCM320','Esurface83':'EDCM83'}
site_order = ['Ecoastal18','Ecoastal320','Ecoastal83','Eupwelling18','Eupwelling320','Eupwelling83','Esurface18','Esurface320','Esurface83','EDCM18','EDCM320','EDCM83']
for each in file_list:
	if each.find('.tsv') != -1 and each.find('_change') == -1:
		file = path + each
		input = open(file,'r')
		taxa_count = {}
		for line in input:
			if line.find('gene') == -1:
				split_line = line.strip('\n').split('\t')
				gene = split_line[0]
				if gene.find('COG') != -1 and each[0] == 'E':
					site = split_line[1]
					size = split_line[2]
					taxcnt = split_line[3]
					ntaxcnt = int(float(split_line[4]))
					scinm = split_line[5]
					domnm = split_line[6]
					hiclass = split_line[7]
					subhiclass = split_line[8]
					rdcntlib = split_line[10]
					nfactor = split_line[11]
					funccats = split_line[12]
					func = split_line[13]
					if funccats == '':
						funccats = 'unid'
					if func == '':
						func = 'unid'
					# making circos file
					for funccat in funccats:
						chr = 'band'
						parent = each[0] + site + '' + size.replace('-','').replace('.','')
						ID = site + '_' + size.replace('-','_').replace('.','')
						LABEL = site + '_' + size.replace('-','_').replace('.','')
						START = '0'
						END = str(rdcntlib)
						COLOR = color_dictionary[LABEL]
						total = ('chr','-',parent,LABEL,COLOR)
						key = (chr,parent,funccat,COLOR)
						if key in taxa_count.keys():
							taxa_count[key] = taxa_count[key] + ntaxcnt
						else:
							taxa_count[key] = ntaxcnt
						if total in taxa_count.keys():
							taxa_count[total] = taxa_count[total] + ntaxcnt
						else:
							taxa_count[total] = ntaxcnt
		input.close()
		chr_list = []
		band_list = []
		parent_dictionary = {}
		for tuple,count in taxa_count.iteritems():
			if tuple[0] == 'chr':
				chr_list.append((tuple,count))
				chr_list.sort(key=lambda l:site_order.index(l[0][2]))
				parent_dictionary[tuple[2]] = count
			elif tuple[0] == 'band':
				band_list.append((tuple,count))
				band_list.sort(key=lambda l:site_order.index(l[0][1]))
		output = open('karyotype.' + file.split('/')[1].split('.')[0] + '.txt', 'w')
		bands_text = open('bands.' + file.split('/')[1].split('.')[0] + '.txt', 'w')
		for (tuple,count) in chr_list:
			output.write(' '.join([tuple[0],tuple[1],tuple[2],tuple[3],'0',str(count),tuple[4]]) + '\n')
		cyto_index = 0
		func_dictionary = {}
		for (tuple,count) in band_list:
			start = parent_dictionary[tuple[1]] - count
			stop = parent_dictionary[tuple[1]]
			output.write(' '.join([tuple[0],tuple[1],tuple[2],tuple[2],str(start),str(stop),cyto_list[cyto_index]]) + '\n')
			bands_text.write(' '.join([tuple[1],str(start),str(stop),tuple[2]]) + '\n')
			if tuple[2] in func_dictionary.keys():
				func_dictionary[tuple[2]].append((tuple[1],str(start),str(stop),tuple[3]))
			else:
				func_dictionary[tuple[2]] = [(tuple[1],str(start),str(stop),tuple[3])]
			parent_dictionary[tuple[1]] = start
			if cyto_index != 9:
				cyto_index = cyto_index + 1
			else:
				cyto_index = 0
		output.close()
		bands_text.close()
		link_lib = open('link.' + file.split('/')[1].split('.')[0] + '.txt','w')
		for func,start_stop_list in func_dictionary.iteritems():
			#if func == 'E' or func == 'Z':
			nr_set = list(itertools.product(start_stop_list,start_stop_list))
			for link_tup in nr_set:
				if link_tup[0] != link_tup[1] and link_tup[0][0] in lib_change_key.keys():
					if lib_change_key[link_tup[0][0]] == link_tup[1][0]:
						link_lib.write(' '.join(link_tup[0][:3]) + ' ' + ' '.join(link_tup[1][:3]) + ' color=' + link_tup[0][-1] + '\n')
			
		link_lib.close()

			




