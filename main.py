import time
import shutil
import os
import subprocess
import glob

import matplotlib.pyplot as plot
import pylab

# The filesystem currently being tested
FS_UNDER_TEST = 'ext4'

RESULTS_PATH = 'results/' + FS_UNDER_TEST

GO_PATH = '/home/damouse/.gvm/gos/go1.6'
GOPG_RESULTS_PATH = RESULTS_PATH + '/go-pg/'

# Used for downloads, temporary files, etc
WORKING_DIR = 'scratch'

# Each tuple here is a test. Format is (#clients, #requests)
GOPG_PARAMS = [(1, 10), (1, 100), (1, 1000), (10, 10), (10, 100), (10, 1000)]
# GOPG_PARAMS = [(1, 10), (1, 100)]

def compilation_test():
    # Copy the go source tree
    cleardir('ext4')
    shutil.copytree(WORKING_DIR + '/go', WORKING_DIR + '/ext4/go')
    os.environ['GOROOT_BOOTSTRAP'] = GO_PATH

    start = time.time()
    subprocess.call("cd %s/ext4/go/src; ./all.bash" % WORKING_DIR, shell=True)
    end = time.time()

    print "Done. Time: ", end - start, 'seconds'

def webserver_test():
    cleardir(GOPG_RESULTS_PATH)
    [subprocess.call("go run goserver/*.go %s %s %s" % (x, y, GOPG_RESULTS_PATH), shell=True) for x, y in GOPG_PARAMS]
    graph_go_pg()

def graph_go_pg():
    ''' Read every csv output from goserver and graph the results '''

    for name in glob.glob(os.path.join(GOPG_RESULTS_PATH, "*")):
        with open(name, 'r') as f:
            lines = [x.split(',') for x in f.readlines()]

        sorted(lines, key=lambda x: x[1])
        start = int(lines[0][1])
        end = int(lines[-1][1])

        maxDuration = int(max(lines, key=lambda x: int(x[3]))[3])

        times = [int(x[1]) - start for x in lines]
        latency = [int(x[3]) for x in lines]

        plot.scatter(times, latency, label="N=" + " M=")
        plot.axis([-1000, (end - start) *1.1, 0, maxDuration * 1.1])
        plot.ylabel('Latency (us)')
        plot.xlabel('Request Send Time (us from start)')

        plot.savefig(name + '.png')
        plot.clf()

def cleardir(d):
    ''' Destroy and remake the target directory '''
    if os.path.isdir(d):
        shutil.rmtree(d)
        os.mkdir(d)


if __name__ == '__main__':
    compilation_test()
    webserver_test()


