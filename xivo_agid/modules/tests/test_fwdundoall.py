# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock
from xivo_agid.modules.fwdundoall import fwdundoall


class TestFwdUndoAll(unittest.TestCase):

    def test_that_fwdundoall_call_confd(self):
        self._client = Mock().return_value
        user_id = 2
        agi = Mock()
        agi.get_variable.return_value = user_id
        agi.config = {'confd': {'client': self._client}}

        fwdundoall(agi, None, None)

        disabled = {'enabled': False}
        expected_body = {'busy': disabled,
                         'noanswer': disabled,
                         'unconditional': disabled}

        self._client.users(user_id).update_forwards.assert_called_once_with(expected_body)
