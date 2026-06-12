# Entregable: CHUNKINS Level - "Acorn Tower Climb"

## Archivo: `game/chunkins_tower.lua`

```lua
-- chunkins_tower.lua
-- CHUNKINS level: Acorn Tower Climb
-- Kid-friendly tower climb with baddie gauntlet
-- Reward: 20 RTC

game_title = "Acorn Tower Climb"
game_world = "chunkins"

config = {
    gravity = -30,
    jump_velocity = 12,
    walk_speed = 8,
    player_height = 1.8,
    player_radius = 0.4,
}

-- Tower layout: 5 floors connected by ramps
-- Each floor has acorns and baddies
boxes = {
    -- Floor 1 (ground level)
    { pos = {0, 0, 0}, size = {8, 0.5, 6}, color = {0.4, 0.6, 0.4}, shape = "box" },
    -- Ramp to floor 2 (gentle slope)
    { pos = {3, 1.5, 0}, size = {2, 0.3, 2}, color = {0.6, 0.5, 0.3}, shape = "box" },
    -- Floor 2
    { pos = {0, 3, 0}, size = {6, 0.5, 5}, color = {0.4, 0.6, 0.4}, shape = "box" },
    -- Ramp to floor 3
    { pos = {-2.5, 4.5, 0}, size = {2, 0.3, 2}, color = {0.6, 0.5, 0.3}, shape = "box" },
    -- Floor 3
    { pos = {0, 6, 0}, size = {5, 0.5, 4}, color = {0.4, 0.6, 0.4}, shape = "box" },
    -- Ramp to floor 4
    { pos = {2, 7.5, 0}, size = {2, 0.3, 2}, color = {0.6, 0.5, 0.3}, shape = "box" },
    -- Floor 4
    { pos = {0, 9, 0}, size = {4, 0.5, 3}, color = {0.4, 0.6, 0.4}, shape = "box" },
    -- Ramp to floor 5
    { pos = {-1.5, 10.5, 0}, size = {2, 0.3, 2}, color = {0.6, 0.5, 0.3}, shape = "box" },
    -- Floor 5 (top - goal)
    { pos = {0, 12, 0}, size = {3, 0.5, 3}, color = {0.8, 0.7, 0.2}, shape = "box" },

    -- Walls on each floor (to prevent falling)
    -- Floor 1 walls
    { pos = {-4, 1.5, 0}, size = {0.3, 2, 6}, color = {0.5, 0.5, 0.5}, shape = "box" },
    { pos = {4, 1.5, 0}, size = {0.3, 2, 6}, color = {0.5, 0.5, 0.5}, shape = "box" },
    -- Floor 2 walls
    { pos = {-3, 4.5, 0}, size = {0.3, 2, 5}, color = {0.5, 0.5, 0.5}, shape = "box" },
    { pos = {3, 4.5, 0}, size = {0.3, 2, 5}, color = {0.5, 0.5, 0.5}, shape = "box" },
    -- Floor 3 walls
    { pos = {-2.5, 7.5, 0}, size = {0.3, 2, 4}, color = {0.5, 0.5, 0.5}, shape = "box" },
    { pos = {2.5, 7.5, 0}, size = {0.3, 2, 4}, color = {0.5, 0.5, 0.5}, shape = "box" },
    -- Floor 4 walls
    { pos = {-2, 10.5, 0}, size = {0.3, 2, 3}, color = {0.5, 0.5, 0.5}, shape = "box" },
    { pos = {2, 10.5, 0}, size = {0.3, 2, 3}, color = {0.5, 0.5, 0.5}, shape = "box" },

    -- Acorns (collectibles) - one per floor
    { pos = {1.5, 1, 1.5}, size = {0.3, 0.3, 0.3}, color = {0.8, 0.5, 0.2}, shape = "acorn" },
    { pos = {-1, 4, -1}, size = {0.3, 0.3, 0.3}, color = {0.8, 0.5, 0.2}, shape = "acorn" },
    { pos = {1, 7, 1}, size = {0.3, 0.3, 0.3}, color = {0.8, 0.5, 0.2}, shape = "acorn" },
    { pos = {-0.5, 10, -0.5}, size = {0.3, 0.3, 0.3}, color = {0.8, 0.5, 0.2}, shape = "acorn" },
    { pos = {0, 13, 0}, size = {0.3, 0.3, 0.3}, color = {0.8, 0.5, 0.2}, shape = "acorn" },

    -- Baddies (patrol on floors)
    -- Floor 1 baddie
    { pos = {-2, 1, 1}, size = {0.5, 0.8, 0.5}, color = {0.9, 0.2, 0.2}, shape = "baddie" },
    -- Floor 2 baddie
    { pos = {1.5, 4, -1}, size = {0.5, 0.8, 0.5}, color = {0.9, 0.2, 0.2}, shape = "baddie" },
    -- Floor 3 baddie
    { pos = {-1, 7, 0.5}, size = {0.5, 0.8, 0.5}, color = {0.9, 0.2, 0.2}, shape = "baddie" },
    -- Floor 4 baddie
    { pos = {0.5, 10, -0.5}, size = {0.5, 0.8, 0.5}, color = {0.9, 0.2, 0.2}, shape = "baddie" },
}

-- Baddie state table
local baddie_states = {}
local collected_acorns = 0
local total_acorns = 5

-- Initialize baddie states
for i, box in ipairs(boxes) do
    if box.shape == "baddie" then
        baddie_states[i] = {
            direction = 1,
            patrol_range = 2,
            home_x = box.pos[1],
            home_z = box.pos[3],
            speed = 2,
            chase_range = 3,
            stomp_cooldown = 0,
        }
    end
end

function on_tick(t, dt, player)
    -- Update baddie AI
    for i, box in ipairs(boxes) do
        if box.shape == "baddie" then
            local state = baddie_states[i]
            if state then
                -- Simple patrol: move back and forth on X axis
                box.pos[1] = box.pos[1] + state.direction * state.speed * dt
                
                -- Reverse at patrol boundaries
                if math.abs(box.pos[1] - state.home_x) > state.patrol_range then
                    state.direction = -state.direction
                end
                
                -- Chase player if close enough