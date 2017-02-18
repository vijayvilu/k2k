import json  
import os
import time
import sys

from keystoneclient import session as ksc_session  
from keystoneclient.auth.identity import v3  
from keystoneclient.v3 import client as keystone_v3

try:
    OS_AUTH_URL = os.environ['OS_AUTH_URL']
    OS_PROJECT_ID = os.environ['OS_PROJECT_ID']
    OS_USER_ID = os.environ['OS_USER_ID']
    OS_PASSWORD = os.environ['OS_PASSWORD']
except KeyError as e:
    raise SystemExit('%s environment variable not set.' % e)

sp_ip = sys.argv[1]

class K2KClient(object):  
    def __init__(self):
        self.sp_id = 'keystone-sp'
        self.sp_ip = sp_ip
        self.auth_url = OS_AUTH_URL
        self.project_id = OS_PROJECT_ID
        self.user_id = OS_USER_ID
        self.password = OS_PASSWORD

    def v3_authenticate(self):
        auth = v3.Password(auth_url=self.auth_url,
                           user_id=self.user_id,
                           password=self.password,
                           project_id=self.project_id)
        self.session = ksc_session.Session(auth=auth, verify=False)
        self.token = self.session.auth.get_token(self.session)

    def _generate_token_json(self):
        return {
            "auth": {
                "identity": {
                    "methods": [
                        "token"
                    ],
                    "token": {
                        "id": self.token
                    }
                },
                "scope": {
                    "service_provider": {
                        "id": self.sp_id
                    }
                }
            }
        }

    def _check_response(self, response):
        if not response.ok:
            raise Exception("Something went wrong, %s" % response.__dict__)

    def get_saml2_ecp_assertion(self):
        token = json.dumps(self._generate_token_json())
        url = self.auth_url + '/auth/OS-FEDERATION/saml2/ecp'
        r = self.session.post(url=url, data=token, verify=False)
        self._check_response(r)
        self.assertion = str(r.text)

    def _get_sp(self):
        url = self.auth_url + '/OS-FEDERATION/service_providers/' + self.sp_id
        r = self.session.get(url=url, verify=False)
        self._check_response(r)
        sp = json.loads(r.text)[u'service_provider']
        return sp

    def _handle_http_302_ecp_redirect(self, response, location, **kwargs):
        return self.session.get(location, authenticated=False, **kwargs)

    def exchange_assertion(self):
        """Send assertion to a Keystone SP and get token."""
        sp = self._get_sp()

        r = self.session.post(
            sp[u'sp_url'],
            headers={'Content-Type': 'application/vnd.paos+xml'},
            data=self.assertion,
            authenticated=False,
            redirect=False)

        self._check_response(r)

        r = self._handle_http_302_ecp_redirect(r, sp[u'auth_url'],
                                               headers={'Content-Type':
                                               'application/vnd.paos+xml'})
        self.fed_token_id = r.headers['X-Subject-Token']
        self.fed_token = r.text

    def list_federated_projects(self):
        url = 'http://' + self.sp_ip + ':5000/v3/OS-FEDERATION/projects'
        headers = {'x-auth-token': self.fed_token_id}
        print headers
        r = self.session.get(url=url, headers=headers, verify=False)
        print json.loads(str(r.text))
        self._check_response(r)
        return json.loads(str(r.text))

    def _get_scoped_token_json(self, project_id):
        return {
            "auth": {
                "identity": {
                    "methods": [
                        "token"
                    ],
                    "token": {
                        "id": self.fed_token_id
                    }
                },
                "scope": {
                    "project": {
                        "id": project_id
                    }
                }
            }
        }

    def scope_token(self, project_id):
        # project_id can be select from the list in the previous step
        token = json.dumps(self._get_scoped_token_json(project_id))
        print token
        url = 'http://' + self.sp_ip + ':5000/v3/auth/tokens'
        headers = {'x-auth-token': self.fed_token_id,
        'Content-Type': 'application/json'}
        r = self.session.post(url=url, headers=headers, data=token,
        verify=False)
        self._check_response(r)
        self.r = r
        self.scoped_token_id = r.headers['X-Subject-Token']
        self.scoped_token_ref = str(r.text)

def main():  
    client = K2KClient()
    client.v3_authenticate()
    client.get_saml2_ecp_assertion()
    print('ECP wrapped SAML assertion: %s' % client.assertion)
    client.exchange_assertion()
    print('Unscoped token id: %s' % client.fed_token_id)
    print "==================SCOPE TOKEN================="
    project_list = client.list_federated_projects()
    project_id = str(project_list[u'projects'][0][u'id'])
    print('scope to project [%s]' % project_list[u'projects'][0]['name'])
    print ('project id: %s' % project_id)
    client.scope_token(project_id=project_id)
    print('Scoped token id: %s' % client.scoped_token_id)
#    client.scoped_auth_ref = client.r.json()
#    client.scoped_auth = v3.Token(auth_url="http://128.52.183.216:5000/v3", 
#                                token=client.scoped_token_id)
#    client.scoped_auth.auth_ref = client.scoped_auth_ref
#    client.scoped_session = ksc_session.Session(auth=client.scoped_auth, verify=False)
#    client.unscoped_auth = v3.Token(auth_url="http://128.52.183.216:5000/v3", 
#                                token=client.fed_token_id)
#    client.unscoped_session = ksc_session.Session(auth=client.unscoped_auth, verify=False)

if __name__ == "__main__":  
    main()

