# RustChain Vintage Hardware Museum 3D

Issue: [#65](https://github.com/Scottcjn/rustchain-bounties/issues/65)

This folder contains a static Three.js museum for RustChain proof-of-antiquity hardware.

## Implemented Scope

- Full-screen WebGL exhibit built with Three.js.
- Procedural 3D exhibits for:
  - PowerBook G4 collection.
  - Power Mac G4 MDD + G5 Dual.
  - IBM POWER8 S824 centerpiece.
  - Dell C4130 GPU cluster.
  - 486/386 laptops and SPARCstations.
- Keyboard movement and pointer look.
- Mobile touch movement controls.
- Click/tap exhibit inspection panel.
- Live read-only miner fetch from `https://explorer.rustchain.org/api/miners`.
- Green glow and ring state for exhibits with matching active miner data.
- Responsive HUD with total miners, active miners, and vintage miner count.

## Files

- `index.html` - static entry point and import map.
- `styles.css` - HUD, detail panel, and mobile controls.
- `museum.mjs` - Three.js scene, procedural exhibit models, movement, raycast interaction, and live API mapping.

## Local Validation

The Three.js import map loads from a CDN, so serve the folder over HTTP:

```powershell
python -m http.server 8080
```

Then open `http://localhost:8080/museum/`.

## Notes

The app is read-only and does not request wallet secrets, private keys, or write credentials. It uses the explorer miners API to map live data onto the closest matching exhibit by architecture, miner name, family, or hardware type.
