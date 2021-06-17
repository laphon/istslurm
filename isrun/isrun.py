import paramiko
import sh
from getpass import getpass, getuser
import os
import sys


def get_arg(argv, opt):
    arg = argv[argv.index(opt) + 1]
    argv.remove(opt)
    argv.remove(arg)
    return arg
    

class IstSlurmClient:
    def __init__(self, key_path):
        self.client = paramiko.SSHClient()
        self.key_path = key_path
        self.key = paramiko.RSAKey.from_private_key_file(key_path)
        self.sudo_pass = getpass(f"(sudo) password for {getuser()}: ")
        self.username = self.__get_host_info()["username"]
        self.hostname = self.__get_host_info()["hostname"]
        print(f'\nUSER: {self.username}')
        print(f'HOST: {self.hostname}')
    
    def connect(self):
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=self.hostname, username=self.username, pkey=self.key)
    
    def __create_sbatch_script(self, argv, command):
        sbatch_file = "#!/bin/sh\n"
        remote_path = self.__remote_path()
        '''
        if '--error' in argv:
            error = get_arg(argv, '--error')
            if error[0] != '/':
            	 error = remote_path + '/' + error
            sbatch_file += "#SBATCH --error=" + error + '\n'
        if '--output' in argv:
            output = get_arg(argv, '--output')
            if output[0] != '/':
            	 output = remote_path + '/' + output
            sbatch_file += "#SBATCH --output=" + output + '\n'
        '''
        for i in range(0, len(argv), 2):
            sbatch_file += "#SBATCH " + argv[i] + "=" + argv[i + 1] + "\n"
        sbatch_file += "cd " + self.__remote_path() + "\n"
        sbatch_file += command
        return sbatch_file
        
    def sbatch(self, args, command):
        sbatch_file = self.__create_sbatch_script(args, command)
        print(f"SBATCH SCRIPT: \n\n{sbatch_file}\n")
        self.__run_command(f"sbatch <<< '{sbatch_file}'")

    def __run_command(self, command):
        stdin , stdout, stderr= self.client.exec_command(command)
        print("\n=====Output=====\n")
        print(stdout.read().decode())
        print("\n=====Error=====\n")
        print(stderr.read().decode())
    
    def pwd(self):
        stdin, stdout, stderr= self.client.exec_command("pwd")
        output = stdout.read().decode()
        return str(output).strip()

    def squeue(self):
        return self.__run_command("squeue")
    
    def sinfo(self):
        self.__run_command("sinfo")
    
    def scancel(self, job_id):
        self.__run_command(f"scancel {job_id}")
        
    def __mntinfo(self):
        local_dir = os.getcwd()
        sh_sudo = sh.sudo.bake("-S", _in=self.sudo_pass)
        info = str(sh_sudo.findmnt("-T", local_dir)).split()
        target = info[4]
        src = info[5]
        return {"target": target, "src": src}

    def __remote_path(self):
        local_dir = os.getcwd()
        info = self.__mntinfo()
        rel_dir = local_dir.replace(info['target'], '')
        abs_dir = info['src'].split(':')[1] + rel_dir[1:]
        return abs_dir
    
    def __get_host_info(self):
        info = self.__mntinfo()
        host = info["src"].split(':')[0]
        username = host.split('@')[0]
        hostname = host.split('@')[1]
        return {"username": username, "hostname": hostname}
    

def main():
    argv = sys.argv
    job_command = argv[1]
    key_path = get_arg(argv, "--key")
    env = get_arg(argv, "--env")
    print(key_path)
    sbatch_args = argv[2:]
    s = IstSlurmClient(key_path)
    s.connect()
    activate_env = f". /ist/apps/modules/software/Anaconda3/5.3.0/etc/profile.d/conda.sh\nconda activate /ist/ist-share/robotics/laphonp/envs/{env}\n"
    s.sbatch(command=activate_env + job_command, args=sbatch_args)
    

if __name__ == "__main__":
    main()
