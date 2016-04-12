# -*- coding: utf-8 -*-

# Copyright (C) 2006-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging

from xivo_agid import agid
from xivo_agid import objects

logger = logging.getLogger(__name__)


def phone_set_feature(agi, cursor, args):
    try:
        feature_name = args[0]
    except IndexError:
        agi.dp_break('Missing feature name argument')

    function_name = '_phone_set_%s' % feature_name
    try:
        function = globals()[function_name]
    except KeyError:
        agi.dp_break('Unknown feature name %r' % feature_name)

    try:
        function(agi, cursor, args)
    except LookupError, e:
        agi.dp_break(str(e))


def _phone_set_callrecord(agi, cursor, args):
    calling_user = _get_calling_user(agi, cursor)
    calling_user.toggle_feature('callrecord')

    agi.set_variable('XIVO_CALLRECORDENABLED', calling_user.callrecord)
    agi.set_variable('XIVO_USERID_OWNER', calling_user.id)


def _get_calling_user(agi, cursor):
    return objects.User(agi, cursor, _get_id_of_calling_user(agi))


def _get_id_of_calling_user(agi):
    return int(agi.get_variable('XIVO_USERID'))


def _phone_set_dnd(agi, cursor, args):
    try:
        user_id = _get_id_of_calling_user(agi)
        new_value = _user_set_service(agi, user_id, 'dnd')
    except Exception, e:
        logger.error('Error during setting dnd : %s', e)
    else:
        agi.set_variable('XIVO_DNDENABLED', int(new_value['enabled']))
        agi.set_variable('XIVO_USERID_OWNER', user_id)


def _phone_set_incallfilter(agi, cursor, args):
    try:
        user_id = _get_id_of_calling_user(agi)
        new_value = _user_set_service(agi, user_id, 'incallfilter')
    except Exception, e:
        logger.error('Error during setting incallfilter : %s', e)
    else:
        agi.set_variable('XIVO_INCALLFILTERENABLED', int(new_value['enabled']))
        agi.set_variable('XIVO_USERID_OWNER', user_id)


def _phone_set_vm(agi, cursor, args):
    exten = args[1]
    if exten:
        user = _get_user_from_exten(agi, cursor, exten)
    else:
        user = _get_calling_user(agi, cursor)

    vmbox = objects.VMBox(agi, cursor, user.voicemailid, commentcond=False)
    if vmbox.password and user.id != _get_id_of_calling_user(agi):
        agi.appexec('Authenticate', vmbox.password)

    user.toggle_feature('enablevoicemail')

    agi.set_variable('XIVO_VMENABLED', user.enablevoicemail)
    agi.set_variable('XIVO_USERID_OWNER', user.id)


def _user_set_service(agi, user_id, service_name):
    confd_client = agi.config['confd']['client']
    response = confd_client.users(user_id).get_service(service_name)
    new_value = {'enabled': not(response['enabled'])}
    confd_client.users(user_id).update_service(service_name, new_value)
    return new_value


def _get_user_from_exten(agi, cursor, exten):
    context = _get_context_of_calling_user(agi)

    return objects.User(agi, cursor, exten=exten, context=context)


def _get_context_of_calling_user(agi):
    context = agi.get_variable('XIVO_BASE_CONTEXT')
    if not context:
        agi.dp_break('Could not get the context of the caller')
    return context


def _phone_set_unc(agi, cursor, args):
    enabled = _phone_set_forward(agi, 'unconditional', args)
    if enabled is not None:
        agi.set_variable('XIVO_UNCENABLED', int(enabled))


def _phone_set_rna(agi, cursor, args):
    enabled = _phone_set_forward(agi, 'noanswer', args)
    if enabled is not None:
        agi.set_variable('XIVO_RNAENABLED', int(enabled))


def _phone_set_busy(agi, cursor, args):
    enabled = _phone_set_forward(agi, 'busy', args)
    if enabled is not None:
        agi.set_variable('XIVO_BUSYENABLED', int(enabled))


def _phone_set_forward(agi, forward_name, args):
    try:
        user_id = _get_id_of_calling_user(agi)
        result = _user_set_forward(agi, user_id, forward_name, args)
    except Exception, e:
        logger.error('Error during setting %s: %s', forward_name, e)
        return None
    else:
        agi.set_variable('XIVO_USERID_OWNER', user_id)
        return result['enabled']


def _user_set_forward(agi, user_id, forward_name, args):
    enabled = args[1] == '1'
    destination = args[2]
    confd_client = agi.config['confd']['client']
    body = {'enabled': enabled}
    if enabled:
        body['destination'] = destination
    confd_client.users(user_id).update_forward(forward_name, body)
    return body


agid.register(phone_set_feature)
