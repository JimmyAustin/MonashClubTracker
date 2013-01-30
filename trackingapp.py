import datetime
import logging
import webapp2
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
import re
import os
from google.appengine.ext.webapp import template

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

class userPermissions(db.Model):
  email = db.StringProperty()
  clubKey = db.IntegerProperty()
  permissionLevel = db.IntegerProperty()
  #permission levels
  #2 = admin
  #1 = club personel

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
	
def userPermissions_key(person_name=None):
	return db.Key.from_path('person', 'userPermissions' or 'default_person')    
  
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
			match = False
			persons = db.GqlQuery("SELECT * "
							"FROM Person "
							"WHERE ANCESTOR IS :1 AND studentID = :2 LIMIT 1",
							person_key('default_person'), studentID)
			for people in persons:
				error = '4'
				
			person.studentID = studentID
		else:
			error = '1'
	except:
		error = '2'
		
	if campus:
		person.campus = int(campus)
	else:
		error = '1'
		
	if address:
		person.address = address
	else:
		error = '1'	
		
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
			error = '1'
			
		if error == '':
			error = "0"
		
			clubKey = get_primaryKey()
		
			newClub.primaryKey = clubKey
		
			newClub.put();
			
			newUserPermissions = userPermissions(parent=userPermissions_key('userPermissions'))
			newUserPermissions.permissionLevel = 2
			newUserPermissions.clubKey = clubKey
			newUserPermissions.email = clubEmail
			newUserPermissions.put()
		
		self.redirect('/addClub?error=%s' % error)		
	
		def get_primaryKey():
			data = memcache.get('clubPrimaryKey')
			if data is not None:
				return int(data)
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
				memcache.add(str(highestNumber), 'clubPrimaryKey', 10000)
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
		

	
			
		template_values = {
			'error': error,
			'clubs': clubsMasterString
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
	
	year = self.request.get('year')
	if year:
		year = int(self.request.get('year'))
	else:
		error = '1' 

	try:
		studentID = int(self.request.get('studentid'))
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
			error = '4'
	
	if error == '':
		
		newClubStatus = PersonClubStatus(parent=personClubStatus_key('defaultkey'))
		
		newClubStatus.studentID = studentID
		newClubStatus.year = year
		newClubStatus.clubKey = int(clubPrimaryKey)
		
		newClubStatus.put();
		error = '0'
		
	
	self.redirect('/addMembers?error=%s' % error)

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
		#Check if it already exists.
				
		MSAMemberships = db.GqlQuery("SELECT * "
								"FROM PersonClubStatus "
								"WHERE studentID = :1 AND year = :2 AND clubKey = 0",
								studentID,year)
		
		for person in MSAMemberships:
			error = '4'
		
	
	if error == '':
		
		newClubStatus = PersonClubStatus(parent=personClubStatus_key('defaultkey'))
		
		newClubStatus.studentID = studentID
		newClubStatus.year = year
		newClubStatus.clubKey = 0
		
		newClubStatus.put();
		error = '0'
		
	
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
			addEvent = False
			addPeopleToEvents = False
			viewAllEvents = False
			viewEventAttendees = False
			
			
			
			logoutMessage = ''
			if user:
				logoutMessage = '<a href="%s">Click here to logout.</a>' % users.create_logout_url(self.request.uri)

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
					addEvent = True
					addPeopleToEvents = True
					viewAllEvents = True
					viewEventAttendees = True					

				else: #Logged in, but not a admin. Determine if can do anything before granting any rights.
					#Have to determine if they have proper rights
					match = False
					memberOf = db.GqlQuery("SELECT * "
								"FROM userPermissions "
								"WHERE ANCESTOR IS :1 AND email = :2",
								userPermissions_key('default_permissions'), user.email())	
					
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
						addEvent = True
						addPeopleToEvents = True
						viewAllEvents = False
						viewEventAttendees = True	
			else:
				loginMessage = 'You do not appear to be logged in. <a href="%s">Click here to login.</a> You do not have to be logged in to perform some actions.' % users.create_login_url(self.request.uri)
	
			template_values = {
				'loginMessage': loginMessage,
				'logoutMessage': logoutMessage,
				'addNewPerson': addNewPerson,
				'addMSACard': addMSACard,
				'addClub': addClub,
				'addMemberToClub': addMemberToClub,
				'viewClubPermissions': viewClubPermissions,
				'viewClubs': viewClubs,
				'viewClubMembers': viewClubMembers,
				'addPersonnelToClub':addClubPersonnel,
				'addEvent': addEvent,
				'addPeopleToEvents': addPeopleToEvents,
				'viewAllEvents': viewAllEvents,
				'viewEventAttendees': viewEventAttendees
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
		
		nameOfClub = ''
		
		if clubKey == 0:
			if users.is_current_user_admin() == False:
				nameOfClub = 'MSA Cards'
			else:
				self.redirect('/')
		else:
			
			permissionLevel = securityManager.getLevelOfAuthenticationForUserForClub(clubKey)
			
			if permissionLevel != 2:
				self.redirect('/')
			
			clubs = db.GqlQuery("SELECT * "
                            "FROM Club WHERE primaryKey = :1", clubKey)
			
			nameOfClub = clubs.get().name
								
		template_values = {
		}
		
		if nameOfClub:
			
			clubMemberships = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE clubKey = :1 AND year = :2",
											int(clubKey),year)
			masterString = '<table border="1"><th>Full Name</th><th>Student ID</th><th>MSA At Signup</th><th>MSA As Of End Of Year</th><th>Address</th><th>Phone Number</th><th>Monash Email</th><th>Email</th><th>Signup Date</th>'	

			for membership in clubMemberships:
				people = db.GqlQuery("SELECT * FROM Person WHERE studentID = :1",
											membership.studentID)

				for person in people:
					name = person.firstName + ' ' + person.lastName
					studentID = str(person.studentID)
					address = person.address
					phoneNumber = 0
					if person.phoneNumber:
						phoneNumber = person.phoneNumber
					monashEmail = person.authcate + '@student.monash.edu'
					email = person.email
					signupDate = membership.joiningDate
					day = signupDate.day
					month = signupDate.month
					year = signupDate.year
					
					MSACardHolderAtSignup = 'N'
					MSACardHolderAtEndOfThatYear = 'N'

					msaMemberships = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE clubKey = 0 AND year = :1",year)
					for memberships in msaMemberships:
						MSACardHolderAtEndOfThatYear = 'Y'
						if memberships.joiningDate < signupDate:
							MSACardHolderAtSignup = 'Y'
					masterString = masterString + '<tr><td>' + name + '</td><td>' + str(studentID) + '</td><td>' + MSACardHolderAtSignup + '</td><td>' + MSACardHolderAtEndOfThatYear + '</td><td>' + address + '</td><td>' + str(phoneNumber) + '</td><td>' + monashEmail + '</td><td>' + email + '</td><td>' + str(day) + '/' + str(month) + '/' + str(year) + '</td></tr>'

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
				logging.info('1')
				self.redirect('/')
		else:
			logging.info('2')

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
		
	if clubPrimaryKey:
		clubPrimaryKey = int(self.request.get('clubinput'))
		if securityManager.getLevelOfAuthenticationForUserForClub(clubPrimaryKey) == 2:
			if email:
				newUserPermissions = userPermissions(parent=userPermissions_key('userPermissions'))
				newUserPermissions.permissionLevel = 1
				newUserPermissions.clubKey = clubPrimaryKey
				newUserPermissions.email = email
				
			#Check if it already exists.
				
				userPermission = db.GqlQuery("SELECT * "
								"FROM userPermissions "
								"WHERE email = :1 AND clubKey = :2",
								email, clubPrimaryKey)
		
				for permissions in userPermission:
					error = '6'
				
				if error == '':
					newUserPermissions.put()
					error = '0'

			else:
				error = '3'
		else:
			error = '5'
	else:
		error = '2'

		
		
	
	self.redirect('/addPersonnelToClub?error=%s' % error)

		
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
							
	logging.info('Event')
	logging.info(clubPrimaryKey)
	intClubPrimaryKey = int(clubPrimaryKey)
	newEvent.clubName = ''
	for Club in clubs:
		if Club.primaryKey == intClubPrimaryKey:
			newEvent.clubName = Club.name
			logging.info('Matched name')

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
				error = 'Student ID match not found'
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
			
			personEventStatus.put();
			logging.info('successfully put')

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
		
		masterString = '<table border="1"><th>Full Name</th><th>Club Member</th><th>Clayton Student</th><th>Monash Clayton Student ID Number</th><th>MSA Card Holder</th><th>Phone Number</th>'	
		template_values = {
		}	
		
		for membership in eventMemberships:
			logging.info('person2')

			people = db.GqlQuery("SELECT * FROM Person WHERE studentID = :1",
											membership.studentID)
			for person in people:
				
				logging.info('person')
				
				name = ''
				claytonStudent = ''
				studentID = ''
				phoneNumber = ''
				
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
				else:
					claytonStudent = 'N'
				
				MSACardStatus = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE studentID = :1 AND clubKey = 0", membership.studentID)
				MSACardHolder = 'N'
				
				for status in MSACardStatus:
					MSACardHolder = 'Y'
					
				ClubStatus = db.GqlQuery("SELECT * FROM PersonClubStatus WHERE studentID = :1 AND clubKey = :2", membership.studentID, clubKey)
				clubMember = 'N'
				
				for status in ClubStatus:
					clubMember = 'Y'	
					
				masterString = masterString + '<tr><td>' + name + '</td><td>' + clubMember +'</td><td>' + claytonStudent + '</td><td>' + studentID + '</td><td>' + MSACardHolder + '</td><td>' + phoneNumber + '</td></tr>'
	
	
		masterString = masterString + '</table>'
			

			
		template_values = {
			'nameOfEvent': eventName,
			'table'		: masterString,
			'title'		: eventName + ' - ' + clubName + ' - ' + eventDate + ' - ' + eventLocation
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

class securityManager():
	@staticmethod
	def getLevelOfAuthenticationForUserForClub(clubPrimaryKey):
		user = users.get_current_user()
		if not user:
			return 0 #User has 0 rights.
		else:
			if users.is_current_user_admin():
				return 2 #User has same rights as club admin.
			else:
				#User is logged in, but not a admin. Search for priorites
				memberOf = db.GqlQuery("SELECT * "
								"FROM userPermissions "
								"WHERE ANCESTOR IS :1 AND email = :2 AND clubKey = :3",
								userPermissions_key('default_permissions'), user.email(), clubPrimaryKey)
				for permissions in memberOf:
					if permissions.clubKey == clubPrimaryKey:
						return permissions.permissionLevel
	@staticmethod			
	def getClubsUserIsAdminOf():
		return securityManager.getClubsWhereUserHasPermissionLevelsOf(2)
		
	@staticmethod			
	def getClubsWhereUserHasPermissionLevelsOf(minimumPermissionLevel):		
		user = users.get_current_user()
		logging.info('Getting level of auth:' + str(minimumPermissionLevel))

		if not user:
			logging.info('User not found')
			return [] #User not logged in, no rights.
		else:
			if users.is_current_user_admin():
				logging.info('User admin')

				return securityManager.getAllClubs()
			else:	
				array = []
				
				memberOf = db.GqlQuery("SELECT * "
								"FROM userPermissions "
								"WHERE ANCESTOR IS :1 AND email = :2",
								userPermissions_key('default_permissions'), user.email())
								
				for userPermissions in memberOf:
					if userPermissions.permissionLevel >= minimumPermissionLevel:
						logging.info('Found permission, with correct levels')

						clubs = db.GqlQuery("SELECT * "
								"FROM Club "
								"WHERE ANCESTOR IS :1 AND primaryKey = :2",
								club_key('default_club'), userPermissions.clubKey)
						for club in clubs:
							array.append(club)
							logging.info('Found something')
					else:
						logging.info('Not permission')
	
				return array
	@staticmethod			
	def getAllClubs():
		clubs = db.GqlQuery("SELECT * "
								"FROM Club")			
		return clubs
	@staticmethod			
	def getClubsUserIsPersonnelOf():
		return securityManager.getClubsWhereUserHasPermissionLevelsOf(1)

		
logging.info('Run 1')		
app = webapp2.WSGIApplication(
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
									  
									  ('/addPersonnelToClub',addPersonnelToClub),
									  ('/addPersonnelToClub_Submit',addPersonnelToClub_Submit),

									  
									  ('/selectClubPermissionsToView',selectClubPermissionsToView),
									  ('/selectClubPermissionsToView_Submit',selectClubPermissionsToView_Submit),
									  
									  ('/addEvent', addEvent),
									  ('/addEventSubmit', addEvent_Submit),
									  ('/addMembersToEvent', addMembersToEvent),
									  ('/addMembersToEvent_Submit', addMembersToEvent_Submit),
									  ('/viewEvents', viewEvents),
									  ('/eventAttendees',viewEventMembers),
									  ('/selectEventToView',selectEventToView)
									  ],
                                     debug=True)
#
#def main():
#    run_wsgi_app(application)

#if __name__ == "__main__":
#    main()