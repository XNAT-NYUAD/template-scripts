%% XNAT Download Configuration and Execution Script
% Edit this script to configure and run your XNAT downloads

%% Path Configuration
% Set where you want to save downloads and logs
scriptDir = fileparts(mfilename('fullpath'));  % Get current script's directory
config = struct();
config.download_dir = fullfile(scriptDir, 'downloads');  % Default download location
config.logs_dir = fullfile(scriptDir, 'logs');          % Default logs location

%% XNAT Configuration
% Edit these settings to match your XNAT server and project
config.server_url = 'https://xnat.abudhabi.nyu.edu/';
config.api_token_id = 'applebanana';
config.api_token_secret = 'applebanana';
config.project_id = 'rokerslab_ari-clean';

%% Example 1: Download DICOM files
% subjects = {'sub-0201'};
% sessions = {'ses-01'};
% 
% % Run the DICOM download
% status = downloadXNAT(...
%     'config', config, ...
%     'subjects', subjects, ...
%     'sessions', sessions ...
%     );

%% Example 2: Download Resources
% Download 'rawdata' folder from session resources
status = downloadXNAT(...
    'config', config, ...
    'subjects', {'sub-0201'}, ...
    'sessions', {'ses-01'}, ...
    'resource', 'rawdata' ...
);

