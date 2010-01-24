# -*- coding: iso-8859-1 -*-

#Copyright (C) Fiz Vazquez vud1@sindominio.net

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import os
import logging
from SimpleGladeApp import SimpleGladeApp
from windowcalendar import WindowCalendar
from filechooser import FileChooser
from pytrainer.lib.date import Date
import dateutil.parser
from dateutil.tz import * # for tzutc()

class WindowRecord(SimpleGladeApp):
	def __init__(self, data_path = None, listSport = None, parent = None, date = None, title=None, distance=None, time=None, upositive=None, unegative=None, bpm=None, calories=None, comment=None, windowTitle=None):
		self.parent = parent
		self.data_path = data_path
		glade_path="glade/newrecord.glade"
		root = "newrecord"
		domain = None
		self.mode = "newrecord"
		self.id_record = ""
		SimpleGladeApp.__init__(self, data_path+glade_path, root, domain)
		self.conf_options = [
			"rcd_date",
			"rcd_sport",
			"rcd_distance",
			"rcd_beats",
			"rcd_comments",
			"rcd_average",
			"rcd_calories",
			"rcd_title",
			"rcd_gpxfile",
			"rcd_upositive",
			"rcd_unegative",
			"rcd_maxbeats",
			"rcd_pace",
			"rcd_maxpace",
			"rcd_maxvel",
			]
		self.listSport = {}
		for i in listSport:
			self.listSport[i[3]] = i[0] #Create dictionary using SportID as key (may be non sequential if sports have been deleted)
		for i in self.listSport:	
			self.rcd_sport.insert_text(i,self.listSport[i])
		self.rcd_sport.set_active(0)

		if windowTitle is not None:
			self.newrecord.set_title(windowTitle)
		if date != None:
			self.setDate(date)
		if title != None:
			self.rcd_title.set_text(title)
		if distance != None:
			self.rcd_distance.set_text(distance)
		if time != None:
			self.setTime(time)
		if distance!=None and time!=None:
			self.on_calcaverage_clicked(None)
		if upositive != None:
			self.rcd_upositive.set_text(upositive)
		if unegative != None:
			self.rcd_unegative.set_text(unegative)
		if calories != None:
			self.rcd_calories.set_text(calories)
		
	def on_accept_clicked(self,widget):
		list_options = {}
		trackSummary = {}
		for i in self.conf_options:
			var = getattr(self,i)
			if i == "rcd_title":
				list_options[i] = var.get_text().replace("\"","'")
			elif i != "rcd_sport" and i != "rcd_comments":
				list_options[i] = var.get_text()
			elif i == "rcd_sport":
				list_options[i] = var.get_active_text()
			elif i == "rcd_comments":
				buffer = var.get_buffer()
				start,end = buffer.get_bounds()
				list_options[i] = buffer.get_text(start,end, True)
				list_options[i] = list_options[i].replace("\"","'")
			list_options["rcd_time"] = [self.rcd_hour.get_value_as_int(),self.rcd_min.get_value_as_int(),self.rcd_second.get_value_as_int()]
		if self.mode == "newrecord":
			logging.debug('Track data: '+str(list_options))
			if list_options["rcd_gpxfile"] != "":
				logging.info('Adding new activity based on GPX file')	
				trackSummary=(list_options["rcd_sport"],"","")
				self.parent.insertNewRecord(list_options["rcd_gpxfile"], trackSummary)
			else:
				logging.info('Adding new activity based on provided data')
				#Manual entry, calculate time info
				record_time = self.rcd_time.get_text()
				record_date = self.rcd_date.get_text()
				localtz = Date().getLocalTZ()
				date = dateutil.parser.parse(record_date+" "+record_time+" "+localtz)
				local_date = str(date)
				utc_date = date.astimezone(tzutc()).strftime("%Y-%m-%dT%H:%M:%SZ")
				list_options["date_time_utc"] = utc_date
				list_options["date_time_local"] = local_date
				self.parent.insertRecord(list_options)
		elif self.mode == "editrecord":
			self.parent.updateRecord(list_options, self.id_record)
		self.close_window()
	
	def on_cancel_clicked(self,widget):
		self.close_window()

	def close_window(self, widget=None):
		self.newrecord.hide()
		#self.newrecord = None
		self.quit()

	def on_calendar_clicked(self,widget):
		calendardialog = WindowCalendar(self.data_path,self, date=self.rcd_date.get_text())
		calendardialog.run()

	def setDate(self,date):
		self.rcd_date.set_text(date)

	def setTime(self,timeInSeconds):
		time_in_hour = int(timeInSeconds)/3600.0
		hour = int(time_in_hour)
		min = int((time_in_hour-hour)*60)
		sec = (((time_in_hour-hour)*60)-min)*60
		self.rcd_hour.set_value(hour)
		self.rcd_min.set_value(min)
		self.rcd_second.set_value(sec)

	def setValue(self,var,value, format="%0.2f"):
		var = getattr(self,var)
		try:
			valueString = format %value
			var.set_text(valueString)
		except:
			pass
	
	def setValues(self,values):
		#(24, u'2009-12-26', 4, 23.48, u'9979', 0.0, 8.4716666232200009, 2210, u'', None, u'', 573.0, 562.0, 11.802745244400001, 5.0499999999999998, 7.04, 0.0, u'2009-12-25T19:41:48Z', u'2009-12-26 08:41:48+13:00')
		#(50, u'2006-10-13', 1, 25.0, u'5625', 0.0, 16.0, 0, u'', gpsfile, title,upositive,unegative,maxspeed|maxpace|pace|maxbeats
		self.id_record = values[0]
		self.setTime(values[4])
		self.rcd_date.set_text(str(values[1]))
		self.setValue("rcd_distance",values[3])
		self.setValue("rcd_average",values[6])
		self.setValue("rcd_calories",values[7], "%0.0f")
		self.setValue("rcd_beats",values[5], "%0.0f")
		self.setValue("rcd_upositive",values[11])
		self.setValue("rcd_unegative",values[12])
		self.setValue("rcd_maxvel",values[13])
		self.setValue("rcd_maxpace",values[14])
		self.setValue("rcd_pace",values[15])
		self.setValue("rcd_maxbeats",values[16], "%0.0f")
		self.rcd_title.set_text("%s"%values[10])
		
		local_time = values[18]
		if local_time is not None:
			dateTime = dateutil.parser.parse(local_time)
			sTime = dateTime.strftime("%X")
			self.rcd_time.set_text("%s" % sTime)
		sportID = values[2]
		sportPosition = self.getSportPosition(sportID)
		self.rcd_sport.set_active(sportPosition) 
		buffer = self.rcd_comments.get_buffer()
		start,end = buffer.get_bounds()
		buffer.set_text(values[8])
		self.mode = "editrecord"

	def getSportPosition(self, sportID):
		"""
			Function to determin the position in the sport array for a given sport ID
			Needed as once sports are deleted there are gaps in the list...
		"""
		count = 0
		for key, value in self.listSport.iteritems():
			if key == sportID: 
				return count
			count +=1
		return 0

	def on_calctime_clicked(self,widget):
		try:
			distance = self.rcd_distance.get_text()
			average = self.rcd_average.get_text()
			time_in_hour = float(distance)/float(average)
			self.set_recordtime(time_in_hour)
		except:
			pass

	def on_calcaverage_clicked(self,widget):
		try:
			hour = self.rcd_hour.get_value_as_int()
			min = self.rcd_min.get_value_as_int()
			sec = self.rcd_second.get_value_as_int()
			time = sec + (min*60) + (hour*3600)
			time_in_hour = time/3600.0
			distance = float(self.rcd_distance.get_text())
			average = distance/time_in_hour
			self.rcd_average.set_text("%0.2f" %average)
		except:
			pass
	
	def on_calcpace_clicked(self,widget):
		hour = self.rcd_hour.get_value_as_int()
		min = self.rcd_min.get_value_as_int()
		sec = self.rcd_second.get_value_as_int()
		time = sec + (min*60) + (hour*3600)
		if time<1:
			return false
		time_in_min = time/60.0
		distance = float(self.rcd_distance.get_text())
		if distance<1:
			return false
		average = time_in_min/distance
		self.rcd_pace.set_text("%0.2f" %average)
	
	def on_calccalories_clicked(self,widget):
		sport = self.rcd_sport.get_active_text()
		hour = self.rcd_hour.get_value_as_int()
		min = self.rcd_min.get_value_as_int()
		sec = self.rcd_second.get_value_as_int()
		hour += min/60 + sec/60/60
		weight = float("0%s"%self.parent.configuration.getValue("pytraining","prf_weight"))
		met = self.parent.getSportMet(sport)
		extraweight = self.parent.getSportWeight(sport)
		if met:
			calories = met*(weight+extraweight)*hour
			self.rcd_calories.set_text(str(calories))

	def on_calcdistance_clicked(self,widget):
		try:
			hour = self.rcd_hour.get_value_as_int()
			min = self.rcd_min.get_value_as_int()
			sec = self.rcd_second.get_value_as_int()
			time = sec + (min*60) + (hour*3600)
			time_in_hour = time/3600.0
			average = float(self.rcd_average.get_text())
			distance = average*time_in_hour
			self.set_distance(distance) 
		except:
			pass
	
	def set_distance(self,distance):
		self.rcd_distance.set_text("%0.2f" %distance)
			
	def set_maxspeed(self,vel):
		self.rcd_maxvel.set_text("%0.2f" %vel)
			
	def set_maxhr(self,hr):
		self.rcd_maxbeats.set_text("%0.2f" %hr)
			
	def set_recordtime (self,time_in_hour):
		hour = int(time_in_hour)
		min = int((time_in_hour-hour)*60)
		sec = (((time_in_hour-hour)*60)-min)*60
		self.rcd_hour.set_value(hour)
		self.rcd_min.set_value(min)
		self.rcd_second.set_value(sec)

	def on_selectfile_clicked(self,widget):
		self.filechooser = FileChooser(self.data_path,self,"set_gpxfile","open")
		self.filechooser.run()

	def set_gpxfile(self):
		namefile = self.filechooser.filename
		self.rcd_gpxfile.set_text(namefile)

	def on_calculatevalues_clicked(self,widget):
		gpxfile = self.rcd_gpxfile.get_text()
		if os.path.isfile(gpxfile):
			self.frameGeneral.set_sensitive(0)
			self.frameVelocity.set_sensitive(0)	
			self.parent.actualize_fromgpx(gpxfile)

