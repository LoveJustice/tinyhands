import toml
import os
from pathlib import Path

toml_file = Path(".streamlit/secrets.toml").resolve()
# Load TOML data
with open(toml_file, "r") as file:
    data = toml.load(file)

# Convert TOML data to environment variables
for key, value in data.items():
    if isinstance(value, dict):  # For nested TOML structures
        for sub_key, sub_value in value.items():
            env_var = f"{key.upper()}_{sub_key.upper()}"
            os.environ[env_var] = str(sub_value)
    else:
        os.environ[key.upper()] = str(value)

# Convert TOML data to environment variables
with open("env.list", "w") as env_file:
    for key, value in data.items():
        if isinstance(value, dict):  # For nested TOML structures
            for sub_key, sub_value in value.items():
                env_var = f"{key.upper()}_{sub_key.upper()}"
                env_file.write(f"{env_var}={sub_value}\n")
        else:
            env_file.write(f"{key.upper()}={value}\n")

for name, value in os.environ.items():
    print("{0}: {1}".format(name, value))

import os


def load_env_from_file(env_file):
    with open(env_file, "r") as file:
        for line in file:
            key, value = line.strip().split("=", 1)
            print(key, value)
            os.environ[key] = value


env_list = load_env_from_file("env.list")

# Import the Secret Manager client library.
from google.cloud import secretmanager

# GCP project in which to store secrets in Secret Manager.
project_id = "YOUR_PROJECT_ID"

# ID of the secret to create.
secret_id = "YOUR_SECRET_ID"

# Create the Secret Manager client.
client = secretmanager.SecretManagerServiceClient()

# Build the parent name from the project.
parent = f"projects/{project_id}"

# Create the parent secret.
secret = client.create_secret(
    request={
        "parent": parent,
        "secret_id": secret_id,
        "secret": {"replication": {"automatic": {}}},
    }
)

# Add the secret version.
version = client.add_secret_version(
    request={"parent": secret.name, "payload": {"data": b"hello world!"}}
)

# Access the secret version.
response = client.access_secret_version(request={"name": version.name})

# Print the secret payload.
#
# WARNING: Do not print the secret in a production environment - this
# snippet is showing how to access the secret material.
payload = response.payload.data.decode("UTF-8")
print(f"Plaintext: {payload}")
