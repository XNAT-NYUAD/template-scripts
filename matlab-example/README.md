# XNAT Download Tools

A MATLAB-based toolset for downloading DICOM and resource data from XNAT servers.

## Prerequisites

Before you begin, ensure you have:
- MATLAB installed
- Miniconda or Anaconda installed ([download here](https://docs.conda.io/en/latest/miniconda.html))
  1. During Miniconda installation, select "Add Miniconda to PATH"
  2. Open a new terminal to verify installation:
     ```bash
     conda --version
     ```
- XNAT server access
- XNAT API tokens (obtain from your XNAT administrator)

## Installation

### If you're installing Conda for the first time:
1. Download and install Miniconda ([download here](https://docs.conda.io/en/latest/miniconda.html))
   - During installation, select "Add Miniconda to PATH"
   - Open a new terminal and verify:
     ```bash
     conda --version
     ```
   - Run this command in terminal:
     ```bash
     conda init
     ```
   - Close and reopen your terminal

### If you already have Conda installed:
1. Open terminal and verify Conda is in your PATH:
   ```bash
   conda --version
   ```
   If this fails, you need to add Conda to your PATH

### For everyone - MATLAB setup:
1. Place these files in your working directory:
   - `run_download.m`
   - `downloadXNAT.m`
   - `session-download-v1.py`
   - `session-resources-v1.py`
   - `setup_xnat_env.m`

2. Open MATLAB and navigate to your working directory

3. Run the setup script:
   ```matlab
   setup_xnat_env
   ```
   This will:
   - Create a new Conda environment named 'xnat_env'
   - Install required Python packages
   - If you see any errors about Conda not being found, you need to fix your Conda PATH first

## Configuration

Edit `run_download.m` to set your XNAT credentials:
```matlab
config.server_url = 'https://xnat.abudhabi.nyu.edu/';    % Your XNAT server URL
config.api_token_id = 'your-token-id';                   % Your API token ID
config.api_token_secret = 'your-token-secret';           % Your API token secret
config.project_id = 'your-project-id';                   % Your XNAT project ID
```

## Authentication Setup

### Getting API Tokens
1. Log into your XNAT server in a web browser
2. Click on your username in the top-right corner
3. Select "Manage API Keys"
4. Click "Create New API Key"
5. Save both the:
   - API Token ID (e.g., "656059bb-0b85-4c5d-8deb-4a7c397a7ba0")
   - API Token Secret (e.g., "9ZjS8KoLRPfvYHInjMcU13w9FdLWkMjU7h0MNf5u8r8rhJLNZpg0xDNg6OSIsddM")

### Configuring Authentication
In `run_download.m`, ensure your credentials are correct:
```matlab
config.server_url = 'https://xnat.abudhabi.nyu.edu/';    % Include trailing slash
config.api_token_id = 'your-token-id';                   % From "Manage API Keys"
config.api_token_secret = 'your-token-secret';           % From "Manage API Keys"
config.project_id = 'rokerslab_ari-clean';               % Your project ID
```

### Common Authentication Issues
1. **Login Failed Error**
   - Verify your API tokens are correct
   - Make sure tokens haven't expired
   - Check if you have access to the project
   - Ensure server URL has trailing slash (/)

2. **JSESSION Warning**
   - This warning is normal, the script will fall back to API token authentication
   - Only worry if you see a "Login attempt failed" error

## Usage Examples

### 1. Download DICOM Files
```matlab
status = downloadXNAT(...
    'config', config, ...
    'subjects', {'sub-0201'}, ...
    'sessions', {'ses-01'} ...
);
```

### 2. Download Resource Folders
```matlab
status = downloadXNAT(...
    'config', config, ...
    'subjects', {'sub-0201'}, ...
    'sessions', {'ses-01'}, ...
    'resource', 'rawdata' ...
);
```

### 3. Download Multiple Subjects
```matlab
status = downloadXNAT(...
    'config', config, ...
    'subjects', {'sub-0201', 'sub-0202'}, ...
    'sessions', {'ses-01'}, ...
    'resource', 'rawdata' ...
);
```

## Output Directory Structure

### For DICOM Downloads:
```
downloads/
└── sub-0201/
    └── ses-01/
        └── scans/
            └── [DICOM files]
```

### For Resource Downloads:
```
downloads/
└── rawdata/
    ├── sub-0201/
    │   └── ses-01/
    │       └── anat/
    │           └── [data files]
    └── sub-0202/
        └── ses-01/
            └── anat/
                └── [data files]
```

## Features

- Downloads both DICOM files and resource folders
- Supports multiple subjects and sessions
- Compatible with both 'ses-01' and 'ses_01' formats
- Excludes unnecessary files (README, dataset_description.json, CHANGES)
- Creates organized directory structure
- Provides download progress logs

## Troubleshooting

### Common Issues

1. **"Conda not found" error**
   - Verify Miniconda/Anaconda installation
   - Ensure conda is in your system PATH

2. **"XNAT environment not found" error**
   - Run `setup_xnat_env` again
   - Verify conda environment 'xnat_env' exists

3. **Connection issues**
   - Check XNAT server URL
   - Verify API token validity
   - Test network connection to XNAT server

4. **Session not found**
   - Verify subject/session exists in project
   - Check session format (script tries both 'ses-01' and 'ses_01')

### Logs

Download progress and errors are logged to:
```
logs/download.log
```

## Support

For issues or questions, contact [Your Contact Information]

## License

[Your License Information]