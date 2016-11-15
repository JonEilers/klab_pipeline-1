import gzip
import subprocess
import sys
from os import walk, path


def find_fastq(file_path):
    # walk the path and find the fastq files
    fastq_list = []
    for root, dirs, files in walk(file_path):
        for f in files:
            if 'fastq' in f:
                file_path = path.join(root, f)
                fastq_list.append(file_path)
    return fastq_list


def ungzip(fastq, save_path):
    # unzip the file and save to save_path, added norm to deal with repeated file names
    unzip = gzip.open(fastq, 'rb')
    rename = '.'.join([fastq.rsplit('/', 1)[1].rsplit('.', 2)[0], 'fastq'])
    new_file = path.join(save_path, rename)
    out = open(new_file, 'wb')
    out.write(unzip.read())
    unzip.close()
    out.close()
    print(new_file, 'saved...')
    return new_file


def run_fastx_trimmer(fastq, save_path):
    # Trim front
    trim_front = path.join(save_path, '.'.join([fastq.rsplit('/', 1)[1].rsplit('.', 1)[0], 'front']))
    front = subprocess.Popen(
        ' '.join(['fastx_trimmer', '-Q33', '-f', '30', '-i', fastq, '-o', trim_front]), shell=True)
    front.wait()
    if front.returncode != 0:
        sys.exit()
    print(trim_front, 'front trimmed...')
    # Trim end
    trim_end = path.join(save_path, '.'.join([fastq.rsplit('/', 1)[1].rsplit('.', 1)[0], 'fastx']))
    end = subprocess.Popen(
        ' '.join(['fastx_trimmer', '-Q33', '-t', '30', '-m', '50', '-i', trim_front, '-o', trim_end]),
        shell=True)
    end.wait()
    if end.returncode != 0:
        sys.exit()
    print(trim_end, 'end trimmed...')
    return trim_end


def run_fastq_trimmer(fastq, save_path):
    fastq_trim = path.join(save_path, '.'.join([fastq.rsplit('/', 1)[1], 'trim']))
    trim = subprocess.Popen(
        ' '.join(['fastq_quality_trimmer', '-Q33', '-t', '30', '-l', '100', '-i', fastq, '-o', fastq_trim]), shell=True)
    trim.wait()
    if trim.returncode != 0:
        sys.exit()
    print(fastq_trim, 'run...')
    return fastq_trim


def run_fastq_filter(fastq, save_path):
    fastq_filter = path.join(save_path, '.'.join([fastq.rsplit('/', 1)[1], 'filter', 'fastq']))
    filter = subprocess.Popen(
        ' '.join(['fastq_quality_filter', '-Q33', '-q', '30', '-p', '50', '-i', fastq, '-o', fastq_filter]), shell=True)
    filter.wait()
    if filter.returncode != 0:
        sys.exit()
    print(fastq_filter, 'run...')
    return fastq_filter


def run_derep(fastq, save_path):
    fasta_derep = path.join(save_path, '.'.join([fastq.rsplit('/', 1)[1], 'derep', 'fasta']))
    derep = subprocess.Popen(
        ' '.join(['vsearch', '--derep_fulllength', fastq, '--sizeout', '--minuniquesize 2', '--output', fasta_derep]),
        shell=True)
    derep.wait()
    if derep.returncode != 0:
        sys.exit()
    print(fasta_derep, 'run...')
    return fasta_derep


def run_swarm(fasta, save_path):
    fasta_swarm = path.join(save_path, '.'.join([fastq.rsplit('/', 1)[1], 'swarm', 'fastq']))
    derep = subprocess.Popen(
        ' '.join(['swarm', '-f', '-z', '-t 8', '-w', fasta_swarm, fasta, ' > /dev/null']), shell=True)
    derep.wait()
    if derep.returncode != 0:
        sys.exit()
    print(fasta_swarm, 'run...')
    return fasta_swarm


fastq_path = sys.argv[1]
fastq_list = find_fastq(fastq_path)

save_path = sys.argv[2]
fastq_save_path = path.join(save_path, 'raw')
fastx_save_path = path.join(save_path, 'fastx')
trimmer_save_path = path.join(save_path, 'fastq_trimmer')
filter_save_path = path.join(save_path, 'fastq_filter')
derep_save_path = path.join(save_path, 'derep')
# swarm_save_path = path.join(save_path, 'swarm')

for fastq in fastq_list:
    # Deal with repeated names in sub-projects
    # if 'eDNA_not-normalized_recirc' in fastq:
    #    norm = 'not_norm'
    # else:
    #    norm = 'norm'
    # They are gzipped
    if '.gz' in fastq:
        fastq = ungzip(fastq, fastq_save_path)
    # Process fastq's using fastx toolkit
    fastx_trim = run_fastx_trimmer(fastq, fastx_save_path)
    fastq_trim = run_fastq_trimmer(fastx_trim, trimmer_save_path)
    fastq_filter = run_fastq_filter(fastq_trim, filter_save_path)
    fastq_derep = run_derep(fastq_filter, derep_save_path)
    # fasta_swarm = run_swarm(fastq_derep, swarm_save_path)
