import unittest
import os
import json
import pandas as pd
import pyarrow.parquet as pq
from attestation_export_pipeline import AttestationExportPipeline, generate_sample_data

class TestAttestationExportPipeline(unittest.TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.test_data = generate_sample_data(10)
        self.pipeline = AttestationExportPipeline(self.test_data)
        self.test_dir = 'test_output'
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up test files."""
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)
    
    def test_csv_export(self):
        """Test CSV export functionality."""
        filepath = os.path.join(self.test_dir, 'test.csv')
        result_path = self.pipeline.to_csv(filepath)
        
        self.assertTrue(os.path.exists(result_path))
        df = pd.read_csv(result_path)
        self.assertEqual(len(df), len(self.test_data))
        self.assertIn('export_timestamp', df.columns)
        self.assertIn('export_format', df.columns)
    
    def test_json_export(self):
        """Test JSON export functionality."""
        filepath = os.path.join(self.test_dir, 'test.json')
        result_path = self.pipeline.to_json(filepath)
        
        self.assertTrue(os.path.exists(result_path))
        with open(result_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn('metadata', data)
        self.assertIn('data', data)
        self.assertEqual(len(data['data']), len(self.test_data))
        self.assertEqual(data['metadata']['export_format'], 'json')
    
    def test_parquet_export(self):
        """Test Parquet export functionality."""
        filepath = os.path.join(self.test_dir, 'test.parquet')
        result_path = self.pipeline.to_parquet(filepath)
        
        self.assertTrue(os.path.exists(result_path))
        df = pd.read_parquet(result_path)
        self.assertEqual(len(df), len(self.test_data))
    
    def test_export_all_formats(self):
        """Test export to all formats."""
        files = self.pipeline.export_all_formats(self.test_dir, 'test_attestations')
        
        self.assertEqual(len(files), 3)
        self.assertIn('csv', files)
        self.assertIn('json', files)
        self.assertIn('parquet', files)
        
        for filepath in files.values():
            self.assertTrue(os.path.exists(filepath))
    
    def test_from_file_csv(self):
        """Test loading from CSV file."""
        csv_path = os.path.join(self.test_dir, 'test.csv')
        self.pipeline.to_csv(csv_path)
        
        loaded_pipeline = AttestationExportPipeline.from_file(csv_path, 'csv')
        self.assertEqual(len(loaded_pipeline.data), len(self.test_data))
    
    def test_from_file_json(self):
        """Test loading from JSON file."""
        json_path = os.path.join(self.test_dir, 'test.json')
        self.pipeline.to_json(json_path)
        
        loaded_pipeline = AttestationExportPipeline.from_file(json_path, 'json')
        self.assertEqual(len(loaded_pipeline.data), len(self.test_data))
    
    def test_from_file_parquet(self):
        """Test loading from Parquet file."""
        parquet_path = os.path.join(self.test_dir, 'test.parquet')
        self.pipeline.to_parquet(parquet_path)
        
        loaded_pipeline = AttestationExportPipeline.from_file(parquet_path, 'parquet')
        self.assertEqual(len(loaded_pipeline.data), len(self.test_data))
    
    def test_invalid_format(self):
        """Test handling of invalid format."""
        with self.assertRaises(ValueError):
            AttestationExportPipeline.from_file('test.txt', 'txt')


if __name__ == '__main__':
    unittest.main()