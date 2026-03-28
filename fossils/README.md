# Fossil Record

Static deployment bundle for RustChain's "Attestation Archaeology" visualization.

## Files

- `index.html`: terminal-style visualizer with hover details, first-appearance markers, epoch settlement lines, and architecture toggles.
- `fossil_record_export.py`: creates `fossil-record.sample.json` from either:
  - a SQLite export with attestation-like tables,
  - a JSON snapshot, or
  - the live RustChain API (`/api/miners` + `/epoch`) with deterministic synthetic history.
- `fossil-record.sample.json`: ready-to-open dataset for local preview or static hosting.

## Usage

```powershell
python fossils/fossil_record_export.py --sample --epochs 64
python -m http.server 8080
```

Then open `http://localhost:8080/fossils/`.

## SQLite mode

If you have a RustChain SQLite export:

```powershell
python fossils/fossil_record_export.py --sqlite C:\path\to\rustchain.db --output fossils/fossil-record.sample.json
```
