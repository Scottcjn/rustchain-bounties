#!/usr/bin/env python3
"""
Script to validate and merge new machine submissions into the green tracker data file.
This script processes submissions from the community to add machines to the green tracker.
"""

import json
import sys
import os
import re
from datetime import datetime
from typing import Dict, List, Any, Optional

class GreenTrackerUpdater:
    def __init__(self, data_file: str = "data/green_tracker.json"):
        self.data_file = data_file
        self.data = self.load_existing_data()
        
    def load_existing_data(self) -> Dict[str, Any]:
        """Load existing green tracker data."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "machines": [],
            "statistics": {
                "total_machines": 0,
                "total_co2_saved": 0,
                "last_updated": datetime.now().isoformat()
            }
        }
    
    def validate_submission(self, submission: Dict[str, Any]) -> List[str]:
        """Validate a new machine submission."""
        errors = []
        required_fields = ['name', 'model', 'year', 'architecture', 'power', 'purpose', 'miner_id']
        
        for field in required_fields:
            if field not in submission:
                errors.append(f"Missing required field: {field}")
        
        # Validate year is reasonable (1970-current year)
        if 'year' in submission:
            current_year = datetime.now().year
            if not isinstance(submission['year'], int) or submission['year'] < 1970 or submission['year'] > current_year:
                errors.append(f"Invalid year: {submission['year']}")
        
        # Validate miner_id format (alphanumeric with optional numbers)
        if 'miner_id' in submission:
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', submission['miner_id']):
                errors.append(f"Invalid miner_id format: {submission['miner_id']}")
        
        return errors
    
    def add_machine(self, submission: Dict[str, Any]) -> bool:
        """Add a validated machine to the tracker."""
        errors = self.validate_submission(submission)
        if errors:
            print(f"Validation errors: {', '.join(errors)}")
            return False
        
        # Generate new ID
        max_id = max([m.get('id', 0) for m in self.data['machines']], default=0)
        submission['id'] = max_id + 1
        
        # Add to machines list
        self.data['machines'].append(submission)
        
        # Update statistics
        self.data['statistics']['total_machines'] = len(self.data['machines'])
        self.data['statistics']['last_updated'] = datetime.now().isoformat()
        
        return True
    
    def save_data(self) -> None:
        """Save the updated data to file."""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python update_green_tracker.py <submission_file>")
        sys.exit(1)
    
    submission_file = sys.argv[1]
    if not os.path.exists(submission_file):
        print(f"Error: Submission file {submission_file} not found")
        sys.exit(1)
    
    try:
        with open(submission_file, 'r', encoding='utf-8') as f:
            submission = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
    
    updater = GreenTrackerUpdater()
    if updater.add_machine(submission):
        updater.save_data()
        print(f"Successfully added machine: {submission.get('name', 'Unknown')}")
    else:
        print("Failed to add machine due to validation errors")
        sys.exit(1)

if __name__ == "__main__":
    main()ew machine submission."""
        errors = []
        required_fields = [
            "machine_type", "brand", "model", "year_rescued",
            "rescue_story", "current_use", "submitter_name"
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in submission or not submission[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate machine_type
        valid_types = [
            "laptop", "desktop", "server", "tablet", "smartphone",
            "printer", "monitor", "router", "switch", "other"
        ]
        if "machine_type" in submission:
            if submission["machine_type"].lower() not in valid_types:
                errors.append(f"Invalid machine_type. Must be one of: {', '.join(valid_types)}")
        
        # Validate year
        if "year_rescued" in submission:
            try:
                year = int(submission["year_rescued"])
                current_year = datetime.now().year
                if year < 1980 or year > current_year:
                    errors.append(f"Invalid year_rescued. Must be between 1980 and {current_year}")
            except (ValueError, TypeError):
                errors.append("year_rescued must be a valid integer")
        
        # Validate rescue_story length
        if "rescue_story" in submission:
            if len(submission["rescue_story"]) < 50:
                errors.append("rescue_story must be at least 50 characters long")
            if len(submission["rescue_story"]) > 1000:
                errors.append("rescue_story must be no more than 1000 characters long")
        
        # Validate current_use length
        if "current_use" in submission:
            if len(submission["current_use"]) < 10:
                errors.append("current_use must be at least 10 characters long")
            if len(submission["current_use"]) > 500:
                errors.append("current_use must be no more than 500 characters long")
        
        # Validate submitter_name
        if "submitter_name" in submission:
            if not re.match(r'^[a-zA-Z0-9_\-\s]+$', submission["submitter_name"]):
                errors.append("submitter_name contains invalid characters")
            if len(submission["submitter_name"]) > 100:
                errors.append("submitter_name must be no more than 100 characters long")
        
        # Validate optional fields
        if "estimated_co2_saved" in submission:
            try:
                co2_saved = float(submission["estimated_co2_saved"])
                if co2_saved < 0 or co2_saved > 1000:
                    errors.append("estimated_co2_saved must be between 0 and 1000 kg")
            except (ValueError, TypeError):
                errors.append("estimated_co2_saved must be a valid number")
        
        return errors
    
    def check_duplicate(self, submission: Dict[str, Any]) -> bool:
        """Check if a similar machine already exists."""
        for machine in self.data["machines"]:
            if (machine["brand"].lower() == submission["brand"].lower() and
                machine["model"].lower() == submission["model"].lower() and
                machine["submitter_name"].lower() == submission["submitter_name"].lower()):
                return True
        return False
    
    def estimate_co2_savings(self, machine_type: str, year_rescued: int) -> float:
        """Estimate CO2 savings based on machine type and age."""
        current_year = datetime.now().year
        age = current_year - year_rescued
        
        # Base CO2 savings by machine type (kg CO2 equivalent)
        base_savings = {
            "laptop": 50,
            "desktop": 80,
            "server": 200,
            "tablet": 30,
            "smartphone": 15,
            "printer": 40,
            "monitor": 35,
            "router": 25,
            "switch": 45,
            "other": 40
        }
        
        # Apply age multiplier (older machines have higher impact if saved)
        age_multiplier = min(1.0 + (age * 0.1), 2.0)
        
        return base_savings.get(machine_type.lower(), 40) * age_multiplier
    
    def add_machine(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        """Add a validated machine to the tracker."""
        # Generate unique ID
        machine_id = f"machine_{len(self.data['machines']) + 1:04d}"
        
        # Estimate CO2 savings if not provided
        if "estimated_co2_saved" not in submission or not submission["estimated_co2_saved"]:
            submission["estimated_co2_saved"] = self.estimate_co2_savings(
                submission["machine_type"], 
                int(submission["year_rescued"])
            )
        
        # Create machine record
        machine = {
            "id": machine_id,
            "machine_type": submission["machine_type"].lower(),
            "brand": submission["brand"],
            "model": submission["model"],
            "year_rescued": int(submission["year_rescued"]),
            "rescue_story": submission["rescue_story"],
            "current_use": submission["current_use"],
            "estimated_co2_saved": float(submission["estimated_co2_saved"]),
            "submitter_name": submission["submitter_name"],
            "submission_date": datetime.now().isoformat(),
            "verified": False
        }
        
        # Add optional fields
        if "photo_url" in submission:
            machine["photo_url"] = submission["photo_url"]
        if "location" in submission:
            machine["location"] = submission["location"]
        
        self.data["machines"].append(machine)
        
        # Update statistics
        self.update_statistics()
        
        return machine
    
    def update_statistics(self):
        """Update tracker statistics."""
        self.data["statistics"] = {
            "total_machines": len(self.data["machines"]),
            "total_co2_saved": sum(m["estimated_co2_saved"] for m in self.data["machines"]),
            "last_updated": datetime.now().isoformat(),
            "machines_by_type": {},
            "machines_by_year": {}
        }
        
        # Count by type
        for machine in self.data["machines"]:
            machine_type = machine["machine_type"]
            self.data["statistics"]["machines_by_type"][machine_type] = \
                self.data["statistics"]["machines_by_type"].get(machine_type, 0) + 1
        
        # Count by rescue year
        for machine in self.data["machines"]:
            year = str(machine["year_rescued"])
            self.data["statistics"]["machines_by_year"][year] = \
                self.data["statistics"]["machines_by_year"].get(year, 0) + 1
    
    def save_data(self):
        """Save the updated data to file."""
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def process_submission(self, submission_file: str) -> Dict[str, Any]:
        """Process a submission file."""
        try:
            with open(submission_file, 'r', encoding='utf-8') as f:
                submission = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return {"success": False, "error": f"Error reading submission file: {e}"}
        
        # Validate submission
        errors = self.validate_submission(submission)
        if errors:
            return {"success": False, "errors": errors}
        
        # Check for duplicates
        if self.check_duplicate(submission):
            return {"success": False, "error": "Similar machine already exists in the tracker"}
        
        # Add machine
        try:
            machine = self.add_machine(submission)
            self.save_data()
            return {
                "success": True, 
                "machine": machine,
                "message": f"Successfully added machine {machine['id']} to the green tracker"
            }
        except Exception as e:
            return {"success": False, "error": f"Error adding machine: {e}"}
    
    def list_machines(self, machine_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List machines, optionally filtered by type."""
        machines = self.data["machines"]
        if machine_type:
            machines = [m for m in machines if m["machine_type"] == machine_type.lower()]
        return sorted(machines, key=lambda x: x["submission_date"], reverse=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tracker statistics."""
        return self.data["statistics"]

def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python update_green_tracker.py <command> [args]")
        print("Commands:")
        print("  add <submission_file>  - Add a new machine from JSON file")
        print("  list [type]           - List machines (optionally by type)")
        print("  stats                 - Show statistics")
        sys.exit(1)
    
    tracker = GreenTrackerUpdater()
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) != 3:
            print("Usage: python update_green_tracker.py add <submission_file>")
            sys.exit(1)
        
        result = tracker.process_submission(sys.argv[2])
        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"Machine ID: {result['machine']['id']}")
            print(f"CO2 Saved: {result['machine']['estimated_co2_saved']:.1f} kg")
        else:
            print("❌ Failed to add machine:")
            if "errors" in result:
                for error in result["errors"]:
                    print(f"  - {error}")
            else:
                print(f"  {result['error']}")
            sys.exit(1)
    
    elif command == "list":
        machine_type = sys.argv[2] if len(sys.argv) > 2 else None
        machines = tracker.list_machines(machine_type)
        
        if not machines:
            print("No machines found.")
        else:
            print(f"Found {len(machines)} machines:")
            for machine in machines:
                print(f"  {machine['id']}: {machine['brand']} {machine['model']} "
                      f"({machine['machine_type']}, {machine['year_rescued']}) "
                      f"- {machine['estimated_co2_saved']:.1f}kg CO2 saved")
    
    elif command == "stats":
        stats = tracker.get_statistics()
        print(f"Green Tracker Statistics:")
        print(f"  Total Machines: {stats['total_machines']}")
        print(f"  Total CO2 Saved: {stats['total_co2_saved']:.1f} kg")
        print(f"  Last Updated: {stats['last_updated']}")
        
        if "machines_by_type" in stats:
            print(f"  By Type:")
            for machine_type, count in stats["machines_by_type"].items():
                print(f"    {machine_type}: {count}")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()