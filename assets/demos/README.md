# RustChain Demo Recordings

Terminal recordings of the miner install and first attestation workflow.

## Recordings

| File | Description | Duration |
|------|-------------|----------|
| `miner-install.cast` | Clone repo, start miner, first attestation | ~35s |
| `first-attestation.cast` | Verify attestation, check balance, epoch info | ~25s |

## Playback

### asciinema (recommended)

```bash
# Install asciinema
pip install asciinema

# Play a recording in your terminal
asciinema play assets/demos/miner-install.cast
asciinema play assets/demos/first-attestation.cast

# Play at 2x speed
asciinema play -s 2 assets/demos/miner-install.cast
```

### Convert to GIF

Use [agg](https://github.com/asciinema/agg) (asciinema GIF generator):

```bash
# Install agg (Rust required)
cargo install --git https://github.com/asciinema/agg

# Convert cast → GIF
agg assets/demos/miner-install.cast miner-install.gif
agg assets/demos/first-attestation.cast first-attestation.gif
```

### Embed on GitHub

GitHub renders `.cast` files as plain text, but you can link to asciinema.org
for web playback or use the GIF versions directly in markdown:

```markdown
![Miner Install Demo](assets/demos/miner-install.gif)
```

## Re-recording

To re-record with a live node:

```bash
./scripts/record_demos.sh              # Record both
./scripts/record_demos.sh install      # Install demo only
./scripts/record_demos.sh attestation  # Attestation demo only
```

See `scripts/record_demos.sh --help` for details.
