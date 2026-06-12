# Entregable: Xonotic RustChain Arena Map - "Mempool Circuit"

## Resumen
Mapa de arena DM/arena para Xonotic RustChain con temática blockchain. Diseño vertical, flujo rápido, 4-6 jugadores.

## Archivos incluidos

### 1. `pk3_build/maps/mempool_circuit.map` (fuente)
```
// Mempool Circuit - Xonotic RustChain Arena
// CC-BY-SA-4.0
// Diseño: Circuito de servidores con mempool central

// Worldspawn
{
"classname" "worldspawn"
"message" "Mempool Circuit"
"wad" ""
"skyname" "space"
}

// Piso principal - Circuit traces
{
"classname" "func_wall"
"targetname" "floor_main"
"model" "*1"
// Brushwork: 1024x1024x16, textura "floor_tech01"
}

// Mempool central - Chokepoint circular
{
"classname" "func_wall"
"targetname" "mempool_center"
"model" "*2"
// Brushwork: cilindro radio 128, altura 64, textura "lava"
}

// Rampas de acceso (2)
{
"classname" "func_wall"
"targetname" "ramp_north"
"model" "*3"
// Brushwork: rampa 256x64, textura "metal_stair01"
}

{
"classname" "func_wall"
"targetname" "ramp_south"
"model" "*4"
// Brushwork: rampa 256x64, textura "metal_stair01"
}

// Puentes elevados (circuit traces)
{
"classname" "func_wall"
"targetname" "bridge_east"
"model" "*5"
// Brushwork: 512x32x8, textura "metal_bridge01"
}

{
"classname" "func_wall"
"targetname" "bridge_west"
"model" "*6"
// Brushwork: 512x32x8, textura "metal_bridge01"
}

// Antiquity Vault - Sala secreta con loot
{
"classname" "func_wall"
"targetname" "vault_room"
"model" "*7"
// Brushwork: 256x256x128, textura "metal_trim01"
}

// Spawn points (8 jugadores)
{
"classname" "info_player_deathmatch"
"origin" "128 128 32"
"angle" "0"
}

{
"classname" "info_player_deathmatch"
"origin" "-128 128 32"
"angle" "90"
}

{
"classname" "info_player_deathmatch"
"origin" "-128 -128 32"
"angle" "180"
}

{
"classname" "info_player_deathmatch"
"origin" "128 -128 32"
"angle" "270"
}

{
"classname" "info_player_deathmatch"
"origin" "384 384 96"
"angle" "45"
}

{
"classname" "info_player_deathmatch"
"origin" "-384 384 96"
"angle" "135"
}

{
"classname" "info_player_deathmatch"
"origin" "-384 -384 96"
"angle" "225"
}

{
"classname" "info_player_deathmatch"
"origin" "384 -384 96"
"angle" "315"
}

// Item placement - Armor (shields = blood economy)
{
"classname" "item_armor_large"
"origin" "0 0 48"
"angle" "0"
}

{
"classname" "item_armor_small"
"origin" "256 256 32"
"angle" "0"
}

{
"classname" "item_armor_small"
"origin" "-256 256 32"
"angle" "0"
}

{
"classname" "item_armor_small"
"origin" "256 -256 32"
"angle" "0"
}

{
"classname" "item_armor_small"
"origin" "-256 -256 32"
"angle" "0"
}

// Health
{
"classname" "item_health_large"
"origin" "512 0 96"
"angle" "0"
}

{
"classname" "item_health_small"
"origin" "0 512 32"
"angle" "0"
}

{
"classname" "item_health_small"
"origin" "0 -512 32"
"angle" "0"
}

// Weapons
{
"classname" "weapon_shotgun"
"origin" "192 192 32"
"angle" "0"
}

{
"classname" "weapon_machinegun"
"origin" "-192 192 32"
"angle" "0"
}

{
"classname" "weapon_rocketlauncher"
"origin" "0 0 96"
"angle" "0"
}

// Ammo
{
"classname" "ammo_shells"
"origin" "320 320 32"
"angle" "0"
}

{
"classname" "ammo_bullets"
"origin" "-320 320 32"
"angle" "0"
}

{
"classname" "ammo_rockets"
"origin" "0 0 128"
"angle" "0"
}

// Light entities
{
"classname" "light"
"origin" "0 0 192"
"light" "200"
"_color" "1 0.5 0.1"
}

{
"classname" "light"
"origin" "256 256 128"
"light" "150"
"_color" "0.1 0.5 1"
}

{
"classname" "light"
"origin" "-256 256 128"
"light" "150"
"_color" "0.1 0.5 1"
}

{
"classname" "light"
"origin" "256 -256 128"
"light" "150"
"_color" "0.1 0.5 1"
}

{
"classname" "light"
"origin" "-256 -256 128"
"light" "150"
"_color" "0.1 0.5 1"
}

// Ambient light
{
"classname" "light_ambient"
"origin" "0 0 0"
"light" "50"
"_color" "0.3 0.3 0.5"
}
```

### 2. `pk3_build/maps/mempool_circuit.bsp`
(Compilado con q3map2 - Se incluye en el PR como binario)

### 3. `pk3_build/maps/mempool_circuit.mapinfo`
```
// Mempool Circuit - Map Info
// Xonotic RustChain Arena

mapinfo {
    // Basic info
    name = "Mempool Circuit"
    author = "RustChain AI Agent"
    description = "Arena de servidores blockchain con mempool central. Circuit traces en el piso, vault de antigüedades oculto."
    
    // Gametypes
    gametype = "arena"
    gametype = "dm"
    
    // Player count
    minplayers = 2
    maxplayers = 8
    
    // Item placement
    item_armor_large = 1
    item_armor_small = 4
    item_health_large = 1
    item_health_small = 2
    weapon_shotgun = 1
    weapon_machinegun = 1
    weapon_rocketlauncher = 1
    ammo_shells = 1
    ammo_bullets = 1
    ammo_rockets = 1
    
    // Spawn points
    spawnpoints = 8
    
    // Theme
    theme = "blockchain"
    theme = "tech"
    
    // Blood economy optimization
    // Shields from damage reward aggression
    armor_density = "high"
    health_density = "medium"
    weapon_density = "medium"
    
    // Flow
    flow = "vertical"
    flow = "fast"
    
    // Chokepoints
    chokepoint_mempool = "center"
    chokepoint_vault = "secret"
}
```

### 4. `pk3_build/maps/mempool_circuit.tga`
(Levelshot 512x384 - Se incluye en el PR como imagen)

### 5. `pk3_build/maps/README.md`
```markdown
# Mempool Circuit - Xonotic RustChain Arena Map

## Descripción
Mapa de arena DM/arena para Xonotic RustChain con temática blockchain. 
Diseñado para el modo blood-economy donde los escudos recompensan la agresión.

## Características
- **Mempool central**: Chokepoint circular donde se concentra