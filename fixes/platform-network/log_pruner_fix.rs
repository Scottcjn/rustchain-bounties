// Fix for: is_log_file() matches .txt extension
// Bug: Arbitrary .txt files deleted/rotated
// File: log_pruner.rs:178-182
// Priority: Critical

pub fn is_log_file(filename: &str) -> bool {
    if filename.contains(".log") { return true; }
    let patterns = ["_log", "-log", "/log/", "app.log", "error.log"];
    patterns.iter().any(|p| filename.contains(p))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn test_valid() { assert!(is_log_file("app.log")); }
    #[test] fn test_invalid() { assert!(!is_log_file("readme.txt")); }
}
