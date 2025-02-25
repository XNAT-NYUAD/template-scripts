#!/usr/bin/env python3

# Import required libraries
import time
import xnat          # For connecting to and downloading from XNAT server
import os           # For operating system operations
import shutil       # For file operations like moving files
from pathlib import Path  # For cross-platform path handling
import tempfile     # For creating temporary directories
import argparse     # For parsing command line arguments
import logging
import sys

# Default lists for subjects and sessions
DEFAULT_SUBJECTS = [
    "Subject_0248" # Default list of subjects to process if none specified
]
DEFAULT_SESSIONS = []  # Empty list means download all sessions

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--logs-dir', required=True, help='Directory for log files')
parser.add_argument('--download-dir', required=True, help='Base directory for downloads')
parser.add_argument('--server-url', required=True, help='XNAT server URL')
parser.add_argument('--api-token-id', required=True, help='XNAT API token ID')
parser.add_argument('--api-token-secret', required=True, help='XNAT API token secret')
parser.add_argument('--project-id', required=True, help='XNAT project ID')
parser.add_argument('--test', action='store_true', help='Run in test mode')
parser.add_argument('--subjects', nargs='+', help='List of subject IDs to download')
parser.add_argument('--sessions', nargs='+', help='List of session labels to download')

args = parser.parse_args()

# Use the provided directories
log_file = os.path.join(args.logs_dir, 'download.log')
DOWNLOAD_BASE_DIR = Path(args.download_dir)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def create_clean_dir(path):
    """Create directory if it doesn't exist."""
    path = Path(path)
    if not path.exists():
        path.mkdir(parents=True)  # Create directory and any necessary parent directories
        logging.info(f"Created directory {path}")

def check_existing_scan(scan_dir, scan):
    """Check if scan is already downloaded completely."""
    if not scan_dir.exists():
        return False
        
    # Get XNAT file count
    total_files = len(scan.files.values())

    # Check for single file case
    if total_files == 1:
        local_dicoms = list(scan_dir.glob('*.dcm'))
    # Check for multiple files case directly in scan directory
    else:
        local_dicoms = list(scan_dir.glob('*.dcm'))

    local_dicom_count = len(local_dicoms)
    if local_dicom_count == total_files:
        logging.info(f"      Scan {scan.id} already exists with {local_dicom_count} DICOM file(s)")
        return True
            
    return False

def move_files_from_download(temp_dir, target_dir, scan_label):
    """Move files from XNAT's directory structure to our desired location."""
    # Find all DICOM files in the temporary directory
    dicom_files = list(Path(temp_dir).rglob('*.dcm'))
    num_files = len(dicom_files)
    
    # Move each DICOM file to target directory
    moved_files = 0
    for filepath in dicom_files:
        if filepath.is_file():
            shutil.move(str(filepath), str(target_dir / filepath.name))
            moved_files += 1
    logging.info(f"      Moved {moved_files}/{num_files} DICOM files to {target_dir}")

def download_project_data(test_mode=False, subjects=None, sessions=None):
    """Download all subject data from the specified project."""
    # Use provided lists or fall back to defaults
    subjects_to_download = subjects if subjects else DEFAULT_SUBJECTS
    sessions_to_download = sessions if sessions else DEFAULT_SESSIONS
    
    logging.info(f"Starting download from XNAT server: {args.server_url}")
    logging.info(f"Subjects to process: {subjects_to_download}")
    if sessions_to_download:
        logging.info(f"Sessions to process: {sessions_to_download}")
    else:
        logging.info("Processing all available sessions")
    
    # Connect to XNAT server using credentials
    with xnat.connect(args.server_url, user=args.api_token_id, password=args.api_token_secret) as session:
        project = session.projects[args.project_id]
        logging.info(f"Connected to project: {project.id}")
        
        create_clean_dir(DOWNLOAD_BASE_DIR)
        
        # In test mode, only process the first available subject
        if test_mode:
            first_subject = next(iter(project.subjects.values()))
            process_subject(first_subject, sessions_to_download)
            logging.info("\nTest download completed!")
            return
        
        # Process each specified subject
        total_subjects = len(subjects_to_download)
        processed_subjects = 0
        failed_subjects = []
        
        for subject_id in subjects_to_download:
            if subject_id in project.subjects:
                try:
                    process_subject(project.subjects[subject_id], sessions_to_download)
                    processed_subjects += 1
                    logging.info(f"Successfully processed subject {subject_id} ({processed_subjects}/{total_subjects})")
                except Exception as e:
                    failed_subjects.append(subject_id)
                    logging.error(f"Failed to process subject {subject_id}: {str(e)}")
            else:
                failed_subjects.append(subject_id)
                logging.warning(f"\nWarning: Subject {subject_id} not found in project")
        
        # Log summary
        logging.info("\n=== Download Summary ===")
        logging.info(f"Total subjects processed: {processed_subjects}/{total_subjects}")
        if failed_subjects:
            logging.warning(f"Failed subjects: {failed_subjects}")

def process_subject(subject, sessions):
    """Process a single subject's data."""
    logging.info(f"\nProcessing subject: {subject.label}")
    subject_dir = DOWNLOAD_BASE_DIR / subject.label
    create_clean_dir(subject_dir)
    
    # Process each experiment (session) for the subject
    total_sessions = 0
    processed_sessions = 0
    
    for experiment in subject.experiments.values():
        # If sessions list is empty, process all sessions
        # Otherwise, only process sessions that match the specified session labels
        if not sessions or any(session in experiment.label for session in sessions):
            try:
                process_session(experiment, subject_dir)
                processed_sessions += 1
            except Exception as e:
                logging.error(f"Failed to process session {experiment.label}: {str(e)}")
            total_sessions += 1
    
    logging.info(f"Completed subject {subject.label}: {processed_sessions}/{total_sessions} sessions processed")

def process_session(experiment, subject_dir):
    """Process a single session's data."""
    logging.info(f"  Processing session: {experiment.label}")
    session_dir = subject_dir / experiment.label
    create_clean_dir(session_dir)
    
    # Process each scan in the session
    total_scans = len(experiment.scans)
    processed_scans = 0
    skipped_scans = 0
    failed_scans = []
    
    for scan in experiment.scans.values():
        try:
            scan_dir = session_dir / f"scan-{scan.id}_{scan.type}"
            if check_existing_scan(scan_dir, scan):
                skipped_scans += 1
                continue
                
            process_scan(scan, session_dir)
            processed_scans += 1
        except Exception as e:
            failed_scans.append(scan.id)
            logging.error(f"Failed to process scan {scan.id}: {str(e)}")
    
    logging.info(f"  Session {experiment.label} complete: {processed_scans} processed, {skipped_scans} skipped, {len(failed_scans)} failed out of {total_scans} total scans")
    if failed_scans:
        logging.warning(f"  Failed scans in session: {failed_scans}")

def process_scan(scan, fmri_dir):
    """Process a single scan's data."""
    logging.info(f"    Processing scan: {scan.id} ({scan.type})")
    
    # Create directory for this specific scan
    scan_dir = fmri_dir / f"scan-{scan.id}_{scan.type}"
    create_clean_dir(scan_dir)
    
    # Use temporary directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        if 'DICOM' in scan.resources:
            max_retries = 5
            retry_count = 0
            while retry_count < max_retries:
                try:
                    if retry_count == 0:
                        logging.info(f"      Downloading DICOM files...")
                    else:
                        logging.info(f"      Downloading DICOM files... (Attempt {retry_count + 1}/{max_retries})")
                    temp_download_dir = Path(temp_dir) / "DICOM"
                    scan.resources['DICOM'].download_dir(str(temp_download_dir))
                    move_files_from_download(temp_download_dir, scan_dir, scan.type)
                    logging.info(f"      Successfully downloaded scan {scan.id}")
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        logging.error(f"      Error downloading DICOM for scan {scan.id} after {max_retries} attempts: {str(e)}")
                        raise
                    else:
                        logging.warning(f"      Download attempt {retry_count} failed: {str(e)}. Retrying in 5 seconds...")
                        time.sleep(5)

def main():
    try:
        start_time = time.time()
        logging.info("\nStarting download process...")
        download_project_data(
            test_mode=args.test,
            subjects=args.subjects,
            sessions=args.sessions
        )
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
    main()  # Remove the exit() call here