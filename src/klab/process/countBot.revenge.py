# Scavenged code from Eric's mbari_lineage.py
import sys
sys.path.append('/home/ryan/Dropbox/Ryan_Grad/collabs/KLab/klab_pipeline/src/klab/process')
from derived_info import group_and_count, FUZZY, CONFIDENT
from file_manager import create_placements, write_df_to_file
from lineage import create_lineage
from pandas import DataFrame


def create_lineage_files(base):
    jplace_dir = base
    lineage_file = base + '_placements_with_lineage.tsv'

    p = create_placements(dir=jplace_dir)
    l = create_lineage(ncbi_dir='/home/ryan/Dropbox/Ryan_Grad/collabs/KLab/klab_pipeline/src/data', placements=p)
    write_df_to_file(l, lineage_file)
    return l


def create_and_write_count_files(lineage, grouping, path):
    c = group_and_count(lineage, grouping)
    fuzzy_counts = c[c.placement_type == FUZZY]
    confident_counts = c[c.placement_type == CONFIDENT]
    write_df_to_file(fuzzy_counts, path + 'count_fuzzy.tsv')
    write_df_to_file(confident_counts, path + 'count_confident.tsv')


def do_the_do(base):
    l = create_lineage_files(base)
    l = DataFrame.from_csv('/media/ryan/PI/WDFW_data/recirc/place_files_placements_with_lineage.tsv', sep='\t')
    create_and_write_count_files(l, ['cluster', 'domain_name', 'placement_type'], base + '_domain_')
    create_and_write_count_files(l, ['cluster', 'domain_name', 'division_name', 'placement_type'],
                                 base + '_division_')
    create_and_write_count_files(l, ['cluster', 'domain_name', 'division_name', 'class_name',
                                     'placement_type'], base + '_class_')
    create_and_write_count_files(l, ['cluster', 'domain_name', 'division_name', 'class_name','lowest_classification_name',
                                     'placement_type'], base + '_lowest_classification_')


# rjm [ech] 2015-03-19 - take the repetition out of rebuilding the ETSP data
if __name__ == '__main__':
	do_the_do('/media/ryan/PI/WDFW_data/recirc/place_files')