#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Author:   --<v1ll4n>
  Purpose: Poller
  Created: 08/16/17
"""

from collections import defaultdict
import select

POLLIN = 1
POLLOUT = 2
POLLERR = 4

class Poller(object):
    """"""

    def __init__(self):
        """Constructor"""
        self._inputs = []
        self._outputs = []
        self._errs = []
        
        self._connections = []
    
    def regist(self, socket, flags=POLLIN):
        """"""
        assert flags != 0
        
        if flags & POLLIN:
            if socket not in self._inputs:
                self._inputs.append(socket)
        
        if flags & POLLOUT:
            if socket not in self._outputs:
                self._outputs.append(socket)
                
        if flags & POLLERR:
            if socket not in self._errs:
                self._errs.append(socket)
    
    def unregist(self, socket):
        """"""
        if socket in self._inputs:
            self._inputs.remove(socket)
        
        if socket in self._outputs:
            self._outputs.remove(socket)
            
        if socket in self._errs:
            self._errs.remove(socket)
            
    def poll(self, timeout):
        """"""
        reads, writes, errs = select.select(self._inputs, self._outputs, self._errs, timeout)
        if not (reads or writes, errs):
            return []
        
        _buffers = {}
        flags = 0
        for i in reads:
            flags = _buffers[i] = flags | POLLIN
        
        for i in writes:
            flags = _buffers[i] = flags | POLLOUT
        
        for i in errs:
            flags = _buffers[i] = flags | POLLERR
        
        return _buffers.items()
            
        
        
    
    