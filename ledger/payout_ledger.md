# Bounty Payout Ledger

This ledger tracks all bounty payouts for transparency and accountability. All amounts are in USD unless otherwise specified.

## Payout Status Legend
- 🟡 **Queued**: Payment approved, awaiting processing
- 🔄 **Pending**: Payment initiated, awaiting confirmation
- ✅ **Confirmed**: Payment completed and verified
- ❌ **Failed**: Payment failed, requires retry
- ⏸️ **Hold**: Payment temporarily suspended

## Current Payouts

| Date | Bounty ID | Contributor | Task | Amount | Method | Status | Tx Hash/Reference | Notes |
|------|-----------|-------------|------|--------|---------|---------|-------------------|--------|
| 2024-01-15 | BNT-001 | alice_dev | Frontend UI Fix | $150 | ETH | 🔄 | 0x1a2b3c... | Processing |
| 2024-01-14 | BNT-002 | bob_coder | API Integration | $300 | USDC | ✅ | 0x4d5e6f... | Completed |
| 2024-01-13 | BNT-003 | carol_test | Bug Report | $75 | PayPal | ✅ | PP-789xyz | Completed |

## Payout Summary

### By Status
- **Queued**: 0 payments, $0
- **Pending**: 1 payment, $150
- **Confirmed**: 2 payments, $375
- **Failed**: 0 payments, $0
- **Hold**: 0 payments, $0

### By Payment Method
- **ETH**: $150
- **USDC**: $300
- **PayPal**: $75
- **Bank Transfer**: $0

### Monthly Totals
- **January 2024**: $525 (3 payments)
- **December 2023**: $0 (0 payments)

## Payment Processing Notes

### Pending Actions Required
- [ ] Confirm ETH payment for BNT-001 (alice_dev)
- [ ] Process weekly batch payments on Fridays
- [ ] Update contributor payment preferences

### Recent Issues
- None reported

### Payment Schedule
- **Weekly Processing**: Fridays at 2 PM UTC
- **Emergency Payments**: Within 24 hours
- **Minimum Payout**: $25 USD equivalent

---

*Last Updated: 2024-01-15 14:30 UTC*  
*Ledger Maintained By: Finance Team*