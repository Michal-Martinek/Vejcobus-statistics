import os
import datetime
import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_ns_dtype
import pytz

os.chdir(os.path.dirname(__file__))

DATAPOINT_FOLDER = 'downloadedDatapoints'

START_DATE = datetime.date(2023, 10, 14)
END_DATE = datetime.date(2023, 10, 17)

def check(val: bool, msg: str, *objs):
	if val: return
	if objs: msg = msg.format(*objs)
	print('ERROR: ' + msg)
	exit()

def iterPeriod(startDate=START_DATE, endDate=END_DATE) -> list[datetime.date]:
	days = int((endDate - startDate).days) + 1
	return [startDate + datetime.timedelta(days=n) for n in range(days)]

def getFilenames():
	check(os.path.exists(DATAPOINT_FOLDER), "Datapoint folder '{}' not found", DATAPOINT_FOLDER)
	files = {}
	for day in iterPeriod():
		filename = os.path.join(DATAPOINT_FOLDER, day.strftime('%Y-%m-%d.csv'))
		check(os.path.exists(filename), 'Day {} not found', day)
		files[str(day)] = filename
	check(len(files) == (numFiles := len(os.listdir(DATAPOINT_FOLDER))), 'Expected {} files, got {}', len(files), numFiles)
	return files

HEADERS = 'time_ran,lon,lat,bearing,is_canceled,origin_timestamp,shape_dist_traveled,speed,state_position,tracking,origin_route_name,sequence_id,start_timestamp,vehicle_registration_number,wheelchair_accessible,air_conditioned,route_id,route_short_name,route_type,trip_headsign,trip_id,trip_short_name,delay_actual,delay_last_stop_arrival,delay_last_stop_departure,last_stop_arrival_time,last_stop_departure_time,last_stop_id,last_stop_sequence,next_stop_arrival_time,next_stop_departure_time,next_stop_id,next_stop_sequence,agency_name_real,agency_name_scheduled,cis_line_id,cis_trip_number,vehicle_type_description_cs,vehicle_type_description_en,vehicle_type_id'
DATETIME_COLS = ['time_ran', 'origin_timestamp', 'start_timestamp', 'last_stop_arrival_time', 'last_stop_departure_time', 'next_stop_arrival_time', 'next_stop_departure_time']
UNNECESSARY_COLS = ['is_canceled', 'speed', 'tracking', 'route_type', 'trip_short_name', 'cis_line_id', 'cis_trip_number', 'vehicle_type_description_cs', 'vehicle_type_description_en', 'vehicle_type_id']

def getFrames(filenames):
	allFrame = pd.DataFrame()
	for name, file in filenames.items():
		df = pd.read_csv(file, names=HEADERS.split(','), parse_dates=DATETIME_COLS, infer_datetime_format=True, skiprows=1)
		df.insert(0, 'file', name)
		if not allFrame.size: allFrame = df.copy()
		else: allFrame = pd.concat((allFrame, df), axis=0, ignore_index=True, copy=False)
	print(f'INFO: total {allFrame.shape[0]} datapoints found')
	return allFrame

def checkUniqueVals(data: pd.DataFrame, col: str, *values):
	uniques = data[col].unique()
	if not values and np.isnan(uniques).all(): return
	check(set(values).intersection(uniques) == set(uniques), "Expected values {} along column '{}', got {}", values, col, uniques)
def checkDtype(data: pd.DataFrame, col: str, dtype, allowNans=False):
	check(data[col].dtype == dtype, "Expected dtype {} along column '{}', actual {}", dtype, col, data[col].dtype)
	if not allowNans and dtype == np.float64: check(not np.isnan(data[col]).any(), "Unexpected NaN in col '{}'", col)
def checkTimestamp(data: pd.DataFrame, col: str, utc=False):
	if utc:
		check(is_datetime64_ns_dtype(data[col]), "Expected datetime col '{}', actual type is {}", col, data[col].dtype)
		return check(data[col].dt.tz == pytz.UTC, "Expected UTC timestamp in col '{}', got {}", col, data[col].dtype)
	split = data[col].astype(str).str.rsplit('+', n=1, expand=True)
	data[col] = split[0].astype(np.datetime64)
	if 'timezone' in data.columns:
		check((split[1] == data['timezone']).all(), 'Identical timezone expected along datapoint')
	else: data['timezone'] = split[1]
def checkVals(data: pd.DataFrame):
	checkTimestamp(data, 'time_ran', utc=True)
	for col in DATETIME_COLS[1:]:
		checkTimestamp(data, col)
	checkDtype(data, 'lon', np.float64)
	checkDtype(data, 'lat', np.float64)
	checkDtype(data, 'bearing', np.int64)
	checkUniqueVals(data, 'is_canceled')
	checkDtype(data, 'shape_dist_traveled', np.float64)
	checkDtype(data, 'speed', np.float64, allowNans=True)
	check(np.isnan(data['speed']).all(), "Expected only NaNs in col 'speed'")
	checkUniqueVals(data, 'state_position', 'on_track', 'at_stop')
	checkUniqueVals(data, 'tracking', True)
	checkDtype(data, 'sequence_id', np.int64)
	checkDtype(data, 'vehicle_registration_number', np.int64)
	checkUniqueVals(data, 'wheelchair_accessible', True)
	checkUniqueVals(data, 'air_conditioned', True, False)
	checkUniqueVals(data, 'route_id', 'L202')
	checkUniqueVals(data, 'route_short_name', 202)
	checkUniqueVals(data, 'route_type', 3)
	checkUniqueVals(data, 'trip_headsign', 'Čakovice', 'Poliklinika Mazurská', 'Kbelský pivovar', 'Kbelský hřbitov')
	checkUniqueVals(data, 'trip_short_name')
	checkDtype(data, 'delay_actual', np.int64)
	checkDtype(data, 'delay_last_stop_arrival', np.float64, allowNans=True)
	checkDtype(data, 'delay_last_stop_departure', np.float64, allowNans=True)
	checkDtype(data, 'last_stop_sequence', np.int64)
	checkDtype(data, 'next_stop_sequence', np.int64)
	checkUniqueVals(data, 'agency_name_real', 'DP PRAHA')
	checkUniqueVals(data, 'agency_name_scheduled', 'DP PRAHA')
	checkUniqueVals(data, 'cis_line_id')
	checkUniqueVals(data, 'cis_trip_number')
	checkUniqueVals(data, 'vehicle_type_description_cs', 'autobus')
	checkUniqueVals(data, 'vehicle_type_description_en', 'bus')
	checkUniqueVals(data, 'vehicle_type_id', 3)
	checkUniqueVals(data, 'timezone', '01:00', '02:00')
	data['timezone'] = data['timezone'].str.split(':', expand=True)[0].astype(int)

	data = data.drop(UNNECESSARY_COLS, axis=1)
	return data

def main():
	filenames = getFilenames()
	frames = getFrames(filenames)
	frames = checkVals(frames)

if __name__ == '__main__':
	main()
