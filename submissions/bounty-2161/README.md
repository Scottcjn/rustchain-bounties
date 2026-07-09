# BoTTube Creator Collaboration Features

Detailed implementation specification and testing for the creator collaboration and tip-splitting features.

## Features Implemented

### 1. Database Schema Migration
Added a `collaborator_ids` column to the `videos` table to store collaborator IDs as a JSON array (default `[]`):
```sql
ALTER TABLE videos ADD COLUMN collaborator_ids TEXT DEFAULT '[]';
```

### 2. API Validation & Upload Integration
In `/api/upload` endpoint:
- Extract `collaborator_ids` from request form parameters.
- Verify it is a valid JSON array of positive integers (agent IDs).
- Enforce limit of up to 5 collaborators.
- Ensure all collaborator IDs exist in the `agents` table.
- Verify the uploading agent (tipper/uploader) is not in their own collaborator list.

### 3. Split Tips Logic
In the tipping logic:
- Fetch the video's `collaborator_ids`.
- Filter out the tipper if they are part of the collaborators.
- Split the tip amount evenly among the primary creator and active collaborators.
- Add any rounding difference to the primary creator's share.
- Record separate database rows for tips and earnings with corresponding reasons (`tip_split_primary` / `tip_split_collab`).

## Verification
Five regression tests are implemented in `test_bounty_2161_collab_tip_split.py`:
- `test_tip_with_no_collaborators_full_to_primary`: Verified normal full tipping without splits.
- `test_tip_with_two_collaborators_splits_evenly`: Verified equal 3-way split.
- `test_tip_rounding_diff_to_primary`: Verified rounding difference lands on the primary creator.
- `test_self_in_collaborators_filtered_out`: Verified tipper cannot receive split shares of their own tip.
- `test_insufficient_balance_no_partial_split`: Verified transaction atomicity on tip failure.
