import cgi
import datetime
import urllib
import wsgiref.handlers
import logging

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
  phoneNumber = db.StringProperty()
  
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
  
class Event(db.Model):
  name = db.StringProperty()  
  primaryKey = db.IntegerProperty()
  clubKey = db.IntegerProperty()
  date = db.StringProperty()
  creationDate = db.DateTimeProperty(auto_now_add=True)


def person_key(person_name=None):
  return db.Key.from_path('person', 'person' or 'default_person')
 
def personClubStatus_key(person_name=None):
	return db.Key.from_path('person', 'personClubStatus' or 'default_person')
  
def club_key(person_name=None):
	return db.Key.from_path('person', 'club' or 'default_person') 
  
def personEventStatus_key(person_name=None):
	return db.Key.from_path('person', 'personEventStatus' or 'default_person')  
  
def Event_key(person_name=None):
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
		person.email = email
	else:
		error = '1'
		
	if phoneNumber:
		person.phoneNumber = phoneNumber
	else:
		error = '1'
		
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
		year = int(self.request.get('year'))

		#Searchs for the club (for name/existance)
		clubs = db.GqlQuery("SELECT * "
                            "FROM Club ")
							
		matchingClub = ''
		for club in clubs:
			if club.primaryKey == clubKey:
				matchingClub = club
							
		template_values = {
		}
		
		if matchingClub:
			nameOfClub = matchingClub.name
			
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
		self.response.out.write('Error, attempted to get. Go back and try again.')

class selectClubToView(webapp.RequestHandler):

    def get(self):
			clubsMasterString = ''
			
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
		
application = webapp.WSGIApplication(
                                     [('/',index),
									  ('/register', registerPerson),
									  ('/submit', registerPerson_Submit),
									  ('/addClub', addClub),
									  ('/addClubSubmit', addClub_Submit),
									  ('/addMembers', addMembers),
									  ('/addMembers_Submit', addMembers_Submit),
									  ('/viewClubs', viewClubs),
									  ('/clubmembers',viewClubMembers),
									  ('/selectClubToView',selectClubToView)
									  
									  #('/addEvent', addEvent),
									  #('/addEventSubmit', addEvent_Submit),
									  #'/addMembersToEvent', addMembersToEvent),
									  #('/addMembersToEvent_Submit', addMembersToEvent_Submit),
									  #('/viewEvents', viewEvents),
									  #('/eventAttendees',viewEventMembers),
									  #('/selectEventToView',selectEventToView)
									  ],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()