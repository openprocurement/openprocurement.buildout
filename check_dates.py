from requests import Session
from termcolor import colored


source_url = 'https://public.api.openprocurement.org'
path = '/api/2.3/tenders?descending=1&offset=2017-02-01&limit=1000'
test_url = 'http://edge-prod.office.quintagroup.com/api/2.3/tenders/'
r = Session()
lr = Session()
try:
    response = r.get(source_url + path).json()
except Exception as e:
    print 'InvalidResponse: {}'.format(e.message)
    raise SystemExit

while response['data']:
    for item in response['data']:
        l_resp = lr.get(test_url + item['id']).json()
        if l_resp['data']['dateModified'] != item['dateModified']:
            print colored('API - {}, EDGE - {}, ID: {}'.format(
                item['dateModified'], l_resp['data']['dateModified'],
                item['id']), 'red')
        else:
            print colored('Pass: {}'.format(item['id']), 'green')
    next_page = response['next_page']['path']
    response = r.get(source_url + next_page).json()
