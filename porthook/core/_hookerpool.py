#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Author:   --<v1ll4n>
  Purpose: Hooker Pool
  Created: 08/16/17
"""

import socket

class _EntryPool(object):
    """"""

    def __init__(self, port_hooker_ins):
        """Constructor"""
        #assert isinstance(port_hooker_ins, PortHooker), 'not a valid instance.'
        
        self.master = port_hooker_ins
        self._entry_map = {}
        
    def regist_entry(self, local_port, exposed=False, backlog=10):
        """"""
        assert isinstance(local_port, int), 'local port shell be a int.'
        assert isinstance(backlog, int)
        
        if exposed:
            local_addr = ('0.0.0.0', local_port)
        else:
            local_addr = ('127.0.0.1', local_port)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.bind(local_addr)
        
        sock.listen(backlog)
        self.master.poller.regist(sock)
        
        #
        # record index
        #
        self._entry_map[local_port] = sock
        self._entry_map[sock] = local_port
        
        return sock
    
    def unregist_entry(self, key):
        """"""
        if key in self._entry_map:
            _key2 = self._entry_map.pop(key)
            if isinstance(key, int):
                sock = _key2
            else:
                sock = key
            self._entry_map.pop(_key2)
            
            self.master.poller.unregist(sock)
        
    
    def __contains__(self, subsocket):
        """"""
        return subsocket in self._entry_map

    def get_localport_by_socket(self, sock):
        """"""
        return self._entry_map.get(sock)
    
class _OutputPool(object):
    """"""

    def __init__(self, port_hooker_ins):
        """Constructor"""
        #assert isinstance(port_hooker_ins, PortHooker), 'not a valid instance.'
        
        self.master = port_hooker_ins
        self._output_map = {}
        
    def regist_output(self, local_port, dest_host, dest_port):
        """"""
        assert isinstance(local_port, int)
        assert isinstance(dest_port, int)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((dest_host, dest_port))
        sock.setblocking(False)
        
        self.master.poller.regist(sock)
        
        self._output_map[local_port] = sock
        self._output_map[sock] = local_port
        
        return sock
    
    def unregist(self, key):
        """"""
        if key in self._output_map:
            k2 = self._output_map.get(key)
            if isinstance(key, int):
                port = key
            else:
                sock = key
            self._output_map.pop(key)
            self._output_map.pop(k2)
            self.master.poller.unregist(sock)
            
        
    
    def get_socket_by_localport(self, localport):
        """"""
        return self._output_map.get(localport)
    
    def __contains__(self, subsock):
        """"""
        return subsock in self._output_map.values()
        