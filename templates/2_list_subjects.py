#!/usr/bin/env python3

"""
Template script to list details for a single subject in an XNAT project.
This script demonstrates how to access:
- Subject sessions
- Session scans 
- Scan details
"""

import xnat
import sys
import argparse
from datetime import datetime

# XNAT server configuration
XNAT_SERVER = "https://xnat.abudhabi.nyu.edu"
TOKEN_USER = "<paste your token alias here>"
TOKEN_SECRET = "<paste your token secret here>"
PROJECT_ID = "rokerslab_ari-clean"  # Replace with your project ID

def print_scan_info(scan):
    """Print relevant information about a scan."""
    print(f"    Scan {scan.id}: {scan.type}")
    print(f"      Description: {scan.series_description}")
    # print(f"      Quality: {scan.quality}")
    print(f"      Acquisition Date: {scan.start_date} {scan.start_time}")
    print(f"      Scanner: {scan.scanner} ({scan.field_strength}T)")
    print(f"      Body Part: {scan.body_part_examined}")

def print_session_info(session):
    """Print relevant information about a session."""
    print(f"\n  Session: {session.label}")
    print(f"  Date: {session.insert_date.strftime('%Y-%m-%d')}")
    
    print("\n  Scans:")
    try:
        for scan in session.scans.values():
            try:
                print_scan_info(scan)
            except AttributeError as e:
                print(f"    Scan {scan.id}: Unable to get scan details - {e}")
    except AttributeError as e:
        print("    Unable to access scans")
    
    print("\n  Available Resources:")
    for resource in session.resources.values():
        print(f"    - {resource.label}")

def print_subject_info(subject):
    """Print relevant information about a subject."""
    print(f"\nSubject ID: {subject.id}")
    print(f"Label: {subject.label}")
    
    print("\nSessions:")
    for session in subject.experiments.values():
        print_session_info(session)
    print("-" * 70)

def list_subject(subject_id=None):
    """Connect to XNAT and list details for a single subject in the specified project."""
    try:
        # Create XNAT connection
        with xnat.connect(XNAT_SERVER, user=TOKEN_USER, password=TOKEN_SECRET) as session:
            # Get the project
            project = session.projects[PROJECT_ID]
            print(f"\nProject: {project.name} ({project.id})")
            print("=" * 70)
            
            # Get subjects
            subjects = project.subjects
            if not subjects:
                print("No subjects found in this project.")
                return
            
            # If no subject_id provided, use the first subject
            if subject_id is None:
                subject = next(iter(subjects.values()))
            else:
                subject = subjects[subject_id]
                
            print_subject_info(subject)
                
    except KeyError:
        print(f"Error: Project '{PROJECT_ID}' or subject not found.")
        sys.exit(1)
    except xnat.exceptions.XNATError as e:
        print(f"XNAT Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List details for a single subject in XNAT project")
    parser.add_argument("--subject", help="Subject ID to list (defaults to first subject if not specified)")
    args = parser.parse_args()
    
    list_subject(args.subject)