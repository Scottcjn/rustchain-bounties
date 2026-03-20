#[cfg(test)]
mod tests {
    use std::process::Command;
    
    #[test]
    fn test_dry_run_mode() {
        let output = Command::new("cargo")
            .args(&["run", "--", "--dry-run"])
            .output()
            .expect("Failed to execute command");
            
        assert!(output.status.success());
        let output_str = String::from_utf8_lossy(&output.stdout);
        
        assert!(output_str.contains("Running in DRY-RUN mode"));
        assert!(output_str.contains("[DRY-RUN] Searching for new blocks"));
        assert!(output_str.contains("[DRY-RUN] Block validation successful"));
    }
    
    #[test]
    fn test_help_output() {
        let output = Command::new("cargo")
            .args(&["run", "", "--help"])
            .output()
            .expect("Failed to execute command");
            
        assert!(output.status.success());
        let output_str = String::from_utf8_lossy(&output.stdout);
        
        assert!(output_str.contains("rustchain-miner"));
        assert!(output_str.contains("--dry-run"));
    }
}