# Use the failure info string and the list of the wells detected in the string to
# classify the well failures.

import logging
import re

import numpy as np
import pandas as pd

from customErrors import NoWellsFoundError
from myRegex import onlineRx, rxCauses, surfRx, subsRx

logger = logging.getLogger('__main__.' + __name__)


def xAndClassFailures(date, failInfo):
	failDf = pd.DataFrame(
			columns=['Surface', 'Subsurface', 'Online', 'Unclassified'])

	allCauses = rxCauses.findall(failInfo)

	if allCauses == []:
		logger.error(f'No wells found. Date: {date}, failInfo: {failInfo}')
		return [],[],[]

	# Comma check: Detect whether all there is in what was detected is a coma. In
	# that case the failure for that well needs to be read from the next well (and
	# so on). E.g. 801, 101,606 hit will assign hit to all the listed wells. Same
	# logic goes for "&" and " ".
	comRx = re.compile(r'(^\s?,\s?$|^\s?$|^\s?&\s?$)')

	for failTup in allCauses:
		# Check whether only failure cause is indicated for this well (comma check)
		if failTup[0] not in failDf.index.to_list():
			wellName = failTup[0]
		else:
			# At this point dual failures are not supported. Needs to be
			# reconciled manually. Skip.
			logger.debug(f'Repeated well ({failTup[0]}) found. Date: {date}, failInfo: {failInfo}')
			continue

		if comRx.findall(failTup[1].lower()) != []:
			failDf.loc[wellName, 'Surface'] = np.nan
			failDf.loc[wellName, 'Subsurface'] = np.nan
			failDf.loc[wellName, 'Online'] = np.nan
			continue

		failDf.loc[wellName, 'Subsurface'] = subsRx.findall(failTup[1].lower()) \
											 != []
		failDf.loc[wellName, 'Surface'] = surfRx.findall(failTup[1].lower()) != []
		failDf.loc[wellName, 'Online'] = onlineRx.findall(failTup[1].lower()) != []

	# Two steps of filling the missing values. The first steps takes care of the
	# wells which only had comma after them (we skip those first). Here we
	# backfill the data so in the string (see "Comma check" comment). The second
	# one is when comas were detected, however no causes were. All the wells are
	# marked as unclassified in this case.
	failDf[['Surface', 'Subsurface', 'Online']] = failDf[
		['Surface', 'Subsurface', 'Online']].fillna(method='bfill').fillna(False)

	failDf['Unclassified'] = False
	failDf.loc[np.sum(failDf[['Surface', 'Subsurface', 'Online']],
					  axis=1) != 1, 'Unclassified'] = True

	# Log the unclassified wells
	# if failDf['Unclassified'].sum() != 0:
	# 	unclassWellList = failDf.index[failDf['Unclassified']].tolist()
	# 	logger.debug(
	# 			f"Well(s) {unclassWellList} could not be classified. Date: {date}"
	# 			f"failInfo: {failInfo}.")

	# return lists to keep consistency
	return failDf.index[failDf['Surface']].tolist(), failDf.index[
		failDf['Subsurface']].tolist(), \
		   failDf.index[failDf['Unclassified']].tolist()
