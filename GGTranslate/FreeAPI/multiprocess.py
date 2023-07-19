import subprocess
from multiprocessing import Process
import argparse
import time
import os
import signal

proces_ls = []
def run_consumer(i):
    proc = subprocess.Popen(f"python translate_consumer.py --i {i}", shell=True)
    proces_ls.append(proc)
    print(proc.pid)
    proc.communicate()

if __name__ == '__main__':
   
    execs = []
    
    parser = argparse.ArgumentParser(description='Consumer runner parser.')

    parser.add_argument('--num',
                    type=int, default=30,
                    help='Number of consumer')

    args = parser.parse_args()
    n_pro = args.num
    
    for i in range(n_pro):
        ex = Process(target=run_consumer, args=(i,))
        ex.daemon = True
        execs.append(ex)
        
        ex.start()
    try:
        for exe in execs:
            exe.join()
    except KeyboardInterrupt:
        print('Intertupt')
        for exe in execs:
            exe.terminate()