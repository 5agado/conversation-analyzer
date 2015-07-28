import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from pandas import read_csv
import util.io as mio

def plotHoursStats (filepath):
    description = "Hours Stats"
    labels = ['Hours', 'AM', 'AR']
    plotStats(filepath, description, labels)

def plotStats (filepath, description, labels):
    data = mio.loadDataFromFile(filepath)

    x = range(len(data.ix[:,0]))
    xLabels = data.ix[:,0]
    y1 = data.ix[:,3]
    y2 = data.ix[:,4]

    ax1 = getSubploat(description, labels[0], 'Count')

    ax1.bar(x, y1, facecolor='#9999ff', edgecolor='white', label=labels[1])
    ax1.bar(x, y2, facecolor='#ff9999', edgecolor='white', label=labels[2])

    ax1.xaxis.set_major_formatter(ticker.NullFormatter())

    ax1.xaxis.set_minor_locator(ticker.FixedLocator([(x + 0.5) for x in range(len(data))] ))
    ax1.xaxis.set_minor_formatter(ticker.FixedFormatter(xLabels))

    #plt.xticks(np.arange(len(data)), xLabels)

    data = read_csv(filepath, comment='#')
    mean_line = ax1.plot(x,[data.ix[:,1].median() for i in x], label='Mean', linestyle='--')
    mean_line = ax1.plot(x,[data.ix[:,2].mean() for i in x], label='Mean2', linestyle=':')

    leg = ax1.legend()

    plt.show()

def plotDayCountStats (filepath):
    description, labels, data = mio.loadData(filepath)

    x = range(len(data))
    xLabels = [row.split(', ')[0] for row in data]
    y1 = [int(row.split(', ')[1]) for row in data]
    y2 = [int(row.split(', ')[2]) for row in data]

    ax1 = getSubploat(description, labels[0], 'Count')

    ax1.plot(x,y1, c='r', label=labels[1], linewidth=2.5)
    ax1.plot(x,y2, c='b', label=labels[2], linewidth=2.5)

    leg = ax1.legend()

    plt.show()

def getSubploat(description, xLabel, yLabel):
    fig = plt.figure()

    ax1 = fig.add_subplot(111)

    ax1.set_title(description)
    ax1.set_xlabel(xLabel)
    ax1.set_ylabel(yLabel)
    return  ax1