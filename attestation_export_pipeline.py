import pandas as pd
import json
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime
import os
from typing import List, Dict, Any, Optional

class AttestationExportPipeline:
    """Pipeline for exporting attestation data to various formats (CSV, JSON, Parquet)"""
    
    def __init__(self, data: List[Dict[str, Any]]):
        """Initialize the pipeline with attestation data.
        
        Args:
            data: List of attestation records
        """
        self.data = data
        self.df = pd.DataFrame(data)
    
    def to_csv(self, filepath: str, include_metadata: bool = True) -> str:
        """Export data to CSV format.
        
        Args:
            filepath: Path to save the CSV file
            include_metadata: Whether to include metadata columns
            
        Returns:
            Path to the saved CSV file
        """
        if include_metadata:
            # Add metadata columns
            self.df['export_timestamp'] = datetime.now().isoformat()
            self.df['export_format'] = 'csv'
        
        self.df.to_csv(filepath, index=False)
        return filepath
    
    def to_json(self, filepath: str, orient: str = 'records', indent: int = 2) -> str:
        """Export data to JSON format.
        
        Args:
            filepath: Path to save the JSON file
            orient: JSON orientation ('records', 'index', 'values', 'split', 'table')
            indent: JSON indentation level
            
        Returns:
            Path to the saved JSON file
        """
        # Add metadata
        export_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'export_format': 'json',
                'record_count': len(self.data),
                'orient': orient
            },
            'data': self.data
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=indent, default=str)
        
        return filepath
    
    def to_parquet(self, filepath: str, compression: str = 'snappy') -> str:
        """Export data to Parquet format.
        
        Args:
            filepath: Path to save the Parquet file
            compression: Compression algorithm ('snappy', 'gzip', 'brotli', etc.)
            
        Returns:
            Path to the saved Parquet file
        """
        # Convert DataFrame to Arrow Table
        table = pa.Table.from_pandas(self.df)
        
        # Add metadata as table metadata
        metadata = {
            'export_timestamp': datetime.now().isoformat(),
            'export_format': 'parquet',
            'compression': compression
        }
        table = table.replace_schema_metadata(metadata)
        
        # Write to Parquet file
        pq.write_table(table, filepath, compression=compression)
        
        return filepath
    
    def export_all_formats(self, output_dir: str, filename_prefix: str = 'attestations') -> Dict[str, str]:
        """Export data to all supported formats.
        
        Args:
            output_dir: Directory to save the files
            filename_prefix: Prefix for output filenames
            
        Returns:
            Dictionary mapping format names to file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        files = {}
        
        # Export to CSV
        csv_path = os.path.join(output_dir, f'{filename_prefix}_{timestamp}.csv')
        files['csv'] = self.to_csv(csv_path)
        
        # Export to JSON
        json_path = os.path.join(output_dir, f'{filename_prefix}_{timestamp}.json')
        files['json'] = self.to_json(json_path)
        
        # Export to Parquet
        parquet_path = os.path.join(output_dir, f'{filename_prefix}_{timestamp}.parquet')
        files['parquet'] = self.to_parquet(parquet_path)
        
        return files
    
    @staticmethod
    def from_file(filepath: str, format_type: str) -> 'AttestationExportPipeline':
        """Create an instance from an existing file.
        
        Args:
            filepath: Path to the input file
            format_type: Format of the input file ('csv', 'json', 'parquet')
            
        Returns:
            AttestationExportPipeline instance
        """
        if format_type == 'csv':
            data = pd.read_csv(filepath).to_dict('records')
        elif format_type == 'json':
            with open(filepath, 'r') as f:
                json_data = json.load(f)
                data = json_data.get('data', [])
        elif format_type == 'parquet':
            df = pd.read_parquet(filepath)
            data = df.to_dict('records')
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        return AttestationExportPipeline(data)


def generate_sample_data(num_records: int = 100) -> List[Dict[str, Any]]:
    """Generate sample attestation data for testing."""
    sample_data = []
    
    for i in range(num_records):
        sample_data.append({
            'id': f'attestation_{i:04d}',
            'miner_id': f'miner_{i % 10:03d}',
            'timestamp': datetime.now().isoformat(),
            'claim_type': ['social_proof', 'follow_proof', 'data_quality'][i % 3],
            'value': float(i * 0.1),
            'confidence_score': min(0.95 + (i % 100) * 0.001, 1.0),
            'verified': i % 5 != 0,
            'metadata': {
                'source': f'source_{i % 5}',
                'category': f'category_{i % 3}'
            }
        })
    
    return sample_data


if __name__ == '__main__':
    # Generate sample data
    sample_data = generate_sample_data(50)
    
    # Create pipeline instance
    pipeline = AttestationExportPipeline(sample_data)
    
    # Export to all formats
    output_files = pipeline.export_all_formats('output', 'sample_attestations')
    
    print("Exported files:")
    for format_type, filepath in output_files.items():
        print(f"{format_type.upper()}: {filepath}")
    
    # Example: Load from JSON
    loaded_pipeline = AttestationExportPipeline.from_file(
        output_files['json'], 'json'
    )
    
    print(f"\nLoaded {len(loaded_pipeline.data)} records from JSON")