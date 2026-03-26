#!/usr/bin/env python3
"""Generate mock attestation data for the Fossil Record visualization."""
import json
import random

arch_templates = [
    {"arch": "68K", "family": "Motorola", "color": "#8B4513", "devices": [
        {"name": "Commodore Amiga 500", "cores": 1}, {"name": "Apple Macintosh II", "cores": 1},
        {"name": "Atari ST", "cores": 1}, {"name": "Apple Macintosh IIcx", "cores": 1},
        {"name": "Sun Microsystems Sun-3", "cores": 1}, {"name": "Apple Macintosh SE/30", "cores": 1},
        {"name": "NeXTcube", "cores": 1}, {"name": "Apple Macintosh IIfx", "cores": 1},
    ]},
    {"arch": "G3", "family": "IBM", "color": "#CD7F32", "devices": [
        {"name": "Apple Power Macintosh 8100", "cores": 1}, {"name": "IBM PowerPC 604", "cores": 1},
        {"name": "Apple PowerBook 5300", "cores": 1}, {"name": "Apple Power Macintosh G3", "cores": 1},
        {"name": "IBM RS/6000 44P", "cores": 2}, {"name": "Apple iBook G3", "cores": 1},
    ]},
    {"arch": "G4", "family": "Freescale", "color": "#B87333", "devices": [
        {"name": "Apple PowerBook G4", "cores": 1}, {"name": "Apple MacBook Pro G4", "cores": 1},
        {"name": "Apple Mac Pro G4", "cores": 2}, {"name": "Apple Mac mini G4", "cores": 1},
    ]},
    {"arch": "G5", "family": "IBM", "color": "#CD853F", "devices": [
        {"name": "IBM PowerMac G5", "cores": 2}, {"name": "Apple Power Macintosh G5", "cores": 2},
        {"name": "Apple Mac Pro G5", "cores": 2}, {"name": "Apple iMac G5", "cores": 1},
        {"name": "Apple MacBook Air G5", "cores": 1}, {"name": "Apple PowerBook G5", "cores": 1},
        {"name": "Apple Xserve G5", "cores": 2}, {"name": "IBM Cell Blade", "cores": 2},
    ]},
    {"arch": "SPARC", "family": "SPARC", "color": "#8B0000", "devices": [
        {"name": "Sun Microsystems Sun-4", "cores": 1}, {"name": "Sun SPARCstation 1", "cores": 1},
        {"name": "Sun SPARCstation 2", "cores": 1}, {"name": "Sun Ultra 1", "cores": 1},
        {"name": "Sun SPARCstation 10", "cores": 2}, {"name": "Sun Ultra 5", "cores": 2},
        {"name": "Sun Blade 100", "cores": 2}, {"name": "Sun Fire V210", "cores": 2},
        {"name": "Sun Fire V440", "cores": 4}, {"name": "Sun SPARC T3", "cores": 16},
        {"name": "Sun Oracle SPARC T4", "cores": 8}, {"name": "Oracle SPARC T5-8", "cores": 16},
        {"name": "Oracle SPARC M5-8", "cores": 32},
    ]},
    {"arch": "MIPS", "family": "MIPS", "color": "#00A86B", "devices": [
        {"name": "SGI Indigo", "cores": 1}, {"name": "SGI Octane", "cores": 2},
        {"name": "DEC AlphaStation 200", "cores": 1},
    ]},
    {"arch": "ARM", "family": "ARM", "color": "#556B2F", "devices": [
        {"name": "Debian ARM Cluster", "cores": 4}, {"name": "Apple iPad A4", "cores": 1},
        {"name": "Apple iPhone 4 A4", "cores": 1}, {"name": "Cavium ThunderX2", "cores": 32},
        {"name": "Apple iPhone 5 A6", "cores": 2}, {"name": "Ampere eMAG", "cores": 32},
        {"name": "Marvell Armada", "cores": 4}, {"name": "Apple iPad Air A7", "cores": 2},
        {"name": "Qualcomm Centriq", "cores": 48}, {"name": "AWS Graviton2", "cores": 64},
        {"name": "AWS Graviton3", "cores": 64}, {"name": "Azure Dpsv5", "cores": 64},
        {"name": "Google Tau T2A", "cores": 48}, {"name": "AWS Graviton3E", "cores": 64},
        {"name": "Azure Cobalt 100", "cores": 64}, {"name": "Oracle Ampere A1", "cores": 32},
    ]},
    {"arch": "POWER8", "family": "IBM", "color": "#00008B", "devices": [
        {"name": "IBM POWER6 570", "cores": 4}, {"name": "IBM POWER7 795", "cores": 8},
        {"name": "IBM PowerLinux 7R2", "cores": 4}, {"name": "IBM S812L", "cores": 4},
        {"name": "IBM OpenPower 720", "cores": 4}, {"name": "Raptor Computing Talos II", "cores": 8},
        {"name": "IBM POWER8 S822L", "cores": 8},
    ]},
    {"arch": "POWER9", "family": "IBM", "color": "#191970", "devices": [
        {"name": "IBM AC922", "cores": 8}, {"name": "Raptor Blackbird", "cores": 4},
        {"name": "IBM S922LC", "cores": 4}, {"name": "IBM IC922", "cores": 8},
        {"name": "IBM POWER9 9009", "cores": 8},
    ]},
    {"arch": "Apple Silicon", "family": "Apple", "color": "#C0C0C0", "devices": [
        {"name": "Apple MacBook Pro M1", "cores": 8}, {"name": "Apple iMac M1", "cores": 8},
        {"name": "Apple Mac Mini M1", "cores": 8}, {"name": "Apple MacBook Air M1", "cores": 8},
        {"name": "Apple Mac Studio M1 Ultra", "cores": 20}, {"name": "Apple Mac Pro M1", "cores": 20},
        {"name": "Apple MacBook Pro M2", "cores": 10}, {"name": "Apple Mac Mini M2", "cores": 10},
        {"name": "Apple iMac M2", "cores": 10}, {"name": "Apple MacBook Pro M2 Pro", "cores": 12},
        {"name": "Apple Mac Studio M2 Max", "cores": 24}, {"name": "Apple Mac Pro M2 Ultra", "cores": 48},
        {"name": "Apple MacBook Pro M3", "cores": 12}, {"name": "Apple Mac Mini M3", "cores": 12},
    ]},
    {"arch": "Modern x86", "family": "x86", "color": "#D3D3D3", "devices": [
        {"name": "Intel Core 2 Duo E6600", "cores": 2}, {"name": "AMD Phenom 9850", "cores": 4},
        {"name": "Intel Xeon X5460", "cores": 4}, {"name": "AMD Ryzen 5 1600", "cores": 6},
        {"name": "Intel Core i7-8700K", "cores": 6}, {"name": "AMD Threadripper 2970WX", "cores": 24},
        {"name": "Intel Xeon W-2295", "cores": 18}, {"name": "AMD Ryzen 9 5950X", "cores": 16},
        {"name": "Intel Core i9-12900K", "cores": 16}, {"name": "AMD EPYC 7763", "cores": 64},
        {"name": "Intel Xeon w9-3595X", "cores": 56}, {"name": "AMD Ryzen 9 7950X3D", "cores": 16},
        {"name": "Intel Core Ultra 9 285K", "cores": 24}, {"name": "AMD Ryzen 9 9950X", "cores": 16},
        {"name": "Intel Xeon 6980P", "cores": 128}, {"name": "AMD EPYC 9654", "cores": 96},
        {"name": "Intel Xeon 6 6788P", "cores": 128}, {"name": "AMD EPYC 9754", "cores": 128},
    ]},
]

# Epoch ranges for each architecture (when they first appeared)
arch_epochs = {
    "68K": (0, 12),
    "G3": (7, 25),
    "G4": (13, 30),
    "G5": (13, 35),
    "SPARC": (3, 35),
    "MIPS": (5, 20),
    "ARM": (24, 80),
    "POWER8": (16, 55),
    "POWER9": (25, 65),
    "Apple Silicon": (50, 119),
    "Modern x86": (10, 119),
}

# How many attestations per epoch per arch (roughly proportional to miner count)
arch_density = {
    "68K": 0.05, "G3": 0.08, "G4": 0.1, "G5": 0.12,
    "SPARC": 0.1, "MIPS": 0.05, "ARM": 0.2, "POWER8": 0.08,
    "POWER9": 0.1, "Apple Silicon": 0.25, "Modern x86": 0.3,
}

random.seed(42)

def gen_miner_id():
    chars = "0123456789ABCDEF"
    return "0x" + "".join(random.choices(chars, k=4)) + "..." + "".join(random.choices(chars, k=4))

def gen_fingerprint_quality():
    return round(random.uniform(0.38, 0.99), 2)

def gen_rtc(arch, cores):
    base = {"68K": 0.1, "G3": 0.22, "G4": 0.32, "G5": 0.37,
            "SPARC": 0.3, "MIPS": 0.2, "ARM": 0.35, "POWER8": 0.45,
            "POWER9": 0.58, "Apple Silicon": 0.6, "Modern x86": 0.5}
    mult = base.get(arch, 0.3) * (cores / 2) * random.uniform(0.8, 1.2)
    return round(mult, 2)

attestations = []
total_epochs = 120

for epoch in range(total_epochs):
    for arch_info in arch_templates:
        arch = arch_info["arch"]
        min_ep, max_ep = arch_epochs.get(arch, (0, 119))
        if epoch < min_ep or epoch > max_ep:
            continue
        density = arch_density.get(arch, 0.1)
        count = max(1, int(density * 10))
        for _ in range(count):
            dev = random.choice(arch_info["devices"])
            attestations.append({
                "miner": gen_miner_id(),
                "device": dev["name"],
                "arch": arch,
                "family": arch_info["family"],
                "epoch": epoch,
                "rtc_earned": gen_rtc(arch, dev["cores"]),
                "fingerprint_quality": gen_fingerprint_quality(),
                "cpu_cores": dev["cores"],
                "color": arch_info["color"],
            })

random.shuffle(attestations)

output = {
    "metadata": {
        "chain": "RustChain",
        "total_epochs": total_epochs,
        "genesis_epoch": 0,
        "latest_epoch": total_epochs - 1,
        "total_attestations": len(attestations),
        "miner_count": len(set(a["miner"] for a in attestations))
    },
    "attestations": attestations
}

with open("attestations.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"Generated {len(attestations)} attestations, {output['metadata']['miner_count']} unique miners")
