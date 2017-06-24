import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import util.io as mio
from model.message import Message

SAVE_PLOT = False

#TODO use K for diagrams, vertical lines separate between senders

def plotBasicLengthStatsByYearAndMonth(data, yearsToShow=[]):
    #sns.plt.title('Basic Length Stats')

    df = data[data['year'].isin(yearsToShow)]
    df = df.set_index(['year', 'month', 'sender'])

    df = transformStats(df, 'stat', 'val')
    g = sns.factorplot(x="month", y="val", row="stat", hue='sender', col='year', data=df,
                       kind="bar", sharey=False,
                        size=3, aspect=2.5)
    sns.plt.show()

#TODO FIX too complex visualization
def plotBasicLengthStatsByMonthAndHourForYear(data, yearToShow):
    #figureAesthetic()
    sns.set_context("poster")
    #sns.plt.title('Basic Length Stats')

    grouped = data.groupby('year')
    for year, group in grouped:
        if yearToShow and yearToShow!=year:
            continue
        df = group.drop('year', 1)
        df = df.set_index(['hour', 'month', 'sender'])
        df = transformStats(df, 'stats', 'val')
        g = sns.FacetGrid(df, col='month', row='stat', margin_titles=True, sharey=False)
        g.map(sns.barplot, 'hour', 'val', 'sender')
        g.add_legend()
    sns.plt.show()

def plotSingleBasicLengthStatByYearAndMonth(data, stat, yearToShow=None):
    figureAesthetic()
    def plot(ax, df, count):
        ax = sns.barplot(x="month", y="lenMsgs", hue="sender", data=df, ax=ax)
        ax.set(ylabel=stat if count == 1 else '')

    _plotByYear(data, stat, plot, yearToShow)

def plotSingleBasicLengthStatByHour(data, stat):
    figureAesthetic()
    ax = sns.barplot(x="hour", y=stat, hue="sender", data=data)
    ax.set(ylabel=stat)
    #ax.set_title("Hour Stats")
    sns.plt.show()

def plotSingleBasicLengthStatByYearAndHour(data, stat, yearsToShow=[]):
    figureAesthetic()
    def plot(ax, df, count):
        ax = sns.barplot(x="hour", y=stat, hue="sender", data=df, ax=ax)
        ax.set(ylabel=stat if count == 1 else '')

    _plotByYear(data, stat, plot, yearsToShow)

def plotSingleBasicLengthStatByYearAndMonth(data, stat, yearsToShow=[]):
    figureAesthetic()
    def plot(ax, df, count):
        ax = sns.barplot(x="month", y=stat, hue="sender", data=df, ax=ax)
        ax.set(ylabel=stat if count == 1 else '')

    _plotByYear(data, stat, plot, yearsToShow)

def plotSingleBasicLengthStatHeatmap(data, stat, yearsToShow=[]):
    figureAesthetic()
    def plot(ax, df, count):
        df = df.pivot('month', 'day', stat)
        ax = sns.heatmap(df, mask=df.isnull(), ax=ax)
        #ax.set(ylabel=stat if count == 1 else '')
        ax.set(ylabel='month' if count == 1 else '')
        ax.set_title(stat)
        #sns.heatmap(df, mask=df.notnull(), cmap=ListedColormap(['red', 'blue']), cbar=False)

    _plotByYear(data, stat, plot, yearsToShow)

#----------------------------#
#       WORDS USAGE
#----------------------------#

# TODO fill all possible values for the index (dates, month, year)
# Add sender or total labels
def plotWordsCount(wordsCountStats, words, sender=None, yearsToShow=None):
    data = wordsCountStats.getWordsCount(words, sender)
    if data is None:
        return
    def plot(ax, df, count):
        df.reset_index(level='year').plot(ax=ax)

    if 'year' in list(data.index.names):
        _plotByYear(data, 'Word count', plot, yearsToShow)
    else:
        data.plot()
        sns.plt.show()

def plotZipfLaw(words, count):
    figureAesthetic()

    #plt.figure(1).suptitle("Zip's Law", fontsize=20)
    ax = plt.subplot(1,2,1)
    plt.xlabel("word")
    plt.ylabel("frequency")
    numWords = 20
    x = np.arange(numWords)
    y = count[:numWords]
    plt.xticks(np.arange(len(x)), words[:numWords])
    plt.gcf().autofmt_xdate()
    ax.plot(x, y, c='r', linewidth=2)

    ax = plt.subplot(1,2,2)
    plt.xlabel("rank (log scale)")
    plt.ylabel("frequency (log scale)")
    x = np.arange(len(words))
    plt.xscale('log')
    plt.yscale('log')
    ax.plot(x,count, c='r', linewidth=2)

    plt.show()

def plotRichnessVariation(data, yearsToShow=[]):
    figureAesthetic()
    max_val = data['lexicalRichness'].max()
    min_val = data['lexicalRichness'].min()
    def plot(ax, df, count):
        ax = sns.pointplot(data=df, y='lexicalRichness', x='month', hue='sender', ax=ax)
        ax.set_ylim([min_val - 0.1, max_val + 0.1])
        ax.set(ylabel='lexical richness (%)' if count == 1 else '')

    _plotByYear(data, 'Vocabulary Richness', plot, yearsToShow)

def plotSentimentStatsByHour(sentimentStats, valueNames):
    data = _transformSentimentStats(sentimentStats, valueNames, ['sender', 'hour'])
    ax = sns.factorplot(x="hour", y="val", col="emotion", hue='sender',
                   data=data, kind="point", sharey=False)
    ax.set(ylabel='mean(val)')
    sns.plt.show()

def plotSentimentStatsByYearAndMonth(sentimentStats, valueNames):
    data = _transformSentimentStats(sentimentStats, valueNames, ['sender', 'year', 'month'])
    sns.factorplot(x="month", y="val", row="emotion", hue='sender', col='year',
                   data=data, kind="point", sharey=False)
    sns.plt.show()

def _transformSentimentStats(sentimentStats, valueNames, groupByColumns, aggFun='mean'):
    data = sentimentStats.groupby(groupByColumns).agg(dict([(x, aggFun) for x in valueNames]))
    data = transformStats(data, 'emotion', 'val')

    return data

def transformStats(stats, statsName, valName):
    """
    Transform stats for plotting with stacking of current indexes
    :param stats: df to transform
    :param statsName: name to give to stats column (previously different column values)
    :param valName: name to give to value column (previously cell values)
    :return:
    """
    res = stats.stack().reset_index()
    res.columns.values[-2] = statsName
    res.columns.values[-1] = valName

    return res

#TODO refactor
def plotDaysWithoutMessages(conv):
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

def figureAesthetic():
    sns.set_context("poster")
    sns.set_style("darkgrid")
    sns.plt.grid(True)

def _plotByYear(data, title, plotFun, yearsToShow=None):
    plt.title(title)
    if 'year' in list(data.index.names):
        grouped = data.groupby(level='year')
    else:
        grouped = data.groupby('year')
    numberOfYears = len(grouped) if not yearsToShow else len(yearsToShow)
    count = 1
    fig = plt.figure(1)
    for year, group in grouped:
        if yearsToShow and year not in yearsToShow:
            continue
        ax = plt.subplot(1,numberOfYears,count)
        ax.set_title(year)
        plotFun(ax, group, count)
        count += 1
    #savePlotAsImage(fig, "image.png")
    sns.plt.show()

def plotStatsLines(description, labels, x, xLabels, y1, y2):
    figureAesthetic()

    sns.set_style("darkgrid")
    plt.plot(x,y1, c='r', label=labels[1], linewidth=2)

    if type(y2) != type(None):
        plt.plot(x,y2, c='b', label=labels[2], linewidth=2)


    #plt.yscale('log')
    plt.xticks(np.arange(len(xLabels)), xLabels)
    plt.legend()
    plt.gcf().autofmt_xdate()
    plt.show()

def savePlotAsImage(plot, filename):
    folderPath = os.path.join(mio.getResourcesPath(), 'imgs')
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    if SAVE_PLOT:
        filepath = os.path.join(folderPath, filename)
        plot.savefig(filepath)
    else:
        pass