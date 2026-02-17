// Fix for: evaluate_shell_command_with_details() incomplete checks
// Priority: High

use std::collections::HashSet;

pub struct SecurityPolicy {
    pub denied_programs: HashSet<String>,
    pub allowed_directories: HashSet<String>,
    pub max_command_length: usize,
}

impl Default for SecurityPolicy {
    fn default() -> Self {
        let mut denied = HashSet::new();
        denied.insert("rm".to_string());
        denied.insert("mkfs".to_string());
        let mut allowed = HashSet::new();
        allowed.insert("/home".to_string());
        allowed.insert("/tmp".to_string());
        Self { denied_programs: denied, allowed_directories: allowed, max_command_length: 1000 }
    }
}

pub struct SecurityChecker { policy: SecurityPolicy }

impl SecurityChecker {
    pub fn new() -> Self { Self { policy: SecurityPolicy::default() } }
    pub fn is_command_allowed(&self, command: &str, working_dir: &str) -> (bool, String) {
        if command.len() > self.policy.max_command_length {
            return (false, "Command too long".to_string());
        }
        let program = command.split_whitespace().next().unwrap_or("");
        if self.policy.denied_programs.contains(program) {
            return (false, format!("Denied program: {}", program));
        }
        if !self.policy.allowed_directories.iter().any(|d| working_dir.starts_with(d)) {
            return (false, "Working directory not allowed".to_string());
        }
        (true, "OK".to_string())
    }
}
