// Update the main function to include the new route
use actix_web::{web, App, HttpServer};

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    // ... existing code ...

    // Update the App configuration to include the new route
    let app = move || {
        App::new()
            .configure(routes)
            // ... existing middleware and routes ...
    };

    // ... existing code ...
}