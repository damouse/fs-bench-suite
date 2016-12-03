import time
import shutil
import os
import subprocess
import glob

import matplotlib.pyplot as plot
import pylab

# The filesystem currently being tested
FS_UNDER_TEST = 'ntfs'

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
NUM_CLIENTS = [1, 10, 20, 30, 40]
TEST_TIME = 30  # seconds


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
        [subprocess.call(".\goserver.exe %s %s %s" % (x, TEST_TIME, GOPG_RESULTS_PATH), shell=True) for x in NUM_CLIENTS]
    else:
        [subprocess.call("go run goserver/*.go %s %s %s" % (x, TEST_TIME, GOPG_RESULTS_PATH), shell=True) for x in NUM_CLIENTS]


def imgserver_test():
    cleardir(IMAGE_DIR)
    cleardir(IMGSERVER_RESULTS_PATH)
    copies = NUM_CLIENTS[-1]
    [shutil.copy('1.jpg', os.path.join(IMAGE_DIR, str(x) + '.jpg')) for x in range(copies)]

    for x in NUM_CLIENTS:
        if FS_UNDER_TEST == 'ntfs':
            subprocess.call("go build ./imgclient", shell=True)
            subprocess.call(".\imgclient.exe %s %s true %s" % (x, TEST_TIME, IMGSERVER_RESULTS_PATH), shell=True)
            subprocess.call(".\imgclient.exe %s %s false %s" % (x, TEST_TIME, IMGSERVER_RESULTS_PATH), shell=True)
        else:
            subprocess.call("go run imgclient/*.go %s %s true %s" % (x, TEST_TIME, IMGSERVER_RESULTS_PATH), shell=True)
            subprocess.call("go run imgclient/*.go %s %s false %s" % (x, TEST_TIME, IMGSERVER_RESULTS_PATH), shell=True)


def cleardir(d):
    if not os.path.isdir(d):
        os.mkdir(d)
    else:
        for f in glob.glob(os.path.join(d, '*')):
            os.remove(f)


if __name__ == '__main__':
    # compilation_test()
    webserver_test()
    # imgserver_test()
