import matplotlib.pyplot as plot
import os
import pylab


outputDir = os.getcwd() + "/results/"


def graph(peers, links, groups, tasks, duration):
    test(peers)


def graphAllPeers(peers):
    for peer in peers:
        plot.plot(peer.throughput)

    plot.ylabel('Throuput (bytes)')
    plot.xlabel('Time (10s of ms)')
    plot.savefig(outputDir + 'peerThroughput.png')


def plotThrouput(stats):
    lresults, lines = [], []
    for test in stats:
        sumT = 0
        for i in range(0, len(stats[0].peers[0].throughput)):
            for peer in test.peers:
                sumT += peer.throughput[i]

            test.average.append(sumT / len(test.peers))
            sumT = 0

    for test in stats:
        addedPlot, = plot.plot(toKB(test.average), label="Peers, N=" + str(test.num))
        lines.append(addedPlot)

    pylab.legend(loc='best')
    plot.legend(handles=lines)
    plot.ylabel('Throuput (KB)')
    plot.xlabel('Time (100s of ms)')

    axe = plot.subplot(111)
    axe.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, fancybox=True, shadow=True)

    plot.savefig(outputDir + 'avg_throughput_peers.png')
    plot.clf()


def toKB(values):
    return [x / 1024 for x in values]


def plotTraditionalAverage(stats):
    lines = []

    for test in stats:
        sumClients = 0
        server = [x for x in test.peers if x.server][0]
        peers = [x for x in test.peers if not x.server]

        for i in range(0, len(stats[0].peers[0].throughput)):
            for peer in peers:
                sumClients += peer.throughput[i]

            test.average.append(sumClients / len(test.peers))
            sumClients = 0

        addedPlot, = plot.plot(toKB(test.average), label="Clients, N=" + str(test.num))
        lines.append(addedPlot)
        addedPlot, = plot.plot(toKB(server.throughput), label="Server, N=" + str(test.num))
        lines.append(addedPlot)

    pylab.legend(loc='best')
    plot.legend(handles=lines)
    plot.ylabel('Throuput (KB)')
    plot.xlabel('Time (100s of ms)')

    axe = plot.subplot(111)
    axe.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, fancybox=True, shadow=True)

    plot.savefig(outputDir + 'avg_throughput_traditional.png')
    plot.clf()


def toKB(values):
    return [x / 1024 for x in values]


def plotMulticastThroughput(stats):
    lresults, lines = [], []
    for test in stats:
        sumT = 0
        for i in range(0, len(stats[0].peers[0].throughput)):
            for peer in test.peers:
                sumT += peer.throughput[i]

            test.average.append(sumT / len(test.peers))
            sumT = 0

    for test in stats:
        addedPlot, = plot.plot(toKB(test.average), label="N=" + str(test.num) + " M=" + str(test.connectivity))
        lines.append(addedPlot)

    pylab.legend(loc='best')
    plot.legend(handles=lines)
    plot.ylabel('Throuput (KB)')
    plot.xlabel('Time (100s of ms)')

    axe = plot.subplot(111)
    axe.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, fancybox=True, shadow=True)

    plot.savefig(outputDir + 'avg_throughput_aoi_peers.png')
    plot.clf()


def plotLatency(stats):
    ignore = 1000  # ignore the last chunk of time, its incorrect
    maxTime = max(stats[0].tasks, key=lambda x: x.startTime).startTime - 1000
    results, lines = [], []

    for test in stats:
        latency = {}
        time, averageLat = [], []

        for task in test.tasks:
            if not task.startTime in latency:
                latency[task.startTime] = []
            latency[task.startTime].append(task.time)

        for key in sorted(latency.keys()):
            if key >= maxTime:
                continue
            total = 0.0
            for x in latency[key]:
                total += x
            averageLat.append(total / len(latency[key]))
            time.append(key / 100)

        if test.comment != None:
            addedPlot, = plot.plot(time, averageLat, label="CSA, N=" + str(test.num))
        else:
            addedPlot, = plot.plot(time, averageLat, label="N=" + str(test.num) + " M=" + str(test.connectivity))
        lines.append(addedPlot)

    pylab.legend(loc='best')
    plot.legend(handles=lines)
    plot.ylabel('Latency (ms)')
    plot.xlabel('Time (100s of ms)')

    axe = plot.subplot(111)
    axe.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=2, fancybox=True, shadow=True)

    plot.savefig(outputDir + 'avg_latency_peers.png')
    plot.clf()
