import os
import subprocess
import shutil
import signal
import sys
from datetime import datetime
import matplotlib.pyplot as plt

def control_c(signum, frame):
    print("exiting")
    sys.exit(1)

signal.signal(signal.SIGINT, control_c)

def main():
    dirname = 'wifi-dcf'
    ns3_path = os.path.join('../../../../ns3')
    
    # Check if the ns3 executable exists
    if not os.path.exists(ns3_path):
        print(f"Please run this program from within the correct directory.")
        sys.exit(1)

    results_dir = os.path.join(os.getcwd(), 'results', f"{dirname}-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    os.system('mkdir -p ' + results_dir)


    # Move to ns3 top-level directory
    os.chdir('../../../../')
    

    # Check for existing data files and prompt for removal
    check_and_remove('wifi-dcf.dat')

    # Experiment parameters
    rng_run = 1
    max_packets = 1500
    min_lambda = -4
    max_lambda = -1
    step_size = 1
    lambdas = []
    # Run the ns3 simulation for each distance
    for lam in range(min_lambda, max_lambda + 1, step_size):
        lambda_val = 10 ** lam
        lambdas.append(lambda_val)
        cmd = f"./ns3 run 'single-bss-sld --rngRun={rng_run} --payloadSize={max_packets} --perSldLambda={lambda_val}'"
        print(f'Running {cmd}')
        subprocess.run(cmd, shell=True)

    # draw plots
    plt.figure()
    plt.title('Throughput vs. Offered Load')
    plt.xlabel('Offered Load')
    plt.ylabel('Throughput (Mbps)')
    plt.grid()
    plt.xscale('log')
    throughput = []
    with open('wifi-dcf.dat', 'r') as f:
        lines = f.readlines()
        for line in lines:
            tokens = line.split(',')
            throughput.append(float(tokens[1]))
    plt.plot(lambdas, throughput, marker='o')
    plt.savefig(os.path.join(results_dir, 'wifi-dcf.png'))
    # Move result files to the experiment directory
    move_file('wifi-dcf.dat', results_dir)


    # Save the git commit information
    with open(os.path.join(results_dir, 'git-commit.txt'), 'w') as f:
        commit_info = subprocess.run(['git', 'show', '--name-only'], stdout=subprocess.PIPE)
        f.write(commit_info.stdout.decode())

    
def check_and_remove(filename):
    if os.path.exists(filename):
        response = input(f"Remove existing file {filename}? [Yes/No]: ").strip().lower()
        if response == 'yes':
            os.remove(filename)
            print(f"Removed {filename}")
        else:
            print("Exiting...")
            sys.exit(1)

def move_file(filename, destination_dir):
    if os.path.exists(filename):
        shutil.move(filename, destination_dir)

if __name__ == "__main__":
    main()
