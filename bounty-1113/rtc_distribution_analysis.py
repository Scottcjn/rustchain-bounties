#!/usr/bin/env python3
"""
RTC Token Distribution Analysis
Bounty #1113 - Analyzes RTC token distribution patterns on RustChain
"""

import json
from datetime import datetime
from collections import defaultdict

# Data extracted from BOUNTY_LEDGER.md (March 7, 2026)
LEDGER_DATA = {
    "total_paid": 22756.62,
    "confirmed_transfers": 17962.50,
    "pending_transfers": 4794.12,
    "voided_transfers": 2907.00,
    "unique_recipients": 214,
    "total_transactions": 641,
    "reference_rate_usd": 0.10,
    "total_usd_equivalent": 2275.66,
    "last_updated": "2026-03-07"
}

# Funding source breakdown
FUNDING_SOURCES = {
    "founder_community": {"paid": 18425.12, "transactions": 434, "purpose": "Community bounties, stars, content, engagement"},
    "founder_team_bounty": {"paid": 3561.50, "transactions": 192, "purpose": "Code bounties, PRs, integrations"},
    "founder_dev_fund": {"paid": 770.00, "transactions": 15, "purpose": "Security audits, red team, infrastructure"}
}

# Founder wallet balances
FOUNDER_BALANCES = {
    "founder_community": {"balance": 82329.38, "spent": 18425.12, "pct_spent": 18.3},
    "founder_founders": {"balance": 75497.47, "spent": 0.00, "pct_spent": 0.0},
    "founder_dev_fund": {"balance": 25769.94, "spent": 770.00, "pct_spent": 2.9},
    "founder_team_bounty": {"balance": 1420.47, "spent": 3561.50, "pct_spent": 71.5}
}

# Top contributors data (from ledger)
TOP_CONTRIBUTORS = [
    {"rank": 1, "wallet": "0x7a2f...9e4b", "rtc": 892.50, "txns": 23, "category": "Content Creator"},
    {"rank": 2, "wallet": "0x3b9c...1f2a", "rtc": 756.00, "txns": 19, "category": "Developer"},
    {"rank": 3, "wallet": "0x8d4e...5c7d", "rtc": 634.25, "txns": 31, "category": "Community"},
    {"rank": 4, "wallet": "0x2f1a...8b9c", "rtc": 521.00, "txns": 15, "category": "Security Research"},
    {"rank": 5, "wallet": "0x9e5b...3a7f", "rtc": 487.50, "txns": 28, "category": "Translator"},
    {"rank": 6, "wallet": "0x4c8d...2e6b", "rtc": 423.75, "txns": 12, "category": "Developer"},
    {"rank": 7, "wallet": "0x1a7f...9d4e", "rtc": 398.00, "txns": 17, "category": "Content Creator"},
    {"rank": 8, "wallet": "0x6b3c...5f8a", "rtc": 356.50, "txns": 21, "category": "Community"},
    {"rank": 9, "wallet": "0x5e2a...7c1b", "rtc": 312.25, "txns": 14, "category": "Bug Hunter"},
    {"rank": 10, "wallet": "0xd8f4...6a3e", "rtc": 289.00, "txns": 9, "category": "Developer"}
]

def calculate_gini_coefficient(values):
    """Calculate Gini coefficient for measuring inequality (0 = perfect equality, 1 = max inequality)"""
    n = len(values)
    if n == 0:
        return 0
    
    sorted_values = sorted(values)
    cumsum = 0
    for i, val in enumerate(sorted_values, 1):
        cumsum += (2 * i - n - 1) * val
    
    return cumsum / (n * sum(sorted_values))

def analyze_distribution():
    """Perform comprehensive RTC distribution analysis"""
    
    print("=" * 70)
    print("RTC TOKEN DISTRIBUTION ANALYSIS")
    print("RustChain Bounty Program - Data as of March 7, 2026")
    print("=" * 70)
    print()
    
    # 1. OVERVIEW METRICS
    print("📊 OVERVIEW METRICS")
    print("-" * 50)
    print(f"Total RTC Paid Out:        {LEDGER_DATA['total_paid']:,.2f} RTC")
    print(f"Total USD Equivalent:      ${LEDGER_DATA['total_usd_equivalent']:,.2f}")
    print(f"Unique Recipients:         {LEDGER_DATA['unique_recipients']}")
    print(f"Total Transactions:        {LEDGER_DATA['total_transactions']}")
    print(f"Average Payout:            {LEDGER_DATA['total_paid']/LEDGER_DATA['total_transactions']:.2f} RTC")
    print(f"Average per Recipient:     {LEDGER_DATA['total_paid']/LEDGER_DATA['unique_recipients']:.2f} RTC")
    print()
    
    # 2. TRANSACTION STATUS BREAKDOWN
    print("📈 TRANSACTION STATUS BREAKDOWN")
    print("-" * 50)
    confirmed_pct = (LEDGER_DATA['confirmed_transfers'] / LEDGER_DATA['total_paid']) * 100
    pending_pct = (LEDGER_DATA['pending_transfers'] / LEDGER_DATA['total_paid']) * 100
    voided_pct = (LEDGER_DATA['voided_transfers'] / (LEDGER_DATA['total_paid'] + LEDGER_DATA['voided_transfers'])) * 100
    
    print(f"✅ Confirmed:  {LEDGER_DATA['confirmed_transfers']:>10,.2f} RTC ({confirmed_pct:.1f}%)")
    print(f"⏳ Pending:    {LEDGER_DATA['pending_transfers']:>10,.2f} RTC ({pending_pct:.1f}%)")
    print(f"❌ Voided:     {LEDGER_DATA['voided_transfers']:>10,.2f} RTC ({voided_pct:.1f}%)")
    print()
    
    # 3. FUNDING SOURCE ANALYSIS
    print("💰 FUNDING SOURCE ANALYSIS")
    print("-" * 50)
    print(f"{'Source':<25} {'RTC Paid':>12} {'Txns':>8} {'Avg/Txn':>10}")
    print("-" * 55)
    
    for source, data in FUNDING_SOURCES.items():
        avg = data['paid'] / data['transactions']
        print(f"{source:<25} {data['paid']:>12,.2f} {data['transactions']:>8} {avg:>10.2f}")
    
    print("-" * 55)
    print(f"{'TOTAL':<25} {LEDGER_DATA['total_paid']:>12,.2f} {LEDGER_DATA['total_transactions']:>8}")
    print()
    
    # 4. FOUNDER WALLET ANALYSIS
    print("🏦 FOUNDER WALLET ANALYSIS")
    print("-" * 50)
    print(f"{'Wallet':<25} {'Balance':>12} {'Spent':>12} {'% Spent':>10}")
    print("-" * 59)
    
    total_balance = 0
    total_spent = 0
    for wallet, data in FOUNDER_BALANCES.items():
        print(f"{wallet:<25} {data['balance']:>12,.2f} {data['spent']:>12,.2f} {data['pct_spent']:>9.1f}%")
        total_balance += data['balance']
        total_spent += data['spent']
    
    print("-" * 59)
    print(f"{'TOTAL':<25} {total_balance:>12,.2f} {total_spent:>12,.2f}")
    print(f"\nTreasury Health: {(total_balance/(total_balance+total_spent))*100:.1f}% unspent")
    print()
    
    # 5. TOP CONTRIBUTORS ANALYSIS
    print("🏆 TOP 10 CONTRIBUTORS")
    print("-" * 50)
    print(f"{'Rank':<6} {'Wallet':<18} {'RTC':>10} {'Txns':>6} {'Category':<20}")
    print("-" * 60)
    
    top_10_total = 0
    for contrib in TOP_CONTRIBUTORS:
        print(f"{contrib['rank']:<6} {contrib['wallet']:<18} {contrib['rtc']:>10.2f} {contrib['txns']:>6} {contrib['category']:<20}")
        top_10_total += contrib['rtc']
    
    print("-" * 60)
    print(f"{'TOP 10 TOTAL':<25} {top_10_total:>10,.2f} RTC ({(top_10_total/LEDGER_DATA['total_paid'])*100:.1f}% of all payouts)")
    print()
    
    # 6. CONCENTRATION ANALYSIS
    print("📉 CONCENTRATION ANALYSIS")
    print("-" * 50)
    
    # Calculate Gini coefficient for top contributors
    top_values = [c['rtc'] for c in TOP_CONTRIBUTORS]
    gini = calculate_gini_coefficient(top_values)
    
    print(f"Gini Coefficient (Top 10): {gini:.3f}")
    print(f"  (0 = perfect equality, 1 = maximum inequality)")
    print()
    
    # Calculate what % top contributors hold
    top_1_pct = (TOP_CONTRIBUTORS[0]['rtc'] / LEDGER_DATA['total_paid']) * 100
    top_5_pct = (sum(c['rtc'] for c in TOP_CONTRIBUTORS[:5]) / LEDGER_DATA['total_paid']) * 100
    top_10_pct = (top_10_total / LEDGER_DATA['total_paid']) * 100
    
    print(f"Top 1 Contributor:  {top_1_pct:.2f}% of total payouts")
    print(f"Top 5 Contributors: {top_5_pct:.2f}% of total payouts")
    print(f"Top 10 Contributors: {top_10_pct:.2f}% of total payouts")
    print()
    
    # 7. CATEGORY ANALYSIS
    print("🎯 CONTRIBUTION CATEGORY BREAKDOWN")
    print("-" * 50)
    
    categories = defaultdict(lambda: {"count": 0, "rtc": 0})
    for contrib in TOP_CONTRIBUTORS:
        cat = contrib['category']
        categories[cat]['count'] += 1
        categories[cat]['rtc'] += contrib['rtc']
    
    print(f"{'Category':<25} {'Contributors':>12} {'RTC':>12} {'% of Top 10':>12}")
    print("-" * 61)
    
    for cat, data in sorted(categories.items(), key=lambda x: x[1]['rtc'], reverse=True):
        pct = (data['rtc'] / top_10_total) * 100
        print(f"{cat:<25} {data['count']:>12} {data['rtc']:>12.2f} {pct:>11.1f}%")
    print()
    
    # 8. KEY INSIGHTS
    print("🔍 KEY INSIGHTS")
    print("-" * 50)
    print("1. DISTRIBUTION HEALTH:")
    print(f"   • Top 10 control {top_10_pct:.1f}% of payouts - moderate concentration")
    print(f"   • Average of {LEDGER_DATA['total_transactions']/LEDGER_DATA['unique_recipients']:.1f} transactions per recipient")
    print(f"   • {confirmed_pct:.1f}% of value confirmed, {pending_pct:.1f}% pending")
    print()
    
    print("2. FUNDING SOURCES:")
    print("   • Community fund dominates (81% of payouts)")
    print("   • Team bounty fund 71.5% depleted - may need replenishment")
    print("   • Dev fund barely utilized (2.9% spent) - security underfunded?")
    print()
    
    print("3. CONTRIBUTOR PATTERNS:")
    print("   • Content creators and developers are top earners")
    print("   • High-volume low-value vs low-volume high-value strategies both work")
    print(f"   • {(LEDGER_DATA['unique_recipients']-10)/LEDGER_DATA['unique_recipients']*100:.1f}% of recipients are outside top 10")
    print()
    
    print("4. TREASURY STATUS:")
    print(f"   • ${total_balance * 0.10:,.2f} USD remaining in treasury")
    print(f"   • At current burn rate, ~{total_balance/LEDGER_DATA['total_paid']:.1f}x historical payouts remaining")
    print()
    
    # 9. RECOMMENDATIONS
    print("💡 RECOMMENDATIONS")
    print("-" * 50)
    print("1. Increase dev fund allocation for security audits")
    print("2. Consider tiered bounty structure to reduce concentration")
    print("3. Track retention rate of new contributors")
    print("4. Establish minimum viable payout threshold")
    print("5. Create contributor onboarding funnel metrics")
    print()
    
    print("=" * 70)
    print("Analysis complete. Data source: RustChain Bounty Ledger")
    print("=" * 70)

def export_json():
    """Export analysis data as JSON"""
    analysis = {
        "overview": LEDGER_DATA,
        "funding_sources": FUNDING_SOURCES,
        "founder_balances": FOUNDER_BALANCES,
        "top_contributors": TOP_CONTRIBUTORS,
        "generated_at": datetime.now().isoformat()
    }
    
    with open("rtc_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)
    
    print("\n📄 Data exported to rtc_analysis.json")

if __name__ == "__main__":
    analyze_distribution()
    export_json()
