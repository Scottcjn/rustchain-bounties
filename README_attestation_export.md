# Attestation Data Export Pipeline

This pipeline provides functionality to export attestation data to multiple formats including CSV, JSON, and Parquet.

## Features

- Export to CSV, JSON, and Parquet formats
- Automatic metadata inclusion (timestamp, format info)
- Batch export to all formats
- Support for loading from existing files
- Type hints and comprehensive documentation

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from attestation_export_pipeline import AttestationExportPipeline, generate_sample_data

# Generate sample data
data = generate_sample_data(100)

# Create pipeline instance
pipeline = AttestationExportPipeline(data)

# Export to specific format
pipeline.to_csv('output.csv')
pipeline.to_json('output.json')
pipeline.to_parquet('output.parquet')

# Export to all formats
files = pipeline.export_all_formats('output_dir', 'my_attestations')
```

### Loading from Files

```python
# Load from existing file
pipeline = AttestationExportPipeline.from_file('data.json', 'json')
```

### Sample Data Generation

```python
# Generate test data
sample_data = generate_sample_data(50)
pipeline = AttestationExportPipeline(sample_data)
```

## File Formats

### CSV
- Standard comma-separated values format
- Includes metadata columns when exported

### JSON
- Structured format with metadata wrapper
- Configurable orientation and indentation

### Parquet
- Columnar storage format with compression
- Preserves data types efficiently

## Metadata

All exports include metadata such as:
- Export timestamp
- Export format
- Record count
- Additional format-specific information

## Examples

See the `if __name__ == '__main__':` block in the source file for a complete example.