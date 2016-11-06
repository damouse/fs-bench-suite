'''
Graphing and processing
'''

import numpy
import matplotlib.pyplot as plot
from math import ceil, floor, sqrt
import math

# Load webserver data


def load_webserver():
    pass


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


def pdf(x, mu=0, sigma=1):
    term1 = 1.0 / (sqrt(2 * numpy.pi) * sigma)
    term2 = numpy.exp(-0.5 * ((x - mu) / sigma)**2)
    return term1 * term2


def pretty_cdf():
    with open('results/ext4/go-pg/10c-10r', 'r') as f:
        lines = [x.split(',') for x in f.readlines()]

    sorted(lines, key=lambda x: x[1])
    start = int(lines[0][1])
    end = int(lines[-1][1])
    maxDuration = int(max(lines, key=lambda x: int(x[3]))[3])
    times = [int(x[1]) - start for x in lines]
    latencies = [int(x[3]) for x in lines]
    data = latencies

    data1 = numpy.array(data)
    data1.sort()

    min_val = floor(min(data1))
    max_val = ceil(max(data1))

    cdfx = numpy.sort(latencies)
    cdfy = numpy.linspace(1 / len(latencies), 1.0, len(latencies))
    logcdfy = [-math.log10(1.0 - (float(idx) / len(latencies))) for idx in range(len(latencies))]

    plot.subplot(2, 2, 1)
    plot.plot(cdfx, logcdfy)
    plot.title('Latency CDF')
    plot.ylabel('Count')
    plot.xlabel('Latency')
    # plot.legend(loc='upper left')

    plot.xlim([0, 1500])
    plot.ylim([0, 1])
    plot.grid()
    plot.show()


def samples():
    with open('results/ext4/go-pg/10c-10r', 'r') as f:
        lines = [x.split(',') for x in f.readlines()]

    sorted(lines, key=lambda x: x[1])
    start = int(lines[0][1])
    end = int(lines[-1][1])
    maxDuration = int(max(lines, key=lambda x: int(x[3]))[3])
    times = [int(x[1]) - start for x in lines]
    latencies = [int(x[3]) for x in lines]
    data = latencies


if __name__ == '__main__':
    pretty_cdf()

    # samples()
