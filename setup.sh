#Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
echo 'export UV_LINK_MODE=copy' >> ~/.bashrc
source ~/.bashrc


uv sync


#install ruff
uv tool install ruff

#install mypy
uv tool install mypy

#install precommit
uv tool install pre-commit
pre-commit install

#!/bin/bash
set -e

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs