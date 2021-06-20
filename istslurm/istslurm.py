import os
from subprocess import Popen, PIPE
import sys
import json
from getpass import getpass, getuser
import sh


def mntinfo():
    local_dir = os.getcwd()
    info = str(sh.findmnt("-T", local_dir)).split()
    target = info[4]
    src = info[5]
    return {"target": target, "src": src}


def remote_path():
    local_dir = os.getcwd()
    info = mntinfo()
    rel_dir = local_dir.replace(info['target'], '')
    abs_dir = info['src'].split(':')[1] + rel_dir[1:]
    if len(info['src'].split(':')[1]) == 0:
    	abs_dir = '/ist/users/' + info['src'].split('@')[0] + '/' + rel_dir[1:]
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
    conda_activate = '. /ist/apps/modules/software/Anaconda3/5.3.0/etc/profile.d/conda.sh;'
    if "--env" in argv:
        env = get_arg(argv, "--env")
        if env[0] != '/':
            conda_activate += f' conda activate /ist/ist-share/robotics/envs/{env};'
        else:
            conda_activate += f' conda activate {env};'
    host = argv[1]
    option = argv[2]
    if '-h' in argv:
    	print('Job Submission Commands (run in a mounted directory):\n')
    	print('SRUN:\tistslurm <host> srun <srun arguments> <executable commands>')
    	print('SBATCH:\tistslurm <host> sbatch <sbatch arguments> "<executable command>"\n')
    elif option == "sinfo":
    	sinfo = ' '.join(argv[2:])
    	os.system(f'ssh {key_input} {host} -t "{sinfo}"')
    elif option == "squeue":
    	squeue = ' '.join(argv[2:])
    	os.system(f'ssh {key_input} {host} -t "{squeue}"')
    elif option == "scancel":
    	scancel = ' '.join(argv[2:])
    	os.system(f'ssh {key_input} {host} -t "{scancel}"')
    elif option == "srun":
        cd_command = f"cd {remote_path()};"
        srun_command = 'srun ' + ' '.join(argv[3:]) + ';'
        print(f'sudo ssh {key_input} {host} -t "{command}"')
        os.system(f'ssh {key_input} {host} -t "{conda_activate} {cd_command} {srun_command}"')
    elif option == "sbatch":
    	cd_command = f"cd {remote_path()};"
    	command = f'{conda_activate}\n{cd_command}\n{argv[-1]}\n'
    	sbatch_file = create_sbatch_script(argv[3:-1], command)
    	print(f"\nSBATCH SCRIPT: \n\n{sbatch_file}\n\n")
    	os.system(f'ssh {key_input} {host} -t "sbatch <<< ' + f"'{sbatch_file}'\"")
    '''
    elif option == "sinteractive":
        cd_command = f"cd {remote_path()};"
        command = f'{conda_activate}{cd_command}{argv[-1]}'
        sinteractive_args = ' '.join(argv[3:-1])
        print(f'sudo ssh {key_input} {host} -t "{conda_activate} {cd_command} sinteractive {sinteractive_args}; {argv[-1]}"')
        os.system(f'sudo ssh {key_input} {host} -t "{conda_activate} {cd_command} sinteractive {sinteractive_args}; {argv[-1]}"')
    '''

if __name__ == "__main__":
    main()
