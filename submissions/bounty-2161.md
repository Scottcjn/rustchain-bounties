## Creator Collaboration Features (Co-uploads & Split-Tips)

Implemented Creator Collaboration Features (Issue #427) in the BoTTube repository, focusing on the tip-split flow.

**Platform:** BoTTube
**Features Implemented:**
1. **Database Migration:** Added a `collaborator_ids` column (JSON array) to the `videos` table to store multiple creators.
2. **API Verification:** Full schema validation for the `collaborator_ids` array in `/api/upload` endpoint (max 5 collaborators, positive integers, matching existing agent IDs).
3. **Split-Tips Support:** Dividable tip logic that automatically splits any RTC tips equally among the primary uploader and all listed collaborators, handling rounding differences (given to the primary creator) and excluding the tipper.
4. **Validation Suite:** Five regression test cases verifying normal tipping, 3-way split, rounding logic, and tipper self-filtering.

**Source Code Specification:** [README.md](./bounty-2161/README.md)
**Regression Tests:** [test_bounty_2161_collab_tip_split.py](./bounty-2161/test_bounty_2161_collab_tip_split.py)

### Verification
- Run tests via pytest in BoTTube:
  ```bash
  pytest tests/test_bounty_2161_collab_tip_split.py
  ```
- All five verification tests pass successfully, validating correct tip splits, database logging (reasons: `tip_split_primary` / `tip_split_collab`), and integrity checks.

---

**Wallet:** RTCfe13452d122263caf633ab1876bd9631133b68b1