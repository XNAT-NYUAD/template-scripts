function setup_xnat_env()
    % SETUP_XNAT_ENV Set up the Python environment for XNAT downloads
    
    % Find conda command
    if ismac || isunix
        conda_paths = {
            fullfile(getenv('HOME'), 'miniconda3', 'bin', 'conda'),
            fullfile(getenv('HOME'), 'anaconda3', 'bin', 'conda'),
            '/usr/local/bin/conda',
            'conda'  % try system path as fallback
        };
    else  % Windows
        conda_paths = {
            fullfile(getenv('USERPROFILE'), 'miniconda3', 'Scripts', 'conda.exe'),
            fullfile(getenv('USERPROFILE'), 'anaconda3', 'Scripts', 'conda.exe'),
            'conda.exe'  % try system path as fallback
        };
    end
    
    % Find working conda command
    conda_cmd = '';
    for i = 1:length(conda_paths)
        if ismac || isunix
            [status, ~] = system([conda_paths{i} ' --version']);
        else
            [status, ~] = system(['"' conda_paths{i} '" --version']);
        end
        if status == 0
            conda_cmd = conda_paths{i};
            break;
        end
    end
    
    if isempty(conda_cmd)
        error('Conda not found. Please install Miniconda or Anaconda');
    end
    
    % Check if xnat_env exists
    [status, ~] = system([conda_cmd ' env list | grep xnat_env']);
    if status ~= 0
        % Create environment if it doesn't exist
        fprintf('Creating conda environment ''xnat_env''...\n');
        [status, output] = system([conda_cmd ' create -y -n xnat_env python=3.9']);
        if status ~= 0
            error('Failed to create conda environment:\n%s', output);
        end
        
        % Install required packages
        fprintf('Installing required packages...\n');
        [status, output] = system([conda_cmd ' run -n xnat_env pip install xnat']);
        if status ~= 0
            error('Failed to install packages:\n%s', output);
        end
    end
    
    % Verify Python and package installation
    [status, result] = system([conda_cmd ' run -n xnat_env python --version']);
    if status == 0
        fprintf('Python version in xnat_env: %s', result);
    else
        error('Failed to find Python in conda environment');
    end
    
    % Verify xnat package installation
    [status, ~] = system([conda_cmd ' run -n xnat_env python -c "import xnat"']);
    if status == 0
        fprintf('XNAT package verified\n');
    else
        error('XNAT package not found in Python environment');
    end
    
    fprintf('\nSetup completed successfully!\n');
    fprintf('The xnat_env conda environment is ready for use.\n');
end 