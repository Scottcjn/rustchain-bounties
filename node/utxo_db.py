def apply_transaction(self, tx: Transaction, conn=None):
    own = conn is None
    try:
        if own:
            conn = self._conn()
        # ... (rest of the method remains the same)
    finally:
        if own:
            conn.close()