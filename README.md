# istslurm

## Installation

Clone the repository:
``git clone https://github.com/laphon/istslurm.git;``

Install the package:
``cd istslurm; python setup.py install;``

## Usage

### Slurm Controls Commands

**sinfo**
- Format: ``istslurm sinfo <sinfo arguments>``
- Example: ``istslurm user@10.204.100.209 sinfo`` (logs partitions info)

See more available sinfo arguments: [https://slurm.schedmd.com/sbatch.html](https://slurm.schedmd.com/sinfo.html)

**squeue**
- Format: ``istslurm squeue <squeue arguments>``
- Example: ``istslurm user@10.204.100.209 squeue`` (logs all jobs info)

See more available squeue arguments: [https://slurm.schedmd.com/sbatch.html](https://slurm.schedmd.com/squeue.html)

**scancel**
- Format: ``istslurm scancel <scancel arguments>``
- Example: ``istslurm user@10.204.100.209 scancel 12345`` (cancels job with id 12345)

See more available scancel arguments: [https://slurm.schedmd.com/sbatch.html](https://slurm.schedmd.com/scancel.html)

### Job Submission Commands
To submit jobs, run these following commands in a mounted directory from IST frontend.

**srun**
This command will run the job on a real-time interactive shell.

- Format: ``istslurm <host> srun <srun arguments> <executable commands>``
- Example: ``istslurm user@10.204.100.209 srun -N 1 -p gpu-cluster -t 72:0:0 python main.py``

See more available srun arguments: [https://slurm.schedmd.com/srun.html](https://slurm.schedmd.com/srun.html)

**sbatch**
This command will generate an sbatch script according to the arguments given and submit for later execution on the cluster.

- Format: ``istslurm <host> sbatch <sbatch arguments> "<executable commmands>"``
- Example: ``istslurm user@10.204.100.209 sbatch --job-name sample-job --nodes 1 --partition gpu-cluster --time 72:0:0 --error %j-err --output --%j-out "python main.py"``

See more available sbatch arguments: [https://slurm.schedmd.com/sbatch.html](https://slurm.schedmd.com/sbatch.html)

- Optional:
	- If a conda environment is needed, add ``--env <environment name>`` (The only available environment now is ``test``. It will soon be fixed.)
	- If a private key is needed for connection, add ``--key <path to private key>``
