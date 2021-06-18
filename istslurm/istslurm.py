import os
from subprocess import Popen, PIPE
import sys
import json
from getpass import getpass, getuser
import sh


def mntinfo():
    local_dir = os.getcwd()
    #sh_sudo = sh.sudo.bake("-S", _in=PASSWORD)
    info = str(sh.findmnt("-T", local_dir)).split()
    target = info[4]
    src = info[5]
    return {"target": target, "src": src}


def remote_path():
    local_dir = os.getcwd()
    info = mntinfo()
    print(info)
    rel_dir = local_dir.replace(info['target'], '')
    abs_dir = info['src'].split(':')[1] + rel_dir[1:]
    return abs_dir


def get_host_info():
    info = mntinfo()
    host = info["src"].split(':')[0]
    username = host.split('@')[0]
    hostname = host.split('@')[1]
    return {"username": username, "hostname": hostname}


def get_arg(argv, opt):
    arg = argv[argv.index(opt) + 1]
    argv.remove(opt)
    argv.remove(arg)
    return arg


def create_sbatch_script(argv, command):
    sbatch_file = "#!/bin/sh\n"
    for i in range(0, len(argv), 2):
        sbatch_file += "#SBATCH " + argv[i] + "=" + argv[i + 1] + "\n"
    sbatch_file += "cd " + remote_path() + "\n"
    sbatch_file += command
    return sbatch_file

'''
def run(command):
    process = Popen(command, stderr=PIPE, stdout=PIPE, shell=True)
    while True:
        line = process.stdout.readline().rstrip()
        if not line:
            break
        print(line.decode())
    while True:
        line = process.stderr.readline().rstrip()
        if not line:
            break
        print(line.decode())
'''
 
def main():
    argv = sys.argv
    key_input = ""
    if "--key" in argv:
        key_path = get_arg(argv, "--key")
        key_input = "-i " + key_path
    host = argv[1]
    option = argv[2]
    if '-h' in argv:
    	print('Job Submission Commands (run in a mounted directory):\n')
    	print('SRUN:\tistslurm <host> -srun <srun arguments> <executable commands>')
    	print('SBATCH:\tistslurm <host> -sbatch "<executable command>" <sbatch arguments>\n')
    	print('\nOptional: add --key <path to a private key> in case an identity file is required\n')
    elif option == "-sinfo":
        os.system(f'sudo ssh {key_input} {host} -t "sinfo"')
    elif option == "-squeue":
        os.system(f'sudo ssh {key_input} {host} -t "squeue"')
    elif option == "-scancel":
    	job_id = argv[2]
    	os.system(f'sudo ssh {key_input} {host} -t "scancel {job_id}"')
    elif option == "-srun":
        env = get_arg(argv, "--env")
        srun_command = 'srun ' + ' '.join(argv[3:]) + ';'
        cd_command = f"cd {remote_path()}"
        command = f'. /ist/apps/modules/software/Anaconda3/5.3.0/etc/profile.d/conda.sh; conda activate /ist/ist-share/robotics/laphonp/envs/{env};{cd_command};{srun_command}'
        print(f'sudo ssh {key_input} {host} -t "{command}"')
        os.system(f'sudo ssh {key_input} {host} -t "{command}"')
    elif option == "-sbatch":
    	env = get_arg(argv, "--env")
    	command = f'. /ist/apps/modules/software/Anaconda3/5.3.0/etc/profile.d/conda.sh;\n conda activate /ist/ist-share/robotics/laphonp/envs/{env};\n{argv[3]}'
    	sbatch_file = create_sbatch_script(argv[4:], command)
    	print(f"\nSBATCH SCRIPT: \n\n{sbatch_file}\n\n")
    	os.system(f'sudo ssh {key_input} {host} -t "sbatch <<< ' + f"'{sbatch_file}'\"")

if __name__ == "__main__":
    main()
