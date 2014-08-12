# -*- coding: utf-8 -*-

# Copyright (C) 2012-2014 Avencall
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

from xivo_bus.resources.agent import error
from xivo_bus.resources.agent.client import AgentClient
from xivo_bus.resources.agent.exception import AgentClientError

AGENTSTATUS_VAR = 'XIVO_AGENTSTATUS'

_agent_client = AgentClient()


def _setup_client(fun):
    def aux(*args, **kwargs):
        if not _agent_client.connected:
            _agent_client.connect()
        return fun(*args, **kwargs)
    return aux


@_setup_client
def login_agent(agi, agent_id, extension, context):
    try:
        _agent_client.login_agent(agent_id, extension, context)
    except AgentClientError as e:
        if e.error == error.ALREADY_LOGGED:
            agi.set_variable(AGENTSTATUS_VAR, 'already_logged')
        elif e.error == error.ALREADY_IN_USE:
            agi.set_variable(AGENTSTATUS_VAR, 'already_in_use')
        else:
            raise
    else:
        agi.set_variable(AGENTSTATUS_VAR, 'logged')


@_setup_client
def logoff_agent(agi, agent_id):
    try:
        _agent_client.logoff_agent(agent_id)
    except AgentClientError as e:
        if e.error != error.NOT_LOGGED:
            raise


@_setup_client
def get_agent_status(agi, agent_id):
    status = _agent_client.get_agent_status(agent_id)
    login_status = 'logged_in' if status.logged else 'logged_out'
    agi.set_variable('XIVO_AGENT_LOGIN_STATUS', login_status)
