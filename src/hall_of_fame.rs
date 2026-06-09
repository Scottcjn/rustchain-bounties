// Define the Hall of Fame API logic
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize)]
struct HallOfFame {
    ancient_iron: Vec<String>,
    most_dedicated: Vec<String>,
    exotic_arch: Vec<String>,
    top_earners: Vec<String>,
    fleet_commanders: Vec<String>,
}

async fn get_hall_of_fame() -> HallOfFame {
    // TO DO: implement the logic to fetch the Hall of Fame data
    // For now, return a placeholder response
    HallOfFame {
        ancient_iron: vec![],
        most_dedicated: vec![],
        exotic_arch: vec![],
        top_earners: vec![],
        fleet_commanders: vec![],
    }
}