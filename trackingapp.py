import datetime
import logging
import webapp2
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
import re
import os
from google.appengine.ext.webapp import template
from google.appengine.api import mail

from datetime import datetime, timedelta, tzinfo


import sys
class Person(db.Model):

  #Models an individual event entry with an name, location, starting date, ending date
  firstName = db.StringProperty()
  lastName = db.StringProperty()
  authcate = db.StringProperty()
  studentID = db.IntegerProperty()
  email = db.StringProperty()
  address= db.StringProperty()
  campus = db.IntegerProperty()
  phoneNumber = db.StringProperty()
  personType = db.IntegerProperty()
  
  #PersonTypes
  # 1: Student
  # 2: Staff
  # 3: Non-Student

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
  joiningDate = db.DateTimeProperty(auto_now_add=True)  
  memberType = db.IntegerProperty()
  addedBy = db.StringProperty()

  #Member Type
  # 0: Ordinary
  # 1: Associate
  
class Club(db.Model):
  name = db.StringProperty()  
  primaryKey = db.IntegerProperty()  
	
class PersonEventStatus(db.Model):
  studentID = db.IntegerProperty()  
  eventKey = db.IntegerProperty() 
  creationDate = db.DateTimeProperty(auto_now_add=True)  
  addedBy = db.StringProperty()

class Event(db.Model):
  name = db.StringProperty()  
  primaryKey = db.IntegerProperty()
  clubKey = db.IntegerProperty()
  date = db.StringProperty()
  clubName = db.StringProperty()
  location = db.StringProperty()
  creationDate = db.DateTimeProperty(auto_now_add=True)

class userPermissions(db.Model):
  email = db.StringProperty()
  clubKey = db.IntegerProperty()
  permissionLevel = db.IntegerProperty()
  name = db.StringProperty()
  #permission levels
  #2 = admin
  #1 = club personel

class ClubCounter(db.Model):
  year = db.IntegerProperty()
  clubKey = db.IntegerProperty()
  numberOfMembers = db.IntegerProperty()
  numberOfMSAMembers = db.IntegerProperty()
  
def person_key(person_name=None):
	return db.Key.from_path('Person', person_name or 'default_person')
	
def personClubStatus_key(personClubStatus_name=None,year = None, clubKey = None):
	return db.Key.from_path('PersonClubStatus', (str(personClubStatus_name) + str(year) + str(clubKey))  or 'personClubStatus')
  
def club_key(club_name=None):
	return db.Key.from_path('Club', club_name or 'club') 
  
def personEventStatus_key(personEventStatus_name=None, eventKey = None):
	return db.Key.from_path('PersonEventStatus', (str(personEventStatus_name) + str(eventKey)) or 'personEventStatus')  
  
def event_key(event_name=None):
	return db.Key.from_path('Event', event_name or 'event')  
	
def userPermissions_key(userPermissions_name=None,clubKey=None):
	return db.Key.from_path('userPermissions', (str(userPermissions_name) + str(clubKey)) or 'userPermissions')    

def ClubCounter_key(clubKey=None,year=None):
	return db.Key.from_path('ClubCounter', (str(clubKey) + str(year)) or 'ClubCounter')    
  
	
#Security: Unsecured. Accessible to all

class registerPerson(webapp2.RequestHandler):

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
			elif error == '6':
				error = 'Error with student ID'
			elif error == '7':
				error = 'You need to accept the Terms and Conditions'
			template_values = {
				'error': error
			}

			path = os.path.join(os.path.dirname(__file__), 'register.html')
			self.response.out.write(template.render(path, template_values))			

#Security: Unsecured. Accessible to all
			
class registerPerson_Submit(webapp2.RequestHandler):
  def post(self):
	
	firstName = self.request.get('firstname')
	lastName = self.request.get('lastname')
	authcate = self.request.get('authcate')
	email = self.request.get('email')
	phoneNumber = self.request.get('phonenumber')
	campus = self.request.get('campus')
	address = self.request.get('address')
	termsAndConditions = self.request.get('TermsAndConditions')
	personType = self.request.get('personType')
	personType = int(personType)

	studentID = ''
	error = '';
	
	if error == '':
		try:		

			studentID = self.request.get('studentid')
			stringLength = studentID.__len__()

			studentID = str(securityManager.trimStudentID(studentID))

			if stringLength > 7:
				studentID = int(studentID[:8])
				if studentID:
					match = False
					personToMatch = db.get(person_key(studentID))
					
					if personToMatch is None:
						if personType != 3:
							persons = db.GqlQuery("SELECT * "
										"FROM Person "
										"WHERE authcate = :1 LIMIT 1", authcate)
							personToMatch = persons.get()
							if personToMatch is not None:
								error = '4'
					else:
						error = '4'
					
				else:
					error = '1'
				
			else:
				error = '6'
			
			
			
		except:
			error = '2'
			
	if error == '':
		person = Person(key=person_key(studentID))
		person.studentID = studentID
	else:
		self.redirect('/register?error=%s' % error)
		return None
	if firstName:
		person.firstName = firstName
	else:
		error = '1'
		
	if lastName:
		person.lastName = lastName
	else:
		error = '1'
		
	if authcate:
		person.authcate = authcate.lower()
	else:
		if personType != 3:
			error = '1'
			
	
		
	if termsAndConditions != 'YES':
		error = '7'

	
	if campus:
		person.campus = int(campus)
	else:
		error = '1'
		
	if address:
		person.address = address	
		
	if email:
		if re.match(r"[^@]+@[^@]+\.[^@]+", email):
			person.email = email.lower()
		else:
			error = '3'
		
	if phoneNumber:
		person.phoneNumber = phoneNumber
	
	if personType:
		person.personType = personType
	else:
		error = '1'
	
	if error == '':
		error = "0"
		person.put();
		
		
	
	self.redirect('/register?error=%s' % error)

#Security: Restricted to only admins.
	
class addClub(webapp2.RequestHandler):
	def get(self):
		if users.is_current_user_admin() == False:
			self.redirect('/')

		error = self.request.get('error')
		if error == '0':
			error = 'Success!'
		elif error == '1':
			error = 'Looks like you missed something'
		elif error == '3':
			error = 'Email address invalid'
		template_values = {
			'error': error
		}
		path = os.path.join(os.path.dirname(__file__), 'addClub.html')
		self.response.out.write(template.render(path, template_values))	

#Security: Restricted to only admins.
			
class addClub_Submit(webapp2.RequestHandler):
	def post(self):
		if users.is_current_user_admin() == False:
			self.redirect('/')
		
		clubName = self.request.get('clubname')
		clubEmail = self.request.get('clubgoogleaccount')

		error = '';
		if clubName is None:
			error = '1'

			
		if clubEmail:
			if re.match(r"[^@]+@[^@]+\.[^@]+", clubEmail) == False:
				error = '3'
		else:
			error = '1'
			
		if error == '':
			error = "0"
		
			clubKey = self.get_primaryKey()
			newClub = Club(key=club_key(str(clubKey)))

			newClub.name = clubName
			newClub.primaryKey = clubKey
			newClub.clubEmail = clubEmail.lower()

			newClub.put();
			
			newUserPermissions = userPermissions(key=userPermissions_key(clubEmail,clubKey))
			newUserPermissions.permissionLevel = 2
			newUserPermissions.name = 'Club Secretary'
			newUserPermissions.clubKey = clubKey
			newUserPermissions.email = clubEmail
			newUserPermissions.put()
				
		self.redirect('/addClub?error=%s' % error)		
	
	def get_primaryKey(addClub_Submit):
		data = memcache.get('clubPrimaryKey')
		if data is not None:
			primaryKey = int(data)
			memcache.add(str(primaryKey + 1), 'clubPrimaryKey', 200)
			return primaryKey
		else:
			highestNumber = 0
	
			clubs = db.GqlQuery("SELECT * "
							"FROM Club ")
		
			for club in clubs:
				if highestNumber < club.primaryKey:
					highestNumber = club.primaryKey
		
			highestNumber = highestNumber + 1
			memcache.add(str(highestNumber + 1), 'clubPrimaryKey', 200)
			return highestNumber
	
#Security: Should show all clubs to admins, but only clubs the user is admin in if they are not. 		
		
class addMembers(webapp2.RequestHandler):

    def get(self):
	
		clubs = []
		
		clubsMasterString = ''
		
		clubs = securityManager.getClubsUserIsPersonnelOf()
		
		for Club in clubs:
				clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'				
		
		if clubsMasterString == '':
			self.redirect('/')
		
		error = self.request.get('error')
		if error == '0':
			name = self.request.get('name')
			if name:
				error = 'Successfully added:' + name
			else:
				error = 'Success!'
		elif error == '1':
			error = 'Looks like you missed something'
		elif error == '2':
			error = 'Student ID needs to be a number'
		elif error == '3':
			error = 'Student ID match not found'
		elif error == '4':
			error = 'Match already found'
		elif error == '5':
			error = 'Permission not found'
		elif error == '6':
			error = 'Student ID malformed.'
		year = str(datetime.now().year)
			
		template_values = {
			'error': error,
			'clubs': clubsMasterString,
			'year' : year
		}
		
		
		path = os.path.join(os.path.dirname(__file__), 'addMember.html')
		self.response.out.write(template.render(path, template_values))
	
class addMembers_Submit(webapp2.RequestHandler):
  def post(self):

	error = ''
	
	year = datetime.now().year

	try:
		studentID = self.request.get('studentid')

		stringLength = studentID.__len__()
		if stringLength > 7:
			studentID = int(studentID[:8])
		else:
			error = '6'
	except:
		
		error = '2'
	
	clubPrimaryKey = self.request.get('clubinput')

	if clubPrimaryKey:
		clubPrimaryKey = int(clubPrimaryKey)
	else:
		error = '1' 
	
	personName = ''
	personEmail = ''
	if error == '':
		if studentID:

			person = db.get(person_key(studentID))
			
			if person is None:
				error = '3'
			else:
				personName = person.firstName + ' ' + person.lastName
				
				personEmail = person.email
				if personEmail:
					personEmail = personEmail.lower()
				else:
					personEmail = 'N/A'


				permissionLevel = securityManager.getLevelOfAuthenticationForUserForClub(clubPrimaryKey)
				
				if permissionLevel == 0:
					error = '5'
				msaCardStatus = self.request.get('msacardstatus')
				
				if msaCardStatus == 'YES':
					securityManager.addMSACardToStudent(studentID)	
						

		else:
			error = '1'
	
	if error == '':
	#Check if it already exists.
				
		clubMemberships = db.GqlQuery("SELECT * "
								"FROM PersonClubStatus "
								"WHERE studentID = :1 AND year = :2 AND clubKey = :3",
								studentID,year, clubPrimaryKey)
		
		for person in clubMemberships:
			error = '4'
	
	if error == '':
		
		newClubStatus = PersonClubStatus(key=personClubStatus_key(studentID,year,clubPrimaryKey))
		
		newClubStatus.studentID = studentID
		newClubStatus.year = year
		newClubStatus.clubKey = int(clubPrimaryKey)
		newClubStatus.memberType = int(self.request.get('memberType'))
		
		user = users.get_current_user()
		email = user.email().lower()
		addedByAuthcate = email.split("@")[0]
		
		newClubStatus.addedBy = addedByAuthcate
		logging.info('Added to club')
		logging.info(clubPrimaryKey)
		logging.info(year)
		if personName:
			logging.info(personName)
		else:
			logging.info('No name')
		newClubStatus.put()
		
		club = db.get(club_key(str(clubPrimaryKey)))
		
		clubName = club.name

		clubCounter = db.get(ClubCounter_key(clubPrimaryKey,year))
		
		if clubCounter:
			clubCounter.numberOfMembers = clubCounter.numberOfMembers + 1
			if msaCardStatus == 'YES':
				if clubCounter.numberOfMSAMembers:
					clubCounter.numberOfMSAMembers = clubCounter.numberOfMSAMembers + 1
				else:
					clubCounter.numberOfMSAMembers = 1
			clubCounter.put()
		else:
			clubCounter = ClubCounter(key=ClubCounter_key(clubPrimaryKey,year))
			clubCounter.year = datetime.now().year
			clubCounter.clubKey = club.primaryKey
			clubCounter.numberOfMembers = 1
			msaCardStatus = self.request.get('msacardstatus')	
			if msaCardStatus == 'YES':
				clubCounter.numberOfMSAMembers = 0
			else:
				clubCounter.numberOfMSAMembers = 1
			clubCounter.put()
			
			

			
		user = users.get_current_user()
		email = user.email().lower()
		addedByAuthcate = email.split("@")[0]
		try:
			message = mail.EmailMessage(sender="No Reply <noreply@monashclubs.org>", subject="You have been added to " + clubName)
			message.to = personName + '<' + personEmail + '>'
			message.body = '''
			You have been added as a member of the {!s}. 
			This has been done by {!s} upon receipt of any membership fees that were payable. 
			Your information will be used by the club to contact your with regards to club events/activities and 
			information. If you have been added to this club in error, please contact Clubs & Societies by emailing 
			webmaster@monashclubs.org. If you would like to make a complaint, please contact the 
			Club Development Officer at do@monashclubs.org.
			'''.format(clubName, addedByAuthcate)


			message.send()
		except:
			logging.error('Failure to send email')
			logging.error('error' + str(sys.exc_info()[0]))
		
		error = '0'
		
	if personName != '':
		self.redirect(('/addMembers?error=%s' % error) + ('&name=%s' % personName))
	else:
		self.redirect('/addMembers?error=%s' % error)
		
class deleteMember(webapp2.RequestHandler):

    def get(self):
	
		clubs = []
		
		clubsMasterString = ''
		
		clubs = securityManager.getClubsUserIsAdminOf()
		
		for Club in clubs:
			clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'				
		
		if clubsMasterString == '':
			self.redirect('/')
		
		error = self.request.get('error')
		if error == '0':
			error = 'Success!'
		elif error == '1':
			error = 'Looks like you missed something'
		elif error == '2':
			error = 'Student ID needs to be a number'
		elif error == '3':
			error = 'Student ID match not found'
		elif error == '4':
			error = 'Match already found'
		elif error == '5':
			error = 'Permission not found'
		elif error == '6':
			error = 'Student ID malformed.'
		elif error == '7':
			error = 'Membership not found'
		year = str(datetime.now().year)
			
		template_values = {
			'error': error,
			'clubs': clubsMasterString,
			'year' : year
		}
		
		
		path = os.path.join(os.path.dirname(__file__), 'removeMember.html')
		self.response.out.write(template.render(path, template_values))			
	
class deleteMember_Submit(webapp2.RequestHandler):
  def post(self):

	error = ''
	
	year = datetime.now().year

	try:
		studentID = self.request.get('studentid')


		stringLength = studentID.__len__()
		if stringLength > 7:
			studentID = int(studentID[:8])
		else:
			error = '6'
	except:
		
		error = '2'
	
	clubPrimaryKey = self.request.get('clubinput')

	if clubPrimaryKey:
		clubPrimaryKey = int(clubPrimaryKey)
	else:
		error = '1' 
	
	if error == '':
		try:
			if studentID:
				person = db.get(person_key(studentID))
				
				if person is None:
					error = '3'
				permissionLevel = securityManager.getLevelOfAuthenticationForUserForClub(clubPrimaryKey)
				if permissionLevel == 0:
					error = '5'
			else:
				error = '1'
		except:
			error = '4'
	
	if error == '':
	#Check if it already exists.
				
		clubMemberships = db.GqlQuery("SELECT * "
								"FROM PersonClubStatus "
								"WHERE studentID = :1 AND year = :2 AND clubKey = :3",
								studentID,year, clubPrimaryKey)
		
		for person in clubMemberships:
			
			clubCounter = db.get(ClubCounter_key(clubPrimaryKey,datetime.now().year))

			if clubCounter:
				clubCounter.numberOfMembers = clubCounter.numberOfMembers - 1
				clubCounter.put()

			
			
			person.delete()
			error = '0'
			
			club = db.get(club_key(str(clubPrimaryKey)))
		
			clubName = club.name
			
			user = users.get_current_user()
			email = user.email().lower()
			addedByAuthcate = email.split("@")[0]
			try:
				message = mail.EmailMessage(sender="No Reply <noreply@monashclubs.org>",
				subject="You have been added to " + clubName)

				message.to = personName + '<' + personEmail + '>'
				message.body = '''
				You have been removed as a member of the {!s}.
				This has been done by {!s} upon receipt of a request from yourself
				to terminate your membership or if you have been removed as a member of this club in
				accordance with the clubs constitution and the constitution of the Clubs & Societies Council.
				If you have been added to this club in error, please contact Clubs & Societies by
				emailing webmaster@monashclubs.org. If you would like to make a complaint, please contact
				the Club Development Officer at do@monashclubs.org
				'''.format(clubName, addedByAuthcate)


				message.send()
			except:
				logging.error('Failure to send email')
            
	self.redirect('/deleteMember?error=%s' % error)
	
class deletePerson(webapp2.RequestHandler):

    def get(self):
	
		clubs = []
		
		clubsMasterString = ''
		
		clubs = securityManager.getClubsUserIsAdminOf()
		
		for Club in clubs:
				clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'				
		
		if clubsMasterString == '':
			self.redirect('/')
		
		error = self.request.get('error')
		if error == '0':
			error = 'Success!'
		elif error == '1':
			error = 'Looks like you missed something'
		elif error == '2':
			error = 'Student ID needs to be a number'
		elif error == '3':
			error = 'Student ID match not found'
		elif error == '4':
			error = 'Match already found'
		elif error == '5':
			error = 'Permission not found'
		elif error == '6':
			error = 'Student ID malformed.'
		elif error == '7':
			error = 'Membership not found'
		year = str(datetime.now().year)
			
		template_values = {
			'error': error,
			'clubs': clubsMasterString,
			'year' : year
		}
		
		
		path = os.path.join(os.path.dirname(__file__), 'deletePerson.html')
		self.response.out.write(template.render(path, template_values))			
	
class deletePerson_Submit(webapp2.RequestHandler):
  def post(self):
	error = ''
	
	year = datetime.now().year
	if users.is_current_user_admin() == False:
		self.redirect('/')
	
	try:
		studentID = self.request.get('studentid')


		stringLength = studentID.__len__()
		if stringLength > 7:
			studentID = int(studentID[:8])
		else:
			error = '6'
	except:
		
		error = '2'
	

	
	if error == '':
		try:
			if studentID:
				person = db.get(person_key(studentID))

				if person is None:
					error = '3'
				else:
					person.delete()
				
			else:
				error = '1'
		except:
			error = '4'
	
	if error == '':
	#Check if it already exists.
				
		clubMemberships = db.GqlQuery("SELECT * "
								"FROM PersonClubStatus "
								"WHERE studentID = :1",
								studentID)
		
		for person in clubMemberships:
			person.delete()
			error = '0'
			
		clubMemberships = db.GqlQuery("SELECT * "
								"FROM PersonEventStatus "
								"WHERE studentID = :1",
								studentID)
		for person in clubMemberships:
			person.delete()
			error = '0'	
		
	if error == '':
		error = '7'
	
	self.redirect('/deletePerson?error=%s' % error)

class viewMembershipTotals(webapp2.RequestHandler):	
	def get(self):
		
		clubs = securityManager.getClubsUserIsAdminOf()
		masterString = ''
		for club in clubs:
			counters = db.GqlQuery("SELECT * "
                                    "FROM ClubCounter "
                                    "WHERE clubKey = :1",
                                    club.primaryKey)
									
			for counter in counters:
				masterString = masterString + '<tr><td>' + club.name + '</td><td>' + str(counter.year) + '</td><td>' + str(counter.numberOfMembers) + '</td><td>' + str(counter.numberOfMSAMembers) + '</td></tr>'
								
		
		
		template_values = {
			'masterString'	:masterString
		}
		
		path = os.path.join(os.path.dirname(__file__), 'viewClubsPopulation.html')
		self.response.out.write(template.render(path, template_values))
class checkMemberStatus(webapp2.RequestHandler):

    def get(self):
		error = self.request.get('error')
		if error == '1':
			error = 'Looks like you missed something'
		elif error == '2':
			error = 'Student ID needs to be a number'
		elif error == '3':
			error = 'Student ID match not found'
			
		template_values = {
		}
		
		
		path = os.path.join(os.path.dirname(__file__), 'checkMemberStatusSelector.html')
		self.response.out.write(template.render(path, template_values))		
	
class checkMemberStatus_Submit(webapp2.RequestHandler):
    def post(self):
		error = ''
		try:
		
			studentID = self.request.get('studentid')
			if studentID:
				studentID = int(studentID)
				
			authcate = self.request.get('authcate')

		except:
			error = '2'
			
		if error == '':
			#try:
			person = ''
			logging.info('1')
			if studentID or authcate:
				logging.info('2')

				if studentID:
					logging.info('3')

					person = db.get(person_key(studentID))

				match = False
				
				if person == '':
					authcate = self.request.get('authcate')
					persons = db.GqlQuery("SELECT * "
                            "FROM Person "
                            "WHERE authcate = :1",authcate)
					logging.info('4')

					for foundPeople in persons:
						person = foundPeople
						logging.info('5')

				
				if person:
					name = person.firstName + ' ' + person.lastName
					email = person.email
					campus = person.campus
					phoneNumber = person.phoneNumber
					if campus == 1:
						campus = 'Clayton'
					elif campus == 2:
						campus = 'Caulfield'
					elif campus == 3:
						campus = 'Peninsula'
					elif campus == 4:
						campus = 'Parkville'
					elif campus == 5:
						campus = 'Gippsland'
					elif campus == 6:					
						campus = 'Berwick'
					elif campus == 7:
						campus = 'India'
					elif campus == 8:
						campus = 'South Africa'
					elif campus == 9:
						campus = 'Italy'
					elif campus == 10:
						campus = 'Sunway, Malaysia'
					elif campus == 11:
						campus = 'China'
					authcate = person.authcate
					studentID = person.studentID
					address = person.address
					type = ['Student','Staff','Non-Student']
					index = 0
					if person.personType:
						index = person.personType - 1
					type = type[index]
					tableString = ''
					MSAMemberStatus = 'N'
					clubMemberships = db.GqlQuery("SELECT * "
								"FROM PersonClubStatus "
								"WHERE studentID = :1",
								studentID)
					
					clubList = []
					clubs = securityManager.getClubsUserIsAdminOf()
					
					for club in clubs:
						clubList.append(club)
					
					now = datetime.now()
					year = now.year
					
					for membership in clubMemberships:
						clubKey = membership.clubKey
						clubName = ''
						if membership.year == year and clubKey == 0:
							MSAMemberStatus = 'Y'
							
						for club in clubList:
							if club.primaryKey == clubKey:

								club = db.get(club_key(str(clubKey)))
								
								if club:
									clubName = club.name
								else:
									clubName = 'Error, not found. Key:' + str(clubKey)
									
								addedBy = membership.addedBy
								if addedBy is None:
									addedBy = 'N/A'
									
								date = membership.joiningDate
								
								if date is None:
									date = 'N/A'
								else:
									before = ESTTime()
									after = MelbourneTime()
									
									date = membership.joiningDate
									date = date.replace(tzinfo=before)
									date = date.astimezone(after)

								
								
								year = membership.year
								if year is None:
									year = 'None'
								tableString = tableString + '<tr><td>' + clubName + '</td><td>' + str(year) + '</td><td>' + addedBy  + '</td><td>' + str(date) + '</td></tr>'
						
					if tableString == '' and users.is_current_user_admin() == False:
						self.redirect('/')
					
					
					template_values = {
						'type'				: type,
						'name'				: name,
						'email'				: email,
						'authcate'			: authcate,
						'address'			: address,
						'campus'			: campus,
						'studentID'			: studentID,
						'phoneNumber'		: phoneNumber,
						'memberships'		: tableString,
						'MSAMemberStatus'	: MSAMemberStatus
					}

					path = os.path.join(os.path.dirname(__file__), 'showMemberStatus.html')
					self.response.out.write(template.render(path, template_values))		
				else:
					error = '3'
			else:
				error = '1'
			#except:
			#	error = '4'
		if error != '':	
			self.redirect('/checkMemberStatus?error=%s' % error)
	
class addMSACard(webapp2.RequestHandler):

    def get(self):
			if users.is_current_user_admin() == False:
				self.redirect('/')
				
			error = self.request.get('error')
			if error == '0':
				error = 'Success!'
			elif error == '1':
				error = 'Looks like you missed something'
			elif error == '2':
				error = 'Student ID needs to be a number'
			elif error == '3':
				error = 'Student ID match not found'
			elif error == '4':
				error = 'Already found for year'
				
			template_values = {
				'error': error,
			}
			
			
			path = os.path.join(os.path.dirname(__file__), 'addMSACard.html')
			self.response.out.write(template.render(path, template_values))			
	
class addMSACard_Submit(webapp2.RequestHandler):
  def post(self):

	error = ''
	year = self.request.get('year')
	if year:
		year = int(self.request.get('year'))
	else:
		error = '1'
		
	if users.is_current_user_admin() == False:
		self.redirect('/')
	
	try:
		studentID = int(self.request.get('studentid'))
	except:
		error = '2'
		
	if error == '':
		error = securityManager.addMSACardToStudent(studentID)
	self.redirect('/addMSACard?error=%s' % error)	
	
	
class index(webapp2.RequestHandler):

    def get(self):
			user = users.get_current_user()
			loginMessage = 'Welcome to the Monash Club Registration System.'
			
			addNewPerson = True
			addMSACard = False
			addClub = False
			addMemberToClub = False
			viewClubs = True
			viewClubMembers = False
			viewClubPermissions = False
			addClubPersonnel = False
			deleteClubPersonnel = False
			addEvent = False
			addPeopleToEvents = False
			checkMemberStatus = False
			viewAllEvents = False
			viewEventAttendees = False
			deleteFromClub = False
			deletePersonFromSystem = False
			modifyDetails = False
			clubEmail = False
			viewMembershipTotals = False
			deleteClub = False
			changeID = False
			
			secretaryRights = False
			adminRights = False
			
			
			
			logoutMessage = ''
			if user:
				logoutMessage = '<a href="%s">Click here to logout.</a>' % users.create_logout_url(self.request.uri)
				user = users.get_current_user()
				email = user.email().lower()
				domain = email.split("@")[1]
				if domain == 'student.monash.edu':
					modifyDetails = True

				if users.is_current_user_admin(): #Checks with google app if current user is a admin. Not this doesn't check if they are a club account or not.
					loginMessage = 'Welcome %s, you have been granted admin rights' % user.nickname()
					
					addNewPerson = True
					addMSACard = True
					addClub = True
					addMemberToClub = True
					viewClubs = True
					viewClubMembers = True
					viewClubPermissions = True
					addClubPersonnel = True
					deleteClubPersonnel = True
					addEvent = True
					addPeopleToEvents = True
					viewAllEvents = True
					viewEventAttendees = True	
					clubEmail = True
					deleteFromClub = True
					deletePersonFromSystem = True
					checkMemberStatus = True
					changeID = True
					secretaryRights = True
					adminRights = True
					
					viewMembershipTotals = True
					deleteClub = True

					
					
				else: #Logged in, but not a admin. Determine if can do anything before granting any rights.
					#Have to determine if they have proper rights
					match = False
					memberOf = db.GqlQuery("SELECT * "
								"FROM userPermissions "
								"WHERE email = :1", user.email().lower())	
					
					currentPermissionLevel = 0
					
					for userPermissions in memberOf:
						if userPermissions.permissionLevel > currentPermissionLevel:
							currentPermissionLevel = userPermissions.permissionLevel
					
					if currentPermissionLevel == 1:
						loginMessage = 'Welcome %s, you have been granted standard rights, limited to your club(s).' % user.nickname()

						addNewPerson = True
						addMSACard = False
						addClub = False
						addMemberToClub = True
						viewClubs = True
						viewClubMembers = False
						viewClubPermissions = False
						addClubPersonnel = False
						deleteClubPersonnel = False
						addEvent = False
						addPeopleToEvents = True
						viewAllEvents = False
						viewEventAttendees = False
					elif currentPermissionLevel == 2:
						addNewPerson = True
						addMSACard = False
						addClub = False
						addMemberToClub = True
						viewClubs = True
						viewClubMembers = True
						viewClubPermissions = True
						addClubPersonnel = True
						deleteClubPersonnel = True
						addEvent = True
						checkMemberStatus = True
						addPeopleToEvents = True
						viewAllEvents = False
						viewEventAttendees = True	
						secretaryRights = True
						clubEmail = True
						deleteFromClub = True
						deletePersonFromSystem = False
						viewMembershipTotals = True
			else:
				loginMessage = 'You do not appear to be logged in. <a href="%s">Click here to login.</a> You do not have to be logged in to perform some actions.' % users.create_login_url(self.request.uri)
	
			template_values = {
				'loginMessage'			: loginMessage,
				'logoutMessage'			: logoutMessage,
				'addNewPerson'			: addNewPerson,
				'addMSACard'			: addMSACard,
				'addClub'				: addClub,
				'addMemberToClub'		: addMemberToClub,
				'viewClubPermissions'	: viewClubPermissions,
				'viewClubs'				: viewClubs,
				'viewClubMembers'		: viewClubMembers,
				'addPersonnelToClub'	: addClubPersonnel,		
				'deleteClubPersonnel'	: deleteClubPersonnel,
				'addEvent'				: addEvent,
				'addPeopleToEvents'		: addPeopleToEvents,
				'viewAllEvents'			: viewAllEvents,
				'viewEventAttendees'	: viewEventAttendees,
				'adminRights'			: adminRights,
				'secretaryRights'   	: secretaryRights,
				'modifyDetails'			: modifyDetails,
				'deleteFromClub'		: deleteFromClub,
				'deletePersonFromSystem': deletePersonFromSystem,
				'viewClubEmails'		: clubEmail,
				'checkMemberStatus'		: checkMemberStatus,
				'viewMemberCount'		: viewMembershipTotals,
				'deleteClub'			: deleteClub,
				'changeStudentID'		: changeID,
				'changeStudentID_Submit': changeID_Submit
			}
			
			path = os.path.join(os.path.dirname(__file__), 'index.html')
			self.response.out.write(template.render(path, template_values))		

class viewClubs(webapp2.RequestHandler):
	def get(self):
		masterString = ''	

		clubs = db.GqlQuery("SELECT * "
                            "FROM Club "
                            )
		
		for Club in clubs:
			masterString = Club.name + '<br>' +  masterString
		
		template_values = {
				'clubs': masterString
		}
			
		path = os.path.join(os.path.dirname(__file__), 'viewClubs.html')
		self.response.out.write(template.render(path, template_values))		

class modifyDetails(webapp2.RequestHandler):
	def get(self):
		user = users.get_current_user()
		
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
		elif error == '6':
			error = 'Error with student ID'
			
		template_values = {
			'error': error
		}
		
		if user:
			email = user.email().lower()
			domain = email.split("@")[1]
			if domain == 'student.monash.edu':
				authcate = email.split("@")[0]
				
				persons = db.GqlQuery("SELECT * "
					"FROM Person "
					"WHERE authcate = :1",
					authcate.lower())
				
				person = persons.get()
				
				if person:
				
					claytonselected = False
					caulfieldselected = False
					peninsulaselected = False
					gippslandselected = False
					berwickselected = False
					indiaselected = False
					africaselected = False
					italyselected = False
					sunwayselected = False
					africaselected = False
					chinaselected = False
				
					if person.campus == 1:
						claytonselected = False
					elif person.campus == 2:
						caulfieldselected = False
					elif person.campus == 3:					
						peninsulaselected = False
					elif person.campus == 4:					
						gippslandselected = False
					elif person.campus == 5:					
						berwickselected = False
					elif person.campus == 6:					
						indiaselected = False
					elif person.campus == 7:					
						africaselected = False
					elif person.campus == 8:					
						italyselected = False
					elif person.campus == 9:					
						africaselected = False
					elif person.campus == 10:					
						chinaselected = False
					
					template_values = {
						'firstname' 		: 	person.firstName,
						'lastname'			:	person.lastName,
						'authcate'			:	person.authcate,
						'studentid'			:	person.studentID,
						'email'				:	person.email,
						'address'			:	person.address,
						'phoneNumber'		:	person.phoneNumber,
						'claytonselected' 	:	claytonselected,
						'caulfieldselected' :	caulfieldselected,
						'peninsulaselected' :	peninsulaselected,
						'gippslandselected' :	gippslandselected,
						'berwickselected' 	:	berwickselected,
						'indiaselected' 	:	indiaselected,
						'africaselected' 	:	africaselected,
						'italyselected' 	:	italyselected,
						'sunwayselected' 	:	sunwayselected,
						'africaselected' 	:	africaselected,
						'chinaselected' 	:	chinaselected,
						
						'error': error

					}
					
					
					

					
				else:
					self.redirect('/')
				
			else:
				self.redirect('/')
		else:
			self.redirect('/')
			
		path = os.path.join(os.path.dirname(__file__), 'modifyDetails.html')
		self.response.out.write(template.render(path, template_values))		
	
class modifyDetails_Submit(webapp2.RequestHandler):
	def post(self):

		firstName = self.request.get('firstname')
		lastName = self.request.get('lastname')
		authcate = self.request.get('authcate')
		email = self.request.get('email')
		phoneNumber = self.request.get('phonenumber')
		campus = self.request.get('campus')
		address = self.request.get('address')
		termsAndConditions = self.request.get('TermsAndConditions')

		error = ''
		
		persons = db.GqlQuery("SELECT * "
										"FROM Person "
										"WHERE authcate = :1 LIMIT 1",
										 authcate)
		person = persons.get()
		
		
		if firstName:
			person.firstName = firstName
		else:
			error = '1'
			
		if lastName:
			person.lastName = lastName
		else:
			error = '1'
			
		if campus:
			person.campus = int(campus)
		else:
			error = '1'
			
		if address:
			person.address = address
		else:
			person.address = ''
			
		if email:
			if re.match(r"[^@]+@[^@]+\.[^@]+", email):
				person.email = email.lower()
			else:
				error = '3'
		else:
			error = '1'
			
		if phoneNumber:
			person.phoneNumber = phoneNumber
		
		
		
		if error == '':
			error = "0"
			person.put();	
	
	
		self.redirect('/modifyDetails?error=%s' % error)	
	
class viewClubMembers(webapp2.RequestHandler):
	def post(self):
	
		masterString = ''	
		clubKey = self.request.get('clubinput')
		if clubKey:
			clubKey = int(clubKey)
		else:
			self.redirect('/')
		year = self.request.get('year')
		if year:
			year = int(self.request.get('year'))
			
			now = datetime.now()
			currentYear = now.year
			currentDay = now.day
			currentMonth = now.month
			if currentYear > year:
				if (currentDay < 21 and currentMonth <= 3 and currentYear == year + 1) == False:
					if users.is_current_user_admin() == False:
						self.redirect('/selectClubToView')
		else:
			now = datetime.now()
			year = now.year
		#Searchs for the club (for name/existance)
		
		public = self.request.get('public')
		
		
		nameOfClub = ''
		
		if clubKey == 0:
			if users.is_current_user_admin() == True:
				nameOfClub = 'MSA Cards'
			else:
				self.redirect('/')
		else:
			
			permissionLevel = securityManager.getLevelOfAuthenticationForUserForClub(clubKey)
			
			if permissionLevel != 2:
				self.redirect('/')
			
			club = db.get(club_key(str(clubKey)))

			if club:
				nameOfClub = club.name

		template_values = {
		}
		
		if nameOfClub:
			if public:
				masterString = '<table border="1"><th>Full Name</th><th>Student ID</th>'	
			else:
				masterString = '<table border="1" width = "1200"><th>Full Name</th><th width="70">Student ID</th><th width = "60">MSA Member</th><th width = "60">Clayton Student</th><th>Address</th><th = "50">Phone Number</th><th = "150">Monash Email</th><th = "150">Email</th><th width = "70">Signup Date</th>'	
			
			resultsArray = self.resultsForClubKeyAndYear(clubKey, year, 0, public)
			
			
			masterString = masterString + resultsArray[0]

			masterString = masterString + '</table>'
			
			masterString = masterString + '<br>Number Of Members:' + str(resultsArray[1]) + '<br>Number Of Clayton Members:' + str(resultsArray[2]) + '<br>Number Of MSA Members:' + str(resultsArray[3])

			
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
		
	def resultsForClubKeyAndYear(sender,clubKey, year, offset, public):
		masterString = ''
		#clubMemberships = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE clubKey = :1 AND year = :2 OFFSET :3",
		#								int(clubKey),year, int(offset))
		clubMemberships = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE clubKey = :1 AND year = :2",
										int(clubKey),year)
		memberCount = 0
		claytonMemberCount = 0
		MSAMemberCount = 0
		
		for membership in clubMemberships:
			person = db.get(person_key(membership.studentID))
			if person:
				memberCount = memberCount + 1
				name = person.firstName + ' ' + person.lastName
				studentID = str(person.studentID)
				address = person.address
				if address is None:
					address = 'N/A'
				phoneNumber = 'N/A'
				if person.phoneNumber:
					phoneNumber = person.phoneNumber
					
				monashEmail = person.authcate
				if monashEmail is None:
					monashEmail = 'N/A'
				else:
					if person.personType == 1:
						monashEmail = monashEmail + '@student.monash.edu'
					elif person.personType == 2:
						monashEmail = monashEmail + '@monash.edu'
					elif person.personType == 3:
						monashEmail = 'N/A'
				email = person.email

				if email:
					email = email.lower()
				else:
					email = 'N/A'
				
				before = ESTTime()
				after = MelbourneTime()

				signupDate = membership.joiningDate
				signupDate = signupDate.replace(tzinfo=before)
				signupDate = signupDate.astimezone(after)
				
				signupDateTimezoneAgnostic = membership.joiningDate
				
				day = signupDate.strftime('%m/%d/%Y')
				
				MSACardHolderAtSignup = 'N'
				MSACardHolderAtEndOfThatYear = 'N'
				memberType = membership.memberType
				
				campus = person.campus
				claytonStudent = 'N'
				if campus == 1:
					claytonStudent = 'Y'
					claytonMemberCount = claytonMemberCount + 1
				
				
				if memberType:
					memberType = int(membership.memberType)
					
					if memberType == 0:
						memberType = 'Ordinary'
					else:
						memberType = 'Associate'
				else:
					memberType = 'Ordinary'
				
				msaMemberships = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE clubKey = 0 AND year = :1 AND studentID = :2",year, int(studentID))
				for memberships in msaMemberships:
					MSACardHolderAtEndOfThatYear = 'Y'
					MSAMemberCount = MSAMemberCount + 1
					if memberships.joiningDate < signupDateTimezoneAgnostic:
						MSACardHolderAtSignup = 'Y'
				if public:
					masterString = masterString + '<tr><td>' + name + '</td><td>' + str(studentID)[5:8] + '</td>'
				else:		
					masterString = masterString + '<tr><td>' + name + '</td><td>' + str(studentID) + '</td><td>' + MSACardHolderAtEndOfThatYear + '</td><td>' + claytonStudent + '</td><td>' + address + '</td><td>' + str(phoneNumber) + '</td><td>' + monashEmail + '</td><td>' + email + '</td><td>' + str(day) + '</td></tr>'

		if memberCount == 1000:
			logging.info('Member List Rollover')
			resultArray = resultsForClubKeyAndYear(clubKey, year, offset + 1000, public)
			masterstring = masterString + resultArray[0] 
			memberCount = memberCount + resultArray[1]
			claytonMemberCount = claytonMemberCount + resultArray[2]
			MSAMemberCount = MSAMemberCount + resultArray[3]
		return [masterString, memberCount, claytonMemberCount, MSAMemberCount]
	
class MelbourneTime(tzinfo):
  def utcoffset(self, dt):
    return timedelta(hours=11)

  def tzname(self, dt):
    return "Melbourne"

  def dst(self,dt):
    return timedelta(hours=0)	
	
class ESTTime(tzinfo):
  def utcoffset(self, dt):
    return timedelta(hours=-5)

  def tzname(self, dt):
    return "EST"

  def dst(self,dt):
    return timedelta(hours=0)		
class selectClubEmails(webapp2.RequestHandler):

    def get(self):
			clubsMasterString = ''
			if users.is_current_user_admin():
				clubsMasterString = '<option value="' + '0' + '">' + 'MSA Card Holders' + '</option>'

			clubs = securityManager.getClubsUserIsAdminOf()

			for Club in clubs:
				clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'

			if clubsMasterString == '':
				self.redirect('/')

			template_values = {
				'clubs': clubsMasterString
			}

			path = os.path.join(os.path.dirname(__file__), 'clubEmailSelector.html')
			self.response.out.write(template.render(path, template_values))			

	
class clubEmails(webapp2.RequestHandler):
	def post(self):
	
		masterString = ''	
		clubKey = self.request.get('clubinput')
		if clubKey:
			clubKey = int(clubKey)
		else:
			self.redirect('/')
		year = self.request.get('year')
		if year:
			year = int(self.request.get('year'))
		else:
			now = datetime.now()
			year = now.year
		#Searchs for the club (for name/existance)
		
		public = self.request.get('public')
		
		
		nameOfClub = ''
		
		if clubKey == 0:
			if users.is_current_user_admin() == True:
				nameOfClub = 'MSA Cards'
			else:
				self.redirect('/')
		else:
			
			permissionLevel = securityManager.getLevelOfAuthenticationForUserForClub(clubKey)
			
			if permissionLevel != 2:
				self.redirect('/')
			results = self.resultsForEmail(clubKey, year, 0)
			
			self.response.out.write(results.format('<br><br>Users Emails<br><br>'))

	def resultsForEmail(sender,clubKey, year, offset):
		monashEmails = ''
		userEmails = ''
		#clubMemberships = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE clubKey = :1 AND year = :2 OFFSET :3",
		#								int(clubKey),year, int(offset))
		clubMemberships = db.GqlQuery("SELECT studentID FROM PersonClubStatus WHERE clubKey = :1 AND year = :2",
										int(clubKey),year)
		membercount = 0
		for membership in clubMemberships:
			person = db.get(person_key(membership.studentID))
			logging.info('found a person!')

			if person:
				membercount = membercount + 1
				logging.info('found a email!')
				email = person.email
				if email:
					email = email.lower()
					userEmails = userEmails + '<br>' + email
					
				monashEmail = person.authcate
				if monashEmail:
					monashEmail.strip()
					if person.personType == 1:
						monashEmail = monashEmail + '@student.monash.edu'
						monashEmails = monashEmails + '<br>' + monashEmail

					elif person.personType == 2:
						monashEmail = monashEmail + '@monash.edu'
						monashEmails = monashEmails + '<br>' + monashEmail
					
		masterstring = monashEmails + '{!s}' + userEmails	 		
					
		if membercount == 1000:
			masterstring = masterstring.format(resultsForEmail(clubKey, year, offset + 1000))

		return masterstring

		
class selectClubToView(webapp2.RequestHandler):

    def get(self):
			clubsMasterString = ''
			if users.is_current_user_admin():
				clubsMasterString = '<option value="' + '0' + '">' + 'MSA Card Holders' + '</option>'
			
			clubs = securityManager.getClubsUserIsAdminOf()
		
			for Club in clubs:
				clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'
		
			if clubsMasterString == '':
				self.redirect('/')
		
			template_values = {
				'clubs': clubsMasterString
			}
			
			path = os.path.join(os.path.dirname(__file__), 'clubMemberSelector.html')
			self.response.out.write(template.render(path, template_values))			

			
class selectClubPermissionsToView(webapp2.RequestHandler):

    def get(self):
			clubsMasterString = ''
			
			clubs = securityManager.getClubsUserIsAdminOf()

			for Club in clubs:
				clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'
		
			if clubsMasterString == '':
				self.redirect('/')
		
			template_values = {
				'clubs': clubsMasterString
			}
			
			path = os.path.join(os.path.dirname(__file__), 'clubPermissionSelector.html')
			self.response.out.write(template.render(path, template_values))			

class selectClubPermissionsToView_Submit(webapp2.RequestHandler):
	def post(self):
	
		masterString = ''	
		clubKey = self.request.get('clubinput')
		if clubKey:
			try:
				clubKey = int(clubKey)
			except:
				self.redirect('/')
		else:

			self.redirect('/')
			
		#Searchs for the club (for name/existance)
		
		nameOfClub = ''

		clubs = securityManager.getClubsUserIsAdminOf()
		
		for club in clubs:
			if club.primaryKey == clubKey:
				nameOfClub = club.name
		
		if nameOfClub == '':
			self.redirect('/')
		
		template_values = {
		}
		
		if nameOfClub:
		
			memberOf = db.GqlQuery("SELECT * "
								"FROM userPermissions "
								"WHERE clubKey = :1",
								 clubKey)

			for permissions in memberOf:
				if permissions.permissionLevel == 2:
					masterString = masterString + permissions.email + '<br>Admin<br>' + permissions.name + '<br>'
				elif permissions.permissionLevel == 1:
					masterString = masterString + permissions.email + '<br>Personnel<br>' + permissions.name + '<br><br>'
				else:
					masterString = masterString + permissions.email + '<br>Unknown<br>' + permissions.name + '<br><br>'
			template_values = {
				'nameOfClub': nameOfClub,
				'table'		: masterString
			}
		else:
			template_values = {
				'nameOfClub': 'Error',
				'table'		: 'Club not found'
			}

		path = os.path.join(os.path.dirname(__file__), 'viewClubPermissions.html')
		self.response.out.write(template.render(path, template_values))	
	def get(self):
		self.post()			

class addPersonnelToClub(webapp2.RequestHandler):

    def get(self):
	
		clubs = []
		
		clubsMasterString = ''
		
		clubs = securityManager.getClubsUserIsAdminOf()
		
		for Club in clubs:
				clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'				
		
		if clubsMasterString == '':
			self.redirect('/')
		
		error = self.request.get('error')
		if error == '0':
			error = 'Success!'
		elif error == '1':
			error = 'Looks like you missed something'
		elif error == '2':
			error = 'Student ID needs to be a number'
		elif error == '3':
			error = 'Student ID match not found'
		elif error == '4':
			error = 'Unknown - 4'
		elif error == '5':
			error = 'Permission not found'
		elif error == '6':
			error = 'Match not found'

	
			
		template_values = {
			'error': error,
			'clubs': clubsMasterString
		}
		
		
		path = os.path.join(os.path.dirname(__file__), 'addPersonnel.html')
		self.response.out.write(template.render(path, template_values))			
	
class addPersonnelToClub_Submit(webapp2.RequestHandler):
  def post(self):

	error = ''
		
	clubPrimaryKey = self.request.get('clubinput')
	email = self.request.get('email')
	name = self.request.get('name')
	
	if name is None:
		error = '1'
	else:	
		if clubPrimaryKey:
			clubPrimaryKey = int(self.request.get('clubinput'))
			if securityManager.getLevelOfAuthenticationForUserForClub(clubPrimaryKey) == 2:
				if email:
					email = email.lower() + '@student.monash.edu'
					
					newUserPermissions = userPermissions(key=userPermissions_key(email,clubPrimaryKey))
					newUserPermissions.permissionLevel = 1
					newUserPermissions.clubKey = clubPrimaryKey
					newUserPermissions.name = name
					
				
					newUserPermissions.email = email.lower()
				
				#Check if it already exists.
				
					userPermission = db.get(userPermissions_key(email, clubPrimaryKey))
			
					if userPermission:
						error = '6'
					else:
						newUserPermissions.put()
					
						memcache.delete_multi([email + '1', email + '2'])
					
					
						error = '0'

				else:
					error = '3'
			else:
				error = '5'
		else:
			error = '2'

		
		
	
	self.redirect('/addPersonnelToClub?error=%s' % error)

class deletePersonnelFromClub(webapp2.RequestHandler):

    def get(self):
	
		clubs = []
		
		clubsMasterString = ''
		
		clubs = securityManager.getClubsUserIsAdminOf()

		for Club in clubs:
			clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'				

		if clubsMasterString == '':
			self.redirect('/')
		
		error = self.request.get('error')
		if error == '0':
			error = 'Success!'
		elif error == '1':
			error = 'Looks like you missed something'
		elif error == '2':
			error = 'Student ID needs to be a number'
		elif error == '3':
			error = 'Student ID match not found'
		elif error == '4':
			error = 'Unknown - 4'
		elif error == '5':
			error = 'Permission not found'
		elif error == '6':
			error = 'Personnel not found'

	
			
		template_values = {
			'error': error,
			'clubs': clubsMasterString
		}
		
		
		path = os.path.join(os.path.dirname(__file__), 'removePersonnel.html')
		self.response.out.write(template.render(path, template_values))			
	
class deletePersonnelFromClub_Submit(webapp2.RequestHandler):
  def post(self):

	error = ''
		
	clubPrimaryKey = self.request.get('clubinput')
	email = self.request.get('email')
		
	if clubPrimaryKey:
		clubPrimaryKey = int(self.request.get('clubinput'))
		if securityManager.getLevelOfAuthenticationForUserForClub(clubPrimaryKey) == 2:
			if email:
				
				email = email + '@student.monash.edu'
				
				email = email.lower()
				
			#Check if it already exists.
				
				userPermission = db.GqlQuery("SELECT * "
								"FROM userPermissions "
								"WHERE email = :1 AND clubKey = :2",
								email, clubPrimaryKey)
				match = False
				for permissions in userPermission:
					permissions.delete()
					memcache.delete_multi([email + '1', email + '2'])
					
					match = True
					
				if match == False:	
					error = '6'

			else:
				error = '3'
		else:
			error = '5'
	else:
		error = '2'

		
		
	
	self.redirect('/deletePersonnelFromClub?error=%s' % error)

class deleteClub(webapp2.RequestHandler):
	def get(self):
			if users.is_current_user_admin() == False:
				self.redirect('/')
			
			error = self.request.get('error')
			if error == '0':
				error = 'Success!'
			elif error == '1':
				error = 'Club Missing'
			
			clubsMasterString = ''
			
			clubs = securityManager.getClubsUserIsAdminOf()

		
			for Club in clubs:
				clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'
		
			if clubsMasterString == '':
				self.redirect('/')
				
			template_values = {
				'error': error,
				'clubs': clubsMasterString
			}

			path = os.path.join(os.path.dirname(__file__), 'deleteClubSelector.html')
			self.response.out.write(template.render(path, template_values))	
class deleteClub_Submit(webapp2.RequestHandler):
	def post(self):
		error = ''
		if users.is_current_user_admin() == False:
			self.redirect('/')
		
		clubPrimaryKey = self.request.get('clubinput')
		#First you delete the club.
		
		club = db.get(club_key(str(clubPrimaryKey)))
		if club:
		
			count = 1000
			while (count == 1000):
				count = self.deleteClubMemberships(clubPrimaryKey)
			
		
			club.delete()
			
			#Then you delete the events
			
			clubEvents = db.GqlQuery("SELECT * "
									"FROM Event "
									"WHERE clubKey = :1",
									int(clubPrimaryKey))
									
			for event in clubEvents:
				logging.info('Deleting event')
				event.delete()
				eventMemberships = db.GqlQuery("SELECT * "
									"FROM PersonEventStatus "
									"WHERE eventKey = :1",
									event.primaryKey)
				for memberships in eventMemberships:
					memberships.delete()
				
			#Then you delete the membership records

			counters = db.GqlQuery("SELECT * FROM ClubCounter WHERE clubKey = :1", int(clubPrimaryKey))
			for counter in counters:
				counter.delete()
			
			permissions = db.GqlQuery("SELECT * FROM userPermissions WHERE clubKey = :1", int(clubPrimaryKey))
			for permission in permissions:
				permission.delete()

			
			error = '0'
			
			
			
		else:
			error = '1'

			
		self.redirect('/deleteClub?error=%s' % error)

	def deleteClubMemberships(sender,clubPrimaryKey):	
		clubStatus = db.GqlQuery("SELECT * "
								"FROM PersonClubStatus "
								"WHERE clubKey = :1",
								int(clubPrimaryKey))		
		count = 0
		for membership in clubStatus:
			membership.delete()
			count = count + 1
			
		return count
		

class addEvent(webapp2.RequestHandler):
	def get(self):

		error = self.request.get('error')
		if error == '0':
			error = 'Success!'
		elif error == '1':
			error = 'Looks like you missed something'
		
		clubsMasterString = ''
		
		clubs = securityManager.getClubsUserIsAdminOf()

	
		for Club in clubs:
			clubsMasterString = clubsMasterString + '<option value="' + str(Club.primaryKey) + '">' + Club.name + '</option>'
	
		if clubsMasterString == '':
			self.redirect('/')
			
		template_values = {
			'error': error,
			'clubs': clubsMasterString
		}

		path = os.path.join(os.path.dirname(__file__), 'addEvent.html')
		self.response.out.write(template.render(path, template_values))	
		
class addEvent_Submit(webapp2.RequestHandler):
  def post(self):

	eventName = self.request.get('eventname')
	date = self.request.get('date')
	location = self.request.get('location')

	clubPrimaryKey = self.request.get('clubinput')

	newEvent = Event(parent=event_key('defaultkey'))
	
	error = '';
	
	highestNumber = 0
		
	events = db.GqlQuery("SELECT * "
						"FROM Event "
						" ORDER BY primaryKey DESC"
						)
	
	for event in events:
		if highestNumber < event.primaryKey:
			highestNumber = event.primaryKey
	
	highestNumber = highestNumber + 1
	
	newEvent = Event(key=event_key(highestNumber))

	
	newEvent.primaryKey = highestNumber
	
	
	
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
	
	
	
	clubs = securityManager.getClubsUserIsAdminOf()
							
	intClubPrimaryKey = int(clubPrimaryKey)
	newEvent.clubName = ''
	for Club in clubs:
		if Club.primaryKey == intClubPrimaryKey:
			newEvent.clubName = Club.name

	if newEvent.clubName == '':
		error = '5'
	newEvent.clubKey = int(clubPrimaryKey)

	
	if error == '':
		error = "0"
		
		
		
		newEvent.put();
		
	self.redirect('/addEvent?error=%s' % error)	

class viewEvents(webapp2.RequestHandler):
	def get(self):
	
		if users.is_current_user_admin() == False:
			self.redirect('/')
			
		masterString = ''	

		events = db.GqlQuery("SELECT * "
                            "FROM Event "
                            )
		
		for event in events:
			eventline = ''
			if event.name:
				eventline = event.name
				
			if event.location:
				eventline = eventline + ' - ' + event.location
				
			if event.clubName:
				eventline = eventline + ' - ' + event.clubName
				
			if event.date:
				eventline = eventline + ' - ' + event.date
				
			masterString = eventline  + '<br><br>' + masterString	

		
		template_values = {
				'events': masterString
		}
			
		path = os.path.join(os.path.dirname(__file__), 'viewEvents.html')
		self.response.out.write(template.render(path, template_values))	
	
	
class addMembersToEvent(webapp2.RequestHandler):

    def get(self):
			error = self.request.get('error')
			if error == '0':
				name = self.request.get('name')
				if name:
					error = 'Success:' + name
				else:
					error = 'Success!'
			elif error == '1':
				error = 'Looks like you missed something'
			elif error == '2':
				error = 'Student ID needs to be a number'
			elif error == '3':
				error = 'Student ID match not found. If they have not registered,<a href="/register">click here to register.</a>'
			elif error == '4':
				error = 'Student already in event'
				
			eventsMasterString = ''
			
			events = db.GqlQuery("SELECT * "
                            "FROM Event "
                            )
			
			clubs = securityManager.getClubsUserIsPersonnelOf()
			
			
			for event in events:
				for club in clubs:
					if event.clubKey == club.primaryKey:
						eventline = ''
			
						if event.name:
							eventline = event.name
						
						if event.date:
							eventline = eventline + ' - ' + event.date
						
						if event.clubName:
							eventline = eventline + ' - ' + event.clubName			
					
						eventsMasterString = eventsMasterString + '<option value="' + str(event.primaryKey) + '">' + eventline +'</option>'
			
			if eventsMasterString == '':
				self.redirect('/')
			
			template_values = {
				'error': error,
				'events': eventsMasterString
			}
			
			
			path = os.path.join(os.path.dirname(__file__), 'addToEvent.html')
			self.response.out.write(template.render(path, template_values))			
	
class addMembersToEvent_Submit(webapp2.RequestHandler):
  def post(self):
	error = ''
	try:
		studentID = self.request.get('studentid')
		studentID = securityManager.trimStudentID(studentID)
	except:
		error = '2'
	if error == '':
		try:
			if studentID:
				person = db.get(person_key(studentID))
				
				if person:
					msaCardStatus = self.request.get('msacardstatus')
					if msaCardStatus == 'YES':
						securityManager.addMSACardToStudent(studentID)
					
				else:
					error = '3'

				

			else:
				error = '1'
		except:
			error = '4'
	
	if error == '':
		eventKey = self.request.get('eventinput')
		eventKey = int(eventKey)
		
		clubs = securityManager.getClubsUserIsPersonnelOf()
		
		event = db.get(event_key(eventKey))	
		clubs = securityManager.getClubsUserIsPersonnelOf()
			
		match = False
		
		for club in clubs:
			if event.clubKey == club.primaryKey:
				match = True
		
		if match == False:
			self.redirect('/')
			
		eventStatus = db.GqlQuery("SELECT * "
                            "FROM PersonEventStatus "
                            "WHERE eventKey = :1 AND studentID = :2 LIMIT 1", eventKey, studentID)
			
		for status in eventStatus:	
			error = '4'
			
		if error == '':	
			personEventStatus = PersonEventStatus(key=personEventStatus_key(studentID,eventKey))
			
			personEventStatus.studentID = studentID
			personEventStatus.eventKey = eventKey
			
			
			
			user = users.get_current_user()
			email = user.email().lower()
			addedByAuthcate = email.split("@")[0]
			
			personEventStatus.addedBy = addedByAuthcate
			personEventStatus.put();

			error = '0'
		

	self.redirect('/addMembersToEvent?error=%s' % error)	
	
class viewEventMembers(webapp2.RequestHandler):
	def post(self):

		masterString = ''	
		eventKey = int(self.request.get('eventinput'))

		match = False
		
		event = db.get(event_key(eventKey))
		
		clubKey = -0
		
		clubKey = event.clubKey
		eventName = event.name
		eventDate = event.date
		eventLocation = event.location
							
		clubs = securityManager.getClubsUserIsAdminOf()
		match = False
		for club in clubs:
			if club.primaryKey == clubKey:
				match = True
				clubName = club.name
		
		if match == False:
			self.redirect('/')
		#Searchs for the club (for name/existance)
		
		eventMemberships = db.GqlQuery("SELECT * FROM PersonEventStatus WHERE eventKey = :1",
											int(eventKey))
		
		masterString = '<table border="1"><th>Full Name</th><th>Club Member</th><th>Clayton Student</th><th>Student ID Number</th><th>MSA Card Holder</th><th>Phone Number</th><th>Signin Time</th>'	
		template_values = {
		
		}	
		
		numberOfAttendees = 0
		numberOfClubMembers = 0
		numberOfClaytonStudents = 0
		numberOfMSACardHolders = 0
		
		for membership in eventMemberships:
			person = db.get(person_key(membership.studentID))

			if person:
				name = ''
				claytonStudent = ''
				studentID = ''
				phoneNumber = ''
				
				numberOfAttendees = numberOfAttendees + 1
				
				if person.firstName:
					name = person.firstName
				
				if person.lastName:
					name = name + ' ' + person.lastName
				
				if person.studentID:
					studentID = str(person.studentID)
				
				if person.phoneNumber:
					phoneNumber = str(person.phoneNumber)
				
				if person.campus == 1:
					claytonStudent = 'Y'
					numberOfClaytonStudents = numberOfClaytonStudents + 1
				else:
					claytonStudent = 'N'
				
				MSACardStatus = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE studentID = :1 AND clubKey = 0 AND year = :2", membership.studentID,membership.creationDate.year)
				logging.info(membership.studentID)
				logging.info(str(membership.creationDate.year))

				MSACardHolder = 'N'
				
				for status in MSACardStatus:
					MSACardHolder = 'Y'
					numberOfMSACardHolders = numberOfMSACardHolders + 1
					
				ClubStatus = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE studentID = :1 AND clubKey = :2 AND year = :3", membership.studentID, clubKey,membership.creationDate.year)
				clubMember = 'N'
				
				for status in ClubStatus:
					clubMember = 'Y'	
					numberOfClubMembers = numberOfClubMembers + 1
				signinTime = str(membership.creationDate.hour) + ':' + str(membership.creationDate.minute) + ' ' + str(membership.creationDate.day) + '/' + str(membership.creationDate.month) + '/' + str(membership.creationDate.year)
				
				masterString = masterString + '<tr><td>' + name + '</td><td>' + clubMember +'</td><td>' + claytonStudent + '</td><td>' + studentID + '</td><td>' + MSACardHolder + '</td><td>' + phoneNumber + '</td><td>' + signinTime + '</td></tr>'
	
	
		masterString = masterString + '</table>'
			
		
			
		template_values = {
			'nameOfEvent'				: eventName,
			'table'						: masterString,
			'eventDate'					: eventDate,
			'eventLocation' 			: eventLocation,
			'clubName'					: clubName,
			'numberOfAttendees'			: numberOfAttendees,
			'numberOfClubMembers'		: numberOfClubMembers,
			'numberOfClaytonStudents'	: numberOfClaytonStudents,
			'numberOfMSACardHolders'	: numberOfMSACardHolders
		}

		path = os.path.join(os.path.dirname(__file__), 'viewEventAttendees.html')
		self.response.out.write(template.render(path, template_values))	
	def get(self):
		self.response.out.write('Error, attempted to get. Go back and try again.')

class selectEventToView(webapp2.RequestHandler):

    def get(self):
			eventsMasterString = ''
			
			clubs = securityManager.getClubsUserIsAdminOf()
			
			for club in clubs:
				events = db.GqlQuery("SELECT * "
								"FROM Event "
								"WHERE clubKey = :1", club.primaryKey)
				
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
			
class explanation(webapp2.RequestHandler):

    def get(self):
		template_values = {
		}
			
		path = os.path.join(os.path.dirname(__file__), 'explanation.html')
		self.response.out.write(template.render(path, template_values))				
			

class changeID(webapp2.RequestHandler):

    def get(self):
			error = self.request.get('error')
			if error == '0':
				error = 'Success!'
			elif error == '1':
				error = 'Looks like you missed something'
			elif error == '2':
				error = 'Student ID needs to be a number'
			elif error == '3':
				error = 'Student ID match not found.'
			elif error == '4':
				error = 'Student ID already found.'
			template_values = {
				'error': error,
			}
			
			path = os.path.join(os.path.dirname(__file__), 'changeStudentID.html')
			self.response.out.write(template.render(path, template_values))			
	
class changeID_Submit(webapp2.RequestHandler):
  def post(self):
	error = ''
	try:
		oldStudentID = self.request.get('old_student_id')
		oldStudentID = securityManager.trimStudentID(oldStudentID)
		newStudentID = self.request.get('new_student_id')
		newStudentID = securityManager.trimStudentID(newStudentID)

	except Exception, error:
		error = '2'
	if error == '':
		try:
			if oldStudentID:
				person = db.get(person_key(oldStudentID))
				
				if person is None:
					error = '3'
			else:
				error = '1'
				
			if newStudentID:
				person = db.get(person_key(newStudentID))
				
				if person is not None:
					error = '4'
			else:
				error = '1'				
				
		except:
			error = '4'
	
	person = db.get(person_key(oldStudentID))
	personName = ''
	
	if error == '':
		if person is not None:
			person.studentID = newStudentID
			
			clubMemberships = db.GqlQuery("SELECT * "
									"FROM PersonClubStatus "
									"WHERE studentID = :1", oldStudentID)
									
			for membership in clubMemberships:
				membership.studentID = newStudentID
				membership.put()
				
			eventStatuses = db.GqlQuery("SELECT * "
									"FROM PersonEventStatus "
									"WHERE studentID = :1", oldStudentID)
									
			for eventStatus in eventStatuses:
				eventStatus.studentID = newStudentID
				eventStatus.put()	
			
			newPerson = Person(key=person_key(newStudentID))
			newPerson.studentID = newStudentID

			newPerson.firstName = person.firstName
			newPerson.lastName = person.lastName
			newPerson.authcate = person.authcate
			newPerson.email = person.email
			newPerson.address= person.address
			newPerson.campus = person.campus
			newPerson.phoneNumber = person.phoneNumber
			newPerson.personType = person.personType
			
			person.delete()

			newPerson.put()
			
			
			
			
			personName = person.firstName + ' ' +person.lastName 
		else:
			error = '3'
	if error == '':
		error = '0'
	if personName != '':
		self.redirect(('/changeStudentID?error=%s' % error) + ('&name=%s' % personName))
	else:
		self.redirect('/changeStudentID?error=%s' % error)

class securityManager():
	@staticmethod
	def getClubsUserIsAdminOf():
		return securityManager.getClubsWhereUserHasPermissionLevelsOf(2)
		
	@staticmethod			
	def getClubsWhereUserHasPermissionLevelsOf(minimumPermissionLevel):		
		user = users.get_current_user()

		if not user:
			return [] #User not logged in, no rights.
		else:
			key = user.email().lower()+str(minimumPermissionLevel)
            
			result = memcache.get(key)
            
			if result is not None:
				return result
			else:
				if users.is_current_user_admin():
					result = securityManager.getAllClubs()
					memcache.set(key,result)
					return result
				else:	
					array = []
					
					memberOf = db.GqlQuery("SELECT * "
                                    "FROM userPermissions "
                                    "WHERE email = :1",
                                    user.email().lower())
                                    
					for userPermissions in memberOf:
						if userPermissions.permissionLevel >= minimumPermissionLevel:
							array.append(db.get(club_key(str(userPermissions.clubKey))))
    
					memcache.set(key,array)
                        
					return array

	@staticmethod
	def getLevelOfAuthenticationForUserForClub(clubPrimaryKey):
		user = users.get_current_user()
		if not user:
			return 0 #User has 0 rights.
		else:

			if users.is_current_user_admin():
				return 2 #User has same rights as club admin.
			else:
				key = user.email().lower() + '-levelOfAuthForClub:' + str(clubPrimaryKey)

				result = memcache.get(key)

				if result is not None:
					return result
				else:
                    #User is logged in, but not a admin. Search for priorites

					memberOf = db.get(userPermissions_key(user.email().lower(), clubPrimaryKey))				
									
					if memberOf:
						memcache.set(key,memberOf.permissionLevel)
						return memberOf.permissionLevel


	@staticmethod
	def getAllClubs():
		clubs = db.GqlQuery("SELECT * "
								"FROM Club")			
		return clubs
	@staticmethod			
	def getClubsUserIsPersonnelOf():
		return securityManager.getClubsWhereUserHasPermissionLevelsOf(1)
		
	@staticmethod
	def trimStudentID(studentID):
		studentID = str(studentID)
		stringLength = studentID.__len__()
		if stringLength > 7:
			studentID = int(studentID[:8])
		return studentID
	@staticmethod
	def addMSACardToStudent(studentID):
		error = ''
		
		now = datetime.now()
		year = now.year
		
		try:
			if studentID:
			
				studentID = securityManager.trimStudentID(studentID)
				person = db.get(person_key(studentID))
				if person is None:
					error = '3'					
			else:
				error = '1'
		except:
			error = '4'
			
		if error == '':
		#Check if it already exists.
				
			MSAMemberships = db.GqlQuery("SELECT * "
								"FROM PersonClubStatus "
								"WHERE studentID = :1 AND year = :2 AND clubKey = 0",
								studentID,year)
		
			for person in MSAMemberships:
				error = '4'
		
	
		if error == '':
		
			newClubStatus = PersonClubStatus(key=personClubStatus_key(studentID,year,'0'))
			
			newClubStatus.studentID = int(studentID)
			newClubStatus.year = year
			newClubStatus.clubKey = 0
			
			newClubStatus.put();
			logging.info('added MSA card')
			clubMemberships = db.GqlQuery("SELECT * "
								"FROM PersonClubStatus "
								"WHERE studentID = :1 AND year = :2",
								studentID,year)
			for membership in clubMemberships:
				logging.info('Found a club, incrementing')
				logging.info(year)
				logging.info(membership.clubKey)


				clubCounter = db.get(ClubCounter_key(membership.clubKey,year))
				if clubCounter:
					logging.info('valid')
					if clubCounter.numberOfMSAMembers:
						clubCounter.numberOfMSAMembers = clubCounter.numberOfMSAMembers + 1
					else:
						clubCounter.numberOfMSAMembers = 1
					
					clubCounter.put()

				else:
					logging.info('not found')

			
			error = '0'
			
		return error
		
app = webapp2.WSGIApplication(
                                     [('/',index),
									  ('/register', registerPerson),
									  ('/submit', registerPerson_Submit),
									  ('/addClub', addClub),
									  ('/addClubSubmit', addClub_Submit),
									  ('/addMembers', addMembers),
									  ('/addMembers_Submit', addMembers_Submit),
									  
									  ('/modifyDetails', modifyDetails),
									  ('/modifyDetails_Submit', modifyDetails_Submit),

									  ('/addMSACard', addMSACard),
									  ('/addMSACard_Submit', addMSACard_Submit),
									  
									  ('/viewClubs', viewClubs),
									  ('/clubmembers',viewClubMembers),
									  ('/selectClubToView',selectClubToView),
									  
									  ('/clubEmails',clubEmails),
									  ('/selectClubEmails',selectClubEmails),
									
									  ('/addPersonnelToClub',addPersonnelToClub),
									  ('/addPersonnelToClub_Submit',addPersonnelToClub_Submit),

									  ('/deletePersonnelFromClub',deletePersonnelFromClub),
									  ('/deletePersonnelFromClub_Submit',deletePersonnelFromClub_Submit),
									  
									  ('/checkMemberStatus',checkMemberStatus),
									  ('/checkMemberStatus_Submit',checkMemberStatus_Submit),
									  
									  ('/selectClubPermissionsToView',selectClubPermissionsToView),
									  ('/selectClubPermissionsToView_Submit',selectClubPermissionsToView_Submit),
									  
									  ('/addEvent', addEvent),
									  ('/addEventSubmit', addEvent_Submit),
									  ('/addMembersToEvent', addMembersToEvent),
									  ('/addMembersToEvent_Submit', addMembersToEvent_Submit),
									  ('/viewEvents', viewEvents),
									  ('/eventAttendees',viewEventMembers),
									  ('/selectEventToView',selectEventToView),
									  
									  ('/deleteMember',deleteMember),
									  ('/deleteMember_Submit',deleteMember_Submit),

									  ('/deleteClub',deleteClub),
									  ('/deleteClub_Submit',deleteClub_Submit),
									  
									  ('/deletePerson',deletePerson),
									  ('/deletePerson_Submit',deletePerson_Submit),
									  
									  ('/explanation', explanation),
									  ('/viewMembershipTotals',viewMembershipTotals),
									  
									('/changeStudentID', changeID),
									 ('/changeStudentID_Submit', changeID_Submit)
									  
									  ],
                                     debug=True)
#
#def main():
#    run_wsgi_app(application)

#if __name__ == "__main__":
#    main()