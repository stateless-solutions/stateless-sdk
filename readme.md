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
stateless-cli api-keys create
```

When this command is executed, the CLI will interactively prompt for the required information, including the name of the API key and the number of days until expiration.

Upon completion, a confirmation message will be displayed with details of the newly created API key.

#### Using a JSON Configuration File

```bash
stateless-cli api-keys create --config file <path_to_config_file>
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
stateless-cli api-keys update <api_key_id>
```
The CLI will prompt the user to choose an API key and then provide options to update its name and expiration date.

#### Using a JSON Configuration File

```bash
stateless-cli api-keys update <api_key_id> --config file <path_to_config_file>
```

### Retrieve API key details

```bash
stateless-cli api-keys get <api_key_id>
```

Users can fetch details about a specific API key using this command. The CLI will prompt the user to select an API key, and then display its details.

### List all API keys

```bash
stateless-cli api-keys list
```

Fetches and displays a list of all the API keys associated with the current account. The list will include the ID and name of each API key.

### Delete an API key

```bash
stateless-cli api-keys delete <api_key_id>
```

This command allows for the deletion of a specific API key. The user will be prompted to select an API key for deletion. Please note that this action is irreversible, and deleted keys cannot be recovered.

## Offerings
Offerings are the cataloged services or data streams provided by the platform, which users can utilize within their applications. These offerings may relate to specific blockchain data, services, or entry points for data access. Managing offerings is a crucial aspect for both providers, who supply these services, and consumers, who integrate them into their applications.

## Commands

### List all offerings

```bash
stateless-cli offerings list
```

Use this command to retrieve and list all available offerings. The output displays a table listing all offerings, including their IDs, providers, chains, and the count of entry points associated with each offering.

### See offering details

```bash
stateless-cli offerings detail <id>
```

Retrieve detailed information about a specific offering using this command. The CLI will prompt the user to select an offering, and the output will display a table with detailed information about the offering, including its ID, the provider name, the chain it operates on, and the URLs for each of its entry points.

### Create an offering (Provider only)

The create command allows data service providers to create a new offering either through interactive prompts or by using a JSON configuration file.

```bash
stateless-cli offerings create
```
The CLI will interactively prompt for the required information, including the target blockchain platform for the offering.

#### Using a JSON Configuration File

```bash
stateless-cli offerings create --config file <path_to_config_file>
```
Example JSON:

```json
{
    "chain_id": "1" // Target blockchain platform ID
}
```

### Update an offering (Provider only)

Providers can modify the details of an existing offering either through interactive prompts or by using a JSON configuration file.

```bash
stateless-cli offerings update <offering_id>
```

The CLI will prompt the user to select an offering and then provide options to update its chain ID. If the update is successful, the command prints a confirmation message with the ID of the updated offering.

#### Using a JSON Configuration File

```bash
stateless-cli offerings update <offering_id> --config file <path_to_config_file>
```

### Delete an offering (Provider only)

```bash
stateless-cli offerings delete <offering_id>
```

Use this command to remove an offering from the platform. The user will be prompted to select an offering for deletion. A success message will confirm the offering has been deleted. Please note that this action is irreversible.

## Buckets
Buckets are designated blockchain data providers that applications using the platform's APIs elect to send their requests. The CLI offers commands to seamlessly manage these Buckets. 

Prior to leveraging these commands, please ensure all prerequisites, such as API keys and configurations, are properly implemented.

## Commands

### List Buckets

```bash
stateless-cli buckets list
```

This command fetches and displays all the active Buckets of the current account. Users can view a comprehensive list and glean important information about each 'Bucket,' such as its ID, Name, associated Chain, and Offerings.

### Create Bucket

The create command allows users to create a new Bucket associated with their account either through interactive prompts or by using a JSON configuration file.

```bash
stateless-cli buckets create
```

The CLI will interactively prompt for the required information, including Bucket Name, Chain ID, and Offerings (selected from available offerings).

#### With a JSON Configuration File

```bash
stateless-cli buckets create --config_file <path_to_config_file>
```

Example JSON:

```json
{
   "name": "My first bucket",
   "chain_id": "1",
   "offerings": ["offering_id_1", "offering_id_2"]
}
```

### Update Bucket

This command allows users to modify the details of an existing bucket, either through interactive prompts or by using a JSON configuration file.

```bash
stateless-cli buckets update <bucket_id>
```

The CLI will prompt the user to select a bucket and then provide options to update its name and associated offerings.

#### Using a JSON Configuration File

```bash
stateless-cli buckets update <bucket_id> --config file <path_to_config_file>
```

### Retrieve Bucket Details

```bash
stateless-cli buckets get <bucket_id>
```

Fetches detailed information about a specific Bucket based on its UUID. The CLI will prompt the user to select a bucket, and the output will display detailed information about the Bucket, including its ID, name, associated chain, and offerings.

### Delete a Bucket

```bash
stateless-cli buckets delete <bucket_id>
```

This command provides the functionality to remove a Bucket from an account. The user will be prompted to select a bucket for deletion. Please note that this action will permanently delete the specified Bucket resource and all its associated data. A confirmation message will be displayed upon successful deletion.

## Entrypoints
Entrypoints are specific URLs or access points that applications use to send requests to data providers. Managing entrypoints is essential for providers to control how and where their data is accessed. This set of CLI commands is intended for providers to manage entrypoints, whereas applications utilize these entrypoints to interact with providers' data.

## Commands

### List all entrypoints

```bash
stateless-cli entrypoints list
```

Retrieves and lists all entrypoints associated with a specific offering. Users can view a table displaying each entrypoint's ID, URL, and associated region.

### Retrieve an entrypoint

```bash
stateless-cli entrypoints get <entrypoint_id>
```

Fetches information about a specific entrypoint. The CLI will prompt the user to select an entrypoint, and the output will display a JSON-formatted output detailing the entrypoint's configuration.

### Create an entrypoint (Provider only)

The create command registers a new entrypoint either through interactive prompts or by using a JSON configuration file.

```bash
stateless-cli entrypoints create
```

When executed, the CLI will interactively prompt for the required information, including Entrypoint URL, Offering ID, and Region ID.

#### With a JSON Configuration File

```bash
stateless-cli entrypoints create --config file <path_to_config_file>
```
Example JSON:

```json
{
    "url": "https://example-entrypoint.com",
    "offering_id": "84031ebd-5963-47b1-87f5-887a3e6a8571",
    "region_id": "dbc673ef-834c-438a-889d-45b1b5e0ed20"
}
```

### Update an entrypoint (Provider only)

Allows for updating the configuration of an existing entrypoint.

```bash
stateless-cli entrypoints update <entrypoint_id>
```
The CLI will prompt the user to select an entrypoint and then provide options to update its URL.
 
#### With a JSON Configuration File

```bash
stateless-cli entrypoints update <entrypoint_id> --config_file <path_to_config_file>
```

### Delete an entrypoint (Provider only)

```bash
stateless-cli entrypoints delete <entrypoint_id>
```

Removes an entrypoint from the registry. The user will be prompted to select an entrypoint for deletion. A message confirming the successful deletion of the entrypoint will be displayed. Please note this action is final and cannot be undone.

## Help
The `help` command in the gateway-cli is designed to provide users with assistance and information on how to use various commands within the CLI. It's an essential tool for both new and experienced users to quickly get help on specific commands or to get an overview of the CLI's capabilities.

### General Help

```bash
stateless-cli help
```

This command displays a general help message, which includes a list of all top-level commands available in the gateway-cli. It provides a brief description of what each command does to better understand the overall functionality. 

When you run `gateway-cli help`, you will see an output similar to the following:

```bash
stateless-cli

Usage:
  gateway-cli [command]

Available Commands:
  buckets        Manage your Buckets
  offerings      Handle Offerings on the platform
  entrypoints    Control Entrypoints for data access
  api-keys       Operations related to API keys

Use "stateless-cli [command] help" for more information about a command.
```

### Command Specific Help
To get detailed help on a specific command, append `help` after the command name:

```bash
stateless-cli [command] help
```

For example:

```bash
stateless-cli buckets help
```

Displays help for the `buckets` command, including its subcommands like list, create, update, get, and delete.

```bash
stateless-cli offerings help
```

Shows detailed usage for the `offerings` command, including information on listing, creating, updating, and deleting offerings.

```bash
stateless-cli entrypoints help
```

Provides help specific to the `entrypoints` command, guiding on how to manage entrypoints.
