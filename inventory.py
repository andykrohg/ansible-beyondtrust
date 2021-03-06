#!/usr/bin/env python

import os
import requests
import sys
import json
import urllib3
urllib3.disable_warnings()

def getEnvVariable(variable):
	try:
		return os.environ[variable]
	except:
		sys.stderr.write(variable + ' environment variable not found\n')
		return


# Password safe API URL
BASEURL = getEnvVariable('PS_BASE_URL')

# Authorization key provided by Password Safe Management Team
AUTH_KEY = getEnvVariable('PS_AUTH_KEY')

# User that will be logged on audit controls in the Password Safe
RUN_AS = getEnvVariable('PS_RUN_AS')

# Server name list as it is on Password Safe
HOSTS = getEnvVariable('PS_HOSTS')
if HOSTS:
	HOSTS = HOSTS.split(',')

# Server user account that the password will be retrieved from PAM
HOST_ACCOUNT = getEnvVariable('PS_HOST_ACCOUNT')

# Ansible host group name
GROUP_NAME = getEnvVariable('PS_GROUP_NAME')

# Ansible host group name
REASON = getEnvVariable('PS_REASON')

# Ansible host group name
DURATION_MINUTES = getEnvVariable('PS_DURATION_MINUTES')

# Variables values
if not(BASEURL and AUTH_KEY and RUN_AS and HOSTS and HOST_ACCOUNT and GROUP_NAME and REASON and DURATION_MINUTES):
	sys.exit(1)

# Creating session
header = {'Authorization': 'PS-Auth key=' + AUTH_KEY + '; runas=' + RUN_AS + ';', 'Content-Type' :'application/json'}
session = requests.Session()
session.headers.update(header)

# Logging in
response = session.post(url = BASEURL + 'Auth/SignAppin', verify = False)

# Getting active Requests to avoid to create new ones
response = session.get(url = BASEURL + 'Requests?status=active', verify = False) 
requests = json.loads(response.text)

groupJson = []
variablesJson = {}

for serverName in HOSTS:
	# Getting data to create a password request
	response = session.get(url = BASEURL + 'ManagedAccounts?systemName=' + serverName + '&accountName=' + HOST_ACCOUNT, verify = False)
	
	try:
		account=json.loads(response.text)
		systemId = str(account['SystemId'])
		accountId = str(account['AccountId'])
	except:
		continue

	requestId = ''
	# Check if exists a request for the account
	for request in requests:
		if systemId == str(request['SystemID']) and accountId == str(request['AccountID']):
			requestId = str(request['RequestID'])
			break

	if requestId == '':
		# Create a new request
		postData = {
		'SystemID': systemId,
		'AccountID': accountId,
		'DurationMinutes' : DURATION_MINUTES,
		'Reason' : REASON
		}
		response = session.post(url = BASEURL + 'Requests', json = postData, verify = False)
		requestId = response.text

	# Getting the password using the requestId
	response = session.get(url = BASEURL + '/Credentials/' + requestId, verify = False)
	password=json.loads(response.text)

	groupJson.append(serverName) 
	variablesJson[serverName] = dict(ansible_user = HOST_ACCOUNT, ansible_password = password)
# Logging out
response = session.post(url = BASEURL + 'Auth/Signout', verify = False)

# Assign results to the output structure
inventory = {}
inventory[GROUP_NAME] = []
inventory[GROUP_NAME] = groupJson
inventory['_meta'] = dict(hostvars = variablesJson)

# Print the result JSON
sys.stdout.write(json.dumps(inventory))