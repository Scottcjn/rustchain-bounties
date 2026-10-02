```rust
use std::time::Duration;

//... (other code)

#[derive(Debug, PartialEq, Eq)]
pub enum DisputeError {
    SlaDeadlineOverflow,
    //... (other variants)
}

//... (other code)

impl Dispute {
    pub fn compute_sla_deadline(start_time: u64, duration: u64) -> Result<u64, DisputeError> {
        let deadline = start_time
            .checked_add(duration)
            .map_err(|_| DisputeError::SlaDeadlineOverflow)?;
        Ok(deadline)
    }
    //... (other methods)
}
```