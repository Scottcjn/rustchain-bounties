use std::fs;
use std::io::{self, Write};
use std::path::Path;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    
    if args.len() < 2 {
        eprintln!("Usage: rtc-badge <README.md>");
        std::process::exit(1);
    }
    
    let readme_path = &args[1];
    
    // Check if file exists
    if !Path::new(readme_path).exists() {
        eprintln!("Error: File '{}' does not exist", readme_path);
        std::process::exit(1);
    }
    
    // Read the README content
    let content = fs::read_to_string(readme_path)?;
    
    // Check if badge already exists
    if content.contains("[![RTC Badge](https://img.shields.io/badge/RTC-2%20Bounty-blue)]") {
        println!("Badge already exists in the README");
        return Ok(());
    }
    
    // Find position to insert badge (after first line or after title)
    let mut new_content = String::new();
    let lines: Vec<&str> = content.lines().collect();
    let mut inserted = false;
    
    for (i, line) in lines.iter().enumerate() {
        new_content.push_str(line);
        new_content.push('\n');
        
        // Insert badge after the first line or title
        if !inserted && i == 0 {
            // Check if first line is a title
            if !line.starts_with('#') && !line.trim().is_empty() {
                // Insert badge after first non-title line
                new_content.push_str("\n[![RTC Badge](https://img.shields.io/badge/RTC-2%20Bounty-blue)](https://github.com/your-org/your-repo/issues/1)\n");
                inserted = true;
            }
        } else if !inserted && line.starts_with('#') {
            // Insert badge after first title
            new_content.push_str("\n[![RTC Badge](https://img.shields.io/badge/RTC-2%20Bounty-blue)](https://github.com/your-org/your-repo/issues/1)\n");
            inserted = true;
        }
    }
    
    // If we didn't insert yet, add it at the beginning
    if !inserted {
        new_content.insert_str(0, "[![RTC Badge](https://img.shields.io/badge/RTC-2%20Bounty-blue)](https://github.com/your-org/your-repo/issues/1)\n\n");
    }
    
    // Write back to file
    let mut file = fs::File::create(readme_path)?;
    file.write_all(new_content.as_bytes())?;
    
    println!("RTC badge successfully added to {}", readme_path);
    Ok(())
}