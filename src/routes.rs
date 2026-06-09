// Add a new route for the Hall of Fame API
use actix_web::{web, HttpResponse};

pub fn routes(cfg: &mut web::ServiceConfig) {
    // ... existing routes ...

    // Add a new route for the Hall of Fame API
    cfg.route("/api/hall_of_fame", web::get().to(hall_of_fame));
}

// Define the Hall of Fame API handler
async fn hall_of_fame() -> HttpResponse {
    // TO DO: implement the Hall of Fame API logic
    // For now, return a placeholder response
    HttpResponse::Ok().json(serde_json::json!({
        "ancient_iron": [],
        "most_dedicated": [],
        "exotic_arch": [],
        "top_earners": [],
        "fleet_commanders": [],
    }))
}