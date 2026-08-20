"""Module for generating syndication activity reports and managing run data."""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union

class SyndicationRun:
    """Class representing a single syndication run with metadata and results.

    Attributes:
        timestamp (datetime): When the run was executed
        source (str): Original content source
        targets (List[str]): List of target platforms
        stats (Dict): Performance metrics
    """

    def __init__(self, source: str, targets: List[str]):
        """Initialize a new syndication run.

        Args:
            source: Original content identifier (URL or internal ID)
            targets: List of platforms to syndicate to (e.g., ['twitter', 'linkedin'])
        """
        self.timestamp = datetime.now()
        self.source = source
        self.targets = targets
        self.stats = {}

    def to_dict(self) -> Dict:
        """Serialize run data to dictionary for storage/transmission.

        Returns:
            Dictionary containing all run attributes in JSON-serializable format
        """
        return {
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'targets': self.targets,
            'stats': self.stats
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SyndicationRun':
        """Deserialize run data from dictionary.

        Args:
            data: Dictionary containing run attributes

        Returns:
            New SyndicationRun instance populated with data
        """
        run = cls(data['source'], data['targets'])
        run.timestamp = datetime.fromisoformat(data['timestamp'])
        run.stats = data['stats']
        return run

class SyndicationLogger:
    """Manages storage and retrieval of syndication runs with persistence.

    Handles loading/saving runs to/from disk and provides query methods.
    """

    def __init__(self, storage_path: str = 'syndication_runs.json'):
        """Initialize logger with storage configuration.

        Args:
            storage_path: Path to JSON file for persistence
        """
        self.storage_path = storage_path
        self.runs = []
        self._load()

    def _load(self) -> None:
        """Load existing runs from storage file if it exists."""
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                self.runs = [SyndicationRun.from_dict(run) for run in json.load(f)]

    def _save(self) -> None:
        """Save current runs to storage file."""
        with open(self.storage_path, 'w') as f:
            json.dump([run.to_dict() for run in self.runs], f, indent=2)

    def log_run(self, run: SyndicationRun) -> None:
        """Record a completed syndication run.

        Args:
            run: SyndicationRun instance to store
        """
        self.runs.append(run)
        self._save()

    def get_runs(self, source: Optional[str] = None) -> List[SyndicationRun]:
        """Get runs filtered by source.

        Args:
            source: Optional filter for specific source content

        Returns:
            List of matching SyndicationRun instances
        """
        return [run for run in self.runs if source is None or run.source == source]

    def get_all_runs(self) -> List[SyndicationRun]:
        """Get all stored syndication runs.

        Returns:
            Complete list of all SyndicationRun instances
        """
        return self.runs.copy()

    def get_total_stats(self) -> Dict:
        """Calculate aggregated statistics across all runs.

        Returns:
            Dictionary containing:
            - total_runs: Count of all runs
            - unique_targets: Set of all target platforms
            - avg_stats: Average metrics across runs
        """
        if not self.runs:
            return {}

        total = len(self.runs)
        targets = set()
        avg_stats = {}

        for run in self.runs:
            targets.update(run.targets)
            for k, v in run.stats.items():
                avg_stats[k] = avg_stats.get(k, 0) + v

        return {
            'total_runs': total,
            'unique_targets': list(targets),
            'avg_stats': {k: v/total for k, v in avg_stats.items()}
        }

def main():
    """Command-line interface for managing syndication runs.

    Provides basic operations:
    - Create new runs
    - View statistics
    - Export data
    """
    logger = SyndicationLogger()
    print("Syndication Report Manager")
    print("1. Add new run")
    print("2. View statistics")
    print("3. Exit")

    while True:
        choice = input("Select option: ")
        if choice == '1':
            source = input("Source content: ")
            targets = input("Targets (comma-separated): ").split(',')
            run = SyndicationRun(source, targets)
            logger.log_run(run)
            print("Run logged successfully")
        elif choice == '2':
            stats = logger.get_total_stats()
            print(f"Total runs: {stats.get('total_runs', 0)}")
            print(f"Unique targets: {', '.join(stats.get('unique_targets', []))}")
        elif choice == '3':
            break
        else:
            print("Invalid option")