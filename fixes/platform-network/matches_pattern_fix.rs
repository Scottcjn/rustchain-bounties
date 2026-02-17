// Fix for: matches_pattern() panic on single asterisk
// Bug: `&pattern[1..0]` slice index out of bounds
// File: agent_cmd/utils.rs:78
// Priority: Critical

/// Safe pattern matching with asterisk support
pub fn matches_pattern(pattern: &str, text: &str) -> bool {
    if pattern.is_empty() {
        return text.is_empty();
    }
    if pattern == "*" {
        return true;
    }
    if let Some(asterisk_pos) = pattern.find('*') {
        let before_star = &pattern[..asterisk_pos];
        let after_star = &pattern[asterisk_pos + 1..];
        if !text.starts_with(before_star) {
            return false;
        }
        if !after_star.is_empty() && !text.ends_with(after_star) {
            return text[before_star.len()..].find(after_star).is_some();
        }
        return true;
    }
    pattern == text
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn test_single_asterisk() { assert!(matches_pattern("*", "anything")); }
    #[test] fn test_empty_pattern() { assert!(matches_pattern("", "")); }
    #[test] fn test_prefix_suffix() { assert!(matches_pattern("test*", "test123")); }
}
