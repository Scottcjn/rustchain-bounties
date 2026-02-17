// Fix for: SnapshotIndex unused, O(n) scan instead of O(1)
// Bug: Fully implemented index not used in list_session_snapshots
// File: storage.rs:146-186 vs storage.rs:82-88
// Priority: Medium

use std::collections::HashMap;

/// Session storage with proper index usage
pub struct SessionStorage {
    /// O(1) lookup by ID
    sessions: HashMap<String, SessionData>,
    /// Index for efficient listing
    snapshot_index: HashMap<String, Vec<String>>,
}

impl SessionStorage {
    /// Create new storage
    pub fn new() -> Self {
        Self {
            sessions: HashMap::new(),
            snapshot_index: HashMap::new(),
        }
    }
    
    /// Add a session with proper indexing
    pub fn add_session(&mut self, session: SessionData) {
        let id = session.id.clone();
        self.sessions.insert(id.clone(), session);
        
        // Update index for O(1) lookup
        self.snapshot_index
            .entry(session.snapshot_id.clone())
            .or_insert_with(Vec::new)
            .push(id);
    }
    
    /// List sessions for a snapshot - now O(1) with index
    pub fn list_session_snapshots(&self, snapshot_id: &str) -> Vec<&SessionData> {
        // O(1) lookup using index
        if let Some(session_ids) = self.snapshot_index.get(snapshot_id) {
            session_ids
                .iter()
                .filter_map(|id| self.sessions.get(id))
                .collect()
        } else {
            Vec::new()
        }
    }
}

#[derive(Debug, Clone)]
pub struct SessionData {
    pub id: String,
    pub snapshot_id: String,
    pub data: Vec<u8>,
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_indexed_lookup() {
        let mut storage = SessionStorage::new();
        
        // Add sessions
        storage.add_session(SessionData {
            id: "s1".to_string(),
            snapshot_id: "snap1".to_string(),
            data: vec![1, 2, 3],
        });
        
        storage.add_session(SessionData {
            id: "s2".to_string(),
            snapshot_id: "snap1".to_string(),
            data: vec![4, 5, 6],
        });
        
        storage.add_session(SessionData {
            id: "s3".to_string(),
            snapshot_id: "snap2".to_string(),
            data: vec![7, 8, 9],
        });
        
        // Should find 2 sessions for snap1
        let snap1_sessions = storage.list_session_snapshots("snap1");
        assert_eq!(snap1_sessions.len(), 2);
        
        // Should find 1 session for snap2
        let snap2_sessions = storage.list_session_snapshots("snap2");
        assert_eq!(snap2_sessions.len(), 1);
        
        // Should find 0 sessions for non-existent
        let empty = storage.list_session_snapshots("nonexistent");
        assert!(empty.is_empty());
    }
}
