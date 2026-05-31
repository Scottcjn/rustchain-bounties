use std::sync::atomic::{AtomicBool, Ordering};

pub struct CancellationToken {
    cancelled: AtomicBool,
}

impl CancellationToken {
    pub fn new() -> Self { Self { cancelled: AtomicBool::new(false) } }
    pub fn cancel(&self) { self.cancelled.store(true, Ordering::SeqCst); }
    pub fn is_cancelled(&self) -> bool { self.cancelled.load(Ordering::SeqCst) }
}