#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")/.."

echo "Setting up data for the project..."
cobaya-install inputs/install_data.yaml
echo "Data setup complete..."