function status = downloadXNAT(varargin)
    % DOWNLOADXNAT Download data from XNAT

    % Parse inputs
    p = inputParser;
    p.addParameter('config', [], @isstruct);
    p.addParameter('test', false, @islogical);
    p.addParameter('subjects', {}, @iscell);
    p.addParameter('sessions', {}, @iscell);
    p.addParameter('resource', '', @ischar);  % New parameter for resource name
    p.parse(varargin{:});
    
    % Verify config is provided
    if isempty(p.Results.config)
        error('Config struct must be provided');
    end
    
    % Get the directory where this MATLAB script is located
    scriptDir = fileparts(mfilename('fullpath'));
    
    % Create logs and downloads directories if they don't exist
    logsDir = fullfile(scriptDir, 'logs');
    downloadDir = fullfile(scriptDir, 'downloads');
    if ~exist(logsDir, 'dir')
        mkdir(logsDir);
    end
    if ~exist(downloadDir, 'dir')
        mkdir(downloadDir);
    end
    
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
    
    % Try to use conda environment
    [status, ~] = system([conda_cmd ' run -n xnat_env python --version']);
    if status == 0
        python_cmd = [conda_cmd ' run -n xnat_env python'];
    else
        error(['Conda environment ''xnat_env'' not found. ', ...
               'Please run setup_xnat_env() first']);
    end
    
    % Choose which Python script to use based on whether resource is specified
    if ~isempty(p.Results.resource)
        pythonScript = fullfile(scriptDir, 'session-resources-v1.py');
    else
        pythonScript = fullfile(scriptDir, 'session-download-v1.py');
    end
    
    % Build the command string
    cmd = sprintf(['%s "%s" --logs-dir "%s" --download-dir "%s" ' ...
                  '--server-url "%s" --api-token-id "%s" ' ...
                  '--api-token-secret "%s" --project-id "%s" '], ...
        python_cmd, pythonScript, logsDir, downloadDir, ...
        p.Results.config.server_url, ...
        p.Results.config.api_token_id, ...
        p.Results.config.api_token_secret, ...
        p.Results.config.project_id);
    
    % Add resource name if specified
    if ~isempty(p.Results.resource)
        cmd = sprintf('%s --resource-name "%s" ', cmd, p.Results.resource);
    end
    
    % Add test flag if requested
    if p.Results.test
        cmd = [cmd '--test '];
    end
    
    % Add subjects if specified
    if ~isempty(p.Results.subjects)
        cmd = [cmd '--subjects '];
        for i = 1:length(p.Results.subjects)
            cmd = [cmd p.Results.subjects{i} ' '];
        end
    end
    
    % Add sessions if specified
    if ~isempty(p.Results.sessions)
        cmd = [cmd '--sessions '];
        for i = 1:length(p.Results.sessions)
            cmd = [cmd p.Results.sessions{i} ' '];
        end
    end
    
    % Display the command being run
    fprintf('Executing command: %s\n', cmd);
    
    % Delete any existing done file and log file
    done_file = fullfile(logsDir, 'download_complete');
    log_file = fullfile(logsDir, 'download.log');
    if exist(done_file, 'file')
        delete(done_file);
    end
    if exist(log_file, 'file')
        delete(log_file);
    end
    
    % Run the command with real-time output
    if ispc
        [status, output] = system(cmd);  % Windows doesn't support async output well
        fprintf('%s\n', output);
    else
        % For Mac/Linux, use system with echo
        cmd = [cmd ' 2>&1'];  % Redirect stderr to stdout
        [status, ~] = system(cmd, '-echo');  % Use -echo to show output in real time
        
        % Check the log file for any output
        if exist(log_file, 'file')
            fprintf('\nLog file contents:\n');
            type(log_file);
        end
    end
    
    % Check status
    if status ~= 0
        warning('XNAT download failed with status code: %d', status);
    else
        fprintf('XNAT download completed successfully.\n');
    end
end