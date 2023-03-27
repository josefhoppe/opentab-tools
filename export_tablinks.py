"""
Exports links for all users from local OpenTab instance to `tablinks.csv`
"""

from opentab_api import get_all_tablinks

get_all_tablinks().to_csv('tablinks.csv')