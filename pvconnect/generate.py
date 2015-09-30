#
# Auto Generate servers.pvsc file
#
#
from string import Template


def generate_pvsc(username, servername, ssh_key, remote_paraview):

	script = Template(r"""
<Servers>
  <Server name="autoremote" configuration="" resource="csrc://autoremote">
    <CommandStartup>
      <Options>
        <Option name="PV_SERVER_PORT" label="Server Port: ">
          <Range type="int" min="1" max="65535" step="1" default="11111"/>
        </Option>
        <Option name="LAUNCHER" label="launcher location" save="true">
          <String default="/usr/local/bin"/>
        </Option>
        <Option name="JOB_NTASKS" label="No of tasks" save="true">
          <String default="1"/>
        </Option>
      </Options>
      <Command exec="$$LAUNCHER$$/pvserver_launcher.bsh" delay="5">
        <Arguments>
          <Argument value="$$PV_SERVER_PORT$$"/>
          <Argument value="$DATA_HOST"/>
          <Argument value="$REMOTE_PARAVIEW_HOME"/>
          <Argument value="$$JOB_NTASKS$$"/>
        </Arguments>
      </Command>
    </CommandStartup>
  </Server>
</Servers>
""")
	script_str = script.substitute({'DATA_HOST': username+'@'+servername,
                                    'REMOTE_PARAVIEW_HOME': remote_paraview,
                                    })

	return script_str
