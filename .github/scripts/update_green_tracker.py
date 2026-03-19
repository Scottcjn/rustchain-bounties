#!/usr/bin/env python3
"""
Script to validate and update preserved machines data when new machines are added via PR.
This script ensures data integrity and formats consistency for the Green Tracker.
"""

import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path

# Configuration
MACHINES_FILE = "data/machines.json"
SCHEMA_FILE = "schemas/machine_schema.json"
REQUIRED_FIELDS = [
    "id", "name", "manufacturer", "model", "year", "cpu", "ram", "storage",
    "operating_system", "condition", "rescue_date", "rescue_location",
    "current_use", "submitted_by", "submission_date"
]

def load_json_file(file_path):
    """Load and parse JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File {file_path} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}")
        return None

def save_json_file(data, file_path):
    """Save data to JSON file with proper formatting."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, separators=(',', ': '))
            f.write('\n')  # Add newline at end of file
        return True
    except Exception as e:
        print(f"Error: Could not save {file_path}: {e}")
        return False

def validate_machine_data(machine):
    """Validate individual machine data against requirements."""
    errors = []
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in machine:
            errors.append(f"Missing required field: {field}")
        elif not machine[field] or str(machine[field]).strip() == "":
            errors.append(f"Field '{field}' cannot be empty")
    
    if errors:
        return errors
    
    # Validate ID format (alphanumeric with hyphens/underscores)
    if not re.match(r'^[a-zA-Z0-9_-]+$', machine['id']):
        errors.append("ID must contain only alphanumeric characters, hyphens, and underscores")
    
    # Validate year (reasonable range)
    try:
        year = int(machine['year'])
        if year < 1970 or year > datetime.now().year:
            errors.append(f"Year must be between 1970 and {datetime.now().year}")
    except ValueError:
        errors.append("Year must be a valid integer")
    
    # Validate dates
    date_fields = ['rescue_date', 'submission_date']
    for date_field in date_fields:
        try:
            datetime.strptime(machine[date_field], '%Y-%m-%d')
        except ValueError:
            errors.append(f"{date_field} must be in YYYY-MM-DD format")
    
    # Validate condition field
    valid_conditions = ['excellent', 'good', 'fair', 'poor', 'for_parts']
    if machine.get('condition', '').lower() not in valid_conditions:
        errors.append(f"Condition must be one of: {', '.join(valid_conditions)}")
    
    # Validate current_use field
    valid_uses = ['daily_driver', 'occasional_use', 'display', 'parts_donor', 'project', 'other']
    if machine.get('current_use', '').lower() not in valid_uses:
        errors.append(f"Current use must be one of: {', '.join(valid_uses)}")
    
    return errors

def check_duplicate_ids(machines):
    """Check for duplicate machine IDs."""
    ids = [machine['id'] for machine in machines]
    duplicates = []
    seen = set()
    
    for machine_id in ids:
        if machine_id in seen:
            duplicates.append(machine_id)
        seen.add(machine_id)
    
    return duplicates

def generate_machine_id(machine):
    """Generate a unique machine ID if not provided."""
    base = f"{machine.get('manufacturer', 'unknown').lower().replace(' ', '_')}-{machine.get('model', 'unknown').lower().replace(' ', '_')}"
    # Remove special characters
    base = re.sub(r'[^a-zA-Z0-9_-]', '', base)
    return base

def update_statistics(machines):
    """Update statistics based on current machine data."""
    stats = {
        'total_machines': len(machines),
        'by_manufacturer': {},
        'by_year': {},
        'by_condition': {},
        'by_current_use': {},
        'last_updated': datetime.now().isoformat()
    }
    
    for machine in machines:
        # Count by manufacturer
        manufacturer = machine.get('manufacturer', 'Unknown')
        stats['by_manufacturer'][manufacturer] = stats['by_manufacturer'].get(manufacturer, 0) + 1
        
        # Count by year
        year = str(machine.get('year', 'Unknown'))
        stats['by_year'][year] = stats['by_year'].get(year, 0) + 1
        
        # Count by condition
        condition = machine.get('condition', 'unknown')
        stats['by_condition'][condition] = stats['by_condition'].get(condition, 0) + 1
        
        # Count by current use
        current_use = machine.get('current_use', 'unknown')
        stats['by_current_use'][current_use] = stats['by_current_use'].get(current_use, 0) + 1
    
    return stats

def main():
    """Main function to validate and update machines data."""
    print("🔍 Validating machines data...")
    
    # Check if machines file exists
    if not os.path.exists(MACHINES_FILE):
        print(f"Creating new machines file: {MACHINES_FILE}")
        machines_data = {"machines": [], "statistics": {}}
        if not save_json_file(machines_data, MACHINES_FILE):
            sys.exit(1)
    
    # Load machines data
    machines_data = load_json_file(MACHINES_FILE)
    if machines_data is None:
        sys.exit(1)
    
    machines = machines_data.get('machines', [])
    
    # Validate each machine
    all_valid = True
    for i, machine in enumerate(machines):
        print(f"Validating machine {i + 1}: {machine.get('name', 'Unknown')}")
        
        # Generate ID if missing
        if not machine.get('id'):
            machine['id'] = generate_machine_id(machine)
            print(f"  Generated ID: {machine['id']}")
        
        errors = validate_machine_data(machine)
        if errors:
            print(f"  ❌ Validation errors for machine {i + 1}:")
            for error in errors:
                print(f"    - {error}")
            all_valid = False
        else:
            print(f"  ✅ Valid")
    
    # Check for duplicate IDs
    duplicates = check_duplicate_ids(machines)
    if duplicates:
        print(f"❌ Found duplicate IDs: {', '.join(duplicates)}")
        all_valid = False
    
    if not all_valid:
        print("\n❌ Validation failed. Please fix the errors above.")
        sys.exit(1)
    
    # Sort machines by submission date (newest first)
    machines.sort(key=lambda x: x.get('submission_date', ''), reverse=True)
    
    # Update statistics
    print("📊 Updating statistics...")
    statistics = update_statistics(machines)
    
    # Update machines data
    machines_data['machines'] = machines
    machines_data['statistics'] = statistics
    
    # Save updated data
    if save_json_file(machines_data, MACHINES_FILE):
        print(f"✅ Successfully updated {MACHINES_FILE}")
        print(f"📈 Total machines: {statistics['total_machines']}")
    else:
        print("❌ Failed to save updated data")
        sys.exit(1)
    
    # Also save statistics to separate file for easy access
    stats_file = "data/statistics.json"
    if save_json_file(statistics, stats_file):
        print(f"✅ Statistics saved to {stats_file}")
    
    print("\n🎉 All validations passed and data updated successfully!")

if __name__ == "__main__":
    main()