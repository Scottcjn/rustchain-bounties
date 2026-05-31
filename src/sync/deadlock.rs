use std::collections::HashSet;
use std::sync::Mutex;

pub struct DeadlockDetector {
    held: Mutex<HashSet<u64>>,
}

impl DeadlockDetector {
    pub fn new() -> Self { Self { held: Mutex::new(HashSet::new()) } }
    pub fn acquire(&self, id: u64) -> bool {
        let mut held = self.held.lock().unwrap();
        if held.contains(&id) { return false; }
        held.insert(id); true
    }
    pub fn release(&self, id: u64) { self.held.lock().unwrap().remove(&id); }
}