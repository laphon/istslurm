import os
from subprocess import Popen, PIPE
import sys
import json
from getpass import getpass, getuser
import sh


def mntinfo():
    local_dir = os.getcwd()
    sh_sudo = sh.sudo.bake("-S", _in=PASSWORD)
    info = str(sh_sudo.findmnt("-T", local_dir)).split()
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


def getArg(argv, opt):
    arg = argv[argv.index(opt) + 1]
    argv.remove(opt)
    argv.remove(arg)
    return arg


def getConfig():
    return json.load(open("./config.json"))
    #return {"key_path": "/home/laphon/my-pc/vistec/vistec_id_rsa", "host": "laphonp@10.204.100.209"}


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
    
def main():
    print(getConfig()["host"])
    print(os.getcwd() + '\n')
    print(sys.path[0] + '\n')
    #PASSWORD = getpass(f"(sudo) password for {getuser()}: ")
    argv = sys.argv
    option = argv[1]
    print(option)
    if option == "-config":
        config = json.load(open("config.json"))
        key_path = getArg(argv, '--key')
        host = getArg(argv, '--host')
        config["key_path"] = key_path
        config["host"] = host
        with open('config.json', 'w') as outfile:
            json.dump(config, outfile)
    elif option == "-sinfo":
        print("SINFO")
        os.system(f'sudo -S ssh -i {getConfig()["key_path"]} {getConfig()["host"]} -t "sinfo"')
    elif option == "-squeue":
        os.system(f'sudo -S ssh -i {getConfig()["key_path"]} {getConfig()["host"]} -t "squeue"')
    elif option == "-scancel":
    	job_id = argv[2]
    	os.system(f'sudo -S ssh -i {getConfig()["key_path"]} {getConfig()["host"]} -t "scancel {job_id}"')
    elif option == "-srun":
        env = getArg(argv, "--env")
        srun_command = 'srun ' + ' '.join(argv[2:]) + ';'
        cd_command = f"cd {remote_path()}"
        command = f'. /ist/apps/modules/software/Anaconda3/5.3.0/etc/profile.d/conda.sh; conda activate /ist/ist-share/robotics/laphonp/envs/{env};{cd_command};{srun_command}'
        os.system(f'sudo -S ssh -i {getConfig()["key_path"]} {getConfig()["host"]} -t "{command}"')

if __name__ == "__main__":
    main()
