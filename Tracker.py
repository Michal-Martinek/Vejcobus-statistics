import requests
import pandas as pd
import os, argparse
import datetime, time
import logging, inspect, traceback

API_TOKEN_FILE = 'api_auth_token.txt'
API_TOKEN_VAL = ''
API_URL = 'https://api.golemio.cz/v2'

DT_FEATURE_COLLECTION = 'FeatureCollection'
DT_FEATURE = 'Feature'
DT_POINT = 'Point'

DATAPOINT_FOLDER = 'datapoints'
LOG_FOLDER = 'logs'
DATAPOINT_FILE = '{}.csv'
LOG_FILE = 'log_{}.txt'

DEFAULT_LOGGING_LVL = 'WARNING'
DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S' + f"{'-' if time.altzone > 0 else '+'}{abs(time.altzone)//3600:0>2}:{abs(time.altzone//60) % 60:0>2}"

# helpers -------------------------------------
def init():
	os.chdir(os.path.dirname(__file__))
	initFiles(datetime.datetime.now().strftime('%Y-%m-%d'))
	initLogging()
	global API_TOKEN_VAL
	with open(API_TOKEN_FILE) as f:
		API_TOKEN_VAL = f.read().split('\n')[0]
def initFiles(dateStr):
	global DATAPOINT_FILE, LOG_FILE
	DATAPOINT_FILE = os.path.join(DATAPOINT_FOLDER, DATAPOINT_FILE.format(dateStr))
	LOG_FILE = os.path.join(LOG_FOLDER, LOG_FILE.format(dateStr))
	if not os.path.exists(DATAPOINT_FOLDER): os.mkdir(DATAPOINT_FOLDER)
	if not os.path.exists(LOG_FOLDER): os.mkdir(LOG_FOLDER)
def initLogging():
	parser = argparse.ArgumentParser('Tracker.py')
	parser.add_argument('--log', help='set the logging level', type=str, default=DEFAULT_LOGGING_LVL)
	logLvl = parser.parse_args().log
	logLvl = getattr(logging, logLvl.upper(), DEFAULT_LOGGING_LVL)
	logging.basicConfig(filename=LOG_FILE, level=logLvl, format='[%(levelname)s] %(asctime)s %(module)s:%(funcName)s	%(message)s', datefmt=DATETIME_FORMAT)
	logging.info('running')
def asert(cond, msg, obj=None):
	if cond: return
	if obj is not None:
		msg = f"{msg}: '{obj}'"
	caller = inspect.getframeinfo(inspect.stack()[1][0])
	msg = f'{os.path.basename(caller.filename)}:{caller.lineno} ASSERTION FAILED: {msg}'
	logging.error(msg)
	exit(msg)

def checkType(d, dtype:str):
	asert('type' in d and d['type'] == dtype, 'Unexpected field type')
	del d['type']
def getVal(d: dict, name):
	asert(name in d, 'Element not found', name)
	d = d[name]
	return d
def getTyped(d: dict, name, dtype: str):
	d = d[name]
	checkType(d, dtype)
	return d
def unpack(d: dict, name, dtype: str=None, *, prefix=False):
	'''Unpacks a dictionary field in @d with @name into @d
	@dtype - optionally check the dtype of the field
	@prefix - prefix unpacked keys with @name_'''
	packed = getVal(d, name) if dtype is None else getTyped(d, name, dtype)
	asert(isinstance(packed, dict), 'Packed field is not of dict type')
	del d[name]
	if prefix: packed = {'_'.join((name, k)):v for k, v in packed.items()}
	d.update(packed)
def unpackList(d, name, fieldNames):
	l = getVal(d, name)
	asert(len(l) == len(fieldNames), 'Invalid list length')
	del d[name]
	d.update( {k:v for k, v in zip(fieldNames, l)} )
# requests --------------------------------------
def _makeReg(url, params, method='GET') -> requests.Response:
	try:
		res = requests.request(method, url, params=params, headers={'X-Access-Token': API_TOKEN_VAL})
	except requests.exceptions.RequestException as e:
		logging.error(e)
		exit(e)
	asert(res.status_code == 200, f'{method} request failed with code {res.status_code}\n	URL {res.url}\n	MESSAGE {res.text}\n')
	return res
def makeGetReq(apiPath, **params) -> dict:
	url = API_URL + '/' + apiPath
	res = _makeReg(url, params)
	return res.json()
def getVehiclePositions() -> list[dict]:
	d = makeGetReq('vehiclepositions', routeShortName='202', includeNotTracking=1)
	checkType(d, DT_FEATURE_COLLECTION)
	return getVal(d, 'features')
# processing ---------------------------------------
def unpackVehiclePosition(d: dict):
	checkType(d, DT_FEATURE)
	unpack(d, 'geometry', DT_POINT)
	unpackList(d, 'coordinates', ['lon', 'lat'])

	unpack(d, 'properties')
	unpack(d, 'last_position')
	unpack(d, 'trip')

	unpack(d, 'gtfs')
	for field in ['delay', 'last_stop', 'next_stop', 'agency_name', 'cis', 'vehicle_type']:
		unpack(d, field, prefix=True)
def canAppend():
	return os.path.exists(DATAPOINT_FILE) and os.stat(DATAPOINT_FILE).st_size != 0
def saveToCSV(df):
	df.to_csv(DATAPOINT_FILE, index=False, mode='a' if canAppend() else 'w', header=not canAppend())
def processVehiclePositions(poss: list[dict]) -> pd.DataFrame:
	for d in poss: unpackVehiclePosition(d)
	df = pd.DataFrame(poss)
	df.insert(0, 'time_ran', datetime.datetime.now().strftime(DATETIME_FORMAT))
	return df
	# TODO as multiindex use trip_id and origin_timestamp
def track():
	poss = getVehiclePositions()
	df = processVehiclePositions(poss)
	saveToCSV(df)

def main():
	try:
		init()
		track()
	except Exception as e:
		strs = traceback.format_exception(type(e), e, e.__traceback__)
		strs = 'UNCATCHED ' + strs[-1] + ''.join(['	' + s for s in strs[:-1]])
		logging.critical(strs)
		raise

if __name__ == '__main__':
	main()
