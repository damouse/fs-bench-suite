'''
Graphing and processing
'''

import numpy
import matplotlib.pyplot as plot
from math import ceil, floor, sqrt
import math
import glob
import os
import sys

import runner

RESULTS_PATH = 'results'
GRAPH_PATH = 'graphs'

# Converts us to ms if set
CONVERT_MS = True


class ResultRow():

    def __init__(self, raw):
        self.raw = raw
        split = [x for x in raw.split(',')]

        self.client_num = int(split[0])
        self.start_time = int(split[1])
        self.end_time = int(split[2])
        self.diff_time = int(split[3])

        if CONVERT_MS:
            self.client_num = self.client_num / 1000
            self.start_time = self.start_time / 1000
            self.end_time = self.end_time / 1000
            self.diff_time = self.diff_time / 1000


class TestResults():

    def __init__(self, fs, test, filepath):
        self.fs = fs
        self.filepath = filepath
        self.test = test

        self.name = filepath.split('\\')[-1]
        split = self.name.split('-')
        self.clients = int(split[0].replace('c', ''))
        self.requests = int(split[1].replace('r', ''))
        self.save_name = self.fs + '-' + self.name

        if self.test is 'apache':
            self.unique = split[2]

        # Load the data
        with open(filepath, 'r') as f:
            self.lines = sorted([ResultRow(x) for x in f.readlines()], key=lambda x: x.start_time)

        # Min, max
        self.start = self.lines[0].start_time
        self.end = self.lines[-1].start_time
        self.max_value = max(self.lines, key=lambda x: x.diff_time).diff_time
        self.min_value = min(self.lines, key=lambda x: x.diff_time).diff_time


def load_data():
    # return [TestResults('ntfs', 'apache', 'results/ntfs/apache/10c-10r-shared')]
    # return [TestResults('ntfs', 'apache', 'results/ntfs/apache/10c-1000r-shared')]
    return [TestResults(fs, test, file)
            for test in ['apache', 'go-pg']
            for fs in ['ntfs', 'ext4', 'zfs']
            for file in glob.glob(os.path.join(RESULTS_PATH, fs, test, '*'))]


# Scatter plots
def latency_scatter(result, output_subfolder=None):
    x, y = [x.start_time - result.start for x in result.lines], [x.diff_time for x in result.lines]

    plot.scatter(x, y, label="N=" + " M=")
    plot.axis([0, (result.end - result.start) * 1.1, 0, result.max_value * 1.1])
    plot.ylabel('Latency (ms)')
    plot.xlabel('Request Send Time (ms from start)')

    if output_subfolder is None:
        plot.show()
    else:
        plot.savefig(os.path.join(GRAPH_PATH, output_subfolder, result.save_name))

    plot.clf()


def pretty_cdf():
    with open('results/ext4/go-pg/10c-10r', 'r') as f:
        lines = [x.split(',') for x in f.readlines()]

    sorted(lines, key=lambda x: x[1])
    start = int(lines[0][1])
    end = int(lines[-1][1])
    max_value = int(max(lines, key=lambda x: int(x[3]))[3])
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
    max_value = int(max(lines, key=lambda x: int(x[3]))[3])
    times = [int(x[1]) - start for x in lines]
    latencies = [int(x[3]) for x in lines]
    data = latencies


def pdf(x, mu=0, sigma=1):
    term1 = 1.0 / (sqrt(2 * numpy.pi) * sigma)
    term2 = numpy.exp(-0.5 * ((x - mu) / sigma)**2)
    return term1 * term2

if __name__ == '__main__':
    data = load_data()

    runner.cleardir(os.path.join(GRAPH_PATH, 'scatter'))
    [latency_scatter(d, "scatter") for d in data]

    # print data[0].name
    # latency_scatter(data[0])
    # pretty_cdf()
    # samples()
