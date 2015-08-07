import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import src.util.io as mio

def plotStatsFromFile(filepath, description, y1Idx, y2Idx=None):
    data = mio.loadDataFromFile(filepath)

    labels = ([])
    labels.append(list(data.columns.values)[0])
    labels.append(list(data.columns.values)[y1Idx])

    x = range(len(data.ix[:,0]))
    xLabels = data.ix[:,0]
    y1 = data.ix[:,y1Idx]
    y2 = None

    if y2Idx:
        labels.append(list(data.columns.values)[y2Idx])
        y2 = data.ix[:,y2Idx]

    plotStatsLines(description, labels, x, xLabels, y1, y2)

def plotStatsBars(description, labels, x, xLabels, y1, y2):
    ax1 = getSubploat(description, labels[0], 'Count')

    ax1.bar(x, y1, facecolor='#9999ff', edgecolor='white', label=labels[1])

    if type(y2) != type(None):
        ax1.bar(x, y2, facecolor='#ff9999', edgecolor='white', label=labels[2])

    ax1.xaxis.set_major_formatter(ticker.NullFormatter())

    ax1.xaxis.set_minor_locator(ticker.FixedLocator([(x + 0.5) for x in range(len(x))] ))
    ax1.xaxis.set_minor_formatter(ticker.FixedFormatter(xLabels))

    #plt.xticks(np.arange(len(data)), xLabels)

    #mean_line = ax1.plot(x,[y1.median() for i in x], label='Mean', linestyle='--')
    #mean_line = ax1.plot(x,[y2.mean() for i in x], label='Mean2', linestyle=':')

    leg = ax1.legend()

    plt.show()

def plotStatsLines(description, labels, x, xLabels, y1, y2):
    ax1 = getSubploat(description, labels[0], 'Count')

    ax1.plot(x,y1, c='r', label=labels[1], linewidth=2.5)

    if type(y2) != type(None):
        ax1.plot(x,y2, c='b', label=labels[2], linewidth=2.5)

    leg = ax1.legend()

    plt.show()

def scatterDelayStats(description, labels, x, y):
    ax1 = getSubploat(description, labels[0], 'Count')

    ax1.scatter(x,y, c='r', label=labels[1])

    leg = ax1.legend()

    plt.show()

def getSubploat(description, xLabel, yLabel):
    fig = plt.figure()

    ax1 = fig.add_subplot(111)

    ax1.set_title(description)
    ax1.set_xlabel(xLabel)
    ax1.set_ylabel(yLabel)
    return  ax1