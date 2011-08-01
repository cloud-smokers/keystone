# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from keystone.backends.api import BaseTokenAPI


class TokenAPI(BaseTokenAPI):
    def create(self, token):
        if token.tenant_id != None:
            tenant_user_key = token.tenant_id + "::" + token.user_id
        else:
            tenant_user_key = token.user_id
        #Setting them for  a day.
        MEMCACHE_SERVER.set(token.id, token)
        MEMCACHE_SERVER.set(tenant_user_key, token)

    def get(self, id, session=None):
        return  MEMCACHE_SERVER.get(id)

    def delete(self, id, session=None):
        token = MEMCACHE_SERVER.get(id)
        if token != None:
            MEMCACHE_SERVER.delete(id)

            if token.tenant_id != None:
                MEMCACHE_SERVER.delete(token.tenant_id + "::" + token.user_id)
            else:
                MEMCACHE_SERVER.delete(token.id)
                MEMCACHE_SERVER.delete(token.user_id)

    def get_for_user(self, user_id, session=None):
        return MEMCACHE_SERVER.get(user_id)

    def get_for_user_by_tenant(self, user_id, tenant_id, session=None):
        return MEMCACHE_SERVER.get(tenant_id + "::" + user_id)


def get():
    return TokenAPI()
