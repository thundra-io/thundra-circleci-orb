# thundra-circleci-plugin

A CircleCI Orb to instrument your projects with Thundra Foresight.

Learn about Orbs [here](https://circleci.com/orbs/).
## Usage

Information about available parameters is listed [below](#parameters).

The required parameters are the Thundra API Key and the Thundra Project ID, which can be obtained from [foresight.thundra.io](https://foresight.thundra.io/).

You can learn more about Thundra at [thundra.io](https://thundra.io)

Once you get the Thundra API Key, make sure to set it as a secret. A sample Orb usage would look like this:

### Maven Build Example

```yaml
# Make sure to use version 2.1
version: 2.1

# ...

orbs:
  # Declare a dependency on the welcome-orb
  # Make sure to replace <VERSION> with the latest available
  thundra: thundra-io/thundra-foresight@<VERSION>

# ...

jobs:
  maven:
    docker:
    - image: cimg/openjdk:11.0
    steps:
    - checkout
      # Use `thundra/maven` command
    - thundra/maven:
        apikey: <THUNDRA_APIKEY>
        project_id: <THUNDRA_PROJECT_ID>
    - run:
        command: mvn clean verify
workflows:
  example:
    jobs:
      - maven
```

### Gradle Build Example

```yaml
# Make sure to use version 2.1
version: 2.1

# ...

orbs:
  # Declare a dependency on the welcome-orb
  # Make sure to replace <VERSION> with the latest available
  thundra: thundra-io/thundra-foresight@<VERSION>

# ...

jobs:
  gradle:
    docker:
      - image: cimg/openjdk:11.0
    steps:
      - checkout
      # Use `thundra/gradle` command
      - thundra/gradle:
          apikey: <THUNDRA_APIKEY>
          project_id: <THUNDRA_PROJECT_ID>
      - run:
          # Make sure to use the $THUNDRA_GRADLE_INIT_SCRIPT_PATH
          command: ./gradlew build --init-script $THUNDRA_GRADLE_INIT_SCRIPT_PATH
workflows:
  example:
    jobs:
      - gradle
```

## Parameters

| Name                  | Requirement       | Scope         | Description
| ---                   | ---               | ---           | ---
| apikey                | Required          | Maven, Gradle | Thundra API Key
| project_id            | Required          | Maven, Gradle | Your project id from Thundra. Will be used to filter and classify your testruns.
| instrumenter_version  | Optional          | Maven         | In the action itself, we use a Java script to manipulate pom.xml files. This script is released and versioned separately from the action. Hence, if there is some breaking change or specific version you want to use, you can use it by defining this parameter. You can see all the available version of our instrumenter [here](https://search.maven.org/artifact/io.thundra.plugin/thundra-agent-maven-test-instrumentation).
| plugin_version        | Optional          | Gradle         | For Gradle, we use another plugin to instrument tests. You can see all the available version of our plugin [here](https://search.maven.org/artifact/io.thundra.plugin/thundra-gradle-test-plugin).
| agent_version         | Optional          | Maven, Gradle  | A specific version Thundra Java Agent you want to use should be defined here. Similar to `instrumenter_version` parameter. You can see all the available version of our agent [here](https://repo.thundra.io/service/local/repositories/thundra-releases/content/io/thundra/agent/thundra-agent-bootstrap/maven-metadata.xml).
| parent_pom_path       | Optional          | Maven          | Use if your parent pom is in somewhere other that ./pom.xml. **Must be a relative path.**
