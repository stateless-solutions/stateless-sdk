# Stateless CLI Documentation

## Overview
The Stateless CLI is a powerful command-line interface that allows you to interact with the Stateless services for managing offerings, entrypoints, buckets, and API keys. 

## Installing the CLI

### Prerequisites
Before installing the CLI, ensure you have the following:
- Python 3.6 or newer
- pip installed (Python's package installer)

### Installation Steps
The CLI is available through a Python package repository, and you can download it using pip:

```bash
pip install stateless-sdk
```
After installation, run the setup command to initiate the CLI. This command will also handle API key setup:

```bash
stateless-cli setup
```

During the setup, if you don't have an API key, the CLI will direct you to the Stateless API key registration page. Once you have your API key, you can set it as an environment variable for the CLI to use.

Setting the environment variable with your API key can be done in different ways depending on your operating system.

For Unix-like operating systems (Linux, macOS): 

```bash
export STATELESS_API_KEY='your_api_key_here'
```

For Windows Command Prompt:

```bash
set STATELESS_API_KEY=your_api_key_here
```

For Windows PowerShell:

```bash
$env:STATELESS_API_KEY="your_api_key_here"
```
Replace your_api_key_here with the actual API key provided by Stateless.

To check if the CLI has been installed correctly, you can run the help command:

```bash
stateless-cli --help
```

This should display a list of available commands and their descriptions.

If you installed the CLI in a custom directory or it's not available globally, you might need to update your system's PATH variable to include the directory where the CLI is installed.

Once the CLI is installed and the API key is set, you can start using it to manage various aspects of the Stateless services by calling the corresponding subcommands, like stateless-cli offerings list.

## API Keys
API keys are essential for both applications and providers to interact securely with the platform by authenticating access to resources. Always handle API keys with care, keeping them confidential and using them as per the platform's best practices.

## Commands

### Create an API key

The `create` command lets users generate a new API key. There are two ways to create an API key: using a JSON configuration file or through interactive prompts.

```bash
api keys app create
```

When this command is executed, the CLI will interactively prompt for the required information, including the name of the API key and the number of days until expiration.

Upon completion, a confirmation message will be displayed with details of the newly created API key.

#### Using a JSON Configuration File

```bash
api keys app create --config file <path_to_config_file>
```

Example JSON:

```json
{
  "name": "My API Key",
  "expires_at": "2023-12-31T23:59:59" // Optional expiration date
}
```
### Update an API key

The `update` command allows users to modify the details of an existing API key. Like creating API keys, updates can be done through interactive prompts or by providing a JSON configuration file.

```bash
api keys app update <api_key_id>
```
The CLI will prompt the user to choose an API key and then provide options to update its name and expiration date.

#### Using a JSON Configuration File

```bash
api_keys_app update <api_key_id> --config file <path_to_config_file>
```

### Retrieve API key details

```bash
api keys app get <api_key_id>
```

Users can fetch details about a specific API key using this command. The CLI will prompt the user to select an API key, and then display its details.

### List all API keys

```bash
api keys app list
```

Fetches and displays a list of all the API keys associated with the current account. The list will include the ID and name of each API key.

### Delete an API key

```bash
api keys app delete <api_key_id>
```

This command allows for the deletion of a specific API key. The user will be prompted to select an API key for deletion. Please note that this action is irreversible, and deleted keys cannot be recovered.

## Offerings
Offerings are the cataloged services or data streams provided by the platform, which users can utilize within their applications. These offerings may relate to specific blockchain data, services, or entry points for data access. Managing offerings is a crucial aspect for both providers, who supply these services, and consumers, who integrate them into their applications.

## Commands

### List all offerings

```bash
offerings app list
```

Use this command to retrieve and list all available offerings. The output displays a table that lists all offerings, including their IDs, providers, chains, and the count of entry points associated with each offering.

### See offering details

```bash
offerings app detail <id>
```

Retrieve detailed information about a specific offering using this command. The output displays a table with detailed information about the offering, including its ID, the provider name, the chain it operates on, and the URLs for each of its entry points.

### Create an offering (Provider only)

The `create` command allows data service providers to create a new offering. There are two ways to create an offering: through interactive prompts or using a JSON configuration file.

```bash
offerings app create
```

When this command is executed without a config file, the CLI will interactively prompt for the required information, including Chain ID and Provider ID. Upon completion, a confirmation message will be displayed with details of the newly created offering.

#### Using a JSON Configuration File

```bash
offerings app create --config file <path_to_config_file>
```
Example JSON:

```json
{
    "provider_id": "c233c4fa-7721-45a7-b6f4-10d2f1121620",
    "chain_id": 1
}
```

### Update an offering (Provider only)

The `update` command allows providers to modify the details of an existing offering. There are two ways to update an offering: through interactive prompts or using a JSON configuration file.

```bash
offerings app update <offering_id>
```

If the update is successful, the command prints a confirmation message with the ID of the updated offering.

#### Using a JSON Configuration File

```bash
offerings app update <offering_id> --config file <path_to_config_file>
```

### Delete an offering (Provider only)

```bash
offerings app delete <offering_id>
```

Use this command to remove an offering from the platform. A success message will confirm the offering has been deleted. Please note that this action is irreversible.

## Buckets
Buckets are designated blockchain data providers that applications using the platform's APIs elect to send their requests. The CLI offers commands to seamlessly manage these Buckets. 

Prior to leveraging these commands, please ensure all prerequisites, such as API keys and configurations, are properly implemented.

## Commands

### List Buckets

```bash
buckets app list
```

This command fetches and displays all the active Buckets of the current account. Users can view a comprehensive list and glean important information about each 'Bucket' such as its ID, Name, associated Chain, and Offering IDs.

### Create Bucket

The `create` command allows users to create a new Bucket associated with their account. There are two ways to create a bucket: through interactive prompts or using a JSON configuration file.

```bash
buckets app create
```

When this command is executed without a config file, the CLI will interactively prompt for the required information, including User ID (for admins), Bucket Name, Chain ID, and Offerings (as comma-separated UUIDs). Upon completion, a confirmation message is displayed with the ID of the newly created Bucket.

#### With a JSON Configuration File

```bash
buckets app create --config_file <path_to_config_file>
```

Example JSON:

```json
{
   "name": "My first bucket",
   "chain_id": 1
}
```

### Update Bucket

The `update` command allows users to modify the details of an existing bucket. There are two ways to update a bucket: through interactive prompts or using a JSON configuration file.

```bash
buckets_app update <bucket_id>
```

With this command, users can modify the details of an existing Bucket, such as changing the name or adding a new offering. Upon successful update, a confirmation message showcasing the ID of the updated Bucket will appear.

#### Using a JSON Configuration File

```bash
buckets app update <bucket_id> --config file <path_to_config_file>
```

### Retrieve Bucket Details

```bash
buckets_app get <bucket_id>
```

Fetches detailed information about a specific Bucket based on its UUID. It's useful for inspecting the attributes of a particular Bucket. The output will be a table displaying the ID, region, provider ID, and chain ID.

### Delete a Bucket

```bash
buckets_app delete <bucket_id>
```

Provides the functionality to remove a Bucket from an Account. Please note that this action will permanently delete the specified Bucket resource and all its associated data. After running this command, users will see a confirmation message confirming the bucket deletion.

## Entrypoints
Entrypoints are specific URLs or access points that applications use to send requests to data providers. Managing entrypoints is essential for providers to control how and where their data is accessed. This set of CLI commands is intended for providers to manage entrypoints, whereas applications utilize these entrypoints to interact with providers' data.

## Commands

### List all entrypoints

```bash
entrypoints app list
```

Retrieves and lists all entrypoints that are associated with a bucket. The output will display the Bucket ID and Service URL.

### Retrieve an entrypoint

```bash
entrypoints app get <entrypoint_id>
```

Fetches information about a specific entrypoint using its UUID. Returns a JSON-formatted output detailing the entrypoint's configuration.

### Create an entrypoint (Provider only)

The `create` command registers a new entrypoint. There are two ways to create an entrypoint: through interactive prompts or using a JSON configuration file.

```bash
entrypoints app create
```

When executed, the CLI will interactively prompt for the required information, including Entrypoint URL, Offering ID, and Region ID. Upon completion, a confirmation message with the ID and URL of the newly created entrypoint is returned.

#### With a JSON Configuration File

```bash
entrypoints app create --config file <path_to_config_file>
```
Example JSON:

```json
{
    "url": "https://ss-use.provider.com/eth",
    "offering_id": "84031ebd-5963-47b1-87f5-887a3e6a8571",
    "region_id": "dbc673ef-834c-438a-889d-45b1b5e0ed20"
}
```

### Update an entrypoint (Provider only)

The `update` command allows for updating the configuration of an existing entrypoint.

```bash
entrypoints_app update <entrypoint_id>
```
A success message with the updated entrypoint's ID is displayed if the operation is successful.

#### With a JSON Configuration File

```bash
entrypoints_app update <entrypoint_id> --config_file <path_to_config_file>
```

### Delete an entrypoint (Provider only)

```bash
entrypoints_app delete <entrypoint_id>
```

Removes an entrypoint from the registry. A message confirming the successful deletion of the entrypoint will be displayed. Please note this action is final and cannot be undone.

## Help
The `help` command in the gateway-cli is designed to provide users with assistance and information on how to use various commands within the CLI. It's an essential tool for both new and experienced users to quickly get help on specific commands or to get an overview of the CLI's capabilities.

### General Help

```bash
gateway-cli help
```

This command displays a general help message, which includes a list of all top-level commands available in the gateway-cli. It provides a brief description of what each command does to better understand the overall functionality. 

When you run `gateway-cli help`, you will see an output similar to the following:

```bash
gateway-cli

Usage:
  gateway-cli [command]

Available Commands:
  buckets        Manage your Buckets
  offerings      Handle Offerings on the platform
  entrypoints    Control Entrypoints for data access
  api-keys       Operations related to API keys

Use "gateway-cli [command] help" for more information about a command.
```

### Command Specific Help
To get detailed help on a specific command, append `help` after the command name:

```bash
gateway-cli [command] help
```

For example:

```bash
gateway-cli buckets help
```

Displays help for the `buckets` command, including its subcommands like list, create, update, get, and delete.

```bash
gateway-cli offerings help
```

Shows detailed usage for the `offerings` command, including information on listing, creating, updating, and deleting offerings.

```bash
gateway-cli entrypoints help
```

Provides help specific to the `entrypoints` command, guiding on how to manage entrypoints.
