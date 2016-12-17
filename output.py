'''
Graphing and processing
'''

import math
import glob
import os
import sys

import numpy as np
from scipy.stats.kde import gaussian_kde
import seaborn as sns

from numpy import linspace
import matplotlib.pyplot as plt
from math import ceil, floor, sqrt
from scipy import stats

import runner

# Because thanks, windows
FILE_SEPERATOR = '\\' if os.name == 'nt' else '/'
RESULTS_PATH = 'results'
GRAPH_PATH = 'graphs'
PDF_BINS = 50


class ResultRow():

    def __init__(self, raw):
        self.raw = raw
        split = [x for x in raw.split(',')]
        self.client_num = float(split[0])

        # Convert us to ms
        self.start_time = float(split[1]) / 1000
        self.end_time = float(split[2]) / 1000
        self.diff_time = float(split[3]) / 1000


class MacroResults():

    def __init__(self, fs, test, filepath):
        self.fs = fs
        self.filepath = filepath
        self.test = test

        # Basic names
        self.name = filepath.split(FILE_SEPERATOR)[-1]

        split = self.name.split('-')
        self.clients = int(split[0].replace('c', ''))
        self.requests = int(split[1].replace('r', ''))
        self.pretty_name = 'Apache' if self.test is 'apache' else 'Go Webserver'

        # Load the data
        with open(filepath, 'r') as f:
            self.lines = sorted([ResultRow(x) for x in f.readlines()], key=lambda x: x.start_time)

        # Min, max
        self.start = self.lines[0].start_time
        self.end = self.lines[-1].start_time
        self.max_value = max(self.lines, key=lambda x: x.diff_time).diff_time
        self.min_value = min(self.lines, key=lambda x: x.diff_time).diff_time


def latency_scatter(result, output_subfolder):
    time = [x.start_time - result.start for x in result.lines]
    lat = [x.diff_time for x in result.lines]

    plt.scatter(time, lat, label="N=" + " M=")
    plt.xlim([0, result.end - result.start])
    plt.ylim([0, result.max_value])

    plt.title('{} clients, {}, {}, {}s'.format(result.clients, result.pretty_name, result.fs, result.requests))
    plt.ylabel('Latency (ms)')
    plt.xlabel('Time (ms)')

    plt.savefig(os.path.join(output_subfolder, result.fs + '-' + result.name))
    plt.clf()


def latency_cdf(result, output_subfolder):
    data = np.sort(map(lambda x: x.diff_time, result.lines))

    plot_pdf(data)

    plt.xlim([0, result.max_value])
    plt.ylim([0, 1])
    plt.grid()

    plt.title('{} clients, {}, {}, {}s'.format(result.clients, result.pretty_name, result.fs, result.requests))
    plt.ylabel('Count')
    plt.xlabel('Latency (ms)')

    plt.savefig(os.path.join(output_subfolder, result.fs + '-' + result.name))
    plt.clf()


def latency_boxplot(result, output_subfolder=None):
    bins = np.linspace(result.start, result.end, 30)
    binned = [filter(lambda x: maxx > x.start_time > minn, result.lines) for (minn, maxx) in zip(bins[:-1], bins[1:])]
    binned = [map(lambda x: x.diff_time, y) for y in binned]

    plt.boxplot(binned, 0, '')
    plt.ylabel('Request Latency (ms)')
    plt.xlabel('Time (s)')
    plt.title('Boxed latency for {} clients, {}, {}s'.format(result.clients, result.pretty_name, result.requests))

    plt.savefig(os.path.join(output_subfolder, result.fs + '-' + result.name))
    plt.clf()


def plot_pdf(data, bins=PDF_BINS, label=None):
    sns.kdeplot(np.array(data))
    return
    # Plots a pdf but doesnt save it
    plt.subplot(211)
    hist, bins = np.histogram(data, bins=bins, density=False)
    bin_centers = (bins[1:] + bins[:-1]) * 0.5
    avg = [float(x) / float(len(data)) for x in hist]
    plt.plot(bin_centers, avg)

    kde = gaussian_kde(data)
    dist_space = linspace(min(data), max(data), 500)
    plt.subplot(212)
    plt.plot(dist_space, kde(dist_space), label=label)


def aggregate_client_cdf(results, output_subfolder):
    for test_group in zip(*[filter(lambda x: x.fs == fs, results) for fs in ['ntfs', 'ext4', 'zfs']]):
        for fs in test_group:
            data = map(lambda x: x.diff_time, fs.lines)

            # hist, bins = np.histogram(data, bins=PDF_BINS, density=False)
            # bin_centers = (bins[1:] + bins[:-1]) * 0.5
            # avg = [float(x) / float(len(data)) for x in hist]
            # plt.plot(bin_centers, avg, label=fs.fs)

            plot_pdf(data, label=fs.fs)

        plt.ylabel('Count (%)')
        plt.xlabel('Request Latency (ms)')
        plt.title('CDF for {} clients, {}, {}s'.format(test_group[0].clients, test_group[0].pretty_name, test_group[0].requests))
        plt.legend(loc='lower right')

        plt.xlim([0, max(map(lambda x: x.max_value, test_group))])
        # plt.xlim([0, 100])
        plt.ylim([0, 1.05])

        plt.grid()
        plt.savefig(os.path.join(output_subfolder, '{}-{}'.format(test_group[0].clients, test_group[0].requests)))
        plt.clf()


def aggregate_platform_cdf(results, output_subfolder):
    tests = []

    for fs_slice in [filter(lambda x: x.fs == fs, results) for fs in ['ntfs', 'ext4', 'zfs']]:
        for test_slice in [filter(lambda x: x.test == test, fs_slice) for test in ['go-pg', 'apache']]:
            if len(test_slice) != 0:
                tests.append(test_slice)

    for test_group in tests:
        for fs in sorted(test_group, key=lambda x: x.clients):
            data = map(lambda x: x.diff_time, fs.lines)

            # hist, bins = np.histogram(data, bins=PDF_BINS, density=False)
            # bin_centers = (bins[1:] + bins[:-1]) * 0.5
            # avg = [float(x) / float(len(data)) for x in hist]
            # plt.plot(bin_centers, avg, label=str(fs.clients) + " clients")

            plot_pdf(data, label=str(fs.clients) + " clients")

        plt.ylabel('Count (%)')
        plt.xlabel('Latency (ms)')
        plt.title('CDF for varying Clients, {} on {}, {}s'.format(test_group[0].pretty_name, test_group[0].fs, test_group[0].requests))
        plt.legend(loc='lower right')

        # plt.xlim([0, 100])
        plt.ylim([0, 1.05])

        plt.grid()
        plt.savefig(os.path.join(output_subfolder, '{}'.format(test_group[0].fs)))
        plt.clf()


def load_macrobenchmarks():
    return [MacroResults(fs, test, file)
            for test in ['apache', 'go-pg']
            for fs in ['ntfs', 'ext4', 'zfs']
            for file in glob.glob(os.path.join(RESULTS_PATH, fs, test, '*'))]


def graph(all_data):
    for test in ['apache', 'go-pg']:
        data = filter(lambda x: x.test == test, all_data)

        # # Individual scatter plots
        # p = os.path.join(GRAPH_PATH, test, 'scatter')
        # runner.cleardir(p)
        # [latency_scatter(d, p) for d in data]

        # Individual CDFs
        p = os.path.join(GRAPH_PATH, test, 'cdf')
        runner.cleardir(p)
        [latency_cdf(d, p) for d in data]

        # Aggregate CDFs per # clients
        p = os.path.join(GRAPH_PATH, test, 'aggregate-client-cdf')
        runner.cleardir(p)
        aggregate_client_cdf(data, p)

        # Aggregate CDFs per fs
        p = os.path.join(GRAPH_PATH, test, 'aggregate-fs-cdf')
        runner.cleardir(p)
        aggregate_platform_cdf(data, p)


def test_pdf():
    # Design note: this is an excellent API because it needs the minimum amount of information to dive down the tree
    # without corralling it all together into a full filename (minus requiring the whole name at the end,
    # that was immensely stupid.
    result = MacroResults('zfs', 'apache', 'results/zfs/apache/10c-30r')
    data = np.array([x.diff_time for x in result.lines])

    # Method 1
    plt.subplot(311)
    hist, bins = np.histogram(data, bins=400, density=False)
    bin_centers = (bins[1:] + bins[:-1]) * 0.5
    avg = [float(x) / float(len(data)) for x in hist]
    plt.plot(bin_centers, avg)

    # Method 2
    kde = gaussian_kde(data)
    dist_space = linspace(min(data), max(data), 100)
    plt.subplot(312)
    plt.plot(dist_space, kde(dist_space))

    # Method 3
    plt.subplot(313)
    # sns.set_style('whitegrid')
    sns.kdeplot(np.array(data))

    plt.show()

if __name__ == '__main__':
    all_data = load_macrobenchmarks()
    graph(all_data)
    # test_pdf()
