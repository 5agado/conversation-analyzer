import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

import util.io as mio
from util import statsUtil
from model.message import Message

SAVE_PLOT = False

def plotBasicLengthStatsByYearAndMonth(data, yearsToShow=None, targetStats=None,
                                       targetSenders=None):
    df = statsUtil.filter_stats(data, {'sender':targetSenders, 'year':yearsToShow,
                                        'stat':targetStats})

    g = sns.factorplot(x="month", y="val", row="stat", hue='sender', col='year', data=df,
                       kind="bar", sharey=False, size=3, aspect=2.5, legend_out=False)
    g.fig.suptitle('Basic Length Stats')
    sns.plt.show()

def plotBasicLengthStatsByHour(data, targetStats=None, targetSenders=None, kind='bar'):
    df = statsUtil.filter_stats(data, {'sender':targetSenders, 'stat':targetStats})

    g = sns.factorplot(x="hour", y="val", row="stat", hue='sender', data=df,
                       kind=kind, sharey=False, size=3, aspect=2.5, legend_out=False)
    g.fig.suptitle('Basic Length Stats - Hour')
    #sns.plt.show()

def plotRichnessVariation(data, targetLabel, yearsToShow=None, targetSenders=None):
    df = data.reset_index()
    df = statsUtil.filter_stats(df, {'year':yearsToShow, 'sender':targetSenders})

    g = sns.factorplot(x=targetLabel, y="lexicalRichness", col="year", hue='sender',
                   data=df, kind="point", legend_out=False)
    g.set(ylabel='lexical richness (%)')
    g.fig.suptitle('Vocabulary Richness')
    sns.plt.show()

def _genericFactorPlot(data, xTarget, yTarget, filters, title, yLabel, col=None, row=None,
                       kind='point'):
    df = statsUtil.filter_stats(data, filters)

    g = sns.factorplot(x=xTarget, y=yTarget, col=col, row=row, hue='sender',
                        data=df, kind=kind, legend_out=False)
    g.set(ylabel=yLabel)
    g.fig.suptitle(title)
    sns.plt.show()

# does single year only. Use with animations or to see boxplots
def plotSingleBasicLengthStatByYearAndHour(data, stat, yearsToShow=None,
                                       targetSenders=None, ax=None):
    df = statsUtil.filter_stats(data, {'sender':targetSenders, 'year':yearsToShow,
                                        'stat':[stat]})
    ax = sns.barplot(x="hour", y='val', hue="sender", data=df, ax=ax)
    ax.set(ylabel=stat)
    #sns.plt.show()

def plotSingleBasicLengthStatHeatmap(data, stat, targetSender, yearsToShow=None):
    df = data.xs(targetSender, level='sender')
    df = df.reset_index()

    def plot(ax, df, count):
        df = df.pivot('month', 'day', stat)
        ax = sns.heatmap(df, mask=df.isnull(), ax=ax)#cmap=ListedColormap(['red', 'blue'])
        ax.set(ylabel='month' if count == 1 else '')

    _plotByYear(df, "{} ({})".format(stat, targetSender), plot, yearsToShow)

def plotSentimentStatsByHour(sentimentStats, valueNames):
    data = statsUtil.transformSentimentStats(sentimentStats, valueNames, ['sender', 'hour'])
    ax = sns.factorplot(x="hour", y="val", col="emotion", hue='sender',
                   data=data, kind="point", sharey=False, legend_out=False)
    ax.set(ylabel='mean(val)')
    sns.plt.show()

def plotSentimentStatsByYearAndMonth(sentimentStats, valueNames):
    data = statsUtil.transformSentimentStats(sentimentStats, valueNames, ['sender', 'year', 'month'])
    sns.factorplot(x="month", y="val", row="emotion", hue='sender', col='year',
                   data=data, kind="point", sharey=False, legend_out=False)
    sns.plt.show()

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
    fig.suptitle(title)
    sns.plt.show()

def savePlotAsImage(plot, filename):
    folderPath = os.path.join(mio.getResourcesPath(), 'imgs')
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    if SAVE_PLOT:
        filepath = os.path.join(folderPath, filename)
        plot.savefig(filepath)
    else:
        pass