# XNAT Python Templates

This repository contains simple, single-purpose template scripts for working with XNAT using Python. Each template demonstrates one specific XNAT operation and can be used as a starting point for your own scripts.

## One-Time Setup

1. Install Miniconda (if you haven't already):
   ```bash
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   bash Miniconda3-latest-Linux-x86_64.sh
   ```

2. Create and activate an environment with the XNAT package:
   ```bash
   conda env create -n xnat
   conda activate xnat-env
   ```

3. Install the XNAT package:
   ```bash
   conda install pip
   pip install xnat
   ```

## Available Templates

Each template is a standalone Python script that demonstrates one specific XNAT operation:

1. `1_list_projects.py`: List all accessible projects on XNAT
2. `2_list_subjects.py`: List all subjects in a project
3. `3_download_single_scan.py`: Download a specific scan from XNAT
4. `4_download_session.py`: Download an entire session


## Authentication

1. Each scripts first requires methods to authenticate with XNAT.
   - Use your XNAT API token ID as username
   - Use your XNAT API token secret as password

2. This is available in the XNAT web interface on the top-left corner under `<your name>` -> `Manage Alias Tokens` -> Create Token

3. Click on the created token and copy the 'alias' and 'secret' into the `DEFAULT_TOKEN` and `DEFAULT_SECRET` variables in the script.

## Resources

- [XNAT Python Documentation](https://xnat.readthedocs.io/)