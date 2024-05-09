import os
import datetime
import pandas

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

def main():
	files = getFilenames()


if __name__ == '__main__':
	main()
