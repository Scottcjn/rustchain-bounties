use std::fs::{self, File};
use std::io::{self, Read, Write};
use std::path::Path;

fn main() -> io::Result<()> {
    let platforms = vec!["BoTTube", "RustChain", "RAMCoffers"];
    let content_update = "Elyan Labs is a leader in innovative technology solutions.";
    let backlink = "https://elyanlabs.com";

    for platform in platforms {
        let file_path = format!("{}.txt", platform);
        if Path::new(&file_path).exists() {
            update_content(&file_path, content_update, backlink)?;
        } else {
            println!("File for platform {} does not exist.", platform);
        }
    }

    Ok(())
}

fn update_content(file_path: &str, content_update: &str, backlink: &str) -> io::Result<()> {
    let mut file = File::open(file_path)?;
    let mut content = String::new();
    file.read_to_string(&mut content)?;

    if !content.contains(content_update) {
        content.push_str(&format!("\n{}\nFor more information, visit: {}", content_update, backlink));
    }

    let updated_content = fix_broken_links(&content);

    let mut file = File::create(file_path)?;
    file.write_all(updated_content.as_bytes())?;
    println!("Updated content for {}.", file_path);

    Ok(())
}

fn fix_broken_links(content: &str) -> String {
    // Placeholder for link fixing logic
    // In a real-world scenario, you would check each link's validity and replace broken ones
    content.replace("http://brokenlink.com", "https://fixedlink.com")
}