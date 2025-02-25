#!/usr/bin/env python3

import time
import xnat
import os
from pathlib import Path
import tempfile
import argparse
import logging
import sys
import shutil

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--logs-dir', required=True, help='Directory for log files')
parser.add_argument('--download-dir', required=True, help='Base directory for downloads')
parser.add_argument('--server-url', required=True, help='XNAT server URL')
parser.add_argument('--api-token-id', required=True, help='XNAT API token ID')
parser.add_argument('--api-token-secret', required=True, help='XNAT API token secret')
parser.add_argument('--project-id', required=True, help='XNAT project ID')
parser.add_argument('--subjects', nargs='+', help='List of subject IDs to download')
parser.add_argument('--sessions', nargs='+', help='List of session labels to download')
parser.add_argument('--resource-name', required=True, help='Name of resource folder to download')

args = parser.parse_args()

# Set up logging
log_file = os.path.join(args.logs_dir, 'download.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def download_session_resources(session, resource_name, output_dir):
    """Download specific resource from a session."""
    if resource_name in session.resources:
        logging.info(f"Downloading resource '{resource_name}' from session {session.label}")
        
        # Create a temporary directory for the download
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download to temp directory first
            session.resources[resource_name].download_dir(temp_dir)
            
            # For debugging
            logging.info(f"Temporary directory structure:")
            for root, dirs, files in os.walk(temp_dir):
                logging.info(f"Directory: {root}")
                for f in files:
                    logging.info(f"File: {f}")
            
            source_dir = Path(temp_dir)
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    src_path = Path(root) / file
                    parts = src_path.parts
                    
                    if 'files' in parts:
                        # Get everything after 'files'
                        rel_parts = parts[parts.index('files')+1:]
                        
                        # Remove subject/session from path if they exist
                        if len(rel_parts) >= 2:
                            # Check if first two parts are subject/session
                            if rel_parts[0].startswith('sub-') and rel_parts[1].startswith('ses-'):
                                rel_parts = rel_parts[2:]  # Skip subject/session folders
                        
                        rel_path = Path(*rel_parts)
                        dest_path = output_dir / rel_path
                        
                        # For debugging
                        logging.info(f"Processing file:")
                        logging.info(f"  Source: {src_path}")
                        logging.info(f"  Destination: {dest_path}")
                        
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_path, dest_path)
            
        logging.info(f"Successfully downloaded resource '{resource_name}'")
    else:
        logging.warning(f"Resource '{resource_name}' not found in session {session.label}")

def main():
    try:
        start_time = time.time()
        logging.info("\nStarting resource download process...")
        
        # Connect to XNAT
        session = xnat.connect(args.server_url, user=args.api_token_id, password=args.api_token_secret)
        project = session.projects[args.project_id]
        
        # Create base resource directory
        base_dir = Path(args.download_dir) / args.resource_name
        
        # Files to exclude from download
        exclude_files = {'README', 'dataset_description.json', 'CHANGES'}
        
        for subject_id in args.subjects:
            for session_id in args.sessions:
                # Try both session formats
                experiment_labels = [
                    f"{subject_id}_{session_id}",  # Try ses-01
                    f"{subject_id}_{session_id.replace('-', '_')}"  # Try ses_01
                ]
                
                # Try to find the experiment with either label
                found = False
                for experiment_label in experiment_labels:
                    for exp in project.experiments.values():
                        if exp.label == experiment_label:
                            found = True
                            output_dir = base_dir / subject_id / session_id
                            
                            # Download session resources
                            if args.resource_name in exp.resources:
                                logging.info(f"Downloading resource '{args.resource_name}' from session {exp.label}")
                                
                                with tempfile.TemporaryDirectory() as temp_dir:
                                    # Download to temp directory first
                                    exp.resources[args.resource_name].download_dir(temp_dir)
                                    
                                    source_dir = Path(temp_dir)
                                    for root, dirs, files in os.walk(source_dir):
                                        for file in files:
                                            # Skip excluded files
                                            if file in exclude_files:
                                                continue
                                                
                                            src_path = Path(root) / file
                                            parts = src_path.parts
                                            
                                            if 'files' in parts:
                                                # Get everything after 'files'
                                                rel_parts = parts[parts.index('files')+1:]
                                                
                                                # Remove subject/session from path if they exist
                                                if len(rel_parts) >= 2:
                                                    if rel_parts[0].startswith('sub-') and (
                                                        rel_parts[1].startswith('ses-') or 
                                                        rel_parts[1].startswith('ses_')
                                                    ):
                                                        rel_parts = rel_parts[2:]
                                                
                                                rel_path = Path(*rel_parts)
                                                dest_path = output_dir / rel_path
                                                
                                                # Create parent directories if they don't exist
                                                dest_path.parent.mkdir(parents=True, exist_ok=True)
                                                shutil.copy2(src_path, dest_path)
                                
                                logging.info(f"Successfully downloaded resource '{args.resource_name}'")
                            else:
                                logging.warning(f"Resource '{args.resource_name}' not found in session {exp.label}")
                            break
                    
                    if found:
                        break
                
                if not found:
                    logging.warning(f"Session {subject_id}_{session_id} (or {subject_id}_{session_id.replace('-', '_')}) not found")
        
        end_time = time.time()
        logging.info(f"\nDownload process completed successfully! Time taken: {end_time - start_time:.2f} seconds")
        
        # Create done file to signal completion
        with open(os.path.join(args.logs_dir, 'download_complete'), 'w') as f:
            f.write('done')
        
        sys.exit(0)
    except Exception as e:
        logging.error(f"\nAn error occurred during download process: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 