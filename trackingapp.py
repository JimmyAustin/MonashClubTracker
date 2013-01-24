import cgi
import datetime
import urllib
import wsgiref.handlers
import logging
import re

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

import os
from google.appengine.ext.webapp import template

class Person(db.Model):

  #Models an individual event entry with an name, location, starting date, ending date
  firstName = db.StringProperty()
  lastName = db.StringProperty()
  authcate = db.StringProperty()
  studentID = db.IntegerProperty()
  email = db.StringProperty()
  campus = db.IntegerProperty()
  phoneNumber = db.StringProperty()
  
  #Campus Numbers
  # 1: Clayton
  # 2: Caulfield
  # 3: Peninsula
  # 4: Parkville
  # 5: Gippsland
  # 6: Berwick
  # 7: India
  # 8: South Africa
  # 9: Italy
  # 10: Sunway, Malaysia
  # 11: China
  
class PersonClubStatus(db.Model):
  studentID = db.IntegerProperty()  
  year = db.IntegerProperty()  
  clubKey = db.IntegerProperty() 
  
class Club(db.Model):
  name = db.StringProperty()  
  primaryKey = db.IntegerProperty()  

class PersonEventStatus(db.Model):
  studentID = db.IntegerProperty()  
  eventKey = db.IntegerProperty() 
  creationDate = db.DateTimeProperty(auto_now_add=True)  
  
class Event(db.Model):
  name = db.StringProperty()  
  primaryKey = db.IntegerProperty()
  clubKey = db.IntegerProperty()
  date = db.StringProperty()
  clubName = db.StringProperty()
  location = db.StringProperty()
  creationDate = db.DateTimeProperty(auto_now_add=True)


def person_key(person_name=None):
  return db.Key.from_path('person', 'person' or 'default_person')
 
def personClubStatus_key(person_name=None):
	return db.Key.from_path('person', 'personClubStatus' or 'default_person')
  
def club_key(person_name=None):
	return db.Key.from_path('person', 'club' or 'default_person') 
  
def personEventStatus_key(person_name=None):
	return db.Key.from_path('person', 'personEventStatus' or 'default_person')  
  
def event_key(person_name=None):
	return db.Key.from_path('person', 'event' or 'default_person')  
  
class registerPerson(webapp.RequestHandler):

    def get(self):
			error = self.request.get('error')
			if error == '0':
				error = 'Success!'
			elif error == '1':
				error = 'Looks like you missed something'
			elif error == '2':
				error = 'Student ID needs to be a number'
			elif error == '3':
				error = 'Your email looks invalid. Have you tried to use your monash one?'
			elif error == '4':
				error = 'Student ID already found'
			template_values = {
				'error': error
			}

			path = os.path.join(os.path.dirname(__file__), 'register.html')
			self.response.out.write(template.render(path, template_values))			
	
class registerPerson_Submit(webapp.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
	
	firstName = self.request.get('firstname')
	lastName = self.request.get('lastname')
	authcate = self.request.get('authcate')
	email = self.request.get('email')
	phoneNumber = self.request.get('phonenumber')
	campus = self.request.get('campus')

	person = Person(parent=person_key('defaultkey'))

	

	
	error = '';
	if firstName:
		person.firstName = firstName
	else:
		error = '1'
		
	if lastName:
		person.lastName = lastName
	else:
		error = '1'
		
	if authcate:
		person.authcate = authcate
	else:
		error = '1'
	try:
		studentID = int(self.request.get('studentid'))
		if studentID:
			person.studentID = studentID
		else:
			error = '1'
	except:
		error = '2'
		
	
		
	if email:
		if re.match(r"[^@]+@[^@]+\.[^@]+", email):
			person.email = email
		else:
			error = '3'
	else:
		error = '1'
		
	if phoneNumber:
		person.phoneNumber = phoneNumber
	
	
	
	if error == '':
		error = "0"
		person.put();
		
		
	
	self.redirect('/register?error=%s' % error)
		
class addClub(webapp.RequestHandler):
	def get(self):
			error = self.request.get('error')
			if error == '0':
				error = 'Success!'
			elif error == '1':
				error = 'Looks like you missed something'
				
			template_values = {
				'error': error
			}
			path = os.path.join(os.path.dirname(__file__), 'addClub.html')
			self.response.out.write(template.render(path, template_values))	
		
class addClub_Submit(webapp.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
	
	clubName = self.request.get('clubname')
	
	newClub = Club(parent=club_key('defaultkey'))

	error = '';
	if clubName:
		newClub.name = clubName
	else:
		error = '1'
		
	if error == '':
		error = "0"
		
		highestNumber = 0
		
		clubs = db.GqlQuery("SELECT * "
                            "FROM Club "
                            "WHERE ANCESTOR IS :1 ",
                            club_key('default_club'))
		
		for club in clubs:
			if highestNumber < club.primaryKey:
				highestNumber = club.primaryKey
		
		highestNumber = highestNumber + 1
		
		newClub.primaryKey = highestNumber
		
		newClub.put();
		
		
	
	self.redirect('/addClub?error=%s' % error)		
	
class getClubs(webapp.RequestHandler):
	def get(self):
			
		masterString = ''	
			
		clubs = db.GqlQuery("SELECT * "
                            "FROM Club "
                            "WHERE ANCESTOR IS :1 ",
                            club_key('default_club'))
		
		for Club in clubs:
			masterString = Club.name + '<br>' +  masterString
		
		template_values = {
				'clubs': masterString
		}
			
		path = os.path.join(os.path.dirname(__file__), 'viewClubs.html')
		self.response.out.write(template.render(path, template_values))	
		
class addMembers(webapp.RequestHandler):

    def get(self):
			error = self.request.get('error')
			if error == '0':
				error = 'Success!'
			elif error == '1':
				error = 'Looks like you missed something'
			elif error == '2':
				error = 'Student ID needs to be a number'
			elif error == '3':
				error = 'Student ID match not found'
			
			clubsMasterString = ''
			
			clubs = db.GqlQuery("SELECT * "
                            "FROM Club "
                            "WHERE ANCESTOR IS :1 ",
                            club_key('default_club'))
		
			for Club in clubs:
				clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'
		
			template_values = {
				'error': error,
				'clubs': clubsMasterString
			}
			
			
			path = os.path.join(os.path.dirname(__file__), 'addMember.html')
			self.response.out.write(template.render(path, template_values))			
	
class addMembers_Submit(webapp.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
	error = ''
	try:
		studentID = int(self.request.get('studentid'))
	except:
		error = '2'
		
	if error == '':
		try:
			if studentID:
				persons = db.GqlQuery("SELECT * "
								"FROM Person "
								"WHERE studentID = :1",
								studentID)
				match = False
				for Person in persons:
					match = True
				if match:
					studentID = studentID
				else:
					error = '3'
			else:
				error = '1'
		except:
			error = '4'
	
	if error == '':
		clubPrimaryKey = self.request.get('clubinput')
		
		newClubStatus = PersonClubStatus(parent=personClubStatus_key('defaultkey'))
		
		newClubStatus.studentID = studentID
		newClubStatus.year = int(self.request.get('year'))
		newClubStatus.clubKey = int(clubPrimaryKey)
		
		newClubStatus.put();
		error = '0'
		
	
	self.redirect('/addMembers?error=%s' % error)

class addMSACard(webapp.RequestHandler):

    def get(self):
			error = self.request.get('error')
			if error == '0':
				error = 'Success!'
			elif error == '1':
				error = 'Looks like you missed something'
			elif error == '2':
				error = 'Student ID needs to be a number'
			elif error == '3':
				error = 'Student ID match not found'
			
			template_values = {
				'error': error,
			}
			
			
			path = os.path.join(os.path.dirname(__file__), 'addMSACard.html')
			self.response.out.write(template.render(path, template_values))			
	
class addMSACard_Submit(webapp.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
	error = ''
	try:
		studentID = int(self.request.get('studentid'))
	except:
		error = '2'
		
	if error == '':
		try:
			if studentID:
				persons = db.GqlQuery("SELECT * "
								"FROM Person "
								"WHERE studentID = :1",
								studentID)
				match = False
				for Person in persons:
					match = True
				if match:
					studentID = studentID
				else:
					error = '3'
			else:
				error = '1'
		except:
			error = '4'
	
	if error == '':
		clubPrimaryKey = 0
		
		newClubStatus = PersonClubStatus(parent=personClubStatus_key('defaultkey'))
		
		newClubStatus.studentID = studentID
		newClubStatus.year = int(self.request.get('year'))
		newClubStatus.clubKey = int(clubPrimaryKey)
		
		newClubStatus.put();
		error = '0'
		
	
	self.redirect('/addMSACard?error=%s' % error)	
	
	
class index(webapp.RequestHandler):

    def get(self):

			template_values = {
			}
			
			path = os.path.join(os.path.dirname(__file__), 'index.html')
			self.response.out.write(template.render(path, template_values))		

class viewClubs(webapp.RequestHandler):
	def get(self):
		masterString = ''	

		clubs = db.GqlQuery("SELECT * "
                            "FROM Club "
                            "WHERE ANCESTOR IS :1",
                            club_key('default_club'))
		
		for Club in clubs:
			masterString = Club.name + '<br>' +  masterString
		
		template_values = {
				'clubs': masterString
		}
			
		path = os.path.join(os.path.dirname(__file__), 'viewClubs.html')
		self.response.out.write(template.render(path, template_values))		

	
		
class viewClubMembers(webapp.RequestHandler):
	def post(self):
	
		masterString = ''	
		clubKey = int(self.request.get('clubinput'))
		year = self.request.get('year')
		if year:
			year = int(self.request.get('year'))
		else:
			now = datetime.datetime.now()
			year = now.year
		#Searchs for the club (for name/existance)
		
		nameOfClub = ''
		
		if clubKey == 0:
			nameOfClub = 'MSA Cards'
		else:
			clubs = db.GqlQuery("SELECT * "
                            "FROM Club ")
			
			for club in clubs:
				if club.primaryKey == clubKey:
					nameOfClub = club.name
							
		template_values = {
		}
		
		if nameOfClub:
			
			clubMemberships = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE clubKey = :1 AND year = :2",
											int(clubKey),year)
			masterString = ''			
			for membership in clubMemberships:
				people = db.GqlQuery("SELECT * FROM Person WHERE studentID = :1",
											membership.studentID)
				for person in people:
					masterString = masterString + str(person.studentID) + '<br>' + person.firstName + ' ' + person.lastName + '<br><br>'

			template_values = {
				'nameOfClub': nameOfClub,
				'table'		: masterString
			}
		else:
			template_values = {
				'nameOfClub': 'Error',
				'table'		: 'Club not found'
			}

		path = os.path.join(os.path.dirname(__file__), 'viewClubMembers.html')
		self.response.out.write(template.render(path, template_values))	
	def get(self):
		self.post()

class selectClubToView(webapp.RequestHandler):

    def get(self):
			clubsMasterString = '<option value="' + '0' + '">' + 'MSA Card Holders' + '</option>'
			
			clubs = db.GqlQuery("SELECT * "
                            "FROM Club "
                            "WHERE ANCESTOR IS :1 ",
                            club_key('default_club'))
		
			for Club in clubs:
				clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'
		
			template_values = {
				'clubs': clubsMasterString
			}
			
			path = os.path.join(os.path.dirname(__file__), 'clubMemberSelector.html')
			self.response.out.write(template.render(path, template_values))			

class addEvent(webapp.RequestHandler):
	def get(self):
	
			
	
			error = self.request.get('error')
			if error == '0':
				error = 'Success!'
			elif error == '1':
				error = 'Looks like you missed something'
			
			clubsMasterString = ''
			
			clubs = db.GqlQuery("SELECT * "
                            "FROM Club "
                            "WHERE ANCESTOR IS :1 ",
                            club_key('default_club'))
		
			for Club in clubs:
				clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'
		
			template_values = {
				'error': error,
				'clubs': clubsMasterString
			}

			path = os.path.join(os.path.dirname(__file__), 'addEvent.html')
			self.response.out.write(template.render(path, template_values))	
		
class addEvent_Submit(webapp.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
	
	eventName = self.request.get('eventname')
	date = self.request.get('date')
	location = self.request.get('location')

	clubPrimaryKey = self.request.get('clubinput')

	newEvent = Event(parent=event_key('defaultkey'))

	error = '';
	if eventName:
		newEvent.name = eventName
	else:
		error = '1'
	
	if date:
		newEvent.date = date
	else:
		error = '1'
	
	if location:
		newEvent.location = location
	else:
		error = '1'
		
	clubs = db.GqlQuery("SELECT * "
                            "FROM Club "
                            "WHERE ANCESTOR IS :1 ",
                            club_key('default_club'))
							
	logging.info('Event')
	logging.info(clubPrimaryKey)
	intClubPrimaryKey = int(clubPrimaryKey)
	for Club in clubs:
		if Club.primaryKey == intClubPrimaryKey:
			newEvent.clubName = Club.name
			logging.info('Matched name')

	
	newEvent.clubKey = int(clubPrimaryKey)

	
	if error == '':
		error = "0"
		
		highestNumber = 0
		
		events = db.GqlQuery("SELECT * "
                            "FROM Event "
                            "WHERE ANCESTOR IS :1 ",
                            event_key('default_club'))
		
		for event in events:
			if highestNumber < event.primaryKey:
				highestNumber = event.primaryKey
		
		highestNumber = highestNumber + 1
		
		newEvent.primaryKey = highestNumber
		
		newEvent.put();
		
		
	
	self.redirect('/addEvent?error=%s' % error)	

class viewEvents(webapp.RequestHandler):
	def get(self):
		masterString = ''	

		events = db.GqlQuery("SELECT * "
                            "FROM Event "
                            "WHERE ANCESTOR IS :1 ",
                            event_key('default_event'))
		
		for event in events:
			eventline = ''
			if event.name:
				eventline = event.name
				
			if event.location:
				eventline = eventline + '\t' + event.location
				
			if event.clubName:
				eventline = eventline + '\t' + event.clubName
				
			if event.date:
				eventline = eventline + '\t' + event.date
				
			masterString = eventline  + '<br><br>' + masterString	

		
		template_values = {
				'events': masterString
		}
			
		path = os.path.join(os.path.dirname(__file__), 'viewEvents.html')
		self.response.out.write(template.render(path, template_values))	
	
	
class addMembersToEvent(webapp.RequestHandler):

    def get(self):
			error = self.request.get('error')
			if error == '0':
				error = 'Success!'
			elif error == '1':
				error = 'Looks like you missed something'
			elif error == '2':
				error = 'Student ID needs to be a number'
			elif error == '3':
				error = 'Student ID match not found'
			
			eventsMasterString = ''
			
			events = db.GqlQuery("SELECT * "
                            "FROM Event "
                            "WHERE ANCESTOR IS :1 ",
                            event_key('default_club'))
		
			for event in events:
			
				eventline = ''
			
				if event.name:
					eventline = event.name
				
				if event.date:
					eventline = eventline + ' - ' + event.date
				
				if event.clubName:
					eventline = eventline + ' - ' + event.clubName			
			
				eventsMasterString = eventsMasterString + '<option value="' + str(event.primaryKey) + '">' + eventline +'</option>'
		
			template_values = {
				'error': error,
				'events': eventsMasterString
			}
			
			
			path = os.path.join(os.path.dirname(__file__), 'addToEvent.html')
			self.response.out.write(template.render(path, template_values))			
	
class addMembersToEvent_Submit(webapp.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
	error = ''
	try:
		studentID = int(self.request.get('studentid'))
	except:
		error = '2'
		
	if error == '':
		try:
			if studentID:
				persons = db.GqlQuery("SELECT * "
								"FROM Person "
								"WHERE studentID = :1",
								studentID)
				match = False
				for Person in persons:
					match = True
				if match:
					studentID = studentID
				else:
					error = '3'
			else:
				error = '1'
		except:
			error = '4'
	
	if error == '':
		clubPrimaryKey = self.request.get('eventinput')
		
		personEventStatus = PersonEventStatus(parent=personEventStatus_key('defaultkey'))
		
		personEventStatus.studentID = studentID
		personEventStatus.eventKey = int(clubPrimaryKey)
		
		personEventStatus.put();
		logging.info('successfully put')

		error = '0'
		
	
	self.redirect('/addMembersToEvent?error=%s' % error)	
	
class viewEventMembers(webapp.RequestHandler):
	def post(self):

		masterString = ''	
		eventKey = int(self.request.get('eventinput'))

		#Searchs for the club (for name/existance)
		
		eventMemberships = db.GqlQuery("SELECT * FROM PersonEventStatus WHERE eventKey = :1",
											int(eventKey))
		
		masterString = ''	
		template_values = {
		}	
		logging.info(eventKey)
		
		for membership in eventMemberships:
			logging.info('person2')

			people = db.GqlQuery("SELECT * FROM Person WHERE studentID = :1",
											membership.studentID)
			for person in people:
				logging.info('person')
				
				personLine = ''
			
				if person.firstName:
					personLine = person.firstName
				
				if person.lastName:
					personLine = personLine + ' ' + person.lastName
				
				if person.studentID:
					personLine = personLine + '<br>' + str(person.studentID)
					
				if membership.creationDate:
					personLine = personLine + '<br> Created: ' + str(membership.creationDate)
					
				masterString = masterString + '<br><br>' + personLine
	
	
		if masterString == '':
			masterString = 'No attendees found.'
			
		events = db.GqlQuery("SELECT * "
                            "FROM Event ")
							
		eventName = ''
		for event in events:
			if event.primaryKey == eventKey:
				 eventName = event.name
			
		template_values = {
			'nameOfEvent': eventName,
			'table'		: masterString
		}

		path = os.path.join(os.path.dirname(__file__), 'viewEventAttendees.html')
		self.response.out.write(template.render(path, template_values))	
	def get(self):
		self.response.out.write('Error, attempted to get. Go back and try again.')

class selectEventToView(webapp.RequestHandler):

    def get(self):
			eventsMasterString = ''
			
			events = db.GqlQuery("SELECT * "
                            "FROM Event "
                            "WHERE ANCESTOR IS :1 ",
                            event_key('default_key'))
			
			for event in events:
				eventline = ''
			
				if event.name:
					eventline = event.name
				
				if event.date:
					eventline = eventline + ' - ' + event.date
				
				if event.clubName:
					eventline = eventline + ' - ' + event.clubName			
			
				eventsMasterString = eventsMasterString + '<option value="' + str(event.primaryKey) + '">' + eventline +'</option>'
		
		
			template_values = {
				'events': eventsMasterString
			}
			
			path = os.path.join(os.path.dirname(__file__), 'eventSelector.html')
			self.response.out.write(template.render(path, template_values))		
	
application = webapp.WSGIApplication(
                                     [('/',index),
									  ('/register', registerPerson),
									  ('/submit', registerPerson_Submit),
									  ('/addClub', addClub),
									  ('/addClubSubmit', addClub_Submit),
									  ('/addMembers', addMembers),
									  ('/addMembers_Submit', addMembers_Submit),
									  
									  ('/addMSACard', addMSACard),
									  ('/addMSACard_Submit', addMSACard_Submit),
									  
									  ('/viewClubs', viewClubs),
									  ('/clubmembers',viewClubMembers),
									  ('/selectClubToView',selectClubToView),
									  
									  ('/addEvent', addEvent),
									  ('/addEventSubmit', addEvent_Submit),
									  ('/addMembersToEvent', addMembersToEvent),
									  ('/addMembersToEvent_Submit', addMembersToEvent_Submit),
									  ('/viewEvents', viewEvents),
									  ('/eventAttendees',viewEventMembers),
									  ('/selectEventToView',selectEventToView)
									  ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()