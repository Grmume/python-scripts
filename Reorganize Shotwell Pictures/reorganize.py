# Reorganize Shotwell library

# I really like shotwells events, but i'd like to organize my files on the disk according to the
# events they are in.
# By changing the dstPattern string you can define how you want your pictures organized.
# Additionally to the tags already supported by shotwell, you can add the %e tag which stands for the
# event the picture is in.
# The files are copied from the directory stored in the shotwell database to a new location
# specified by dstPath and dstPattern.
# If you want to update the shotwell library with the new filenames set the variable bUpdateDatabase to True

import sqlite3
import shutil
import datetime
import ntpath
import os

#Global constants

#valid tags are: %Y : Year
#				 %m : Month
#				 %d : Day
#				 %e : Event
dstPattern = "%Y%/%e%"

bUpdateDatabase = True
home = os.path.expanduser("~")
dstPath = home + "/Bilder/Fotos"



class photoRow:
		def __init__(self, id, filename, datetime, eventId, eventName):
			self.id = id
			self.filename = filename
			self.datetime = datetime
			self.eventId = eventId
			self.eventName = eventName

def getAllPhotos(cursor):
	"Read all photos, store them in photoRows and return array"
	photoList = []
	for row in cursor.execute("SELECT PhotoTable.id,PhotoTable.filename,PhotoTable.timestamp,PhotoTable.event_id,EventTable.name FROM PhotoTable, EventTable WHERE PhotoTable.event_id = EventTable.id"):
		photoList.append(photoRow(id=row[0], filename=row[1], datetime=datetime.datetime.fromtimestamp(row[2]), eventId=row[3], eventName=row[4]))
	return photoList;

def updatePhotoRow(cursor, newRow):
	"Store the information of newRow in the database"
	timestamp = row.datetime.timestamp()
	#print("UPDATE PhotoTable SET filename=\"%(filename)s\", timestamp=%(timestamp)d, event_id=%(eventId)d WHERE id=%(id)d" % \
	#	{"filename": row.filename, "timestamp": timestamp, "eventId": row.eventId, "id": row.id})
	cursor.execute("UPDATE PhotoTable SET filename=\"%(filename)s\", timestamp=%(timestamp)d, event_id=%(eventId)d WHERE id=%(id)d" % \
		{"filename": row.filename, "timestamp": timestamp, "eventId": row.eventId, "id": row.id})

conn = sqlite3.connect(home + "/.local/share/shotwell/data/photo.db")
c = conn.cursor()
for row in getAllPhotos(c):
	#Check if the file is already in the targetpath
	print("Filename in database: " + row.filename)
	if not dstPath in row.filename:
		print("File is NOT in destination folder.")
		filename = ntpath.basename(row.filename)
		dstFilledPattern = dstPattern
		dstFilledPattern = dstFilledPattern.replace("%Y%" , str(row.datetime.year))
		dstFilledPattern = dstFilledPattern.replace("%m%" , str(row.datetime.month))
		dstFilledPattern = dstFilledPattern.replace("%d%" , str(row.datetime.day))
		dstFilledPattern = dstFilledPattern.replace("%e%" , row.eventName)

		completeDstPath = dstPath + "/" + dstFilledPattern

		# Create folder if it does not exist yet
		if not os.path.exists(completeDstPath):
			os.makedirs(completeDstPath)

		shutil.copy(row.filename, completeDstPath)
		print("Copied to: " + completeDstPath)

		# Update information in database
		if(bUpdateDatabase):
			row.filename = completeDstPath + "/" + filename
			updatePhotoRow(c,row)
	else:
		print("File IS in destination folder!")

# If the table was updated we have to commit the changes
conn.commit()



