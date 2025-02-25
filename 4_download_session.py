#!/usr/bin/env python3

"""
Template script to download all scans from a session/experiment in XNAT.
This script demonstrates how to download multiple scans and filter by scan type.
"""

import xnat
import sys
import argparse
import tempfile
from pathlib import Path
import shutil

# Default XNAT configuration
DEFAULT_SERVER = "https://xnat.abudhabi.nyu.edu"
DEFAULT_TOKEN = "<paste your token alias here>"
DEFAULT_SECRET = "<paste your token secret here>"
PROJECT_ID = "rokerslab_ari-clean"  # Add default project ID like in script 3

def setup_connection(server, username, password):
    """Create and return an XNAT connection."""
    try:
        return xnat.connect(server, user=username, password=password)
    except Exception as e:
        print(f"Failed to connect to XNAT: {e}")
        sys.exit(1)

def download_scan(session, scan, output_path):
    """Download a single scan from XNAT and save to output directory."""
    # Check if scan has DICOM resource
    if 'DICOM' not in scan.resources:
        print(f"Warning: No DICOM resource found for scan {scan.id}")
        return

    # Create scan-specific directory
    scan_dir = output_path / f"scan-{scan.id}_{scan.type}"
    scan_dir.mkdir(exist_ok=True)

    # Use temporary directory for download
    with tempfile.TemporaryDirectory() as temp_dir:
        print("Downloading DICOM files...")
        
        # Download the DICOM files
        scan.resources['DICOM'].download_dir(temp_dir)
        
        # Move files to output directory
        temp_path = Path(temp_dir)
        dicom_files = list(temp_path.rglob('*.dcm'))
        
        if not dicom_files:
            print("No DICOM files found in this scan")
            return
        
        print(f"Moving {len(dicom_files)} files to {scan_dir}...")
        for file in dicom_files:
            shutil.move(str(file), str(scan_dir / file.name))
        
        print("Scan download complete!")

def download_session(project_id=PROJECT_ID, subject_id=None, session_id=None, output_dir=None, scan_types=None):
    """Download all scans from a session that match the specified scan types."""
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir or "downloaded_data")
    output_path.mkdir(parents=True, exist_ok=True)
    
    with setup_connection(DEFAULT_SERVER, DEFAULT_TOKEN, DEFAULT_SECRET) as session:
        try:
            # Get project
            project = session.projects[project_id]
            
            # Get subject
            if not subject_id:
                subject = next(iter(project.subjects.values()))
                subject_id = subject.id
            else:
                subject = project.subjects[subject_id]
            
            # Get session
            if not session_id:
                experiment = next(iter(subject.experiments.values()))
                session_id = experiment.id
            else:
                experiment = subject.experiments[session_id]
            
            print(f"\nDownloading session:")
            print(f"Project: {project_id}")
            print(f"Subject: {subject.label}")
            print(f"Session: {experiment.label}")
            
            # Create session directory
            session_dir = output_path / f"session-{experiment.label}"
            session_dir.mkdir(exist_ok=True)
            
            # Get all scans
            scans = experiment.scans
            if not scans:
                print("No scans found in this session")
                return
            
            print(f"\nFound {len(scans)} scans in session")
            
            # Download each scan that matches the filter
            for scan_id, scan in scans.items():
                if scan_types and scan.type not in scan_types:
                    print(f"\nSkipping scan {scan_id} (type: {scan.type}) - not in requested types")
                    continue
                
                print(f"\nProcessing scan {scan_id} (type: {scan.type})")
                download_scan(session, scan, session_dir)
            
            print(f"\nSession download complete! Files saved to: {session_dir}")
                
        except KeyError as e:
            print(f"Error: Resource not found - {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error during download: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Download all scans from an XNAT session')
    parser.add_argument('--project', default=PROJECT_ID, help='Project ID')
    parser.add_argument('--subject', help='Subject ID (defaults to first subject)')
    parser.add_argument('--session', help='Session/Experiment ID (defaults to first session)')
    parser.add_argument('--output', help='Output directory for downloaded files')
    parser.add_argument('--scan-types', nargs='+', help='Optional: List of scan types to download (e.g., T1 T2)')
    
    args = parser.parse_args()
    
    download_session(
        args.project,
        args.subject,
        args.session,
        args.output,
        args.scan_types
    )

if __name__ == "__main__":
    main() 