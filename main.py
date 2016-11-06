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


def webserver_test():
    cleardir(GOPG_RESULTS_PATH)

    if FS_UNDER_TEST == 'ntfs':
        subprocess.call("go build ./goserver", shell=True)
        [subprocess.call(".\goserver.exe %s %s %s" % (x, y, GOPG_RESULTS_PATH), shell=True) for x, y in GOPG_PARAMS]
    else:
        [subprocess.call("go run goserver/*.go %s %s %s" % (x, y, GOPG_RESULTS_PATH), shell=True) for x, y in GOPG_PARAMS]


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


def cleardir(d):
    if os.path.isdir(d):
        shutil.rmtree(d)
        os.mkdir(d)


if __name__ == '__main__':
    # compilation_test()
    # webserver_test()
    imgserver_test()
