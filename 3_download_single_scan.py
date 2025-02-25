#!/usr/bin/env python3

"""
Template script to download a single scan from XNAT.
This script demonstrates how to download DICOM files from a specific scan.
If no subject/session/scan specified, downloads first scan of first subject.
"""

import xnat
import sys
import argparse
import tempfile
from pathlib import Path
import shutil

# Default XNAT configuration
DEFAULT_SERVER = "https://xnat.abudhabi.nyu.edu"
DEFAULT_TOKEN = "656059bb-0b85-4c5d-8deb-4a7c397a7ba0"
DEFAULT_SECRET = "9ZjS8KoLRPfvYHInjMcU13w9FdLWkMjU7h0MNf5u8r8rhJLNZpg0xDNg6OSIsddM"
PROJECT_ID = "rokerslab_ari-clean"  # Default project ID required

def setup_connection(server, username, password):
    """Create and return an XNAT connection."""
    try:
        return xnat.connect(server, user=username, password=password)
    except Exception as e:
        print(f"Failed to connect to XNAT: {e}")
        sys.exit(1)

def download_scan(project_id=PROJECT_ID, subject_id=None, session_id=None, scan_id=None, output_dir=None):
    """Download a specific scan from XNAT. If no subject/session/scan IDs provided, downloads first scan of first subject."""
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir or "downloaded_data")
    output_path.mkdir(parents=True, exist_ok=True)
    
    with setup_connection(DEFAULT_SERVER, DEFAULT_TOKEN, DEFAULT_SECRET) as session:
        try:
            # Get project using PROJECT_ID
            project = session.projects[project_id]
            
            # Get first subject if none specified
            if not subject_id:
                subject = next(iter(project.subjects.values()))
                subject_id = subject.id
            else:
                subject = project.subjects[subject_id]
            
            # Get first session if none specified
            if not session_id:
                experiment = next(iter(subject.experiments.values()))
                session_id = experiment.id
            else:
                experiment = subject.experiments[session_id]
            
            # Get first scan if none specified
            if not scan_id:
                scan = next(iter(experiment.scans.values()))
                scan_id = scan.id
            else:
                scan = experiment.scans[scan_id]
            
            print(f"\nDownloading scan:")
            print(f"Project: {project.id}")
            print(f"Subject: {subject_id}")
            print(f"Session: {session_id}")
            print(f"Scan ID: {scan_id}")
            print(f"Scan Type: {scan.type}")
            
            # Check if scan has DICOM resource
            if 'DICOM' not in scan.resources:
                print("Error: No DICOM resource found for this scan")
                sys.exit(1)
            
            # Create a temporary directory for download
            with tempfile.TemporaryDirectory() as temp_dir:
                print("\nDownloading DICOM files...")
                
                # Download the DICOM files
                scan.resources['DICOM'].download_dir(temp_dir)
                
                # Move files to output directory
                temp_path = Path(temp_dir)
                dicom_files = list(temp_path.rglob('*.dcm'))
                
                if not dicom_files:
                    print("No DICOM files found in the scan")
                    sys.exit(1)
                
                # Create scan-specific directory
                scan_dir = output_path / f"scan-{scan_id}_{scan.type}"
                scan_dir.mkdir(exist_ok=True)
                
                print(f"Moving {len(dicom_files)} files to {scan_dir}...")
                for file in dicom_files:
                    shutil.move(str(file), str(scan_dir / file.name))
                
                print(f"\nDownload complete! Files saved to: {scan_dir}")
                
        except KeyError as e:
            print(f"Error: Resource not found - {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error during download: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Download a single scan from XNAT')
    parser.add_argument('--project', default=PROJECT_ID, help='Project ID')
    parser.add_argument('--subject', help='Subject ID (defaults to first subject)')
    parser.add_argument('--session', help='Session/Experiment ID (defaults to first session)')
    parser.add_argument('--scan', help='Scan ID (defaults to first scan)')
    parser.add_argument('--output', help='Output directory for downloaded files')
    
    args = parser.parse_args()
    
    download_scan(
        args.project,
        args.subject,
        args.session,
        args.scan,
        args.output
    )

if __name__ == "__main__":
    main() 
