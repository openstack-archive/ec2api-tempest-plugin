# Copyright 2012 OpenStack Foundation
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


import socket
import time
import warnings

from oslo_log import log as logging

from tempest.lib.common import ssh

from tempest.lib import exceptions

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import paramiko

LOG = logging.getLogger(__name__)

DIS_ALG = dict(pubkeys=['rsa-sha2-256', 'rsa-sha2-512'])


class Client(ssh.Client):

    def _get_ssh_connection(self, sleep=1.5, backoff=1):
        """Returns an ssh connection to the specified host."""
        bsleep = sleep
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        _start_time = time.time()
        if self.pkey is not None:
            LOG.info("Creating ssh connection to '%s:%d' as '%s'"
                     " with public key authentication",
                     self.host, self.port, self.username)
        else:
            LOG.info("Creating ssh connection to '%s:%d' as '%s'"
                     " with password %s",
                     self.host, self.port, self.username, str(self.password))
        attempts = 0
        while True:
            if self.proxy_client is not None:
                proxy_chan = self._get_proxy_channel()
            else:
                proxy_chan = None
            try:
                ssh.connect(self.host, port=self.port,
                        username=self.username,
                        password=self.password,
                        look_for_keys=self.look_for_keys,
                        key_filename=self.key_filename,
                        timeout=self.channel_timeout, pkey=self.pkey,
                        sock=proxy_chan,
                        disabled_algorithms=DIS_ALG)
                LOG.info("ssh connection to %s@%s successfully created",
                         self.username, self.host)
                return ssh
            except (EOFError,
                    socket.error, socket.timeout,
                    paramiko.SSHException) as e:
                ssh.close()
                if self._is_timed_out(_start_time):
                    LOG.exception("Failed to establish authenticated ssh"
                                  " connection to %s@%s after %d attempts. "
                                  "Proxy client: %s",
                                  self.username, self.host, attempts,
                                  self._get_proxy_client_info())
                    raise exceptions.SSHTimeout(host=self.host,
                                                user=self.username,
                                                password=self.password)
                bsleep += backoff
                attempts += 1
                LOG.warning("Failed to establish authenticated ssh"
                            " connection to %s@%s (%s). Number attempts: %s."
                            " Retry after %d seconds.",
                            self.username, self.host, e, attempts, bsleep)
                time.sleep(bsleep)
