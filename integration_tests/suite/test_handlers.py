# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import pytest
from textwrap import dedent
from hamcrest import assert_that, calling, raises
from .helpers.base import IntegrationTest, use_asset
from .helpers.agid import AGIFailException


@use_asset('base')
class TestHandlers(IntegrationTest):
    def test_monitoring(self):
        recv_vars, recv_cmds = self.agid.monitoring()
        assert recv_cmds['Status'] == 'OK'

    def test_incoming_user_set_features_with_dstid(self):
        with self.db.queries() as queries:
            sip = queries.insert_endpoint_sip()
            user, line, extension = queries.insert_user_line_extension(
                firstname='Firstname',
                lastname='Lastname',
                exten='1801',
                endpoint_sip_uuid=sip['uuid'],
            )

        variables = {
            'XIVO_USERID': user['id'],
            'XIVO_DSTID': user['id'],
            'XIVO_DST_EXTEN_ID': extension['id'],
            'XIVO_CALLORIGIN': 'patate',
            'XIVO_SRCNUM': extension['exten'],
            'XIVO_DSTNUM': 1800,
            'XIVO_BASE_CONTEXT': extension['context'],
            'WAZO_USER_MOH_UUID': '',
            'WAZO_CALL_RECORD_ACTIVE': '0',
            'XIVO_FROMGROUP': '0',
            'XIVO_PATH': '',
            f'PJSIP_ENDPOINT({line["name"]},webrtc)': 'no',
            f'PJSIP_DIAL_CONTACTS({line["name"]})': 'contact',
            'CHANNEL(videonativeformat)': '1',
        }
        recv_vars, recv_cmds = self.agid.incoming_user_set_features(variables=variables)

        assert recv_cmds['FAILURE'] is False

        assert recv_vars['XIVO_DST_USERNUM'] == extension['exten']
        assert recv_vars['WAZO_DST_USER_CONTEXT'] == extension['context']
        assert recv_vars['WAZO_DST_NAME'] == 'Firstname Lastname'
        assert recv_vars['XIVO_DST_REDIRECTING_NAME'] == 'Firstname Lastname'
        assert recv_vars['XIVO_DST_REDIRECTING_NUM'] == extension['exten']
        assert recv_vars['WAZO_DST_UUID'] == user['uuid']
        assert recv_vars['WAZO_DST_TENANT_UUID'] == user['tenant_uuid']
        assert recv_vars['XIVO_INTERFACE'] == 'contact'
        assert recv_vars['XIVO_CALLOPTIONS'] == ''
        assert recv_vars['XIVO_SIMULTCALLS'] == str(user['simultcalls'])
        assert recv_vars['XIVO_RINGSECONDS'] == str(user['ringseconds'])
        assert recv_vars['XIVO_ENABLEDND'] == str(user['enablednd'])
        assert recv_vars['XIVO_ENABLEVOICEMAIL'] == str(user['enablevoicemail'])
        assert recv_vars['XIVO_MAILBOX'] == ''
        assert recv_vars['XIVO_MAILBOX_CONTEXT'] == ''
        assert recv_vars['XIVO_USEREMAIL'] == ''
        assert recv_vars['XIVO_ENABLEUNC'] == str(user['enableunc'])
        assert recv_vars['XIVO_FWD_USER_UNC_ACTION'] == 'none'
        assert recv_vars['XIVO_FWD_USER_UNC_ACTIONARG1'] == ''
        assert recv_vars['XIVO_FWD_USER_UNC_ACTIONARG2'] == ''
        assert recv_vars['XIVO_FWD_USER_BUSY_ACTION'] == 'none'
        assert recv_vars['XIVO_FWD_USER_BUSY_ISDA'] == '1'
        assert recv_vars['XIVO_FWD_USER_BUSY_ACTIONARG1'] == ''
        assert recv_vars['XIVO_FWD_USER_BUSY_ACTIONARG2'] == ''
        assert recv_vars['XIVO_FWD_USER_NOANSWER_ACTION'] == 'none'
        assert recv_vars['XIVO_FWD_USER_NOANSWER_ISDA'] == '1'
        assert recv_vars['XIVO_FWD_USER_NOANSWER_ACTIONARG1'] == ''
        assert recv_vars['XIVO_FWD_USER_NOANSWER_ACTIONARG2'] == ''
        assert recv_vars['XIVO_FWD_USER_CONGESTION_ACTION'] == 'none'
        assert recv_vars['XIVO_FWD_USER_CONGESTION_ISDA'] == '1'
        assert recv_vars['XIVO_FWD_USER_CONGESTION_ACTIONARG1'] == ''
        assert recv_vars['XIVO_FWD_USER_CONGESTION_ACTIONARG2'] == ''
        assert recv_vars['XIVO_FWD_USER_CHANUNAVAIL_ACTION'] == 'none'
        assert recv_vars['XIVO_FWD_USER_CHANUNAVAIL_ISDA'] == '1'
        assert recv_vars['XIVO_FWD_USER_CHANUNAVAIL_ACTIONARG1'] == ''
        assert recv_vars['XIVO_FWD_USER_CHANUNAVAIL_ACTIONARG2'] == ''
        assert recv_vars['CHANNEL(musicclass)'] == user['musiconhold']
        assert recv_vars['WAZO_CALL_RECORD_SIDE'] == 'caller'
        assert recv_vars['XIVO_USERPREPROCESS_SUBROUTINE'] == ''
        assert recv_vars['XIVO_MOBILEPHONENUMBER'] == ''
        assert recv_vars['WAZO_VIDEO_ENABLED'] == '1'
        assert recv_vars['XIVO_PATH'] == 'user'
        assert recv_vars['XIVO_PATH_ID'] == str(user['id'])

    def test_agent_get_options(self):
        with self.db.queries() as queries:
            agent = queries.insert_agent()

        recv_vars, recv_cmds = self.agid.agent_get_options(
            agent['tenant_uuid'],
            agent['number'],
        )

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_AGENTEXISTS'] == '1'
        assert recv_vars['XIVO_AGENTPASSWD'] == ''
        assert recv_vars['XIVO_AGENTID'] == str(agent['id'])
        assert recv_vars['XIVO_AGENTNUM'] == agent['number']
        assert recv_vars['CHANNEL(language)'] == agent['language']

    @pytest.mark.skip('NotImplemented: need agentd mock')
    def test_agent_get_status(self):
        with self.db.queries() as queries:
            agent = queries.insert_agent()

        recv_vars, recv_cmds = self.agid.agent_get_status(
            agent['tenant_uuid'],
            agent['id'],
        )

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_AGENT_LOGIN_STATUS'] == 'logged_in'

    @pytest.mark.skip('NotImplemented: need agentd mock')
    def test_agent_login(self):
        with self.db.queries() as queries:
            agent = queries.insert_agent()
            extension = queries.insert_extension()

        recv_vars, recv_cmds = self.agid.agent_login(
            agent['tenant_uuid'],
            agent['id'],
            extension['exten'],
            extension['context'],
        )

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_AGENTSTATUS'] == 'logged'

    @pytest.mark.skip('NotImplemented: need agentd mock')
    def test_agent_logoff(self):
        with self.db.queries() as queries:
            agent = queries.insert_agent()

        recv_vars, recv_cmds = self.agid.agent_logoff(
            agent['tenant_uuid'],
            agent['id'],
        )

        assert recv_cmds['FAILURE'] is False

    def test_callback(self):
        pytest.xfail("Will fail until Wazo-578 is fixed")

        with self.db.queries() as queries:
            extension = queries.insert_extension()

        extension_number, context = extension['exten'], extension['context']
        variables = {
            'XIVO_SRCNUM': extension_number,
            'AST_CONFIG(asterisk.conf,directories,astspooldir)': '/var/spool/asterisk',
        }
        chown = f"asterisk:asterisk"
        self.filesystem.create_path('/var/spool/asterisk/tmp', chown=chown)
        self.filesystem.create_path('/var/spool/asterisk/outgoing', chown=chown)

        recv_vars, recv_cmds = self.agid.callback(context, variables=variables)
        assert recv_cmds['FAILURE'] is False

        file_name = self.filesystem.find_file('/var/spool/asterisk/outgoing/', f'{extension_number}-*.call')
        assert file_name
        assert self.filesystem.read_file(file_name) == dedent(f"""\
            Channel: Local/{extension_number}@{context}
            MaxRetries: 0
            RetryTime: 30
            WaitTime: 30
            CallerID: {extension_number}
            Set: XIVO_DISACONTEXT={context}
            Context: xivo-callbackdisa
            Extension: s
        """).strip('\n')

    def test_callerid_extend(self):
        recv_vars, recv_cmds = self.agid.callerid_extend('en')

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_SRCTON'] == 'en'

    def test_callerid_forphones_without_reverse_lookup(self):
        recv_vars, recv_cmds = self.agid.callerid_forphones(
            calleridname='name',
            callerid='numero',
        )

        assert recv_cmds['FAILURE'] is False

    def test_callfilter(self):
        with self.db.queries() as queries:
            user = queries.insert_user()
            call_filter = queries.insert_call_filter()
            call_filter_member = queries.insert_call_filter_member(
                type='user', typeval=user['id'], callfilterid=call_filter['id'], active=1
            )

        variables = {
            'XIVO_USERID': user['id'],
        }
        recv_vars, recv_cmds = self.agid.callfilter(call_filter_member['id'], variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_BSFILTERENABLED'] == '0'

    @pytest.mark.skip('NotImplemented')
    def test_call_recording(self):
        pass

    def test_check_diversion_hold_time(self):
        queue_name = 'queue-wait-time'
        with self.db.queries() as queries:
            queue = queries.insert_queue_feature(name=queue_name, waittime=5)

        variables = {
            'XIVO_DSTID': queue['id'],
            f'QUEUE_WAITING_COUNT({queue_name})': '1',
            'QUEUEHOLDTIME': '6'
        }

        recv_vars, recv_cmds = self.agid.check_diversion(variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_DIVERT_EVENT'] == 'DIVERT_HOLDTIME'
        assert recv_vars['XIVO_FWD_TYPE'] == 'QUEUE_QWAITTIME'

    def test_check_diversion_wait_ratio(self):
        queue_name = 'queue-wait-ratio'
        with self.db.queries() as queries:
            queue = queries.insert_queue_feature(name=queue_name, waitratio=1.2)

        variables = {
            'XIVO_DSTID': queue['id'],
            f'QUEUE_WAITING_COUNT({queue_name})': '2',
            f'QUEUE_MEMBER({queue_name},logged)': '2',
        }

        recv_vars, recv_cmds = self.agid.check_diversion(variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_DIVERT_EVENT'] == 'DIVERT_CA_RATIO'
        assert recv_vars['XIVO_FWD_TYPE'] == 'QUEUE_QWAITRATIO'

    def test_check_schedule(self):
        with self.db.queries() as queries:
            user = queries.insert_user()
            schedule = queries.insert_schedule()
            schedule_path = queries.insert_schedule_path(schedule_id=schedule['id'], pathid=user['id'])
            queries.insert_schedule_time(mode='closed', schedule_id=schedule['id'])

        variables = {
            'XIVO_PATH': schedule_path['path'],
            'XIVO_PATH_ID': str(schedule_path['path_id']),
        }

        recv_vars, recv_cmds = self.agid.check_schedule(variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_SCHEDULE_STATUS'] == 'closed'
        assert recv_vars['XIVO_PATH'] == ''

    def test_convert_pre_dial_handler(self):
        variables = {
            'XIVO_CALLOPTIONS': 'Xb(foobaz^s^1)B(foobar^s^1)',
        }

        recv_vars, recv_cmds = self.agid.convert_pre_dial_handler(variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_CALLOPTIONS'] == 'XB(foobar^s^1)'
        assert recv_vars['PUSH(_WAZO_PRE_DIAL_HANDLERS,|)'] == 'foobaz,s,1'

    @pytest.mark.skip('NotImplemented')
    def test_fwdundoall(self):
        pass

    def test_getring(self):
        ring_config_path = '/etc/xivo/asterisk/xivo_ring.conf'
        variables = {
            'XIVO_REAL_NUMBER': '1001',
            'XIVO_REAL_CONTEXT': 'default',
            'XIVO_CALLORIGIN': 'patate',
            'XIVO_FWD_REFERER': 'foo:bar',
            'XIVO_CALLFORWARDED': '1',
        }
        self.filesystem.write_file(path=ring_config_path, content=dedent('''
        [number]
        1001@default = linksys
        @default     = linksys
        
        [linksys]
        phonetype = linksys
        intern = Office
        extern = Classic-1
        group = Simple-3
        foo@patate&forwarded = test-ring
        '''))
        self.asset_cls.restart_service('agid')
        self.reset_clients()
        self.agid.wait_until_ready()

        recv_vars, recv_cmds = self.agid.getring(variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_PHONETYPE'] == 'linksys'
        assert recv_vars['XIVO_RINGTYPE'] == 'test-ring'

        self.filesystem.write_file(path=ring_config_path, content='')

    def test_get_user_interfaces(self):
        with self.db.queries() as queries:
            user, line_1, extension_1 = queries.insert_user_line_extension(
                exten='1802',
                endpoint_sip_uuid=queries.insert_endpoint_sip()['uuid'],
            )
            line_2 = queries.insert_line(typeval=user['id'])
            queries.insert_user_line(user['id'], line_2['id'])

        variables = {
            f'HINT({user["uuid"]}@usersharedlines)': f'sccp/{line_1["name"]}&pjsip/{line_2["name"]}',
            f'PJSIP_ENDPOINT({line_2["name"]},webrtc)': 'no',
            f'PJSIP_DIAL_CONTACTS({line_2["name"]})': 'contact',
        }
        recv_vars, recv_cmds = self.agid.get_user_interfaces(user['uuid'], variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_USER_INTERFACES'] == f'sccp/{line_1["name"]}&contact'

    @pytest.mark.skip('NotImplemented')
    def test_group_answered_call(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_group_member(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_handler_fax(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_in_callerid(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_incoming_agent_set_features(self):
        pass

    def test_incoming_conference_set_features(self):
        name = u'My Conférence'
        with self.db.queries() as queries:
            conference = queries.insert_conference(name=name)

        variables = {
            'XIVO_DSTID': conference['id'],
        }
        recv_vars, recv_cmds = self.agid.incoming_conference_set_features(variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_CONFBRIDGE_ID'] == str(conference['id'])
        assert recv_vars['WAZO_CONFBRIDGE_TENANT_UUID'] == conference['tenant_uuid']
        assert recv_vars['WAZO_CONFBRIDGE_BRIDGE_PROFILE'] == f'xivo-bridge-profile-{conference["id"]}'
        assert recv_vars['WAZO_CONFBRIDGE_USER_PROFILE'] == f'xivo-user-profile-{conference["id"]}'
        assert recv_vars['WAZO_CONFBRIDGE_MENU'] == 'xivo-default-user-menu'
        assert recv_vars['WAZO_CONFBRIDGE_PREPROCESS_SUBROUTINE'] == ''
        assert recv_cmds['EXEC CELGenUserEvent'] == 'WAZO_CONFERENCE, NAME: {}'.format(name)

    def test_incoming_did_set_features(self):
        with self.db.queries() as queries:
            incall = queries.insert_incall(preprocess_subroutine='test-subroutine')

        variables = {
            'XIVO_INCALL_ID': incall['id'],
            'XIVO_DSTID': incall['id'],
        }
        recv_vars, recv_cmds = self.agid.incoming_conference_set_features(variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_CONFBRIDGE_ID'] == str(incall['id'])
        assert recv_vars['WAZO_CONFBRIDGE_TENANT_UUID'] == incall['tenant_uuid']
        assert recv_vars['WAZO_CONFBRIDGE_BRIDGE_PROFILE'] == f'xivo-bridge-profile-{incall["id"]}'
        assert recv_vars['WAZO_CONFBRIDGE_USER_PROFILE'] == f'xivo-user-profile-{incall["id"]}'
        assert recv_vars['WAZO_CONFBRIDGE_MENU'] == 'xivo-default-user-menu'
        assert recv_vars['WAZO_CONFBRIDGE_PREPROCESS_SUBROUTINE'] == ''

    @pytest.mark.skip('NotImplemented')
    def test_incoming_group_set_features(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_incoming_queue_set_features(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_outgoing_user_set_features(self):
        pass

    def test_meeting_user(self):
        with self.db.queries() as queries:
            meeting = queries.insert_meeting()

        variables = {
            'WAZO_TENANT_UUID': meeting['tenant_uuid'],
        }

        # Lookup by UUID
        recv_vars, recv_cmds = self.agid.meeting_user(
            'wazo-meeting-{uuid}'.format(**meeting),
            variables=variables,
        )

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_MEETING_NAME'] == meeting['name']
        assert recv_vars['WAZO_MEETING_UUID'] == meeting['uuid']

        # Lookup by number
        recv_vars, recv_cmds = self.agid.meeting_user(
            meeting['number'],
            variables=variables,
        )

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_MEETING_NAME'] == meeting['name']
        assert recv_vars['WAZO_MEETING_UUID'] == meeting['uuid']

    @pytest.mark.skip('NotImplemented')
    def test_paging(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_phone_get_features(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_phone_progfunckey_devstate(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_phone_progfunckey(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_provision(self):
        pass

    @pytest.mark.skip('NotImplemented')
    def test_queue_answered_call(self):
        pass

    def test_queue_skill_rule_set(self):
        with self.db.queries() as queries:
            skill_rule = queries.insert_queue_skill_rule()

        recv_vars, recv_cmds = self.agid.queue_skill_rule_set('queue_skill_rule_set', variables={
            'ARG2': f'timeout;{skill_rule["id"]};{{"opt1":1|"opt2": "val2"}}',
            'XIVO_QUEUESKILLRULESET': 'call'
        })

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_QUEUESKILLRULESET'] == f'skillrule-{skill_rule["id"]}(opt1=1,opt2=val2)'
        assert recv_vars['ARG2_TIMEOUT'] == 'timeout'

    def test_switchboard_set_features_no_switchboard(self):
        assert_that(
            calling(self.agid.switchboard_set_features).with_args('switchboard-not-found'),
            raises(AGIFailException)
        )

    def test_switchboard_set_features_fallback_no_fallback(self):
        with self.db.queries() as queries:
            switchboard = queries.insert_switchboard()

        recv_vars, recv_cmds = self.agid.switchboard_set_features(switchboard['uuid'])

        assert recv_cmds['FAILURE'] is False
        # resetting those variables is important when chaining switcbhoard forwards
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTION'] == ''
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTIONARG1'] == ''
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTIONARG2'] == ''

    def test_switchboard_set_features_with_fallback(self):
        with self.db.queries() as queries:
            fallbacks = {
                'noanswer': {'event': 'noanswer', 'action': 'user', 'actionarg1': '1', 'actionarg2': '2'}
            }
            switchboard = queries.insert_switchboard(fallbacks=fallbacks)

        recv_vars, recv_cmds = self.agid.switchboard_set_features(switchboard['uuid'])

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTION'] == 'user'
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTIONARG1'] == '1'
        assert recv_vars['WAZO_SWITCHBOARD_FALLBACK_NOANSWER_ACTIONARG2'] == '2'
        assert recv_vars['WAZO_SWITCHBOARD_TIMEOUT'] == ''

    def test_switchboard_set_features_with_timeout(self):
        with self.db.queries() as queries:
            switchboard = queries.insert_switchboard(timeout=42)

        recv_vars, recv_cmds = self.agid.switchboard_set_features(switchboard['uuid'])

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['WAZO_SWITCHBOARD_TIMEOUT'] == '42'

    def test_user_get_vmbox(self):
        with self.db.queries() as queries:
            context = 'test-context'
            voicemail = queries.insert_voicemail(context=context, skipcheckpass='1')
            user, line, extension = queries.insert_user_line_extension(
                enablevoicemail=1, voicemail_id=voicemail['id'], context=context,
            )

        variables = {
            'XIVO_USERID': user['id'],
            'XIVO_BASE_CONTEXT': context,
        }
        recv_vars, recv_cmds = self.agid.user_get_vmbox(extension['exten'], variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_VMMAIN_OPTIONS'] == 's'
        assert recv_vars['XIVO_MAILBOX'] == voicemail['mailbox']
        assert recv_vars['XIVO_MAILBOX_CONTEXT'] == context

    @pytest.mark.skip('NotImplemented')
    def test_user_set_call_rights(self):
        pass

    def test_vmbox_get_info(self):
        with self.db.queries() as queries:
            context = 'default'
            voicemail = queries.insert_voicemail(context=context, skipcheckpass='1')
            user, line, extension = queries.insert_user_line_extension(
                enablevoicemail=1, voicemail_id=voicemail['id'], context=context
            )

        variables = {
            'XIVO_USERID': user['id'],
            'XIVO_VMBOXID': voicemail['id'],
            'XIVO_BASE_CONTEXT': context,
        }
        recv_vars, recv_cmds = self.agid.vmbox_get_info(voicemail['mailbox'], variables=variables)

        assert recv_cmds['FAILURE'] is False
        assert recv_vars['XIVO_VMMAIN_OPTIONS'] == 's'
        assert recv_vars['XIVO_MAILBOX'] == voicemail['mailbox']
        assert recv_vars['XIVO_MAILBOX_CONTEXT'] == context
        assert recv_vars['XIVO_MAILBOX_LANGUAGE'] == 'fr_FR'

    @pytest.mark.skip('NotImplemented')
    def test_wake_mobile(self):
        pass
