#!/usr/bin/env python3
"""Quick verification of RustChain epoch settlement formal properties."""
import sqlite3, tempfile, os, time, sys

# ─── Exact copy of the settlement function from node/rip_200_round_robin_1cpu1vote.py ───

ANTIQUITY_MULTIPLIERS = {
    "386": 3.0, "i386": 3.0, "486": 2.9, "68000": 3.0, "68030": 2.5, "68040": 2.4,
    "g4": 2.5, "powerpc g4": 2.5, "g5": 2.0, "powerpc g5": 2.0,
    "arm2": 4.0, "arm3": 3.8, "arm7tdmi": 3.0, "strongarm": 2.8,
    "pentium": 2.5, "pentium_pro": 2.3, "pentium_iii": 2.0,
    "vax": 3.5, "transputer": 3.5, "clipper": 3.5,
    "core2": 1.3, "kaby_lake": 1.0, "modern_intel": 0.8,
    "zen": 1.1, "zen2": 1.05, "zen3": 1.0,
    "m1": 1.2, "m2": 1.15, "m4": 1.05,
    "riscv": 1.4, "default": 0.8, "unknown": 0.8,
    "modern": 0.8, "aarch64": 0.0005, "arm": 0.0005,
    "nes_6502": 2.8, "snes_65c816": 2.7, "ps1_mips": 2.8,
    "dreamcast_sh4": 2.3, "ps2_ee": 2.2,
}

GENESIS_TIMESTAMP = 1764706927
BLOCK_TIME = 600
ATTESTATION_TTL = 86400
DECAY_RATE_PER_YEAR = 0.15

def get_chain_age_years(current_slot):
    return (current_slot * BLOCK_TIME) / (365.25 * 24 * 3600)

def get_time_aged_multiplier(device_arch, chain_age_years):
    base = ANTIQUITY_MULTIPLIERS.get(device_arch.lower(), 1.0)
    if base <= 1.0: return 1.0
    vintage_bonus = base - 1.0
    aged_bonus = max(0, vintage_bonus * (1 - DECAY_RATE_PER_YEAR * chain_age_years))
    return 1.0 + aged_bonus

def create_test_db(miners, ts_ok=None, warthog_bonuses=None):
    """Create a temp DB with miners. ts_ok defaults to genesis + 1 slot."""
    if ts_ok is None:
        ts_ok = GENESIS_TIMESTAMP + BLOCK_TIME  # Within epoch 0 window
    fd, db_path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS miner_attest_recent (
        miner TEXT, device_arch TEXT, ts_ok INTEGER,
        fingerprint_passed INTEGER DEFAULT 1, warthog_bonus REAL DEFAULT NULL
    )""")
    for mid, arch, fp in miners:
        wart = warthog_bonuses.get(mid) if warthog_bonuses else None
        c.execute("INSERT INTO miner_attest_recent VALUES (?,?,?,?,?)", (mid, arch, ts_ok, fp, wart))
    conn.commit()
    conn.close()
    return db_path

def calculate_epoch_rewards_time_aged(db_path, epoch, total_reward_urtc, current_slot):
    """Exact copy from rip_200_round_robin_1cpu1vote.py"""
    chain_age_years = get_chain_age_years(current_slot)
    epoch_start_slot = epoch * 144
    epoch_end_slot = epoch_start_slot + 143
    epoch_start_ts = GENESIS_TIMESTAMP + (epoch_start_slot * BLOCK_TIME)
    epoch_end_ts = GENESIS_TIMESTAMP + (epoch_end_slot * BLOCK_TIME)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT miner, device_arch, COALESCE(fingerprint_passed, 1) as fp
            FROM miner_attest_recent
            WHERE ts_ok >= ? AND ts_ok <= ?
        """, (epoch_start_ts - ATTESTATION_TTL, epoch_end_ts))
        epoch_miners = cursor.fetchall()

    if not epoch_miners:
        return {}

    weighted_miners = []
    total_weight = 0.0

    for row in epoch_miners:
        miner_id, device_arch = row[0], row[1]
        fingerprint_ok = row[2] if len(row) > 2 else 1
        
        if fingerprint_ok == 0:
            weight = 0.0
        else:
            weight = get_time_aged_multiplier(device_arch, chain_age_years)

        # NOTE: cursor is CLOSED here (left the 'with' block above)
        # This means the warthog bonus lookup will FAIL with UnboundLocalError
        # or use a stale/closed cursor — this is a BUG in the original code
        if weight > 0 and fingerprint_ok == 1:
            try:
                wart_row = cursor.execute(
                    "SELECT warthog_bonus FROM miner_attest_recent WHERE miner=?",
                    (miner_id,)
                ).fetchone()
                if wart_row and wart_row[0] and wart_row[0] > 1.0:
                    weight *= wart_row[0]
            except Exception:
                pass  # BUG: silently swallows the closed-connection error

        weighted_miners.append((miner_id, weight))
        total_weight += weight

    rewards = {}
    remaining = total_reward_urtc

    for i, (miner_id, weight) in enumerate(weighted_miners):
        if i == len(weighted_miners) - 1:
            share = remaining
        else:
            share = int((weight / total_weight) * total_reward_urtc)
            remaining -= share
        rewards[miner_id] = share

    return rewards

# ═══════════════════════════════════════════════════════════════
# TESTS
# ═══════════════════════════════════════════════════════════════

passed = 0
failed = 0
bugs_found = []

def check(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}: {detail}")
        failed += 1

print("=" * 60)
print("RustChain RIP-200 Epoch Settlement Formal Verification")
print("=" * 60)

# ─── Property 1: Conservation ───
print("\nPROPERTY 1: CONSERVATION (total distributed == total)")
db = create_test_db([("m1","g4",1), ("m2","modern",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("2 miners", sum(r.values()) == 150_000_000, f"got {sum(r.values())}")
os.unlink(db)

db = create_test_db([("a","g4",1),("b","pentium",1),("c","zen3",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("3 miners", sum(r.values()) == 150_000_000)
os.unlink(db)

db = create_test_db([("a","g4",1),("b","arm2",1),("c","modern",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 100, 0)
check("small reward (100 uRTC)", sum(r.values()) == 100)
os.unlink(db)

db = create_test_db([("a","g4",1),("b","pentium",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 0, 0)
check("zero reward", all(v == 0 for v in r.values()))
os.unlink(db)

db = create_test_db([("a","g4",1),("b","pentium_iii",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 2**50, 0)
check("large reward (2^50)", sum(r.values()) == 2**50)
os.unlink(db)

# ─── Property 2: Non-negative ───
print("\nPROPERTY 2: NON-NEGATIVE (no negative rewards)")
db = create_test_db([("a","g4",1),("b","arm2",1),("c","modern",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("all positive", all(v >= 0 for v in r.values()))
os.unlink(db)

db = create_test_db([("m_good","g4",1),("m_fail","arm2",0)])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("FP fail gets 0", r.get("m_fail", 0) == 0, f"got {r.get('m_fail')}")
os.unlink(db)

# BUG: All-zero weights
db = create_test_db([("m1","g4",0),("m2","arm2",0)])
try:
    r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
    bugs_found.append("BUG: All-zero-weights should return {} but didn't crash")
    print("  ⚠️ BUG: No ZeroDivisionError (unexpected)")
except ZeroDivisionError:
    bugs_found.append("BUG#1: ZeroDivisionError when all miners have fingerprint_passed=0")
    print("  🐛 BUG CONFIRMED: ZeroDivisionError on all-zero weights")
os.unlink(db)

# ─── Property 3: Proportionality ───
print("\nPROPERTY 3: PROPORTIONALITY (rewards proportional to weights)")
db = create_test_db([("m_g4","g4",1),("m_modern","modern",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
if r.get("m_modern", 0) > 0:
    ratio = r["m_g4"] / r["m_modern"]
    check("G4 2.5x vs modern 1.0x", abs(ratio - 2.5) < 0.001, f"ratio={ratio:.4f}")
else:
    check("G4 2.5x vs modern 1.0x", False, "modern got 0")
os.unlink(db)

db = create_test_db([("m1","g4",1),("m2","g4",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("equal weights equal rewards", r["m1"] == r["m2"])
os.unlink(db)

db = create_test_db([("m1","pentium",1),("m2","pentium",1),("m3","pentium",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("3 equal = ~1/3 each", max(r.values()) - min(r.values()) <= 1)
os.unlink(db)

db = create_test_db([("m_arm2","arm2",1),("m_modern","modern",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
if r.get("m_modern", 0) > 0:
    ratio = r["m_arm2"] / r["m_modern"]
    check("ARM2 4.0x vs modern 1.0x", abs(ratio - 4.0) < 0.001, f"ratio={ratio:.4f}")
else:
    check("ARM2 4.0x vs modern", False, "modern got 0")
os.unlink(db)

# ─── Property 4: Idempotency ───
print("\nPROPERTY 4: IDEMPOTENCY (deterministic)")
db = create_test_db([("a","g4",1),("b","pentium",1),("c","arm2",1)])
r1 = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
r2 = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("same inputs = same outputs", r1 == r2)
os.unlink(db)

# ─── Property 5: Empty set ───
print("\nPROPERTY 5: EMPTY SET")
db = create_test_db([])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("no miners = empty dict", r == {})
os.unlink(db)

# ─── Property 6: Single miner ───
print("\nPROPERTY 6: SINGLE MINER (gets full reward)")
db = create_test_db([("solo","g4",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("single G4 gets all", r == {"solo": 150_000_000})
os.unlink(db)

for arch in ["arm2", "pentium", "modern", "vax", "riscv"]:
    db = create_test_db([("solo", arch, 1)])
    r = calculate_epoch_rewards_time_aged(db, 0, 99_999_999, 0)
    check(f"single {arch} gets all", r.get("solo") == 99_999_999, f"got {r.get('solo')}")
    os.unlink(db)

# ─── Property 7: Precision ───
print("\nPROPERTY 7: PRECISION (scale testing)")
arches = list(ANTIQUITY_MULTIPLIERS.keys())
miners = [(f"m{i:04d}", arches[i % len(arches)], 1) for i in range(100)]
db = create_test_db(miners)
t0 = time.time()
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
t1 = time.time()
check("100 miners conserve", sum(r.values()) == 150_000_000)
print(f"    ({t1-t0:.3f}s)")
os.unlink(db)

miners = [(f"m{i:04d}", arches[i % len(arches)], 1) for i in range(1000)]
db = create_test_db(miners)
t0 = time.time()
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
t1 = time.time()
check("1000 miners conserve", sum(r.values()) == 150_000_000)
print(f"    ({t1-t0:.3f}s)")
os.unlink(db)

# ─── Property 8: Time decay ───
print("\nPROPERTY 8: TIME DECAY")
for slot in [0, 1000, 10000, 100000]:
    mult = get_time_aged_multiplier("g4", get_chain_age_years(slot))
    check(f"G4 at slot {slot}: {mult:.3f}", mult <= 2.5 and mult >= 1.0)

mult = get_time_aged_multiplier("modern", 0.0)
check("modern always 1.0x", mult == 1.0)

mult = get_time_aged_multiplier("modern", 20.0)
check("modern at 20yr still 1.0x", mult == 1.0)

# Monotonicity
prev = None
monotonic = True
for slot in range(0, 100000, 100):
    m = get_time_aged_multiplier("g4", get_chain_age_years(slot))
    if prev is not None and m > prev + 1e-10:
        monotonic = False
    prev = m
check("decay is monotonically decreasing", monotonic)

# ─── Property 9: Dust handling ───
print("\nPROPERTY 9: DUST HANDLING")
db = create_test_db([("m_aarch64","aarch64",1),("m_g4","g4",1)])
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("aarch64 gets non-zero", r.get("m_aarch64", 0) > 0, f"got {r.get('m_aarch64')}")
check("G4 > aarch64", r.get("m_g4", 0) > r.get("m_aarch64", 0))
os.unlink(db)

# ─── Property 10: Large multiplier sums ───
print("\nPROPERTY 10: LARGE MULTIPLIER SUMS")
miners = [(f"vintage_{i}", "arm2", 1) for i in range(100)]
db = create_test_db(miners)
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
check("100x ARM2 (400x total weight) conserves", sum(r.values()) == 150_000_000)
os.unlink(db)

db = create_test_db([(f"m_{i}", "vax", 1) for i in range(50)])
r = calculate_epoch_rewards_time_aged(db, 0, 10**18, 0)
check("extreme reward 10^18 conserves", sum(r.values()) == 10**18)
os.unlink(db)

# ─── Warthog bonus tests ───
print("\nWARTHOG BONUS")
# NOTE: Warthog bonus is a BUG in the original code (cursor used outside 'with' block)
# It silently catches the exception and skips the bonus
db = create_test_db([("m1","g4",1),("m2","g4",1)], warthog_bonuses={"m2": 1.15})
r = calculate_epoch_rewards_time_aged(db, 0, 150_000_000, 0)
if r["m1"] == r["m2"]:
    bugs_found.append("BUG#2: Warthog bonus never applied (cursor closed before use)")
    print("  🐛 BUG CONFIRMED: Warthog bonus NOT applied (cursor used after connection closed)")
else:
    check("warthog 1.15x scales correctly", abs(r["m2"]/r["m1"] - 1.15) < 0.001)
os.unlink(db)

# ─── Summary ───
print("\n" + "=" * 60)
print(f"RESULTS: {passed} passed, {failed} failed")
if bugs_found:
    print(f"\n🐛 BUGS FOUND ({len(bugs_found)}):")
    for b in bugs_found:
        print(f"   • {b}")
print("=" * 60)
