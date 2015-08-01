# Reorganize Shotwell library

# I really like shotwells events, but i'd like to organize my files on the disk according to the
# events they are in.
# By changing the photoDstPattern string you can define how you want your pictures organized.
# Additionally to the tags already supported by shotwell, you can add the %e tag which stands for the
# event the picture is in.
# The files are copied from the directory stored in the shotwell database to a new location
# specified by dstPath and photoDstPattern.
# If you want to update the shotwell library with the new filenames set the variable bUpdateDatabase to True

import sqlite3
import shutil
import datetime
import ntpath
import os
import calendar

#Global constants
home = os.path.expanduser("~")


# Options
#valid tags are: %Y : Year
#				 %m : Number of month
#				 %d : Day
#				 %b : Abbreviated name of month(depending on locale)
#				 %e : Event
photoDstPattern = "%Y/%b/%e"
videoDstPattern = "%Y/%b/%e/Videos"

bUpdateDatabase = True

dstPath = home + "/Bilder/Fotos"


# Shotwell setup
strPhotoTable = "PhotoTable"
strVideoTable = "VideoTable"
strEventTable = "EventTable"
strDatabasePath = home + "/.local/share/shotwell/data/photo.db"


class photoRow:
		def __init__(self, id, filename, datetime, eventId, eventName):
			self.id = id
			self.filename = filename
			self.datetime = datetime
			self.eventId = eventId
			self.eventName = eventName

class videoRow:
		def __init__(self, id, filename, datetime, eventId, eventName):
			self.id = id
			self.filename = filename
			self.datetime = datetime
			self.eventId = eventId
			self.eventName = eventName

def getAllPhotos(cursor):
	"Read all photos, store them in photoRows and return array"
	photoList = []
	for row in cursor.execute("SELECT %(PhotoTable)s.id,%(PhotoTable)s.filename,%(PhotoTable)s.timestamp,%(PhotoTable)s.event_id,%(EventTable)s.name FROM %(PhotoTable)s, %(EventTable)s WHERE %(PhotoTable)s.event_id = %(EventTable)s.id" % \
		{"PhotoTable": strPhotoTable, "EventTable": strEventTable}):
		photoList.append(photoRow(id=row[0], filename=row[1], datetime=datetime.datetime.fromtimestamp(row[2]), eventId=row[3], eventName=row[4]))
	return photoList;

def getAllVideos(cursor):
	"Read all videos, store them in videoRows and return array"
	videoList = []
	for row in cursor.execute("SELECT %(VideoTable)s.id,%(VideoTable)s.filename,%(VideoTable)s.timestamp,%(VideoTable)s.event_id,%(EventTable)s.name FROM %(VideoTable)s, %(EventTable)s WHERE %(VideoTable)s.event_id = %(EventTable)s.id" % \
		{"VideoTable":strVideoTable, "EventTable": strEventTable}):
		videoList.append(videoRow(id=row[0], filename=row[1], datetime=datetime.datetime.fromtimestamp(row[2]), eventId=row[3], eventName=row[4]))
	return videoList;

def updatePhotoRow(cursor, newRow):
	"Store the information of newRow in the database"
	timestamp = row.datetime.timestamp()
	cursor.execute("UPDATE %(PhotoTable)s SET filename=\"%(filename)s\", timestamp=%(timestamp)d, event_id=%(eventId)d WHERE id=%(id)d" % \
		{"PhotoTable": strPhotoTable, "filename": row.filename, "timestamp": timestamp, "eventId": row.eventId, "id": row.id})

def updateVideoRow(cursor, newRow):
	"Store the information of newRow in the database"
	timestamp = row.datetime.timestamp()
	cursor.execute("UPDATE %(VideoTable)s SET filename=\"%(filename)s\", timestamp=%(timestamp)d, event_id=%(eventId)d WHERE id=%(id)d" % \
		{"VideoTable":strVideoTable, "filename": row.filename, "timestamp": timestamp, "eventId": row.eventId, "id": row.id})

def fillDestPattern(path, pattern, row):
	dstFilledPattern = pattern
	dstFilledPattern = dstFilledPattern.replace("%Y" , str(row.datetime.year))
	dstFilledPattern = dstFilledPattern.replace("%m" , str(row.datetime.month))
	dstFilledPattern = dstFilledPattern.replace("%d" , str(row.datetime.day))
	dstFilledPattern = dstFilledPattern.replace("%b" , calendar.month_abbr[row.datetime.month])
	dstFilledPattern = dstFilledPattern.replace("%e" , row.eventName)
	return path + "/" + dstFilledPattern;

def processPhotoRow(photoRow):

	destPath = fillDestPattern(dstPath, photoDstPattern, row)

	#Check if the file is already in the targetpath
	if not destPath in row.filename:
		filename = ntpath.basename(row.filename)

		print("File %s is not in destination path." % filename)

		# Create folder if it does not exist yet
		if not os.path.exists(destPath):
			os.makedirs(destPath)

		shutil.copy2(row.filename, destPath)
		print("	Copied to: " + destPath)

		# Update information in database
		if(bUpdateDatabase):
			row.filename = destPath + "/" + filename
			updatePhotoRow(c,row)

def processVideoRow(videoRow):

	destPath = fillDestPattern(dstPath, videoDstPattern, row)

	#Check if the file is already in the targetpath
	if not destPath in row.filename:

		filename = ntpath.basename(row.filename)

		print("File %s is not in destination path." % filename)

		# Create folder if it does not exist yet
		if not os.path.exists(destPath):
			os.makedirs(destPath)

		shutil.copy2(row.filename, destPath)
		print("	Copied to: " + destPath)

		# Update information in database
		if(bUpdateDatabase):
			row.filename = destPath + "/" + filename
			updateVideoRow(c,row)


# Main 
conn = sqlite3.connect(strDatabasePath)
c = conn.cursor()

for row in getAllPhotos(c):
	processPhotoRow(row)

for row in getAllVideos(c):
	processVideoRow(row)

# If the table was updated we have to commit the changes
conn.commit()



