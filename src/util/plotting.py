import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import util.io as mio
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import seaborn as sns
from model.message import Message

def plotBasicLengthStats(conv, anonymise=True):
    totalNum, totalLength, avgLegth = conv.stats.getBasicLengthStats()
    totalNumS1, totalLengthS1, avgLegthS1 = conv.stats.getBasicLengthStats(conv.sender1)
    totalNumS2, totalLengthS2, avgLegthS2 = conv.stats.getBasicLengthStats(conv.sender2)

    if anonymise:
        labels = "Donnie", "Frank"
    else:
        labels = conv.sender1, conv.sender2

    colors = [(152/255,233/255,138/255), (197/255,176/255,213/255)]

    plt.figure(1)
    plt.subplot(121)
    plt.title('Number of Messages')
    sizes = [totalNumS1/totalNum, totalNumS2/totalNum]
    plt.pie(sizes, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')

    plt.subplot(122)
    plt.title('Messages Total Length')
    sizes = [totalLengthS1/totalLength, totalLengthS2/totalLength]
    plt.pie(sizes, colors=colors, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')

    plt.legend(labels, loc='lower right')
    plt.show()

def plotDaysWithoutMessages(conv):
    #TODO extract method
    start = datetime.strptime(conv.messages[0].date, Message.DATE_FORMAT).date()
    end = datetime.strptime(conv.messages[-1].date, Message.DATE_FORMAT).date()
    datelist = pd.date_range(start, end).tolist()
    datelist = [d.date() for d in datelist]
    days = conv.getDaysWithoutMessages()
    y = [1 if d in days else 0 for d in datelist]
    print(y)

    plt.bar(range(len(datelist)),y)
    plt.xticks(np.arange(len(datelist)), datelist)
    plt.gcf().autofmt_xdate()
    plt.show()

def plotHoursStats(data):
    ax = sns.barplot(x="hour", y="len", hue="sender", data=data)
    ax.set_title("Hour Stats")
    sns.plt.show()

def plotMonthStats(data):
    #ax = sns.barplot(x="month", y="len", hue="sender", data=data)
    #ax.set_title("Month Stats"))
    grouped = data.groupby('year')
    count = 1
    plt.figure(1)
    for year, group in grouped:
        ax = plt.subplot(1,2,count)
        ax.set_title(year)
        sns.barplot(x="month", y="len", hue="sender", data=group, ax=ax)
        count += 1

    #g = sns.FacetGrid(data, col="year")
    #g.map(sns.barplot, 'month', 'len')
    sns.plt.show()

def plotHoursStatsFromFile(filepath):
    plotStatsFromFile(filepath, "Hours Stats", 3, 4, True)

def plotMonthStatsFromFile(filepath):
    plotStatsFromFile(filepath, "Months Stats", 3, 4, True)

def plotDayStatsFromFile(filepath):
    plotStatsFromFile(filepath, "Day Stats", 1, 2)
    plotStatsFromFile(filepath, "Day Stats", 3, 4)
    plotStatsFromFile(filepath, "Day Stats", 5, 6)
    plotStatsFromFile(filepath, "Day Stats", 7)
    plotStatsFromFile(filepath, "Day Stats", 8)

def plotStatsFromFile(filepath, description, y1Idx, y2Idx=None, bar=False):
    data = mio.loadDataFromFile(filepath)

    labels = ([])
    labels.append(list(data.columns.values)[0])
    labels.append(list(data.columns.values)[y1Idx])

    x = np.arange(len(data.ix[:,0]))
    xLabels = data.ix[:,0]
    y1 = data.ix[:,y1Idx]
    y2 = None

    if y2Idx:
        labels.append(list(data.columns.values)[y2Idx])
        y2 = data.ix[:,y2Idx]

    if bar:
        plotStatsBars(description, labels, x, xLabels, y1, y2)
    else:
        plotStatsLines(description, labels, x, xLabels, y1, y2)

def plotStatsBars(description, labels, x, xLabels, y1, y2):
    bar_width = 0.45
    preparePlot(description, labels[0], 'Count')

    plt.bar(x, y1, bar_width, facecolor='#9999ff', edgecolor='white', label=labels[1])

    if type(y2) != type(None):
        plt.bar(x+bar_width, y2, bar_width, facecolor='#ff9999', edgecolor='white', label=labels[2])


    plt.xticks(np.arange(len(x))+bar_width, xLabels)

    #plt.xticks(np.arange(len(data)), xLabels)

    #mean_line = ax1.plot(x,[y1.median() for i in x], label='Mean', linestyle='--')
    #mean_line = ax1.plot(x,[y2.mean() for i in x], label='Mean2', linestyle=':')

    plt.legend(loc='upper center')
    plt.tight_layout()
    plt.show()

def plotStatsLines(description, labels, x, xLabels, y1, y2):
    preparePlot(description, labels[0], 'Count')

    plt.plot(x,y1, c='r', label=labels[1], linewidth=2)

    if type(y2) != type(None):
        plt.plot(x,y2, c='b', label=labels[2], linewidth=2)


    plt.yscale('log')
    plt.xticks(np.arange(len(xLabels)), xLabels)
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.show()

def scatterDelayStats(description, labels, x, y):
    preparePlot(description, labels[0], 'Count')

    plt.scatter(x,y, c='r', label=labels[1])
    plt.legend()
    plt.show()

def preparePlot(description, xLabel, yLabel):
    plt.title(description)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)