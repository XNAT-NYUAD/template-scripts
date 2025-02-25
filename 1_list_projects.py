#!/usr/bin/env python3

"""
Template script to list all accessible projects on an XNAT server.
This script demonstrates basic XNAT connection and project listing.
"""

import xnat
import sys
from pathlib import Path

# XNAT server configuration
XNAT_SERVER = "https://xnat.abudhabi.nyu.edu"
TOKEN_USER = "<paste your token alias here>"
TOKEN_SECRET = "<paste your token secret here>"

def list_projects():
    """Connect to XNAT and list all accessible projects."""
    try:
        # Create XNAT connection
        with xnat.connect(XNAT_SERVER, user=TOKEN_USER, password=TOKEN_SECRET) as session:
            
            # Get all projects
            projects = session.projects
            
            print("\nAccessible XNAT Projects:")
            print("-" * 50)
            
            # Print project information
            for project_id, project in projects.items():
                print(f"Project ID: {project_id}")
                print(f"Project Name: {project.name}")
                print(f"Description: {project.description}")
                print("-" * 50)
                
    except xnat.exceptions.XNATError as e:
        print(f"XNAT Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    list_projects() 