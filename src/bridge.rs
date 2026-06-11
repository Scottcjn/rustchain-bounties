use sqlx::PgPool;
use sqlx::postgres::PgRow;

// ...

pub async fn void_bridge_transfer(
    pool: &PgPool,
    hash: &str,
    admin_id: i32,
) -> Result<(), sqlx::Error> {
    sqlx::transaction(pool, |tx| {
        let mut tx = tx?;
        let bridge_transfer = get_bridge_transfer_by_hash(&mut tx, hash)?;
        if bridge_transfer.status != "pending" 
            && bridge_transfer.status != "locked" 
            && bridge_transfer.status != "confirming" {
            return Ok(());
        }
        let result = sqlx::query("UPDATE bridge_transfers 
            SET status = 'voided', voided_by = $1 
            WHERE hash = $2 AND status IN ('pending', 'locked', 'confirming')
            RETURNING *")
            .bind(admin_id)
            .bind(hash)
            .execute(&mut tx)
            .await?;
        if result.rows_affected() == 0 {
            // Another writer beat us, re-read the current status
            let current_status = get_bridge_transfer_by_hash(&mut tx, hash)?.status;
            if current_status == "completed" || current_status == "failed" {
                return Err(sqlx::Error::RowNotFound);
            }
        }
        Ok(())
    })
    .await
}

// ...