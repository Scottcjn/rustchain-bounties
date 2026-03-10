use num_cpus;
use std::cmp;

pub struct WorkerPool {
    pub active_threads: usize,
}

impl WorkerPool {
    /// Initializes the mining worker pool.
    /// Fixed for Windows thread starvation (Issue #179)
    pub fn new(requested_threads: Option<usize>) -> Self {
        let available_cores = num_cpus::get();
        
        // Apply safe default cap for Windows environments to prevent spawn panic
        let safe_default = cmp::min(available_cores, 16);
        
        let active_threads = requested_threads.unwrap_or(safe_default);
        
        println!("[WorkerPool] Initialized with {} threads", active_threads);
        
        Self {
            active_threads,
        }
    }
}
