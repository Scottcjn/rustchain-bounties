# BCOS Certified Directory

Static MVP for bounty #301. The directory lets agents and humans browse certified RustChain ecosystem projects and review trust metadata before clicking through.

## Files

- `data/projects.json` - structured project entries.
- `build.mjs` - dependency-free Node build step.
- `dist/index.html` - generated static site output.

## Add A Project

1. Add an entry to `data/projects.json`.
2. Include `name`, `url`, `githubRepo`, `category`, `bcosTier`, `latestAttestedSha`, `sbomHash`, and `reviewNote`.
3. Run:

```sh
node bcos/certified-directory/build.mjs
```

The generated file is written to `bcos/certified-directory/dist/index.html`.

## Deploy

The `dist/index.html` file is static and can be served from GitHub Pages, rustchain.org, or any static host.
