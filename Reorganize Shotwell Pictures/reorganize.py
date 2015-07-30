import sqlite3
import shutil
import datetime
import ntpath
import os

#Global constants

strPhotoTable = "PhotoTable"
dstPath = "/home/greg/Bilder/Fotos"
#valid tags are: %year%, %month%, %event%
dstPattern = "%year%/%event%"

class photoRow:
		def __init__(self, id, filename, datetime, eventId, eventName):
			self.id = id
			self.filename = filename
			self.datetime = datetime
			self.eventId = eventId
			self.eventName = eventName

def getNumberOfPhotos(cursor):
	"Read the number of photos from table photos"
	cursor.execute("SELECT COUNT(*) FROM ?" , strPhotoTable)
	row = cursor.fetchone()
	return row[0];

def getAllPhotos(cursor):
	"Read all photos, store them in photoRows and return array"
	photoList = []
	for row in cursor.execute("SELECT PhotoTable.id,PhotoTable.filename,PhotoTable.timestamp,PhotoTable.event_id,EventTable.name FROM PhotoTable, EventTable WHERE PhotoTable.event_id = EventTable.id"):
		photoList.append(photoRow(id=row[0], filename=row[1], datetime=datetime.datetime.fromtimestamp(row[2]), eventId=row[3], eventName=row[4]))
	return photoList;



conn = sqlite3.connect("/home/greg/.local/share/shotwell/data/photo.db")
c = conn.cursor()
for row in getAllPhotos(c):
	filename = ntpath.basename(row.filename)
	dstFilledPattern = dstPattern
	dstFilledPattern = dstFilledPattern.replace("%year%" , str(row.datetime.year))
	dstFilledPattern = dstFilledPattern.replace("%month%" , str(row.datetime.month))
	dstFilledPattern = dstFilledPattern.replace("%day%" , str(row.datetime.day))
	dstFilledPattern = dstFilledPattern.replace("%event%" , row.eventName)

	completeDstPath = dstPath + "/" + dstFilledPattern
	if not os.path.exists(completeDstPath):
		os.makedirs(completeDstPath)

	shutil.copy(row.filename, completeDstPath)

	print("Copied to " + completeDstPath)




