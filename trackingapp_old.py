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

class statsLog(db.Model):
  creationDay = db.DateTimeProperty()
  current = db.BooleanProperty()
  uniqueSignUpsThisDay = db.IntegerProperty()
  
def person_key(person_name=None):
	return db.Key.from_path('Person', person_name or 'default_person')
 
def personClubStatus_key(personClubStatus_name=None):
	return db.Key.from_path('PersonClubStatus', personClubStatus_name or 'personClubStatus')
  
def club_key(club_name=None):
	return db.Key.from_path('Club', club_name or 'club') 
  
def personEventStatus_key(personEventStatus_name=None):
	return db.Key.from_path('PersonEventStatus', personEventStatus_name or 'personEventStatus')  
  
def event_key(event_name=None):
	return db.Key.from_path('Event', event_name or 'event')  
	
def userPermissions_key(userPermissions_name=None):
	return db.Key.from_path('userPermissions', userPermissions_name or 'userPermissions')    
  
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
	address = self.request.get('address')
	person = Person(parent=person_key('defaultkey'))
	termsAndConditions = self.request.get('TermsAndConditions')
	personType = self.request.get('personType')
	personType = int(personType)

	
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
		person.authcate = authcate.lower()
	else:
		if personType != 3:
			error = '1'
			
	if error == '':
		try:		

			studentID = self.request.get('studentid')

			studentID = str(securityManager.trimStudentID(studentID))

			stringLength = studentID.__len__()
			if stringLength > 7:
				studentID = int(studentID[:8])
				if studentID:
					match = False
					persons = db.GqlQuery("SELECT * "
									"FROM Person "
									"WHERE ANCESTOR IS :1 AND studentID = :2  LIMIT 1",
									person_key('default_person'), studentID)
					for people in persons:
						error = '4'
					if personType != 3:
						persons = db.GqlQuery("SELECT * "
										"FROM Person "
										"WHERE ANCESTOR IS :1 AND authcate = :2 LIMIT 1",
										person_key('default_person'), authcate)
									
						for people in persons:
							error = '4'

					
					person.studentID = studentID
				else:
					error = '1'
				
			else:
				error = '6'
			
			
			
		except:
			error = '2'
		
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
	else:
		error = '1'
		
	if phoneNumber:
		person.phoneNumber = phoneNumber
	
	
	
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
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
		if users.is_current_user_admin() == False:
			self.redirect('/')
		
		clubName = self.request.get('clubname')
		clubEmail = self.request.get('clubgoogleaccount')
		newClub = Club(parent=club_key('defaultkey'))

		error = '';
		if clubName:
			newClub.name = clubName
		else:
			error = '1'
			
		if clubEmail:
			if re.match(r"[^@]+@[^@]+\.[^@]+", clubEmail) == False:
				error = '3'
			else:
				clubEmail = clubEmail.lower()
		else:
			error = '1'
			
		if error == '':
			error = "0"
		
			clubKey = self.get_primaryKey()
		
			newClub.primaryKey = clubKey
		
			newClub.put();
			
			newUserPermissions = userPermissions(parent=userPermissions_key('userPermissions'))
			newUserPermissions.permissionLevel = 2
			newUserPermissions.clubKey = clubKey
			newUserPermissions.email = clubEmail
			newUserPermissions.put()
		
			memcache.delete_multi([clubEmail() + '1', clubEmail() + '2'])
		
		self.redirect('/addClub?error=%s' % error)		
	
	def get_primaryKey(addClub_Submit):
		data = memcache.get('clubPrimaryKey')
		if data is not None:
			primaryKey = int(data)
			memcache.add(str(primaryKey + 1), 'clubPrimaryKey', 10000)
			return primaryKey
		else:
			highestNumber = 0
	
			clubs = db.GqlQuery("SELECT * "
							"FROM Club "
							"WHERE ANCESTOR IS :1 ",
							club_key('default_club'))
		
			for club in clubs:
				if highestNumber < club.primaryKey:
					highestNumber = club.primaryKey
		
			highestNumber = highestNumber + 1
			memcache.add(str(highestNumber + 1), 'clubPrimaryKey', 10000)
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
		year = str(datetime.datetime.now().year)
			
		template_values = {
			'error': error,
			'clubs': clubsMasterString,
			'year' : year
		}
		
		
		path = os.path.join(os.path.dirname(__file__), 'addMember.html')
		self.response.out.write(template.render(path, template_values))			
	
class addMembers_Submit(webapp2.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
	error = ''
	
	year = datetime.datetime.now().year

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
		try:
			if studentID:
				persons = db.GqlQuery("SELECT * "
								"FROM Person "
								"WHERE studentID = :1 LIMIT 1",
								studentID)
				person = persons.get()
				
				if person is None:
					error = '3'
				else:
					personName = person.firstName + ' ' + person.lastName
					personEmail = person.email.lower()
					permissionLevel = securityManager.getLevelOfAuthenticationForUserForClub(clubPrimaryKey)
					if permissionLevel == 0:
						error = '5'
						
					msaCardStatus = self.request.get('msacardstatus')
					
					if msaCardStatus == 'YES':
						securityManager.addMSACardToStudent(studentID)
							
					
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
			error = '4'
	
	if error == '':
		
		newClubStatus = PersonClubStatus(parent=personClubStatus_key('defaultkey'))
		
		newClubStatus.studentID = studentID
		newClubStatus.year = year
		newClubStatus.clubKey = int(clubPrimaryKey)
		newClubStatus.memberType = int(self.request.get('memberType'))
		
		user = users.get_current_user()
		email = user.email().lower()
		addedByAuthcate = email.split("@")[0]
		
		newClubStatus.addedBy = addedByAuthcate
		
		newClubStatus.put();
		
		clubs = db.GqlQuery("SELECT * "
							"FROM Club "
							"WHERE primaryKey = :1",
							int(clubPrimaryKey))
		
		
		clubName = clubs.get().name
		now = datetime.datetime.now()
		timestamp = now.strftime("%Y-%m-%d %H:%M %Z")
		
		message = mail.EmailMessage(sender="No Reply <noreply@monashclubs.org>",
                            subject="You have been added to " + clubName)

		message.to = personName + '<' + personEmail + '>'
		message.body = '''
			Dear {!s}:
			
			You have been added to the following club:
			
			{!s}

			at

			{!s}
			
			If this is a mistake, please forward this email to Alistair at webmaster@monashclubs.org

			Thank you.
			'''.format(personName, clubName, timestamp)


		message.send()
		
		
		
		error = '0'
		
	
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
		year = str(datetime.datetime.now().year)
			
		template_values = {
			'error': error,
			'clubs': clubsMasterString,
			'year' : year
		}
		
		
		path = os.path.join(os.path.dirname(__file__), 'removeMember.html')
		self.response.out.write(template.render(path, template_values))			
	
class deleteMember_Submit(webapp2.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
	error = ''
	
	year = datetime.datetime.now().year

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
				persons = db.GqlQuery("SELECT * "
								"FROM Person "
								"WHERE studentID = :1 LIMIT 1",
								studentID)
				person = persons.get()
				
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
			person.delete()
			error = '0'
	
	if error == '':
		error = '7'
	
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
		year = str(datetime.datetime.now().year)
			
		template_values = {
			'error': error,
			'clubs': clubsMasterString,
			'year' : year
		}
		
		
		path = os.path.join(os.path.dirname(__file__), 'deletePerson.html')
		self.response.out.write(template.render(path, template_values))			
	
class deletePerson_Submit(webapp2.RequestHandler):
  def post(self):
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
	error = ''
	
	year = datetime.datetime.now().year
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
				persons = db.GqlQuery("SELECT * "
								"FROM Person "
								"WHERE studentID = :1 LIMIT 1",
								studentID)
				person = persons.get()
				
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
			studentID = int(self.request.get('studentid'))
		except:
			error = '2'
			
		if error == '':
			#try:
			if studentID:
				persons = db.GqlQuery("SELECT * "
								"FROM Person "
								"WHERE studentID = :1",
								studentID)
				match = False
				person = ''
				for Person in persons:
					person = Person
					match = True
				if person == '':
					error = '3'
				else:	
					name = person.firstName + person.lastName
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
					clubMemberships = db.GqlQuery("SELECT * "
								"FROM PersonClubStatus "
								"WHERE studentID = :1",
								studentID)
					
					for membership in clubMemberships:
						clubKey = membership.clubKey
						clubName = ''
						if clubKey == 0:
							clubName = 'MSA Card'
						else:
							clubs = db.GqlQuery("SELECT * "
								"FROM Club WHERE primaryKey = :1", clubKey)
							club = clubs.get()
							if club:
								clubName = club.name
							else:
								clubName = 'N/A'
						addedBy = membership.addedBy
						if addedBy is None:
							addedBy = 'N/A'
							
						date = membership.joiningDate
						if date is None:
							date = 'N/A'
						
						
						year = membership.year
						if year is None:
							year = 'None'
						tableString = tableString + '<tr><td>' + clubName + '</td><td>' + str(year) + '</td><td>' + addedBy  + '</td><td>' + str(date) + '</td></tr>'
					
					
					template_values = {
						'type'			: type,
						'name'			: name,
						'email'			: email,
						'authcate'		: authcate,
						'address'		: address,
						'campus'		: campus,
						'studentID'		: studentID,
						'phoneNumber'	: phoneNumber,
						'memberships'	: tableString
					}

					path = os.path.join(os.path.dirname(__file__), 'showMemberStatus.html')
					self.response.out.write(template.render(path, template_values))		
											
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
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
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
					
					deleteFromClub = True
					deletePersonFromSystem = True
			
					secretaryRights = True
					adminRights = True
					
					
				else: #Logged in, but not a admin. Determine if can do anything before granting any rights.
					#Have to determine if they have proper rights
					match = False
					memberOf = db.GqlQuery("SELECT * "
								"FROM userPermissions "
								"WHERE ANCESTOR IS :1 AND email = :2",
								userPermissions_key('default_permissions'), user.email().lower())	
					
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
				'viewClubEmails'		: clubEmails,
				'checkMemberStatus'		: checkMemberStatus
			}
			
			path = os.path.join(os.path.dirname(__file__), 'index.html')
			self.response.out.write(template.render(path, template_values))		

class viewClubs(webapp2.RequestHandler):
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
		person = Person(parent=person_key('defaultkey'))
		termsAndConditions = self.request.get('TermsAndConditions')

		error = ''
		
		persons = db.GqlQuery("SELECT * "
										"FROM Person "
										"WHERE ANCESTOR IS :1 AND authcate = :2 LIMIT 1",
										person_key('default_person'), authcate)
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
		else:
			now = datetime.datetime.now()
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
			
			clubs = db.GqlQuery("SELECT * "
                            "FROM Club WHERE primaryKey = :1", clubKey)
			club = clubs.get()
			if club:
				nameOfClub = club.name

		template_values = {
		}
		
		if nameOfClub:
			if public:
				masterString = '<table border="1"><th>Full Name</th><th>Student ID</th>'	
			else:
				masterString = '<table border="1"><th>Full Name</th><th>Student ID</th><th>MSA Member</th><th>Membertype</th><th>Address</th><th>Phone Number</th><th>Monash Email</th><th>Email</th><th>Signup Date</th>'	

			masterString = masterString + self.resultsForClubKeyAndYear(clubKey, year, 0, public)

			masterString = masterString + '</table>'

			
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
		membercount = 0
		for membership in clubMemberships:
			people = db.GqlQuery("SELECT * FROM Person WHERE studentID = :1",
										membership.studentID)
			membercount = membercount + 1
			for person in people:
				
				name = person.firstName + ' ' + person.lastName
				studentID = str(person.studentID)
				address = person.address
				phoneNumber = 0
				if person.phoneNumber:
					phoneNumber = person.phoneNumber
					
				monashEmail = person.authcate
				if person.personType == 1:
					monashEmail = monashEmail + '@student.monash.edu'
				elif person.personType == 2:
					monashEmail = monashEmail + '@monash.edu'
				elif person.personType == 3:
					monashEmail = 'N/A'
				email = person.email.lower()
				signupDate = membership.joiningDate
				day = signupDate.day
				month = signupDate.month
				year = signupDate.year
				
				MSACardHolderAtSignup = 'N'
				MSACardHolderAtEndOfThatYear = 'N'
				memberType = membership.memberType
				if memberType:
					memberType = int(membership.memberType)
					
					if memberType == 0:
						memberType = 'Ordinary'
					else:
						memberType = 'Associate'
				else:
					memberType = 'N/A'
				
				msaMemberships = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE clubKey = 0 AND year = :1 AND studentID = :2",year, int(studentID))
				for memberships in msaMemberships:
					MSACardHolderAtEndOfThatYear = 'Y'
					if memberships.joiningDate < signupDate:
						MSACardHolderAtSignup = 'Y'
				if public:
					masterString = masterString + '<tr><td>' + name + '</td><td>' + str(studentID)[5:8] + '</td>'
				else:		
					masterString = masterString + '<tr><td>' + name + '</td><td>' + str(studentID) + '</td><td>' + MSACardHolderAtEndOfThatYear + '</td><td>' + memberType + '</td><td>' + address + '</td><td>' + str(phoneNumber) + '</td><td>' + monashEmail + '</td><td>' + email + '</td><td>' + str(day) + '/' + str(month) + '/' + str(year) + '</td></tr>'

		if membercount == 1000:
			masterstring = masterstring + resultsForClubKeyAndYear(clubKey, year, offset + 1000, public)

		return masterString
		
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
			now = datetime.datetime.now()
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
			
			self.response.out.write(self.resultsForEmail(clubKey, year, 0))

	def resultsForEmail(sender,clubKey, year, offset):
		masterString = ''
		#clubMemberships = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE clubKey = :1 AND year = :2 OFFSET :3",
		#								int(clubKey),year, int(offset))
		clubMemberships = db.GqlQuery("SELECT studentID FROM PersonClubStatus WHERE clubKey = :1 AND year = :2",
										int(clubKey),year)
		membercount = 0
		for membership in clubMemberships:
			people = db.GqlQuery("SELECT email FROM Person WHERE studentID = :1",
										membership.studentID)
			membercount = membercount + 1
			for person in people:
			
				email = person.email.lower()
				
				masterString = masterString + '<br>' + email
		if membercount == 1000:
			masterstring = masterstring + resultsForEmail(clubKey, year, offset + 1000)

		return masterString			
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
								"WHERE ANCESTOR IS :1 AND clubKey = :2",
								userPermissions_key('default_permissions'), clubKey)

			for permissions in memberOf:
				if permissions.permissionLevel == 2:
					masterString = masterString + permissions.email + '<br>Admin<br><br>'
				elif permissions.permissionLevel == 1:
					masterString = masterString + permissions.email + '<br>Personnel<br><br>'
				else:
					masterString = masterString + permissions.email + '<br>Unknown<br><br>'
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
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
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
					newUserPermissions = userPermissions(parent=userPermissions_key('userPermissions'))
					newUserPermissions.permissionLevel = 1
					newUserPermissions.clubKey = clubPrimaryKey
					newUserPermissions.name = name
					email = email.lower() + '@student.monash.edu'
				
					newUserPermissions = email.lower()
				
				#Check if it already exists.
				
					userPermission = db.GqlQuery("SELECT * "
									"FROM userPermissions "
									"WHERE email = :1 AND clubKey = :2",
									email, clubPrimaryKey)
		
					for permissions in userPermission:
						error = '6'
				
					if error == '':
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
    # We set the same parent key on the 'Greeting' to ensure each greeting is in
    # the same entity group. Queries across the single entity group will be
    # consistent. However, the write rate to a single entity group should
    # be limited to ~1/second.
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

class viewEvents(webapp2.RequestHandler):
	def get(self):
	
		if users.is_current_user_admin() == False:
			self.redirect('/')
			
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
	
	
class addMembersToEvent(webapp2.RequestHandler):

    def get(self):
			error = self.request.get('error')
			if error == '0':
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
                            "WHERE ANCESTOR IS :1 ",
                            event_key('default_club'))
			
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
				if match == False:
					error = '3'
				
				msaCardStatus = self.request.get('msacardstatus')
				
				if msaCardStatus == 'YES':
					securityManager.addMSACardToStudent(studentID)
					
			else:
				error = '1'
		except:
			error = '4'
	
	if error == '':
		eventKey = self.request.get('eventinput')
		eventKey = int(eventKey)
		
		clubs = securityManager.getClubsUserIsPersonnelOf()
		
		events = db.GqlQuery("SELECT * "
                            "FROM Event "
                            "WHERE ANCESTOR IS :1 AND primaryKey = :2",
                            event_key('default_club'), eventKey)
			
		clubs = securityManager.getClubsUserIsPersonnelOf()
			
		match = False
		
		for event in events:
			for club in clubs:
				if event.clubKey == club.primaryKey:
					match = True
		
		if match == False:
			self.redirect('/')
			
		eventStatus = db.GqlQuery("SELECT * "
                            "FROM PersonEventStatus "
                            "WHERE ANCESTOR IS :1 AND eventKey = :2 AND studentID = :3",
                            personEventStatus_key('default_eventstatus'), eventKey, studentID)
			
		for status in eventStatus:	
			error = '4'
			
		if error == '':	
			personEventStatus = PersonEventStatus(parent=personEventStatus_key('defaultkey'))
			
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
		
		events = db.GqlQuery("SELECT * FROM Event WHERE primaryKey = :1",
											int(eventKey))
		
		currentEvent = Event(parent=event_key('defaultkey'))
		clubKey = -0
		
		eventName = ''
		eventDate = ''
		eventLocation = ''
		clubName = ''
		for event in events:									
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

			people = db.GqlQuery("SELECT * FROM Person WHERE studentID = :1",
											membership.studentID)
			for person in people:
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
				
				MSACardStatus = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE studentID = :1 AND clubKey = 0 AND year = :2", membership.studentID,str(membership.creationDate.year))
				MSACardHolder = 'N'
				
				for status in MSACardStatus:
					MSACardHolder = 'Y'
					numberOfMSACardHolders = numberOfMSACardHolders + 1
					
				ClubStatus = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE studentID = :1 AND clubKey = :2 AND year = :3", membership.studentID, clubKey,str(membership.creationDate.year))
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
								"WHERE ANCESTOR IS :1 AND clubKey = :2",
								event_key('default_key'), club.primaryKey)
				
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
                                    "WHERE ANCESTOR IS :1 AND email = :2",
                                    userPermissions_key('default_permissions'), user.email().lower())
                                    
					for userPermissions in memberOf:
						if userPermissions.permissionLevel >= minimumPermissionLevel:

							clubs = db.GqlQuery("SELECT * "
                                    "FROM Club "
                                    "WHERE ANCESTOR IS :1 AND primaryKey = :2",
                                    club_key('default_club'), userPermissions.clubKey)
							for club in clubs:
								array.append(club)
    
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
					memberOf = db.GqlQuery("SELECT * "
                                    "FROM userPermissions "
                                    "WHERE ANCESTOR IS :1 AND email = :2 AND clubKey = :3",
                                    userPermissions_key('default_permissions'), user.email().lower(), clubPrimaryKey)
					for permissions in memberOf:
						if permissions.clubKey == clubPrimaryKey:
							memcache.set(key,permissions.permissions)

							return permissions.permissionLevel


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
		
		now = datetime.datetime.now()
		year = now.year
		
		try:
			if studentID:
			
				studentID = securityManager.trimStudentID(studentID)
			
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
		#Check if it already exists.
				
			MSAMemberships = db.GqlQuery("SELECT * "
								"FROM PersonClubStatus "
								"WHERE studentID = :1 AND year = :2 AND clubKey = 0",
								studentID,year)
		
			for person in MSAMemberships:
				error = '4'
		
	
		if error == '':
		
			newClubStatus = PersonClubStatus(parent=personClubStatus_key('defaultkey'))
			
			newClubStatus.studentID = int(studentID)
			newClubStatus.year = year
			newClubStatus.clubKey = 0
			
			newClubStatus.put();
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

									  ('/deletePerson',deletePerson),
									  ('/deletePerson_Submit',deletePerson_Submit),
									  
									  ('/explanation', explanation)
									  
									  ],
                                     debug=True)
#
#def main():
#    run_wsgi_app(application)

#if __name__ == "__main__":
#    main()