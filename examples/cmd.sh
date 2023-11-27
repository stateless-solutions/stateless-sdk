# Create a chain using an admin API Key
python main.py chains create --config-file ./examples/chain_config.json

# Create a region using an admin API Key
python main.py regions create --config-file ./examples/region_config.json

# Create provider manually using an admin API Key
python main.py providers create --config-file ./examples/provider_config.json

# Create an API Key manually for the previously created provider using an admin API Key
python main.py api-keys create --config-file ./examples/provider_api_key.json

# Create a offering (provider/chain) using a provider API Key
python main.py offerings create --config-file ./examples/offering_config.json

# Create an entrypoint in the offering using a provider API Key
python main.py entrypoints create --config-file ./examples/entrypoint_config.json

# Create a bucket using a regular API Key
python main.py buckets create --config-file ./examples/bucket_config.json

# Add offering to previously created bucket using a regular API Key
python main.py buckets update --config-file ./examples/bucket_update_config.json d822fdb9-4759-4d4a-b510-23e46107c0a8