import util.stats as s
from pandas import read_csv
import util.io as mio
import util.plotting as mplot

#print(s.cleanWord('futdde342*++-+ure?1', []))
#data = mio.loadDataFromFile(mio.getResourcesPath() + "\hoursStats.txt")
#data.plot(x='Hours', y='AM_numMsgs', style=['o','rx'])
#mplot.plotDataFrame(data)
mplot.plotHoursStats(mio.getResourcesPath() + "\weekDayStats.txt")