import os
import datetime
import numpy as np
import pandas as pd

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
def main():
	filenames = getFilenames()
	frames = getFrames(filenames)
	checkVals(frames)
if __name__ == '__main__':
	main()
