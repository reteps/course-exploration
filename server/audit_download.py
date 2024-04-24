import os
import requests
import base64
import time
import sys
import audit_parser

from bs4 import BeautifulSoup
# from audit_parser import parse_audit
import json

def get_audit(netid, password):
  url = 'https://login.uillinois.edu/auth/SystemLogin/sm_login.fcc'
  creds_bitmask = 0x02000001 # https://support.broadcom.com/web/ecx/solutiondetails?aparNo=QO98016&os=SOLARIS
  # Indicates the realm object ID that identifies the realm where the resource exists. 
  # This ID is may be used by third party applications to make calls to the Policy Server.
  realm_oid = '06-09c2ae97-034e-4857-a8af-0206bb6313a8'
  target = 'uachieve.apps.uillinois.edu/uachieve_uiuc/'
  # Contains the agent name of the agent originally protecting the resource. 
  # If encryptagentname is set to yes the agent name value is encrypted.
  sm_agent_name_enc = 'VMtKKRP4QIbeH8j5F8pFZNjcFl7ogFY6A+xavJKIyye4kJFHglCJ8zJOCz+EEPcmbY7E4tzR7gCuvTj3o0aRs9KrJwaSwLf1'

  params = {
    'TYPE': creds_bitmask,
    'REALMOID': realm_oid,
    'SMAGENTNAME': '-SM-' + sm_agent_name_enc,
    'TARGET': '-SM-HTTPS://' + target,
  }

  body = {
    'USER': netid,
    'PASSWORD': password
  }
  headers = {
    'User-Agent': 'https://github.com/reteps/course-exploration'
  }
  session = requests.Session()

  res = session.post(url, data=body, params=params, headers=headers)

  audit_url = 'https://uachieve.apps.uillinois.edu/uachieve_uiuc/audit/create.html'

  body = {
    'previousInstcd': 'UKL',
    'instcd': 'UKL',
    'whatIfDegreeProgram': '',
    'catalogYearTerm': '',
    'requiredMarker': '',
    'includeInProgressCourses': 'true',
    'includeInProgressCourses': '',
    'includePlannedCourses':  '',
    'sysIn.evalsw': 'A',
    'reportType': 'htm',
    'useDefaultDegreePrograms': 'true',
    'pageRefresh': 'false'
  }
  res = session.post(audit_url, data=body, headers=headers)

  while True:
    res = session.get('https://uachieve.apps.uillinois.edu/uachieve_uiuc/audit/list.html', headers=headers)
    if 'Still running' not in res.text:
      break
    time.sleep(1)

  soup = BeautifulSoup(res.text, 'html.parser')
  # get table class=resultList
  table = soup.find('table', class_='resultList')
  # get first row with class=even
  row = table.find('tr', class_='even')
  # get first column text
  id = row.find('td').text.strip()

  url = 'https://uachieve.apps.uillinois.edu/uachieve_uiuc/audit/read.html'
  params = {
    'id': '!!!!'.join([
      'JobQueueRun',
      base64.b64encode(('!!!!' + '='.join(['intSeqNo', id])).encode('utf-8')).decode('utf-8')
    ])
  }
  res = session.get(url, params=params, headers=headers)
  contents = res.text


  audit = audit_parser.parse_audit(contents)
  return audit