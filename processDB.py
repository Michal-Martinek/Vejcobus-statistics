import os
import datetime
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
DAMAGED_HEADERS_STR = 'time_ran' + 39 * ',nan'
def getFrames(filenames):
	allFrame = pd.DataFrame(columns=['file'] + HEADERS.split(','))
	for name, file in filenames.items():
		df = pd.read_csv(file, names=HEADERS.split(','))
		check(','.join(map(str, df.values[0])) in (HEADERS, DAMAGED_HEADERS_STR), 'First row is expected to be header (file {})', name)
		df = df.drop(0)
		df.insert(0, 'file', name)
		allFrame = pd.concat((allFrame, df), axis=0, ignore_index=True)
	print(f'INFO: total {allFrame.shape[0]} datapoints found')
	return allFrame

def main():
	filenames = getFilenames()
	frames = getFrames(filenames)

if __name__ == '__main__':
	main()
