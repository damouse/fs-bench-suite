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
