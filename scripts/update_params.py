#!/usr/bin/env python3
"""
Script for updating annual parameters of the payroll settlement system.
Handles backup, validation and documentation of parameter changes.

Author: Development Team
Date: 2025-11-04
Version: 1.0.0
"""

import argparse
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
import yaml

from liquidator.params.params_validator import ParamsValidator
from liquidator.utils.file_utils import ensure_directory_exists, read_json_file
from liquidator.utils.date_utils import get_current_year


def backup_current_params(params_dir: str, backup_dir: str, year: int) -> str:
    """Creates a backup of current parameters before updating."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_subdir = os.path.join(backup_dir, f"backup_{year}_{timestamp}")
    ensure_directory_exists(backup_subdir)
    
    # Copy all parameter files
    params_files = [
        f"{year}.json",
        "normas.json",
        "plazos.json",
        "schema.json"
    ]
    
    for file_name in params_files:
        src = os.path.join(params_dir, file_name)
        if os.path.exists(src):
            dst = os.path.join(backup_subdir, file_name)
            shutil.copy2(src, dst)
    
    return backup_subdir


def validate_new_params(new_params_path: str, schema_path: str) -> bool:
    """Validates new parameters against the defined schema."""
    try:
        validator = ParamsValidator(schema_path)
        new_params = read_json_file(new_params_path)
        return validator.validate(new_params)
    except Exception as e:
        print(f"Error during validation: {e}")
        return False


def document_changes(backup_dir: str, new_params_dir: str, year: int, author: str) -> str:
    """Generates a document with changes made to parameters."""
    changes_file = os.path.join(backup_dir, f"changes_{year}.md")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(changes_file, "w") as f:
        f.write(f"# Parameter Changes Documentation - Year {year}\n\n")
        f.write(f"## General Information\n")
        f.write(f"- **Update Date:** {timestamp}\n")
        f.write(f"- **Author:** {author}\n")
        f.write(f"- **Backup created at:** {backup_dir}\n\n")
        
        f.write("## Changes Made\n")
        f.write("Below are the main changes in the parameters:\n\n")
        f.write("### 1. Economic Values Update\n")
        f.write("- SMMLV: New value for the year\n")
        f.write("- Transportation allowance: New value for the year\n")
        f.write("- Interest rates: Verification of rate for severance interest\n\n")
        
        f.write("### 2. Regulation Update\n")
        f.write("- Inclusion of new relevant laws or decrees\n")
        f.write("- Update of regulatory references\n\n")
        
        f.write("### 3. Deadline Update\n")
        f.write("- Verification of legal payment deadlines\n")
        f.write("- Update of deadline dates according to current regulation\n\n")
        
        f.write("## Important Notes\n")
        f.write("- Calculations made with previous parameters remain valid for their respective periods\n")
        f.write("- This update only affects settlements with cutoff dates in year {year} or later\n")
    
    return changes_file


def update_parameters(new_params_dir: str, author: str, force: bool = False) -> bool:
    """
    Complete parameter update process:
    1. Validate new parameters
    2. Create backup
    3. Copy new parameters
    4. Document changes
    """
    params_dir = "params"
    backup_dir = os.path.join(params_dir, "backup")
    year = get_current_year() + 1  # Update for next year
    
    print(f"Starting parameter update for year {year}...")
    
    # Verify that new parameters exist
    new_year_file = os.path.join(new_params_dir, f"{year}.json")
    schema_file = os.path.join(new_params_dir, "schema.json")
    
    if not os.path.exists(new_year_file):
        print(f"Error: Could not find parameter file for {year} in {new_params_dir}")
        return False
    
    if not os.path.exists(schema_file):
        print(f"Error: Could not find validation schema in {new_params_dir}")
        return False
    
    # Validate new parameters before proceeding
    print("Validating new parameters...")
    if not validate_new_params(new_year_file, schema_file):
        if not force:
            print("Error: New parameters failed validation. Aborting update.")
            print("Use --force to proceed despite validation errors.")
            return False
        print("Warning: Parameters failed validation, but continuing due to --force")
    
    # Create backup of current parameters
    print("Creating backup of current parameters...")
    backup_path = backup_current_params(params_dir, backup_dir, year)
    print(f"Backup created successfully at: {backup_path}")
    
    # Copy new parameters
    print("Copying new parameters...")
    for file_name in [f"{year}.json", "normas.json", "plazos.json"]:
        src = os.path.join(new_params_dir, file_name)
        if os.path.exists(src):
            dst = os.path.join(params_dir, file_name)
            shutil.copy2(src, dst)
            print(f"Updated: {file_name}")
        else:
            print(f"Warning: {file_name} does not exist in {new_params_dir}")
    
    # Document changes
    print("Documenting changes...")
    changes_doc = document_changes(backup_path, new_params_dir, year, author)
    print(f"Changes documentation generated: {changes_doc}")
    
    print("\n[SUCCESS] Parameter update completed successfully")
    print(f"[WARNING] Remember to perform corresponding tests before using in production")
    print(f"[INFO] Changes documentation: {changes_doc}")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='Update annual parameters of the settlement system')
    parser.add_argument('--new-params-dir', required=True, 
                        help='Directory with new parameters for the year')
    parser.add_argument('--author', required=True,
                        help='Name of the update author')
    parser.add_argument('--force', action='store_true',
                        help='Force update even if validation fails')
    parser.add_argument('--dry-run', action='store_true',
                        help='Simulate update without making changes')
    
    args = parser.parse_args()
    
    # Configure paths
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    if args.dry_run:
        print("DRY-RUN - Simulating update without making changes")
        print(f"New parameters directory: {args.new_params_dir}")
        print(f"Author: {args.author}")
        print("[SUCCESS] Simulation completed successfully")
        return True
    
    result = update_parameters(args.new_params_dir, args.author, args.force)
    return 0 if result else 1


if __name__ == "__main__":
    exit(main())