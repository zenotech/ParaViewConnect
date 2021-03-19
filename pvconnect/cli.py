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
import errno
from pathlib import Path
from configparser import ConfigParser
import click

from .connection import PVConnect, PVConfig, ConfigurationException


@click.group()
@click.pass_context
def main(ctx):
    """Paraview Connect - Simple helper tool to connect to remote Paraview sessions"""
    click.secho("Paraview Connect", fg="green")
    click.secho("----------------", fg="green")


@main.command()
@click.pass_context
def configure(ctx):
    """ Configure the Paraview CLI tool """
    click.echo("Configuring Paraview Connect")
    config_file = os.path.join(Path.home(), ".paraview-connect", "config")
    config = ConfigParser()
    if os.path.isfile(config_file):
        config.read(config_file)
    if not config.defaults():
        click.secho("Adding defaults")
        config.set("DEFAULT", "cert", "~/.ssh/id_rsa")
        config.set("DEFAULT", "pvserver_command", "pvserver")
        config.set("DEFAULT", "pre_script", "None")
        config.set("DEFAULT", "direction", "reverse")
        config.set("DEFAULT", "cluster", "False")
        config.set("DEFAULT", "local_port", "11111")
        config.set("DEFAULT", "remote_port_range", "12000:13000")
        config.set("DEFAULT", "nprocs", "1")
        config.set("DEFAULT", "load_ssh_configs", "False")

    remote_hostname = click.prompt("Hostname or IP to connect to")
    username = click.prompt("Username on remote system")
    cert = click.prompt(
        "Certificate to connect with", default=config.get("DEFAULT", "cert")
    )
    local_port = click.prompt(
        "Local port to use for connection", default=config.get("DEFAULT", "local_port")
    )
    nprocs = click.prompt(
        "Number of MPI processes to use", default=config.get("DEFAULT", "nprocs")
    )
    pvserver_command = click.prompt(
        "Paraview server command", default=config.get("DEFAULT", "pvserver_command")
    )
    pre_script = click.prompt(
        "Pre script to run before paraview server",
        default=config.get("DEFAULT", "pre_script"),
    )
    profile = click.prompt("Name of profile to store config as")
    if not config.has_section(profile):
        config.add_section(profile)
    config.set(profile, "remote_host", remote_hostname)
    config.set(profile, "username", username)
    if cert != config.get("DEFAULT", "cert"):
        config.set(profile, "cert", cert)
    if local_port != config.get("DEFAULT", "local_port"):
        config.set(profile, "local_port", local_port)
    if pvserver_command != config.get("DEFAULT", "pvserver_command"):
        config.set(profile, "pvserver_command", pvserver_command)
    if pre_script != config.get("DEFAULT", "pre_script"):
        config.set(profile, "pre_script", pre_script)
    try:
        os.makedirs(os.path.dirname(config_file))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    with open(config_file, "w") as configfile:
        config.write(configfile)
        click.echo("Config file written to %s" % config_file)


@main.command()
@click.pass_context
@click.option(
    "--remote",
    prompt="Hostname or IP of remote server",
    help="Hostname or IP of remote server",
)
@click.option(
    "--username",
    prompt="Username on remote system",
    help="Username on remote system",
)
@click.option(
    "--n",
    default=1,
    help="Number of MPI processes for pvserver, set to 1 for non-parallel",
    show_default=True,
)
@click.option(
    "--local_port",
    default=11111,
    help="Port to use on local machine",
    show_default=True,
)
@click.option(
    "--remote_port",
    default=11111,
    help="Port to use on remote machine",
    show_default=True,
)
@click.option(
    "--cert",
    default="~/.ssh/id_rsa",
    show_default=True,
    help="Certificate to use when connecting",
)
@click.option(
    "--pvserver_command",
    default="pvserver",
    show_default=True,
    help="Path to the pvserver executable on the remote system",
)
@click.option(
    "--pre_script",
    default=None,
    show_default=True,
    help="Command to run prior to launching pvserver, for example to source an environment",
)
@click.option(
    "--direction",
    default="REVERSE",
    show_default=True,
    help="Type of ssh connection",
    type=click.Choice(["reverse", "forward"], case_sensitive=False),
)
@click.option(
    "--cluster",
    help="Submit a pvserver job to a remote cluster",
    show_default=True,
    is_flag=True,
)
def connect(
    ctx,
    remote,
    username,
    n,
    local_port,
    remote_port,
    cert,
    pre_script,
    pre,
    direction,
    cluster,
):
    """ Create a new connection based on session """
    click.secho(f"Establising connection to {username}@{remote}...", fg="green")
    config = PVConfig()
    config.configure(
        remote,
        username,
        cert,
        pre_script,
        pre,
        direction,
        cluster,
        local_port,
        remote_port,
    )
    click.secho(
        f"Local connection will be available on localhost:{config.local_port}",
        fg="green",
    )
    pv = PVConnect(config)
    remote_port = pv.select_remote_port()
    click.secho(
        f"Using remote port {remote_port}",
        fg="green",
    )
    pv.run_pvserver(remote_port)
    click.secho(
        f"All done",
        fg="green",
    )


@main.command()
@click.pass_context
@click.argument("profile")
@click.option(
    "-c",
    "--config",
    default="~/.paraview-connect/config",
    show_default=True,
    help="Configuration file to load",
)
def run(ctx, profile, config):
    """ Run paraview connect config with PROFILE stored in config file """
    config_file = os.path.join(Path.home(), ".paraview-connect", "config")
    if config is not None:
        if os.path.isfile(os.path.expanduser(config)):
            config_file = os.path.expanduser(config)
        else:
            click.secho(
                "Config file %s not found, please run configure." % config, fg="red"
            )
            exit(1)
    try:
        click.secho("Loading config from %s" % config_file, fg="green")
        config = PVConfig()
        config.load_configuration(config_file, profile)
        click.secho(
            f"Establising connection to {config.username}@{config.remote_host}...",
            fg="green",
        )
        click.secho(
            f"Local connection will be established on localhost:{config.local_port}",
            fg="green",
        )
        pv = PVConnect(config)
        remote_port = pv.select_remote_port()
        click.secho(
            f"Using remote port {remote_port} on {config.remote_host}",
            fg="green",
        )
        pv.run_pvserver(remote_port)
        click.secho(
            f"All done",
            fg="green",
        )
    except ConfigurationException as e:
        click.secho(
            f"Configuration file not found or invalid, please run configure. {e.msg}",
            fg="red",
        )
        exit(1)


if __name__ == "__main__":
    main()
