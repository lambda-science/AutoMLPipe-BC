'''
Only applied if there are multiple datasets withing experiment folder. Works under the assumption that the file structure generated by phases 1 to 6 have not changed.
'''

import argparse
import os
import sys
import time
import WrapperComparisonJob
import pandas as pd

'''Phase 7 of Machine Learning Analysis Pipeline:
Sample Run Command:
python WrapperComparisonMain.py --output-path /Users/robert/Desktop/outputs --experiment-name test1
'''

def main(argv):
    # Parse arguments
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--output-path', dest='output_path', type=str, help='path to output directory')
    parser.add_argument('--experiment-name', dest='experiment_name', type=str, help='name of experiment (no spaces)')
    #Lostistical arguments
    parser.add_argument('--run-parallel',dest='run_parallel',type=str,help='if run parallel',default="True")
    parser.add_argument('--queue',dest='queue',type=str,help='specify name of LPC queue',default="i2c2_normal") #specific to our research institution and computing cluster
    parser.add_argument('--res-mem', dest='reserved_memory', type=int, help='reserved memory for the job (in Gigabytes)',default=4)
    parser.add_argument('--max-mem', dest='maximum_memory', type=int, help='maximum memory before the job is automatically terminated',default=15)

    options = parser.parse_args(argv[1:])
    output_path = options.output_path
    experiment_name = options.experiment_name
    run_parallel = options.run_parallel
    queue = options.queue
    reserved_memory = options.reserved_memory
    maximum_memory = options.maximum_memory

    metadata = pd.read_csv(output_path + '/' + experiment_name + '/' + 'metadata.csv').values
    sig_cutoff = metadata[5,1]

    if eval(run_parallel):
        submitClusterJob(output_path+'/'+experiment_name,reserved_memory,maximum_memory,queue,sig_cutoff)
    else:
        submitLocalJob(output_path+'/'+experiment_name,sig_cutoff)

def submitLocalJob(experiment_path,sig_cutoff):
    WrapperComparisonJob.job(experiment_path)

def submitClusterJob(experiment_path,reserved_memory,maximum_memory,queue,sig_cutoff):
    job_ref = str(time.time())
    job_name = experiment_path + '/jobs/P7_' + job_ref + '_run.sh'
    sh_file = open(job_name,'w')
    sh_file.write('#!/bin/bash\n')
    sh_file.write('#BSUB -q '+queue+'\n')
    sh_file.write('#BSUB -J '+job_ref+'\n')
    sh_file.write('#BSUB -R "rusage[mem='+str(reserved_memory)+'G]"'+'\n')
    sh_file.write('#BSUB -M '+str(maximum_memory)+'GB'+'\n')
    sh_file.write('#BSUB -o ' + experiment_path+'/logs/P7_'+job_ref+'.o\n')
    sh_file.write('#BSUB -e ' + experiment_path+'/logs/P7_'+job_ref+'.e\n')

    this_file_path = os.path.dirname(os.path.realpath(__file__))
    sh_file.write('python ' + this_file_path + '/DataCompareJob.py ' + experiment_path +" "+ str(sig_cutoff)+ '\n')
    sh_file.close()
    os.system('bsub < ' + job_name)
    pass

if __name__ == '__main__':
    sys.exit(main(sys.argv))