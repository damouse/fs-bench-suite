import time
import shutil
import os
import subprocess
import glob

import matplotlib.pyplot as plot
import pylab

# The filesystem currently being tested
FS_UNDER_TEST = 'zfs'

GO_PATH = '/usr/local/go/'
WORKING_DIR = '/media/damouse/fsb/scratch'
IMAGE_DIR = WORKING_DIR.replace('scratch', 'images')

if FS_UNDER_TEST == 'ntfs':
    GO_PATH = 'C:/bin/go'
    WORKING_DIR = 'E:/scratch'
    IMAGE_DIR = WORKING_DIR.replace('scratch', 'images')

if FS_UNDER_TEST == 'zfs':
    WORKING_DIR = '/fsb/scratch'
    IMAGE_DIR = WORKING_DIR.replace('scratch', 'images')

RESULTS_PATH = 'results/' + FS_UNDER_TEST
GOPG_RESULTS_PATH = RESULTS_PATH + '/go-pg/'
IMGSERVER_RESULTS_PATH = RESULTS_PATH + '/apache/'

# Each tuple here is a test. Format is (#clients, #requests)
GOPG_PARAMS = [(1, 10), (1, 100), (1, 1000), (10, 10), (10, 100), (10, 1000)]
IMG_PARAMS = [(1, 10), (1, 100), (1, 1000), (10, 10), (10, 100), (10, 1000)]


def compilation_test():
    # Copy the go source tree
    cleardir(WORKING_DIR)
    shutil.copytree('scratch/go', WORKING_DIR + '/go')
    os.environ['GOROOT_BOOTSTRAP'] = GO_PATH

    start = time.time()

    if FS_UNDER_TEST == "ntfs":
        subprocess.call("cd %s/go/src; ./make.bat" % WORKING_DIR, shell=True)
    else:
        subprocess.call("cd %s/go/src && ./make.bash" % WORKING_DIR, shell=True)

    end = time.time()

    with open(RESULTS_PATH + '/compilation.txt', 'w') as f:
        f.write(str(end - start))

    print "Done. Time: ", end - start, 'seconds'


def webserver_test():
    cleardir(GOPG_RESULTS_PATH)

    if FS_UNDER_TEST == 'ntfs':
        subprocess.call("go build ./goserver", shell=True)
        [subprocess.call(".\goserver.exe %s %s %s" % (x, y, GOPG_RESULTS_PATH), shell=True) for x, y in GOPG_PARAMS]
    else:
        [subprocess.call("go run goserver/*.go %s %s %s" % (x, y, GOPG_RESULTS_PATH), shell=True) for x, y in GOPG_PARAMS]

    graph_go_pg()


def imgserver_test():
    cleardir(IMAGE_DIR)
    cleardir(IMGSERVER_RESULTS_PATH)

    copies = IMG_PARAMS[-1][1]
    [shutil.copy('1.jpg', os.path.join(IMAGE_DIR, str(x) + '.jpg')) for x in range(copies)]

    for x, y in IMG_PARAMS:
        if FS_UNDER_TEST == 'ntfs':
            subprocess.call("go build ./imgclient", shell=True)
            subprocess.call(".\imgclient.exe %s %s true %s" % (x, y, IMGSERVER_RESULTS_PATH), shell=True)
            subprocess.call(".\imgclient.exe %s %s false %s" % (x, y, IMGSERVER_RESULTS_PATH), shell=True)
        else:
            subprocess.call("go run imgclient/*.go %s %s true %s" % (x, y, IMGSERVER_RESULTS_PATH), shell=True)
            subprocess.call("go run imgclient/*.go %s %s false %s" % (x, y, IMGSERVER_RESULTS_PATH), shell=True)

    graph_apache()


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
        plot.axis([-1000, (end - start) * 1.1, 0, maxDuration * 1.1])
        plot.ylabel('Latency (us)')
        plot.xlabel('Request Send Time (us from start)')

        plot.savefig(name + '.png')
        plot.clf()


def graph_apache():
    ''' Read every csv output from apache and graph the results '''

    for name in glob.glob(os.path.join(IMGSERVER_RESULTS_PATH, "*")):
        with open(name, 'r') as f:
            lines = [x.split(',') for x in f.readlines()]

        sorted(lines, key=lambda x: x[1])
        start = int(lines[0][1])
        end = int(lines[-1][1])

        maxDuration = int(max(lines, key=lambda x: int(x[3]))[3])

        times = [int(x[1]) - start for x in lines]
        latency = [int(x[3]) for x in lines]

        plot.scatter(times, latency, label="N=" + " M=")
        plot.axis([-1000, (end - start) * 1.1, 0, maxDuration * 1.1])
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
    # compilation_test()
    # webserver_test()
    imgserver_test()
