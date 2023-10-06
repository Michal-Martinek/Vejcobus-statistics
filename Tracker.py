import requests
import logging

import pandas as pd
import os, datetime

API_TOKEN_FILE = 'api_auth_token.txt'
API_TOKEN_VAL = ''
API_URL = 'https://api.golemio.cz/v2'

DT_FEATURE_COLLECTION = 'FeatureCollection'
DT_FEATURE = 'Feature'
DT_POINT = 'Point'

DATAPOINT_FILE = 'datapoints.csv'

# helpers -------------------------------------
def init():
	global API_TOKEN_VAL
	with open(API_TOKEN_FILE) as f:
		API_TOKEN_VAL = f.read()
def asert(cond, msg, obj=None):
	if cond: return
	if obj is not None:
		msg = f'{msg}: {obj}'
	logging.error(msg)
	raise RuntimeError(msg) # TODO logging into file

def checkType(d, dtype:str):
	asert('type' in d and d['type'] == dtype, 'Unexpected field type')
	del d['type']
def getVal(d: dict, name, nullable=False, default=None): # TODO default values?
	asert(name in d, 'Element not found', name)
	d = d[name]
	if nullable and d is None: return default
	return d
def getTyped(d: dict, name, dtype: str):
	d = d[name]
	checkType(d, dtype)
	return d
def unpack(d: dict, name, dtype: str=None, *, nullable=False, default=None, prefix=False):
	'''Unpacks a dictionary field in @d with @name into @d
	@dtype - optionally check the dtype of the field
	@prefix - prefix unpacked keys with @name_'''
	packed = getVal(d, name, nullable, default) if dtype is None else getTyped(d, name, dtype)
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
def makeGetReq(apiPath, **params) -> dict:
	url = API_URL + '/' + apiPath
	logging.debug(f'[GET] {url}, params: {params}')
	res = requests.get(url, params, headers={'X-Access-Token': API_TOKEN_VAL})
	asert(res.status_code == 200, f'Get request failed with code {res.status_code}\nURL {res.url}\MESSAGE {res.text}')
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
	df.insert(0, 'time_ran', datetime.datetime.now().strftime('%H:%M:%S'))
	saveToCSV(df)
	# TODO as multiindex use trip_id and origin_timestamp
	# TODO avoid JSON / handle singlequotes

def main():
	init()
	poss = getVehiclePositions()
	processVehiclePositions(poss)

if __name__ == '__main__':
	main()
