'''
Graphing and processing
'''

import math
import glob
import os
import sys

import numpy
import matplotlib.pyplot as plot
from math import ceil, floor, sqrt
from scipy import stats

import runner

RESULTS_PATH = 'results'
GRAPH_PATH = 'graphs'

# Windows paths... why
FILE_SEPERATOR = '\\'


class ResultRow():

    def __init__(self, raw):
        self.raw = raw
        split = [x for x in raw.split(',')]
        self.client_num = float(split[0])

        # Convert us to ms
        self.start_time = float(split[1]) / 1000
        self.end_time = float(split[2]) / 1000
        self.diff_time = float(split[3]) / 1000


class TestResults():

    def __init__(self, fs, test, filepath):
        self.fs = fs
        self.filepath = filepath
        self.test = test

        # Basic names
        self.name = filepath.split(FILE_SEPERATOR)[-1]

        split = self.name.split('-')
        self.clients = int(split[0].replace('c', ''))
        self.requests = int(split[1].replace('r', ''))
        self.pretty_name = 'Go Webserver'

        if self.test is 'apache':
            self.unique = split[2]
            self.pretty_name = 'Apache'

        # Load the data
        with open(filepath, 'r') as f:
            self.lines = sorted([ResultRow(x) for x in f.readlines()], key=lambda x: x.start_time)

        # Min, max
        self.start = self.lines[0].start_time
        self.end = self.lines[-1].start_time
        self.max_value = max(self.lines, key=lambda x: x.diff_time).diff_time
        self.min_value = min(self.lines, key=lambda x: x.diff_time).diff_time


def latency_scatter(result, output_subfolder=None):
    time = [x.start_time - result.start for x in result.lines]
    lat = [x.diff_time for x in result.lines]

    plot.scatter(time, lat, label="N=" + " M=")
    plot.xlim([0, result.end - result.start])
    plot.ylim([0, result.max_value])

    plot.title('{} on {}: {} clients making {} requests'.format(result.pretty_name, result.fs, result.clients, result.requests))
    plot.ylabel('Latency (ms)')
    plot.xlabel('Request Send Time (ms from start)')

    if output_subfolder is None:
        plot.show()
    else:
        plot.savefig(os.path.join(output_subfolder, result.fs + '-' + result.name))

    plot.clf()


def latency_cdf(result, output_subfolder=None):
    data = numpy.sort(map(lambda x: x.diff_time, result.lines))

    plot.plot(data, numpy.linspace(0, 1, len(data)))
    plot.xlim([0, result.max_value])
    plot.ylim([0, 1])
    plot.grid()

    plot.title('{} on {}: {} clients making {} requests'.format(result.pretty_name, result.fs, result.clients, result.requests))
    plot.ylabel('Count')
    plot.xlabel('Latency (ms)')

    if output_subfolder is None:
        plot.show()
    else:
        plot.savefig(os.path.join(output_subfolder, result.fs + '-' + result.name))

    plot.clf()


def aggregate_cdf(results, output_subfolder=None):
    # Create 3-tuples that contain the same test conditions for each fs
    for test_group in zip(*[filter(lambda x: x.fs == fs, results) for fs in ['ntfs', 'ext4', 'zfs']]):
        for fs in test_group:
            latencies = map(lambda x: x.diff_time, fs.lines)

            cdfx = numpy.sort(latencies)
            cdfy = numpy.linspace(1 / len(latencies), 1.0, len(latencies))
            logcdfy = [-math.log10(1.0 - (float(idx) / len(latencies))) for idx in range(len(latencies))]

            # plot.plot(cdfx, logcdfy, label=fs.fs)
            plot.plot(cdfx, numpy.linspace(0, 1, len(cdfx)), label=fs.fs)

        plot.ylabel('Count')
        plot.xlabel('Latency (ms)')
        plot.title('{} Duration CDF: {} clients with {} requests each'.format(test_group[0].pretty_name, test_group[0].clients, test_group[0].requests))
        plot.legend(loc='lower right')

        plot.xlim([0, max(map(lambda x: x.max_value, test_group))])
        plot.ylim([0, 1.05])
        plot.grid()

        if output_subfolder is None:
            plot.show()
        elif test_group[0].test == 'apache':
            plot.savefig(os.path.join(output_subfolder, '{}-{}-{}'.format(test_group[0].clients, test_group[0].requests, test_group[0].unique)))
        else:
            plot.savefig(os.path.join(output_subfolder, '{}-{}'.format(test_group[0].clients, test_group[0].requests)))

        plot.clf()


def pdf(x, mu=0, sigma=1):
    term1 = 1.0 / (sqrt(2 * numpy.pi) * sigma)
    term2 = numpy.exp(-0.5 * ((x - mu) / sigma)**2)
    return term1 * term2


def load_data():
    return [TestResults(fs, test, file)
            for test in ['apache', 'go-pg']
            for fs in ['ntfs', 'ext4', 'zfs']
            for file in glob.glob(os.path.join(RESULTS_PATH, fs, test, '*'))]


def graph(all_data):
    for test in ['apache', 'go-pg']:
        data = filter(lambda x: x.test == test, all_data)

        # Individual scatter plots
        p = os.path.join(GRAPH_PATH, test, 'scatter')
        runner.cleardir(p)
        [latency_scatter(d, p) for d in data]

        # Individual CDFs
        p = os.path.join(GRAPH_PATH, test, 'cdf')
        runner.cleardir(p)
        [latency_cdf(d, p) for d in data]

        # Aggregate CDFs
        p = os.path.join(GRAPH_PATH, test, 'aggregate-cdf')
        runner.cleardir(p)
        aggregate_cdf(data, p)


def test_cdf():
    t = TestResults('ext4', 'apache', 'results\\ext4\\apache\\10c-1000r-shared')
    d = map(lambda x: x.diff_time, t.lines)
    data = numpy.sort(d)

    # cdfx = numpy.sort(latencies)
    cdfy = numpy.linspace(1 / len(d), 1.0, len(d))
    # plot the CDF
    plot.plot(data, cdfy)

    # With linspace, no cdf calculation
    # Can easily do log with [1 + math.log10(d) for d in data], but have to update the axes too
    # cdfy = numpy.linspace(0, 1, len(data))
    # plot.plot(data, cdfy)
    # plot.ylim([0, 1.1])

    plot.grid()
    plot.show()


def test_bars():
    t = TestResults('ext4', 'apache', os.path.join('results', 'ext4', 'apache', '10c-1000r-shared'))
    d = map(lambda x: x.diff_time, t.lines)
    data = numpy.array(d)

    for d in data:
        print d

    # fake up some data
    # spread = numpy.random.rand(50) * 100
    # center = numpy.ones(25) * 50
    # flier_high = numpy.random.rand(10) * 100 + 100
    # flier_low = numpy.random.rand(10) * -100
    # data = numpy.concatenate((spread, center, flier_high, flier_low), 0)

    bins = numpy.linspace(0, 1, 10)
    digitized = numpy.digitize(data, bins)
    bin_means = [list(data[digitized == i]) for i in range(1, len(bins))]

    for i in range(1, len(bins)):
        print data[digitized == i]
        print type(data[digitized == i])
        # plot.boxplot(data[digitized == i], 0, '')

    plot.boxplot(bin_means, 0, '')

    # horizontal boxes
    # plot.figure()
    # plot.boxplot(data, 0, 'rs', 0)

    # # change whisker length
    # plot.figure()
    # plot.boxplot(data, 0, 'rs', 0, 0.75)

    # # fake up some more data
    # spread = numpy.random.rand(50) * 100
    # center = numpy.ones(25) * 40
    # flier_high = numpy.random.rand(10) * 100 + 100
    # flier_low = numpy.random.rand(10) * -100
    # d2 = numpy.concatenate((spread, center, flier_high, flier_low), 0)
    # data.shape = (-1, 1)
    # d2.shape = (-1, 1)
    # # data = concatenate( (data, d2), 1 )
    # # Making a 2-D array only works if all the columns are the
    # # same length.  If they are not, then use a list instead.
    # # This is actually more efficient because boxplot converts
    # # a 2-D array into a list of vectors internally anyway.
    # data = [data, d2, d2[::2, 0]]
    # # multiple box plots on one figure
    # plot.figure()
    # plot.boxplot(data)

    plot.show()

if __name__ == '__main__':
    all_data = load_data()

    # graph(all_data)
    test_bars()
