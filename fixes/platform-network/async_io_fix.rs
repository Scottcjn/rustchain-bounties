// Fix for: Blocking synchronous I/O in async function
// Priority: High

use tokio::fs::File;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

pub async fn async_read_file(path: &str) -> Result<String, std::io::Error> {
    let mut file = File::open(path).await?;
    let mut contents = String::new();
    file.read_to_string(&mut contents).await?;
    Ok(contents)
}

pub async fn async_write_file(path: &str, content: &str) -> Result<(), std::io::Error> {
    let mut file = File::create(path).await?;
    file.write_all(content.as_bytes()).await?;
    Ok(())
}
