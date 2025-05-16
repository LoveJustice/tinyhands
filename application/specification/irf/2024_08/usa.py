import copy
from .core import irf_core

# Since we want a separate google spreadsheet for each country, we need to have a different form for each country
# this is an example of copying the core specification and updating to set the form name and spreadsheet name.
# Any custom questions would be added as well
irf_usa = copy.deepcopy(irf_core)
irf_usa['name'] = 'irfUSA2024_08'
irf_usa['export']['spreadsheet_name'] = 'USA IRF'
