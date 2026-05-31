use std::sync::atomic::{AtomicU64, Ordering};
use std::collections::HashMap;

pub struct ConcurrentMap<K, V> {
    shards: Vec<std::sync::Mutex<HashMap<K, V>>>,
}

impl<K: std::hash::Hash + Eq, V> ConcurrentMap<K, V> {
    pub fn new(shards: usize) -> Self {
        let mut shard_vec = Vec::with_capacity(shards);
        for _ in 0..shards { shard_vec.push(std::sync::Mutex::new(HashMap::new())); }
        Self { shards: shard_vec }
    }
    fn shard(&self, key: &K) -> usize {
        use std::hash::{Hash, Hasher};
        let mut h = std::collections::hash_map::DefaultHasher::new();
        key.hash(&mut h);
        h.finish() as usize % self.shards.len()
    }
    pub fn insert(&self, key: K, val: V) { self.shards[self.shard(&key)].lock().unwrap().insert(key, val); }
    pub fn get(&self, key: &K) -> Option<V> where V: Clone { self.shards[self.shard(key)].lock().unwrap().get(key).cloned() }
}