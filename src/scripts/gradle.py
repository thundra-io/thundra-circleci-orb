import os
import urllib3
import shutil
import xml.etree.ElementTree as et

from distutils.version import StrictVersion
from typing import Optional

THUNDRA_AGENT_METADATA: str = 'https://repo.thundra.io/service/local/repositories/thundra-releases/content/io/thundra/agent/thundra-agent-bootstrap/maven-metadata.xml'
GRADLE_TEST_PLUGIN: str = 'https://repo1.maven.org/maven2/io/thundra/plugin/thundra-gradle-test-plugin/maven-metadata.xml'


def get_latest_version(repository: str, version: str = None) -> str:
    http = urllib3.PoolManager()
    response = http.request('GET', repository)
    xml = et.fromstring(response.data)

    available_versions = xml.findall('./versioning/versions/version')
    available_versions_set = set(map(lambda x: x.text, available_versions))

    latest_version = xml.find('./versioning/latest').text

    if (version and (version in available_versions_set)):
        return version
    else:
        return latest_version


def instrument(plugin_version: str = None, agent_version: str = None):
    agent_path: str
    http = urllib3.PoolManager()

    gradle_plugin_version: Optional[str] = get_latest_version(
        GRADLE_TEST_PLUGIN,
        plugin_version,
    )
    if not gradle_plugin_version:
        print("> Couldn't find an available version for Thundra Gradle Test Plugin")
        print("> Instrumentation failed!")
        return

    thundra_agent_version: Optional[str] = get_latest_version(
        THUNDRA_AGENT_METADATA,
        agent_version,
    )
    if not thundra_agent_version:
        print("> Couldn't find an available version for Thundra Agent")
        print("> Instrumentation failed!")
        return
    thundra_agent_url = f'https://repo.thundra.io/service/local/repositories/thundra-releases/content/io/thundra/agent/thundra-agent-bootstrap/{thundra_agent_version}/thundra-agent-bootstrap-{thundra_agent_version}.jar'

    if os.environ.get('LOCAL_AGENT_PATH'):
        agent_path = os.environ.get('LOCAL_AGENT_PATH')
        print(f'> Using the local agent at {agent_path}')
    else:
        print("> Downloading the agent...")
        agent_path = '/tmp/thundra-agent-bootstrap.jar'
        with open(agent_path, 'wb') as out:
            r = http.request('GET', thundra_agent_url, preload_content=False)
            shutil.copyfileobj(r, out)
        print(f'> Successfully downloaded the agent to {agent_path}')

    print("> Generating init file...")
    init_file_path = "/tmp/thundra.gradle"
    with open(init_file_path, 'w') as out:
        init_file = f'''initscript {{
    repositories {{
        mavenCentral()
    }}

    dependencies {{
        classpath "io.thundra.plugin:thundra-gradle-test-plugin:{gradle_plugin_version}"
    }}
}}

allprojects {{
    apply plugin: io.thundra.plugin.gradle.ThundraTestPlugin

    repositories {{
        mavenCentral()
    }}

    thundra {{
        agentPath = "{agent_path}"
    }}
}}
'''
        out.write(init_file)
        bash_env_file = os.environ.get("BASH_ENV")
        with open(bash_env_file, "a") as bash_env:
            bash_env.write(
                f'export THUNDRA_GRADLE_INIT_SCRIPT_PATH={init_file_path}'
            )
        print(f'> Successfully generated init file at {init_file_path}')


api_key_env_name = os.environ.get("THUNDRA_APIKEY_ENV_NAME")
if not os.environ.get(api_key_env_name):
    print('> Thundra API Key is not present. Exiting early...')
    print('> Instrumentation failed.')
    exit(0)


project_id_env_name = os.environ.get("THUNDRA_AGENT_TEST_PROJECT_ID_ENV_NAME")
if not os.environ.get(project_id_env_name):
    print('> Thundra Project ID is not present. Exiting early...')
    print('> Instrumentation failed.')
    exit(0)


if os.environ.get('THUNDRA_AGENT_VERSION') and (StrictVersion(os.environ.get('THUNDRA_AGENT_VERSION') < StrictVersion("2.7.0"))):
    print(f'Thundra Java Agent prior to 2.7.0 doesn\'t work with this action')
    exit(0)


def run():
    print(f'> [Thundra] Initializing the Thundra Action...')
    print(f'> Instrumenting the application')
    instrument(os.environ.get('THUNDRA_GRADLE_TEST_PLUGIN_VERSION'),
               os.environ.get('THUNDRA_AGENT_VERSION'))


run()
