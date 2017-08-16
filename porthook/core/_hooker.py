#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  Author:   --<v1ll4n>
  Purpose: 
  Created: 08/16/17
"""

import socket
from threading import Thread

from ._poller import Poller
from ._hookerpool import _EntryPool, _OutputPool

class PortHooker(Thread):
    """Hook Ports"""

    def __init__(self, **config):
        """Constructor"""
        Thread.__init__(self, name='porthooker')
        
        self._config = config
        
        # poller
        self.poller = Poller()
        
        self.entry_pool = _EntryPool(self)
        self.output_pool = _OutputPool(self)
        
        self.connections = []
        self.server_connections_map = {}
        self.connection_map_port = {}
        self.maps = {}
        self.port_maps = {}
        
        self._working = False
    
    def hook(self, remote_host, remote_port, local_port, 
             local_hook_callback=None,
             remote_hook_callback=None, 
             exposed=False, localbacklog=10,
             **kw):
        """"""
        #try:
            #entry = self.output_pool.regist_output(local_port, remote_host, remote_port)
        #except ConnectionRefusedError:
            #return False
        if local_port not in self.port_maps:
            self.port_maps[local_port] = {}
        
        self.port_maps[local_port]['addr'] = (remote_host, remote_port)
        self.port_maps[local_port]['remote_hook_callback'] = remote_hook_callback
        self.port_maps[local_port]['local_hook_callback'] = local_hook_callback
        
        self.entry_pool.regist_entry(local_port, exposed, localbacklog)
    
    def run(self):
        """"""
        self._working = True
        while self._working:
            for sock, flags in self.poller.poll(0):
                if sock in self.entry_pool:
                    connection, client_addr = sock.accept()
                    print('connection {} client_addr {}'.format(connection, client_addr))
                    localport = self.entry_pool.get_localport_by_socket(sock)
                    remote_addr = self.port_maps.get(localport, {}).get('addr')
                    if not remote_addr:
                        connection.close()
                    _sock = self.output_pool.regist_output(localport,
                                                           remote_addr[0],
                                                           remote_addr[1])
                    if not _sock:
                        connection.close()
                    
                    self.server_connections_map[connection] = sock
                    self.connection_map_port[connection] = self.entry_pool.get_localport_by_socket(
                        sock
                    )
                    self.connections.append(connection)
                    self.connections.append(_sock)
                    self.create_bind(_sock, connection)
                    self.poller.regist(sock)
                    self.poller.regist(connection)
                
                if sock in self.connections:
                    data = b''
                    while True:
                        try:
                            buffer = sock.recv(1024)
                        except ConnectionResetError:
                            self.clean_sock(sock)
                            break
                        
                        data = data + buffer
                        if len(buffer) < 1024:
                            break
                    
                    dsock = self.get_peer_sock(sock)
                    if dsock:
                        if data != b'':
                            #
                            # hook me
                            #
                            localport = self.connection_map_port.get(dsock)
                            if not localport:
                                localport = self.connection_map_port.get(self.get_peer_sock(
                                    dsock))
                            
                            if dsock in self.server_connections_map:
                                oc = self.port_maps.get(localport, {}).get('remote_hook_callback')
                                if oc:
                                    data = oc(data)
                            else:
                                ic = self.port_maps.get(localport, {}).get('local_hook_callback')
                                if ic:
                                    data = ic(data)
                            
                            dsock.send(data)
                        else:
                            pass
                    else:
                        self.clean_sock(sock)
        
    def get_peer_sock(self, conn):
        """"""
        return self.maps.get(conn)
        
    
    def create_bind(self, conn1, conn2):
        """"""
        self.maps[conn1] = conn2
        self.maps[conn2] = conn1        
    
    def clean_sock(self, sock):
        """"""
        self.poller.unregist(sock)
        
        sock.close()
        if sock in self.connections:
            self.connections.remove(sock)
            
        _k = self.maps.pop(sock, 0)
        self.maps.pop(_k, 0)
        self.server_connections_map.pop(_k, 0)
        self.server_connections_map.pop(sock, 0)
        self.connection_map_port.pop(sock, 0)
    
    def stop(self):
        """"""
        self._working = False
        self.join()
    
        
        
                
    
    