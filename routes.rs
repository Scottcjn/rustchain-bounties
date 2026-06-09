// Add the following routes to handle the 404 pages
use actix_web::{web, App, HttpResponse, HttpServer, Responder};

async fn fossils() -> impl Responder {
    HttpResponse::Ok().body("Fossil Record")
}

async fn leaderboard() -> impl Responder {
    HttpResponse::Ok().body("Leaderboard")
}

async fn governance() -> impl Responder {
    HttpResponse::Ok().body("Governance")
}

async fn airdrops() -> impl Responder {
    HttpResponse::Ok().body("Airdrops")
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .route("/fossils", web::get().to(fossils))
            .route("/leaderboard", web::get().to(leaderboard))
            .route("/governance", web::get().to(governance))
            .route("/airdrops", web::get().to(airdrops))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}