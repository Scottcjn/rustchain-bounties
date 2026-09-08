use thiserror::Error;

#[derive(Error, Debug)]
pub enum Error {
    #[error("Network connection error: {0}")]
    Connection(#[from] reqwest::Error),

    #[error("API error (status {status}): {message}")]
    Api {
        status: u16,
        message: String,
        body: Option<serde_json::Value>,
    },

    #[error("Validation error: {0}")]
    Validation(String),

    #[error("JSON serialization/deserialization error: {0}")]
    Serialization(#[from] serde_json::Error),
}

pub type Result<T> = std::result::Result<T, Error>;
