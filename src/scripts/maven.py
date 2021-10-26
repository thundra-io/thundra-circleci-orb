import os
import urllib3
import shutil
import subprocess
import xml.etree.ElementTree as et

from distutils.version import StrictVersion
from typing import Optional

THUNDRA_AGENT_METADATA: str = 'https://repo.thundra.io/service/local/repositories/thundra-releases/content/io/thundra/agent/thundra-agent-bootstrap/maven-metadata.xml'
MAVEN_INSTRUMENTATION_METADATA: str = 'https://repo1.maven.org/maven2/io/thundra/plugin/thundra-agent-maven-test-instrumentation/maven-metadata.xml'


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


def instrument(instrumenter_version: str = None, agent_version: str = None):
    agent_path: str
    maven_instrumenter_path: str
    http = urllib3.PoolManager()

    maven_instrumenter_version: Optional[str] = get_latest_version(
        MAVEN_INSTRUMENTATION_METADATA,
        instrumenter_version,
    )
    if not maven_instrumenter_version:
        print(
            "> Couldn't find an available version for Thundra Maven Instrumentation script")
        print("> Instrumentation failed!")
        return
    maven_instrumenter_url = f'https://repo1.maven.org/maven2/io/thundra/plugin/thundra-agent-maven-test-instrumentation/{maven_instrumenter_version}/thundra-agent-maven-test-instrumentation-{maven_instrumenter_version}.jar'

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

    print("> Downloading the maven instrumentater")
    maven_instrumenter_path = f'/tmp/thundra-agent-maven-test-instrumentation-{maven_instrumenter_version}.jar'
    with open(maven_instrumenter_path, 'wb') as out:
        r = http.request('GET', maven_instrumenter_url, preload_content=False)
        shutil.copyfileobj(r, out)
    print(f'> Successfully downloaded the agent to {maven_instrumenter_path}')

    print("> Updating pom.xml...")
    poms = subprocess.run(
        ['sh', '-c', f'find . -name "pom.xml" -exec echo \'{{}}\' +'], capture_output=True)

    if poms.stdout:
        subprocess.call(['java', '-jar', maven_instrumenter_path,
                         agent_path, str(poms.stdout.strip(), 'utf-8')])
        print("> Update to pom.xml is done")
    else:
        print("> Couldn't find any pom.xml files. Exiting the instrumentation step.")


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
    instrument(os.environ.get('THUNDRA_INSTRUMENTER_VERSION'),
               os.environ.get('THUNDRA_AGENT_VERSION'))


run()
