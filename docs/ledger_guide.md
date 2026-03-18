# Bounty Payout Ledger Guide

## Overview

The bounty payout ledger tracks all bounty payments from initiation through completion. This document explains the ledger system, status definitions, and update procedures.

## Ledger Structure

The ledger contains the following fields for each bounty payout:

- **Bounty ID**: Unique identifier for the bounty
- **Recipient**: GitHub username or wallet address
- **Amount**: Payment amount in tokens/currency
- **Status**: Current payment status (see below)
- **Created Date**: When the payout was initiated
- **Updated Date**: Last status update
- **Transaction Hash**: Blockchain transaction identifier (when applicable)
- **Notes**: Additional information or error details

## Status Definitions

### QUEUED
- **Description**: Payment has been approved and added to the processing queue
- **Next Steps**: Awaiting batch processing or manual review
- **Duration**: Typically 1-3 business days
- **Actions Required**: None from recipient

### PENDING
- **Description**: Payment is being processed by the payment system
- **Next Steps**: Transaction submitted to blockchain or payment processor
- **Duration**: Minutes to hours depending on network conditions
- **Actions Required**: None from recipient

### CONFIRMED
- **Description**: Payment has been successfully completed and verified
- **Next Steps**: No further action needed
- **Duration**: Final status
- **Actions Required**: None

### FAILED
- **Description**: Payment could not be completed due to an error
- **Next Steps**: Manual intervention required
- **Common Causes**:
  - Invalid recipient address
  - Insufficient funds
  - Network issues
  - KYC/compliance issues
- **Actions Required**: Contact support team

### CANCELLED
- **Description**: Payment was cancelled before processing
- **Next Steps**: May be requeued if cancellation reason is resolved
- **Common Causes**:
  - Duplicate payment detected
  - Bounty requirements not met
  - Administrative decision
- **Actions Required**: Review bounty completion requirements

## Update Procedures

### Automated Updates
- Status changes are automatically recorded when payment processors report updates
- Transaction hashes are populated once blockchain transactions are confirmed
- Timestamps are updated with each status change

### Manual Updates
For manual status updates:

1. **Access Required**: Admin or finance team permissions
2. **Update Process**:
   - Locate bounty entry in ledger
   - Update status field with appropriate value
   - Add timestamp to updated date
   - Include notes explaining the change
   - Save changes and notify relevant parties

### Batch Updates
For processing multiple payments:

1. **Queue Review**: Verify all QUEUED entries are valid
2. **Batch Processing**: Submit payments to processor
3. **Status Update**: Mark as PENDING during processing
4. **Confirmation**: Update to CONFIRMED once verified
5. **Error Handling**: Mark FAILED entries and add error notes

## Monitoring and Reporting

### Daily Checks
- Review PENDING entries older than 24 hours
- Investigate FAILED transactions
- Verify CONFIRMED payments match processor records

### Weekly Reports
- Summary of payment volumes by status
- Failed payment analysis
- Processing time metrics
- Outstanding issues requiring attention

### Monthly Reconciliation
- Match ledger entries with financial records
- Verify all CONFIRMED payments were actually disbursed
- Update any discrepancies found

## Troubleshooting

### Common Issues

**Payment Stuck in PENDING**:
- Check blockchain network status
- Verify processor system status
- Review transaction details for errors

**Incorrect Recipient Information**:
- Update recipient details
- Cancel and requeue payment
- Verify KYC/compliance requirements

**Duplicate Payments**:
- Check for existing entries
- Cancel duplicates before processing
- Implement prevention measures

### Support Contacts
- Technical Issues: dev-team@company.com
- Payment Questions: finance@company.com
- Process Clarification: bounty-admin@company.com

## Best Practices

1. **Regular Monitoring**: Check ledger status daily during business hours
2. **Prompt Updates**: Update statuses within 4 hours of changes
3. **Clear Notes**: Always include explanatory notes for manual changes
4. **Verification**: Double-check recipient information before queuing
5. **Documentation**: Keep detailed records of all manual interventions
6. **Communication**: Notify recipients of significant delays or issues

## API Integration

The ledger supports programmatic access via REST API:

- `GET /ledger/bounty/{id}` - Get specific bounty status
- `POST /ledger/bounty` - Create new ledger entry
- `PUT /ledger/bounty/{id}` - Update bounty status
- `GET /ledger/status/{status}` - Get all entries by status

Refer to the API documentation for complete endpoint details and authentication requirements.