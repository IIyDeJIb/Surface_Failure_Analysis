import re

from fullWellList import fullWellList

onlineRx = re.compile(
		r'back|(?<!not\s)pumping(?!\s(un|te|ja))|rtp|return|repaired|level')

# Special treatment for 105 not to confuse it with 1105 (actually not necessary
# anymore since 1105 was added to the full well list). Special treatment for 105
# not to confuse it with 1105
fullWellStr = '(104|(?<!1)105|106|107|108|109|201(?![0-9])|202(?![0-9])|' + '|'.join(fullWellList[8:]) + ')'

rxCauses = re.compile(fullWellStr + r'(.+?)(?=' + fullWellStr + r'|$)')

subsRx = re.compile(
		r'(p/r|p\\r|r\\p|r/p|rdp|prt|tbg|hit|h/t|h\\t|part|rp|r\.p|p\.r|p\\u|p/u'
		r'|tubing'
		r'|[^a-z]hic|csg|cg'
		r'|casing|not pumping'
		r'|shut(\s|-)?in|trash|trsh|h\\c|h/c|h\.i\.c|reent'
		r'|rig|w/o|w\\o|p/t|p\\t|(?:[^a-z]|^)pt'
		r'|frac|joint|wor(?![a-z])|h\.i|s\\i|h/i/t'
		r'|s/i|(?:[^a-z]|^)ht(?:[^a-z]|$)|pump(?!\sja)(?:[^a-z]|$)|(?:[^a-z]|^)si('
		r'?:['
		r'^a-z]|$))')

surfRx = re.compile(r'((?:[^a-z]|^)el[ei](?![a-bd-z])|(?<!on)lin{1,'
					r'2}e|flowl|belt|grbox|gear|rrc|reset|resset|tee|brdl|brid{'
					r'1,2}'
					r'le|jack|power'
					r'|rail'
					r'|saddle|trans(?=fo|[^a-z]|$)|bridel|starter'
					r'|brg|wellhead|well head|bullwheel'
					r'|bearing|s\\b|panel|contact|pipe'  # |pump jack'
					r'|motor|meter|mtr|fuse|pin[^g]|wrist|tim{1,2}'
					r'er|unit|lock|brok|puley|pulley|voltage|stuffi|stufi|sheav)')
