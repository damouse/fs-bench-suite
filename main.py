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

RESULTS_PATH = 'results/' + FS_UNDER_TEST
GOPG_RESULTS_PATH = RESULTS_PATH + '/go-pg/'
IMGSERVER_RESULTS_PATH = RESULTS_PATH + '/apache/'

# Each tuple here is a test. Format is (#clients, #requests)
GOPG_PARAMS = [(1, 10), (1, 100), (1, 1000), (10, 10), (10, 100), (10, 1000)]
IMG_PARAMS = [(1, 10), (1, 100), (1, 1000), (10, 10), (10, 100), (10, 1000)]


def compilation_test():
    # Copy the go source tree
    # cleardir(WORKING_DIR)
    # shutil.copytree('go', WORKING_DIR + '/go')
    os.environ['GOROOT_BOOTSTRAP'] = GO_PATH
    print "cd %s/go/src; ./make.bat" % WORKING_DIR

    start = time.time()
    subprocess.call("cd %s/go/src; ./make.bat" % WORKING_DIR, shell=True)
    end = time.time()

    with open(RESULTS_PATH + '/compilation.txt', 'w') as f:
        f.write(str(end - start))

    print "Done. Time: ", end - start, 'seconds'


def webserver_test():
    cleardir(GOPG_RESULTS_PATH)

    if FS_UNDER_TEST == 'ntfs':
        [subprocess.call("(go build .\goserver\) -and (.\goserver.exe %s %s %s)" % (x, y, GOPG_RESULTS_PATH), shell=True) for x, y in GOPG_PARAMS]
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
            subprocess.call("(go build .\imgclient\) -and (.\imgclient.exe 1 1 1 1) %s %s true %s" % (x, y, IMGSERVER_RESULTS_PATH), shell=True)
            subprocess.call("(go build .\imgclient\) -and (.\imgclient.exe 1 1 1 1) %s %s false %s" % (x, y, IMGSERVER_RESULTS_PATH), shell=True)
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


def graph_test():
    import numpy as np

    with open('results/ext4/go-pg/10c-1000r', 'r') as f:
        lines = [x.split(',') for x in f.readlines()]

    sorted(lines, key=lambda x: x[1])
    start = int(lines[0][1])
    end = int(lines[-1][1])

    maxDuration = int(max(lines, key=lambda x: int(x[3]))[3])

    times = [int(x[1]) - start for x in lines]
    latency = [int(x[3]) for x in lines]
    data = latency

    values, base = np.histogram(data, bins=100)
    cumulative = np.cumsum(values)
    plot.plot(base[:-1], cumulative, c='blue')

    plot.show()


def samples():
    import numpy as np
    import matplotlib.pyplot as plt
    from math import ceil, floor, sqrt

    with open('results/ext4/go-pg/10c-1000r', 'r') as f:
        lines = [x.split(',') for x in f.readlines()]

    sorted(lines, key=lambda x: x[1])
    start = int(lines[0][1])
    end = int(lines[-1][1])

    maxDuration = int(max(lines, key=lambda x: int(x[3]))[3])

    times = [int(x[1]) - start for x in lines]
    data = [int(x[3]) for x in lines]

    def pdf(x, mu=0, sigma=1):
        """
        Calculates the normal distribution's probability density 
        function (PDF).  

        """
        term1 = 1.0 / (sqrt(2 * np.pi) * sigma)
        term2 = np.exp(-0.5 * ((x - mu) / sigma)**2)
        return term1 * term2

    # Drawing sample date poi
    ##################################################

    # Random Gaussian data (mean=0, stdev=5)
    # data1 = np.random.normal(loc=0, scale=5.0, size=30)
    # data2 = np.random.normal(loc=2, scale=7.0, size=30)

    data1 = data
    data2 = data

    data1.sort(), data2.sort()
    print data1

    min_val = floor(min(data1 + data2))
    max_val = ceil(max(data1 + data2))

    min_val = min(data1)

    ##################################################

    fig = plt.gcf()
    fig.set_size_inches(12, 11)

    # # Cumulative distributions, stepwise:
    # plt.subplot(2, 2, 1)
    # plt.step(np.concatenate([data1, data1[[-1]]]), np.arange(data1.size + 1), label='$\mu=0, \sigma=5$')
    # plt.step(np.concatenate([data2, data2[[-1]]]), np.arange(data2.size + 1), label='$\mu=2, \sigma=7$')

    # plt.title('30 samples from a random Gaussian distribution (cumulative)')
    # plt.ylabel('Count')
    # plt.xlabel('X-value')
    # plt.legend(loc='upper left')
    # plt.xlim([min_val, max_val])
    # plt.ylim([0, data1.size + 1])
    # plt.grid()

    # # Cumulative distributions, smooth:
    # plt.subplot(2, 2, 2)

    # plt.plot(np.concatenate([data1, data1[[-1]]]), np.arange(data1.size + 1), label='$\mu=0, \sigma=5$')
    # plt.plot(np.concatenate([data2, data2[[-1]]]), np.arange(data2.size + 1), label='$\mu=2, \sigma=7$')

    # plt.title('30 samples from a random Gaussian (cumulative)')
    # plt.ylabel('Count')
    # plt.xlabel('X-value')
    # plt.legend(loc='upper left')
    # plt.xlim([min_val, max_val])
    # plt.ylim([0, data1.size + 1])
    # plt.grid()

    # Probability densities of the sample points function
    plt.subplot(2, 2, 3)

    pdf1 = pdf(data1, mu=0, sigma=5)
    pdf2 = pdf(data2, mu=2, sigma=7)
    plt.plot(data1, pdf1, label='$\mu=0, \sigma=5$')
    plt.plot(data2, pdf2, label='$\mu=2, \sigma=7$')

    plt.title('30 samples from a random Gaussian')
    plt.legend(loc='upper left')
    plt.xlabel('X-value')
    plt.ylabel('probability density')
    plt.xlim([min_val, max_val])
    plt.grid()

    # Probability density function
    plt.subplot(2, 2, 4)

    x = np.arange(min_val, max_val, 0.05)

    pdf1 = pdf(x, mu=0, sigma=5)
    pdf2 = pdf(x, mu=2, sigma=7)
    plt.plot(x, pdf1, label='$\mu=0, \sigma=5$')
    plt.plot(x, pdf2, label='$\mu=2, \sigma=7$')

    plt.title('PDFs of Gaussian distributions')
    plt.legend(loc='upper left')
    plt.xlabel('X-value')
    plt.ylabel('probability density')
    plt.xlim([min_val, max_val])
    plt.grid()

    plt.show()

if __name__ == '__main__':
    # compilation_test()
    webserver_test()
    # imgserver_test()
    # graph_test()

    # samples()
