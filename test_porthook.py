#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Author:   --<v1ll4n>
  Purpose: Port Hook
  Created: 08/16/17
"""

import socket
import time

from porthook import PortHooker

import unittest

def local_handler(packet):
    """"""
    print('packet passby >>>>>: {}'.format(packet))
    return packet

def remote_handler(packet):
    """"""
    print('packet passby <<<<<: {}'.format(packet))
    return packet

class PortHookTester(unittest.TestCase):
    """"""

    def test_1_smokingtest(self):
        """build hooker and """
        hooker = PortHooker()
        hooker.hook(remote_host='45.78.6.64', 
                    remote_port=80, 
                    local_port=45678,
                    local_hook_callback=local_handler,
                    remote_hook_callback=remote_handler)
        hooker.start()
        
        time.sleep(10)
        hooker.stop()

if __name__ == '__main__':
    unittest.main()