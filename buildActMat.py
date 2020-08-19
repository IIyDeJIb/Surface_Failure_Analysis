import pandas as pd
import logging
from fullWellList import fullWellList
from xAndClassFailures import xAndClassFailures
from customErrors import NoWellsFoundError, RepeatedWellsError
from procFailSeries import procFailSeries
# from pg_pandas import closeSeries, compFillna
from datetime import datetime

# from openpyxl import load_workbook
# import os
# import re

# --- Setup Create a logger
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

formatter = '%(asctime)s : %(name)s : %(funcName)s : %(levelname)s -> %(message)s'

# File logging handler
fh = logging.FileHandler('actMat.log')
fh.setLevel('DEBUG')
fh.setFormatter(formatter)

# Console logging handler
ch = logging.StreamHandler()
ch.setLevel('ERROR')
ch.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.debug('----- Start of Script -----')

failTypeCode = {'subs': -1,
				'surf': 0,
				'uncl': -2,
				'op': 1,
				'tbd': -3}

# --- Read the raw data in
rawData = pd.read_csv('2004-2014_rawFailureData2_prep.csv', engine='python',
					  index_col='Date', parse_dates=True).dropna()
rawData2 = pd.read_csv('rawData2_2014-2019.csv', engine='python', index_col=0,
					   parse_dates=True, header=None).dropna()

rawData2.index.name = 'Date'
rawData2.columns = ['Comments']

rawData = rawData.append(rawData2)

# --- Preprocessing
# Remove some faulty data
rawData = rawData.drop(
	index=[datetime(2016, 10, 2), datetime(2016, 10, 3), datetime(2016, 10, 4),
		   datetime(2016, 10, 5),
		   datetime(2016, 10, 6)])
rawData = rawData.drop(
	index=[datetime(2016, 4, 2), datetime(2016, 4, 3), datetime(2016, 4, 4),
		   datetime(2016, 4, 5),
		   datetime(2016, 4, 6)])
rawData = rawData.drop(index=[datetime(2013, 4, 2)])
rawData = rawData.drop(
	index=pd.date_range(start=datetime(2008, 1, 2), end=datetime(2008, 1, 4)))
rawData = rawData.drop(index=[datetime(2009, 10, 4)])
rawData = rawData.drop(index=[datetime(2011, 8, 14)])

dateList = pd.date_range(rawData.index[0], rawData2.index[-1], freq='D')

actMatFull = pd.DataFrame(index=dateList, columns=fullWellList)

for date, failInfo in rawData.itertuples():
	try:
		surfList, subsList, unclassList = xAndClassFailures(failInfo)
	except NoWellsFoundError:
		logging.info(f'No wells found. Date: {date}, failInfo: {failInfo}')
	except RepeatedWellsError:
		logging.info(f'Repeated wells found. Date: {date}, failInfo: {failInfo}')
		continue

	actMatFull.loc[date, :] = failTypeCode['op']
	actMatFull.loc[date, surfList] = failTypeCode['surf']
	actMatFull.loc[date, subsList] = failTypeCode['subs']
	actMatFull.loc[date, unclassList] = failTypeCode['uncl']

# ------------ Processing
# -- Remove wells which are of no interest
actMatFull = actMatFull.drop(columns=['1408', '752', '1307'])

# Fill in missing data with 1 for the initial few years. The missing data in this
# period of the data typically means
# all the wells are running.
actMatFull.iloc[0:1354] = actMatFull.iloc[0:1354].fillna(1)

# Save the data before processing
actMatFull.to_csv('actMatFull_0_before_proc.csv')

# Upload unprocessed version
# actMatFull = pd.read_csv('actMatFull_0_before_proc.csv', parse_dates=['Unnamed:
# 0']).rename(columns={'Unnamed: 0':
#                                                                                                          'Date'}).set_index('Date')


# Automatic resolution of unclassified errors
actMatFull = actMatFull.apply(procFailSeries)

# --- Post-processing - Manual corrections of data which do not fit the rules
import postProcessor

actMatFull.to_csv('actMatFull_0.csv')
