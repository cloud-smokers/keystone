# vim: tabstop=4 shiftwidth=4 softtabstop=4
# Copyright (c) 2011 OpenStack, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import unittest

from keystone.test.unit import base
from keystone.test.unit.decorators import jsonify, xmlify

LOGGER = logging.getLogger('test.unit.test_authn_v2')


class AuthnMethods(base.ServiceAPITest):

    def test_authn_get_fails(self):
        """
        Test for GH issue #5. GET /tokens works when it should not
        """
        url = "/tokens"
        req = self.get_request('GET', url)
        body = {
            "passwordCredentials": {
                "username": self.auth_user['id'],
                "password": self.auth_user['password'],
                "tenantId": self.auth_user['tenant_id']
            }
        }
        req.body = json.dumps(body)
        self.get_response()
        self.status_not_found()

    @jsonify
    def test_authn_success_json(self):
        """
        Test that good password credentials returns a 200 OK
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        body = {
            "passwordCredentials": {
                "username": self.auth_user['id'],
                "password": self.auth_user['password'],
                "tenantId": self.auth_user['tenant_id']
            }
        }
        req.body = json.dumps(body)
        self.get_response()
        self.status_ok()

        expected = {
            u'auth': {
                u'token': {
                    u'expires': self.expires.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    u'id': self.auth_token_id
                }
            }
        }
        self.assert_dict_equal(expected, json.loads(self.res.body))

    @jsonify
    def test_authn_success_missing_tenant_json(self):
        """
        Test that supplying an existing user/pass, with a missing tenant ID
        in the password credentials results in a 200 OK but a token not
        matching the token with a tenant attached to it.
        """
        # Create a special token for user with no tenant
        _auth_token = self.fixture_create_token(
            user_id=self.auth_user['id'],
            tenant_id=None,
            expires=self.expires,
            token_id='NOTENANTTOKEN')

        url = "/tokens"
        req = self.get_request('POST', url)
        body = {
            "passwordCredentials": {
                "username": self.auth_user['id'],
                "password": self.auth_user['password']
            }
        }
        req.body = json.dumps(body)
        self.get_response()
        self.status_ok()

        expected = {
            u'auth': {
                u'token': {
                    u'expires': self.expires.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    u'id': 'NOTENANTTOKEN'
                }
            }
        }
        self.assert_dict_equal(expected, json.loads(self.res.body))

    @jsonify
    def test_authn_success_none_tenant_json(self):
        """
        Test that supplying an existing user/pass, with a tenant ID of None
        in the password credentials results in a 200 OK but a token not
        matching the token with a tenant attached to it.
        """
        # Create a special token for user with no tenant
        _auth_token = self.fixture_create_token(
            user_id=self.auth_user['id'],
            tenant_id=None,
            expires=self.expires,
            token_id='NOTENANTTOKEN')

        url = "/tokens"
        req = self.get_request('POST', url)
        body = {
            "passwordCredentials": {
                "username": self.auth_user['id'],
                "password": self.auth_user['password'],
                "tenantId": None
            }
        }
        req.body = json.dumps(body)
        self.get_response()
        self.status_ok()

        expected = {
            u'auth': {
                u'token': {
                    u'expires': self.expires.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    u'id': 'NOTENANTTOKEN'
                }
            }
        }
        self.assert_dict_equal(expected, json.loads(self.res.body))

    @jsonify
    def test_authn_malformed_creds_json(self):
        """
        Test that supplying a malformed password credentials
        results in a 400 Bad Request
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        body = {
            "passwordCredMisspelled": {
                "username": 'unknown',
                "password": 'badpass',
                "tenantId": None
            }
        }
        req.body = json.dumps(body)
        self.get_response()
        self.status_bad_request()

    @jsonify
    def test_authn_user_not_found_json(self):
        """
        Test that supplying a non-existing user in the password credentials
        results in a 401 Unauthorized
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        body = {
            "passwordCredentials": {
                "username": 'unknown',
                "password": 'badpass',
                "tenantId": None
            }
        }
        req.body = json.dumps(body)
        self.get_response()
        self.status_unauthorized()

    @jsonify
    def test_authn_user_missing_json(self):
        """
        Test that supplying a missing user in the password credentials
        results in a 401 Unauthorized
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        body = {
            "passwordCredentials": {
                "username": None,
                "password": self.auth_user['password'],
                "tenantId": self.auth_user['tenant_id']
            }
        }
        req.body = json.dumps(body)
        self.get_response()
        self.status_unauthorized()

    @jsonify
    def test_authn_bad_pass_json(self):
        """
        Test that supplying an existing user and a bad password
        in the password credentials results in a 401 Unauthorized
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        body = {
            "passwordCredentials": {
                "username": self.auth_user['id'],
                "password": 'badpass',
                "tenantId": None
            }
        }
        req.body = json.dumps(body)
        self.get_response()
        self.status_unauthorized()

    @jsonify
    def test_authn_bad_tenant_json(self):
        """
        Test that supplying an existing user/pass, with a bad tenant ID
        in the password credentials results in a 401 Unauthorized
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        body = {
            "passwordCredentials": {
                "username": self.auth_user['id'],
                "password": self.auth_user['password'],
                "tenantId": 'badtenant'
            }
        }
        req.body = json.dumps(body)
        self.get_response()
        self.status_unauthorized()

    @xmlify
    def test_authn_success_xml(self):
        """
        Test that good password credentials returns a 200 OK
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        req.body = '<?xml version="1.0" encoding="UTF-8"?> \
                    <passwordCredentials \
                    xmlns="http://docs.openstack.org/identity/api/v2.0" \
                    password="%s" username="%s" \
                    tenantId="%s"/> ' % (self.auth_user['password'],
                                         self.auth_user['id'],
                                         self.auth_user['tenant_id'])
        self.get_response()
        self.status_ok()

        expected = """
            <auth xmlns="http://docs.openstack.org/identity/api/v2.0">
                <token expires="%s" id="%s" />
            </auth>
            """ % (self.expires.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                   self.auth_token_id)
        self.assert_xml_strings_equal(expected, self.res.body)

    @xmlify
    def test_authn_success_missing_tenant_xml(self):
        """
        Test that supplying an existing user/pass, with a missing tenant ID
        in the password credentials results in a 200 OK but a token not
        matching the token with a tenant attached to it.
        """
        # Create a special token for user with no tenant
        _auth_token = self.fixture_create_token(
            user_id=self.auth_user['id'],
            tenant_id=None,
            expires=self.expires,
            token_id='NOTENANTTOKEN')

        url = "/tokens"
        req = self.get_request('POST', url)
        req.body = '<?xml version="1.0" encoding="UTF-8"?> \
                    <passwordCredentials \
                    xmlns="http://docs.openstack.org/identity/api/v2.0" \
                    password="%s" username="%s" /> ' % (
                        self.auth_user['password'],
                        self.auth_user['id'])
        self.get_response()
        self.status_ok()

        expected = """
            <auth xmlns="http://docs.openstack.org/identity/api/v2.0">
                <token expires="%s" id="%s" />
            </auth>
            """ % (self.expires.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                   'NOTENANTTOKEN')
        self.assert_xml_strings_equal(expected, self.res.body)

    @xmlify
    def test_authn_malformed_creds_xml(self):
        """
        Test that supplying a malformed password credentials
        results in a 400 Bad Request
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        req.body = '<?xml version="1.0" encoding="UTF-8"?> \
                    <passwordCredMispelled \
                    xmlns="http://docs.openstack.org/identity/api/v2.0" \
                    password="%s" username="%s" \
                    tenantId="%s"/> ' % (self.auth_user['password'],
                                         self.auth_user['id'],
                                         self.auth_user['tenant_id'])
        self.get_response()
        self.status_bad_request()

    @xmlify
    def test_authn_user_not_found_xml(self):
        """
        Test that supplying a non-existing user in the password credentials
        results in a 401 Unauthorized
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        req.body = '<?xml version="1.0" encoding="UTF-8"?> \
                    <passwordCredentials \
                    xmlns="http://docs.openstack.org/identity/api/v2.0" \
                    password="%s" username="%s" \
                    tenantId="%s"/> ' % (self.auth_user['password'],
                                         'missinguser',
                                         self.auth_user['tenant_id'])
        self.get_response()
        self.status_unauthorized()

    @xmlify
    def test_authn_user_missing_xml(self):
        """
        Test that supplying a missing user in the password credentials
        results in a 400 Bad Request
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        req.body = '<?xml version="1.0" encoding="UTF-8"?> \
                    <passwordCredentials \
                    xmlns="http://docs.openstack.org/identity/api/v2.0" \
                    password="%s" \
                    tenantId="%s"/> ' % (self.auth_user['password'],
                                         self.auth_user['tenant_id'])
        self.get_response()
        self.status_bad_request()

    @xmlify
    def test_authn_bad_pass_xml(self):
        """
        Test that supplying a bad password in the password credentials
        results in a 401 Unauthorized
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        req.body = '<?xml version="1.0" encoding="UTF-8"?> \
                    <passwordCredentials \
                    xmlns="http://docs.openstack.org/identity/api/v2.0" \
                    password="%s" username="%s" \
                    tenantId="%s"/> ' % ('badpass',
                                         self.auth_user['id'],
                                         self.auth_user['tenant_id'])
        self.get_response()
        self.status_unauthorized()

    @xmlify
    def test_authn_bad_tenant_xml(self):
        """
        Test that supplying a bad tenant in the password credentials
        results in a 401 Unauthorized
        """
        url = "/tokens"
        req = self.get_request('POST', url)
        req.body = '<?xml version="1.0" encoding="UTF-8"?> \
                    <passwordCredentials \
                    xmlns="http://docs.openstack.org/identity/api/v2.0" \
                    password="%s" username="%s" \
                    tenantId="%s"/> ' % (self.auth_user['password'],
                                         self.auth_user['id'],
                                         'badtenant')
        self.get_response()
        self.status_unauthorized()


class TestAuthnV2(base.ServiceAPITest, AuthnMethods):

    """
    Tests for the /v2.0/tokens auth endpoint with main service API
    """


class TestAdminAuthnV2(base.AdminAPITest, AuthnMethods):

    """
    Tests for the /v2.0/tokens auth endpoint with admin API
    """

    @jsonify
    def test_validate_token_json(self):
        """
        Test successful validation of the token we use in authn
        """
        url = "/tokens/%s" % self.auth_token_id
        headers = {"X-Auth-Token": self.auth_token_id}
        _req = self.get_request('GET', url, headers)
        self.get_response()
        self.status_ok()

        expected = {
            "auth": {
                "token": {
                    u'expires': self.expires.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                    u'id': self.auth_token_id,
                    "tenantId": self.auth_user['tenant_id']
                },
                "user": {
                    "username": self.auth_user['id'],
                    "tenantId": self.auth_user['tenant_id'],
                    "roleRefs": []
                }
            }
        }
        for user_role in self.auth_user['roles']:
            expected["auth"]["user"]["roleRefs"].append(
                {"roleId": user_role['role_id'], "id": user_role['id']})
        self.assert_dict_equal(expected, json.loads(self.res.body))

    @xmlify
    def test_validate_token_xml(self):
        """
        Test successful validation of the token we use in authn
        """
        url = "/tokens/%s" % self.auth_token_id
        headers = {"X-Auth-Token": self.auth_token_id}
        _req = self.get_request('GET', url, headers)
        self.get_response()
        self.status_ok()

        expected = """
            <auth xmlns="http://docs.openstack.org/identity/api/v2.0">
            <token expires="%s" id="%s" tenantId="%s"/>
            <user username="%s" tenantId="%s">
            <roleRefs xmlns="http://docs.openstack.org/identity/api/v2.0">
            """ % (
                      self.expires.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                      self.auth_token_id,
                      self.auth_user['tenant_id'],
                      self.auth_user['id'],
                      self.auth_user['tenant_id'])

        for user_role in self.auth_user['roles']:
            expected = expected + """
            <roleRef xmlns="http://docs.openstack.org/identity/api/v2.0" 
            id="%s" roleId="%s"/>""" % (user_role['id'],
                                        user_role['role_id'])
        expected = expected + """</roleRefs>
                  </user>
                 </auth>"""
        self.assert_xml_strings_equal(expected, self.res.body)

if __name__ == '__main__':
    unittest.main()
