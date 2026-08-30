use std::fs;
use std::path::Path;
use std::process::Command;

/// Main function to handle the micro-grant submission process
fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Check if we're in a git repository
    if !Path::new(".git").exists() {
        eprintln!("Error: This is not a git repository");
        return Ok(());
    }

    // Get current branch name
    let output = Command::new("git")
        .args(&["rev-parse", "--abbrev-ref", "HEAD"])
        .output()?;
    
    if !output.status.success() {
        eprintln!("Error: Failed to get current branch");
        return Ok(());
    }
    
    let branch_name = String::from_utf8(output.stdout)
        .unwrap()
        .trim()
        .to_string();

    // Check if we're on the main branch
    if branch_name == "main" {
        eprintln!("Error: Cannot submit grant from main branch");
        return Ok(());
    }

    // Create a new branch for the grant
    let grant_branch = format!("grant-{}", branch_name);
    
    let create_branch = Command::new("git")
        .args(&["checkout", "-b", &grant_branch])
        .output()?;
    
    if !create_branch.status.success() {
        eprintln!("Error: Failed to create grant branch");
        return Ok(());
    }

    // Create a simple README.md with grant information
    let grant_content = format!(
        "# Micro-Grant for {}\n\nThis is an auto-submitted micro-grant via RustChain.\n\n**Issue:** #123\n**Bounty:** 150 RTC\n\n## Implementation\n\nImplementation details here...",
        branch_name
    );

    fs::write("GRANT.md", grant_content)?;

    // Stage and commit the changes
    let add_files = Command::new("git")
        .args(&["add", "GRANT.md"])
        .output()?;
    
    if !add_files.status.success() {
        eprintln!("Error: Failed to stage files");
        return Ok(());
    }

    let commit = Command::new("git")
        .args(&["commit", "-m", "Auto-submit micro-grant"])
        .output()?;
    
    if !commit.status.success() {
        eprintln!("Error: Failed to commit changes");
        return Ok(());
    }

    // Push the branch
    let push = Command::new("git")
        .args(&["push", "origin", &grant_branch])
        .output()?;
    
    if !push.status.success() {
        eprintln!("Error: Failed to push branch");
        return Ok(());
    }

    println!("Successfully submitted micro-grant for branch '{}'", branch_name);
    println!("Branch '{}' created and pushed to origin", grant_branch);

    Ok(())
}