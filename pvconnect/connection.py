# BSD 3 - Clause License

# Copyright(c) 2020, Zenotech
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and / or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#         SERVICES
#         LOSS OF USE, DATA, OR PROFITS
#         OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os

from fabric.connection import Connection
from fabric.config import Config

from configparser import ConfigParser


class ConnectionException(Exception):
    """Exception raised for errors with the ssh connection."""

    def __init__(self, msg):
        self.msg = msg


class ConfigurationException(Exception):
    """Exception raised for errors with the client configuration."""

    def __init__(self, msg):
        self.msg = msg


class PVConfig(object):
    """
    Configuration object that can be configured manually or by loading a configuration file
    """

    def __init__(self):
        self.passphrase = None

    def configure(
        self,
        remote_host,
        username,
        cert=None,
        pvserver_command="pvserver",
        pre_script=None,
        direction="reverse",
        cluster=False,
        local_port=11111,
        remote_port_range=(20000, 30000),
        load_ssh_configs=False,
        prompt_for_passphrase=False,
    ):
        self.remote_host = remote_host
        self.username = username
        self.cert = cert
        self.pvserver_command = pvserver_command
        self.direction = direction
        self.cluster = cluster
        self.pre_script = pre_script
        self.local_port = local_port
        self.remote_port_range = remote_port_range
        self.load_ssh_configs = load_ssh_configs
        self.prompt_for_passphrase = prompt_for_passphrase

    def _parse_cert(self, cert_val):
        if os.path.isfile(os.path.expanduser(cert_val)):
            return os.path.expanduser(cert_val)
        else:
            raise ConfigurationException(
                f"Invalid paraview-connect configuration, cannot load certificate {cert_val}"
            )

    def _parse_port_range(self, remote_port_range):
        min, max = remote_port_range.split(":")
        return (int(min), int(max))

    def list_profiles(self, file):
        parser = ConfigParser(allow_no_value=True)
        if os.path.isfile(file):
            parser.read(file)
            for section in parser.sections():
                yield section

    def load_configuration(self, file, config_section):
        parser = ConfigParser(allow_no_value=True)
        if os.path.isfile(file):
            parser.read(file)
            if parser.has_section(config_section):
                self.remote_host = parser.get(config_section, "remote_host")
                self.username = parser.get(config_section, "username")
                self.cert = self._parse_cert(parser.get(config_section, "cert"))
                self.nprocs = parser.getint(config_section, "nprocs")
                self.local_port = parser.getint(config_section, "local_port")
                self.remote_port_range = self._parse_port_range(
                    parser.get(config_section, "remote_port_range")
                )
                self.pre_script = parser.get(config_section, "pre_script")
                self.pvserver_command = parser.get(config_section, "pvserver_command")
                self.load_ssh_configs = parser.getboolean(
                    config_section, "load_ssh_configs"
                )
                self.direction = parser.get(config_section, "direction")
                self.prompt_for_passphrase = parser.getboolean(
                    config_section, "prompt_for_passphrase"
                )
            else:
                raise ConfigurationException(
                    f"Invalid paraview-connect configuration, cannot find profile section {config_section}"
                )
        else:
            raise ConfigurationException(
                f"Invalid paraview-connect configuration file {file}"
            )


class PVConnect(object):
    def __init__(self, pv_config):
        self.config = pv_config
        _conf = Config(lazy=True)
        _conf.load_ssh_config = self.config.load_ssh_configs
        self.conn = Connection(
            config=_conf,
            host=self.config.remote_host,
            user=self.config.username,
            connect_kwargs={
                "look_for_keys": self.config.load_ssh_configs,
                "key_filename": [
                    self.config.cert,
                ],
                "passphrase": self.config.passphrase,
            },
        )

    def get_command_line_forward(self, remote_port):
        if self.config.pre_script:
            return f"{self.config.pre_script}; {self.config.pvserver_command} -sp={remote_port}"
        else:
            return f"{self.config.pvserver_command} -sp={remote_port}"

    def get_command_line_reverse(self, remote_port):
        if self.config.pre_script:
            return f"{self.config.pre_script}; {self.config.pvserver_command} -rc -sp={remote_port}"
        else:
            return f"{self.config.pvserver_command} -rc -sp={remote_port}"

    def is_remote_port_free(self, remote_port):
        try:
            with self.conn.forward_remote(remote_port, self.config.local_port):
                self.conn.run("cd")
                return True
        except Exception as e:
            return False

    def basic_connection_test(self):
        try:
            self.conn.run("cd")
        except Exception as e:
            raise ConnectionException(
                f"Unable to connect to remote host {self.config.remote_host}"
            )

    def select_remote_port(self):
        for port_no in range(
            self.config.remote_port_range[0], self.config.remote_port_range[1]
        ):
            if self.is_remote_port_free(port_no):
                return port_no
        raise ConnectionException(
            f"Unable to find free remote port in range {self.config.remote_port_range}"
        )

    def _run_pvserver_reverse(self, remote_port):
        with self.conn.forward_remote(
            remote_port=remote_port, local_port=self.config.local_port
        ):
            self.conn.run(self.get_command_line_reverse(remote_port))

    def _run_pvserver_forward(self, remote_port):
        with self.conn.forward_local(
            local_port=self.config.local_port, remote_port=remote_port
        ):
            self.conn.run(self.get_command_line_forward(remote_port))

    def run_pvserver(self, remote_port):
        if self.config.direction == "reverse":
            self._run_pvserver_reverse(remote_port)
        elif self.config.direction == "forward":
            self._run_pvserver_forward(remote_port)
        else:
            raise ConfigurationException(
                f"Invalid connection direction specified: {self.config.direction}"
            )
