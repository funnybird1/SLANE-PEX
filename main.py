# =========================================================
# ADVANCED AIR COMBAT SIMULATOR
# IR / RADAR / OPTICAL MISSILES
# FLARES / CHAFF / SMOKE
# 40MM BOFORS AAA
# RWR + OPTICAL WARNING
# JET + HELICOPTER
# =========================================================

import pygame
import math
import random
import os
import sys

pygame.init()
pygame.mixer.init()

# region WINDOW
# =========================================================
# WINDOW
# =========================================================

info = pygame.display.Info()

WIDTH, HEIGHT = info.current_w, info.current_h

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.NOFRAME
)

pygame.display.set_caption(
    "Advanced Air Combat Simulator"
)

clock = pygame.time.Clock()
fx_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

# endregion

# region RESOURCE PATH
# =========================================================
# RESOURCE PATH
# =========================================================

def resource_path(relative_path):

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(
        base_path,
        relative_path
    )

# endregion

# region COLORS
# =========================================================
# COLORS
# =========================================================

BG = (8, 12, 20)

WHITE = (240, 240, 240)

GREEN = (0, 255, 120)

BLUE = (0, 170, 255)
WATER = (0, 80, 140)

CYAN = (0, 220, 255)

LIGHT_BLUE = (120, 180, 255)

RED = (255, 80, 80)

YELLOW = (255, 220, 0)

ORANGE = (255, 140, 0)

PURPLE = (200, 80, 255)

GREY = (100, 100, 100)

BLACK = (30, 30, 30)
LIGHT_BLUE_ALPHA = (120, 180, 255, 80) # For transparent cone

GRASS = (30, 110, 40)

GRASS_LIGHT = (65, 170, 70)

GRASS_DARK = (18, 72, 28)

ROAD = (55, 45, 35)

ROAD_EDGE = (85, 75, 65)

MOUNTAIN = (70, 78, 86)

MOUNTAIN_ALT = (92, 104, 112)

# endregion

# region GAME STATE
# =========================================================
# GAME STATE
# =========================================================

paused = False

result_text = ""
result_timer = 0

show_controls = False
prev_plane_speed = 0
sonic_booms = []
vortex_points = []
last_vortex_pos = [None, None]
ground_radar_enabled = False
ground_radar_lock = 0.0
ground_radar_sweep = 0.0
radar_enabled = False
radar_sweep = 0.0
prev_radar_sweep = 0.0
radar_dots = []
radar_cursor_angle = 0.0
radar_cursor_dist = 0.5

# endregion

# region WARNING SYSTEMS
# =========================================================
# WARNING SYSTEMS
# =========================================================

rwr_state = "NONE"

lwr_warning = False

# endregion

# region AIRCRAFT TYPE
# =========================================================
# AIRCRAFT TYPE
# =========================================================

aircraft_type = "JET"

# endregion

# region PLAYER
# =========================================================
# PLAYER
# =========================================================

plane_x = WIDTH * 0.5
plane_y = HEIGHT * 0.5

plane_speed = 0
max_speed = 19.5
plane_throttle = 0.0
detent_timer = 0
detent_target = 0

plane_angle = 0

applied_turn = 0

turn_speed = 0.0225

camera_zoom = 1.0
MIN_ZOOM = 0.085
MAX_ZOOM = 3.2
ZOOM_STEP = 1.20 #1.08
GRASS_SPAWN_MIN_X = -12000
GRASS_SPAWN_MAX_X = 12000
GRASS_SPAWN_MIN_Y = -12000
GRASS_SPAWN_MAX_Y = 12000

heat_offset = -52

# endregion

# region HELICOPTER
# =========================================================
# HELICOPTER
# =========================================================

heli_velocity_x = 0
heli_velocity_y = 0

# endregion

# region ENEMY AIRCRAFT
# =========================================================
# ENEMY AIRCRAFT (orbits in northern region)
# =========================================================

ENEMY_ORBIT_RADIUS = 800
enemy_cx = 300
enemy_cy = -2000
enemy_orbit_angle = 0
enemy_x = enemy_cx + ENEMY_ORBIT_RADIUS
enemy_y = enemy_cy
enemy_heading = math.pi * 0.5
enemy_image = None
enemy_speed = 0.0
enemy_max_speed = 19.5
enemy_throttle = 0.0
enemy_turn_speed = 0.0225
enemy_ai_active = False
enemy_state = "ORBIT"
enemy_gun_timer = 0
enemy_bullets = []
enemy_health = 100
enemy_max_health = 100

# endregion

# region IMAGES
# =========================================================
# IMAGES
# =========================================================

PLANE_IMAGE_PATH = resource_path("hornet.png")

HELI_IMAGE_PATH = resource_path(
    "helicopter.png"
)

plane_image = None
heli_image = None

if os.path.exists(PLANE_IMAGE_PATH):
    plane_image = pygame.image.load(
        PLANE_IMAGE_PATH
    ).convert_alpha()
    # hornet.png is vertical (nose up), rotate -90 to face East/Right
    plane_image = pygame.transform.rotate(plane_image, -90)
    plane_image = pygame.transform.scale(
        plane_image,
        (120, 90)
    )

if os.path.exists(HELI_IMAGE_PATH):

    heli_image = pygame.image.load(
        HELI_IMAGE_PATH
    ).convert_alpha()

    heli_image = pygame.transform.scale(
        heli_image,
        (120, 120)
    )

ENEMY_IMAGE_PATH = resource_path("plane.png")
enemy_image = None
if os.path.exists(ENEMY_IMAGE_PATH):
    enemy_image = pygame.image.load(ENEMY_IMAGE_PATH).convert_alpha()
    enemy_image = pygame.transform.rotate(enemy_image, 0)
    enemy_image = pygame.transform.scale(enemy_image, (150, 112))

# endregion

# region SOUNDS
# =========================================================
# SOUNDS
# =========================================================

gun_sound = pygame.mixer.Sound(
    resource_path("sounds/gun.wav")
)

ir_launch_sound = pygame.mixer.Sound(
    resource_path("sounds/ir_launch.wav")
)

radar_launch_sound = pygame.mixer.Sound(
    resource_path("sounds/radar_launch.wav")
)

optical_launch_sound = pygame.mixer.Sound(
    resource_path("sounds/optical_launch.wav")
)

flare_sound = pygame.mixer.Sound(
    resource_path("sounds/flare.wav")
)

chaff_sound = pygame.mixer.Sound(
    resource_path("sounds/chaff.wav")
)

explosion_sound = pygame.mixer.Sound(
    resource_path("sounds/explosion.wav")
)

bofors_sound = pygame.mixer.Sound(
    resource_path("sounds/bofors.wav")
)

rwr_search_sound = pygame.mixer.Sound(
    resource_path("sounds/rwr_search.wav")
)

rwr_lock_sound = pygame.mixer.Sound(
    resource_path("sounds/rwr_lock.wav")
)

rwr_missile_sound = pygame.mixer.Sound(
    resource_path("sounds/rwr_missile.wav")
)

# endregion

# region MISSILES
# =========================================================
# MISSILES
# =========================================================

missiles = []

IR_MISSILE_SPEED = 2000 / 66.6  # Setting 2000 here results in 2000 knots
IR_TURN_RATE = 0.09
IR_DRAG = 0.97
IR_THRUST = IR_MISSILE_SPEED * (1 - IR_DRAG) / IR_DRAG  # equilibrium speed = max_speed
IRCCM_MAX_ANGLE = 60  # degrees — angle where flare distraction probability reaches zero
IRCCM_BREAK_ANGLE = 45  # degrees — decoy breaks if flare drifts beyond this from player

FOX1_MISSILE_SPEED = 1500 / 66.6
FOX1_TURN_RATE = 0.055
FOX1_CONE_ANGLE = 60

FOX3_MISSILE_SPEED = 2500 / 66.6
FOX3_TURN_RATE = 0.06
FOX3_CONE_ANGLE = 60
FOX3_TRACK_FOV = 5
FOX3_GIMBAL_ANGLE = 60
FOX3_FUEL = 200  # frames (~3.3s at 60fps)

FOX1_RADAR_RANGE = 10000 # Ground radar range
RADAR_CONE_RANGE = 10000 # Range for visual cone and detection (FOX-3)
FOX1_FUEL = 175  # frames (~2.9s)

OPTICAL_MISSILE_SPEED = 380 / 66.6 # Setting 380 here results in 380 knots
OPTICAL_TURN_RATE = 0.1
OPTICAL_FUEL = 250  # frames (~4.2s)

IR_FUEL = 300  # frames (~5.0s)

# endregion

# region GUN SYSTEM
# =========================================================
# GUN SYSTEM
# =========================================================

bullets = []

gun_fire_timer = 0

VULCAN_FIRE_RATE = 2
CHAIN_GUN_FIRE_RATE = 9

VULCAN_SPEED = 27
CHAIN_SPEED = 18

# endregion

# region COUNTERMEASURES
# =========================================================
# COUNTERMEASURES
# =========================================================

flares = []

chaff_clouds = []

smoke_clouds = []

# endregion

# region BOFORS AAA
# =========================================================
# BOFORS AAA
# =========================================================

aaa_enabled = False

aaa_position = (
    WIDTH // 2,
    HEIGHT - 80
)

aaa_bullets = []

AAA_FIRE_RATE = 18

aaa_timer = 0

bofors_flak = []

# endregion

# region EFFECTS
# =========================================================
# EFFECTS
# =========================================================

explosions = []

terrain_surface = None

mountains = []

mountain_refresh_timer = 0

# endregion
# region TERRAIN
def generate_mountains():

    global mountains
    mountains = []

    for _ in range(45):

        mountains.append({
            "x": random.randint(GRASS_SPAWN_MIN_X, GRASS_SPAWN_MAX_X),
            "y": random.randint(GRASS_SPAWN_MIN_Y, GRASS_SPAWN_MAX_Y),
            "size": random.randint(360, 660),
            "color": MOUNTAIN if random.random() > 0.5 else MOUNTAIN_ALT
        })


generate_mountains()

grass_blades = []

for _ in range(800):

    gx = random.randint(-12000, 12000)
    gy = random.randint(-12000, 12000)

    blade_len = random.randint(18, 42)
    center_len = blade_len + random.randint(4, 10)
    spread = random.randint(4, 9)
    angle = random.uniform(0.08, 0.22)
    
    # Pre-calculate offsets to avoid trig in the main loop
    cos_a = math.cos(angle) * 8
    sin_a = math.sin(angle) * 6

    grass_blades.append({
        "x": gx,
        "y": gy,
        "blade_len": blade_len,
        "center_len": center_len,
        "spread": spread,
        "lx_off": cos_a, "ly_off": sin_a,
        "rx_off": cos_a, "ry_off": sin_a
    })

# =========================================================
# FONT
# =========================================================

font = pygame.font.SysFont(
    "consolas",
    22
)

font_small = pygame.font.SysFont(
    "consolas",
    14
)

big_font = pygame.font.SysFont(
    "consolas",
    44
)

# =========================================================
# RESET PLAYER
# =========================================================

def reset_plane():

    global plane_x
    global plane_y

    global plane_speed
    global plane_throttle
    global detent_timer
    global detent_target
    global last_vortex_pos

    global plane_angle

    global heli_velocity_x
    global heli_velocity_y
    global ground_radar_enabled
    global ground_radar_lock
    global missiles
    global enemy_bullets
    global enemy_gun_timer

    plane_x = WIDTH * 0.5
    plane_y = HEIGHT * 0.5

    plane_speed = 0
    plane_throttle = 0.0
    detent_timer = 0
    detent_target = 0

    plane_angle = 0

    heli_velocity_x = 0
    heli_velocity_y = 0
    last_vortex_pos = [None, None]

    ground_radar_enabled = False
    ground_radar_lock = 0.0
    missiles = []
    enemy_bullets = []
    enemy_gun_timer = 0

# =========================================================
# DRAW AIRCRAFT
# =========================================================

def world_to_screen(x, y):

    return (
        int((x - plane_x) * camera_zoom + WIDTH * 0.5),
        int((y - plane_y) * camera_zoom + HEIGHT * 0.5)
    )


# endregion

# region DRAWING
def draw_plane(x, y, angle, turn_rate=0):

    global aircraft_type

    sx, sy = world_to_screen(x, y)

    if aircraft_type == "JET":

        sprite_zoom = MIN_ZOOM * 1.5 if camera_zoom <= MIN_ZOOM * 1.01 else camera_zoom

        # Afterburner Flames
        if plane_throttle >= 80:
            # Calculate intensity: 0.0 at 80% throttle to 1.0 at 100%
            intensity = (plane_throttle - 80) / 20.0
            # Start very short at 80% and scale up with throttle
            flame_len = (2.0 + intensity * 45) * sprite_zoom * random.uniform(0.85, 1.15)
            
            # Physical offsets relative to the plane's center
            tail_offset = 47 * sprite_zoom
            side_offset = 3 * sprite_zoom
            perp_angle = angle + math.pi / 2
            
            for side in [-1, 1]:
                # Starting point at the engine exhaust
                ex = sx - math.cos(angle) * tail_offset + math.cos(perp_angle) * (side * side_offset)
                ey = sy - math.sin(angle) * tail_offset + math.sin(perp_angle) * (side * side_offset)
                # End point at the tip of the flame
                fx = ex - math.cos(angle) * flame_len
                fy = ey - math.sin(angle) * flame_len
                
                pygame.draw.line(screen, ORANGE, (ex, ey), (fx, fy), max(1, int(4 * sprite_zoom)))

        if plane_image is not None:

            sprite = pygame.transform.scale(
                plane_image,
                (
                    max(1, int(plane_image.get_width() * sprite_zoom)),
                    max(1, int(plane_image.get_height() * sprite_zoom))
                )
            )

            rotated = pygame.transform.rotate(
                sprite,
                -math.degrees(angle)
            )

            rect = rotated.get_rect(
                center=(sx, sy)
            )

            screen.blit(rotated, rect)

        else:

            pygame.draw.circle(
                screen,
                BLUE,
                (sx, sy),
                18
            )

    else:

        if heli_image is not None:

            sprite = pygame.transform.scale(
                heli_image,
                (
                    max(1, int(heli_image.get_width() * sprite_zoom)),
                    max(1, int(heli_image.get_height() * sprite_zoom))
                )
            )

            rotated = pygame.transform.rotate(
                sprite,
                -math.degrees(angle)
            )

            rect = rotated.get_rect(
                center=(sx, sy)
            )

            screen.blit(rotated, rect)

        rotor_surface = pygame.Surface(
            (180, 180),
            pygame.SRCALPHA
        )

        rotor_angle = (
            pygame.time.get_ticks()
            * 0.9
        ) % 360

        for i in range(4):

            ang = math.radians(
                rotor_angle + i * 90
            )

            x1 = 90 + math.cos(ang) * 70
            y1 = 90 + math.sin(ang) * 70

            x2 = 90 - math.cos(ang) * 70
            y2 = 90 - math.sin(ang) * 70

            pygame.draw.line(
                rotor_surface,
                (255, 255, 255, 40),
                (x1, y1),
                (x2, y2),
                10
            )

        screen.blit(
            rotor_surface,
            (
                sx - 90,
                sy - 90
            )
        )

# =========================================================
# DRAW MISSILE
# =========================================================

# endregion

# region MISSILE DRAWING
def draw_missile(
    sx,
    sy,
    angle,
    missile_type,
    scale=1.0
):

    points = [
        (10 * scale, 0),
        (-6 * scale, -3 * scale),
        (-2 * scale, 0),
        (-6 * scale, 3 * scale)
    ]

    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    
    screen_points = [
        (sx + (px * cos_a - py * sin_a), sy + (px * sin_a + py * cos_a))
        for px, py in points
    ]

    color = RED

    if missile_type == "RADAR":
        color = CYAN

    if missile_type == "OPTICAL":
        color = PURPLE

    pygame.draw.polygon(
        screen,
        color,
        screen_points
    )

# =========================================================
# DRAW BOFORS
# =========================================================

# endregion

# region AAA DRAWING
def draw_aaa():

    x, y = aaa_position
    sx, sy = world_to_screen(x, y)

    pygame.draw.rect(
        screen,
        GREY,
        (sx - 26, sy - 14, 52, 28)
    )

    pygame.draw.line(
        screen,
        LIGHT_BLUE,
        (sx, sy),
        (
            sx,
            sy - 55
        ),
        8
    )

    pygame.draw.circle(
        screen,
        GREY,
        (sx - 20, sy + 12),
        8
    )

    pygame.draw.circle(
        screen,
        GREY,
        (sx + 20, sy + 12),
        8
    )

# =========================================================
# FIRE BOFORS
# =========================================================

# endregion

# region ENVIRONMENT
def draw_environment(v_min_x, v_max_x, v_min_y, v_max_y, ox, oy):

    screen.fill(WATER)

    left = max(GRASS_SPAWN_MIN_X, v_min_x)
    right = min(GRASS_SPAWN_MAX_X, v_max_x)
    top = max(GRASS_SPAWN_MIN_Y, v_min_y)
    bottom = min(GRASS_SPAWN_MAX_Y, v_max_y)

    if left < right and top < bottom:
        sx1 = int(left * camera_zoom + ox)
        sy1 = int(top * camera_zoom + oy)
        sx2 = int(right * camera_zoom + ox)
        sy2 = int(bottom * camera_zoom + oy)
        
        rect_x = min(sx1, sx2)
        rect_y = min(sy1, sy2)
        rect_w = max(1, abs(sx2 - sx1))
        rect_h = max(1, abs(sy2 - sy1))

        # Optimization: only draw if within screen pixels
        if rect_x < WIDTH and rect_x + rect_w > 0:
            if rect_y < HEIGHT and rect_y + rect_h > 0:
                pygame.draw.rect(screen, GRASS, (rect_x, rect_y, rect_w, rect_h))

    grass_scale = camera_zoom
    # Skip blades if zoomed very far out to save performance
    step = 1 if camera_zoom > 0.7 else (2 if camera_zoom > 0.35 else 3)

    for blade in grass_blades[::step]:
        if not (v_min_x < blade["x"] < v_max_x and v_min_y < blade["y"] < v_max_y):
            continue

        sx = int(blade["x"] * camera_zoom + ox)
        sy = int(blade["y"] * camera_zoom + oy)

        blade_len = int(blade["blade_len"] * grass_scale)
        center_len = int(blade["center_len"] * grass_scale)
        spread = max(1, int(blade["spread"] * grass_scale))

        pygame.draw.line(
            screen,
            GRASS_LIGHT,
            (sx, sy + 2),
            (sx, sy - center_len),
            max(1, int(3 * grass_scale))
        )

        left_x1 = sx - spread
        left_y1 = sy + 2
        left_x2 = sx - spread - int(blade["lx_off"] * grass_scale)
        left_y2 = sy - blade_len + int(blade["ly_off"] * grass_scale)

        right_x1 = sx + spread
        right_y1 = sy + 2
        right_x2 = sx + spread + int(blade["rx_off"] * grass_scale)
        right_y2 = sy - blade_len - int(blade["ry_off"] * grass_scale)

        pygame.draw.line(
            screen,
            GRASS_LIGHT,
            (left_x1, left_y1),
            (left_x2, left_y2),
            max(1, int(2 * grass_scale))
        )

        pygame.draw.line(
            screen,
            GRASS_LIGHT,
            (right_x1, right_y1),
            (right_x2, right_y2),
            max(1, int(2 * grass_scale))
        )

    # Draw Runway
    rsx = int((WIDTH * 0.5 - 200) * camera_zoom + ox)
    rsy = int((HEIGHT * 0.5 - 100) * camera_zoom + oy)
    r_width = int(2000 * camera_zoom)
    r_height = int(200 * camera_zoom)
    
    if rsx < WIDTH and rsx + r_width > 0:
        pygame.draw.rect(screen, (15, 15, 15), (rsx, rsy, r_width, r_height))

    for hill in mountains:
        if not (v_min_x - 500 < hill["x"] < v_max_x + 500 and v_min_y - 500 < hill["y"] < v_max_y + 500):
            continue

        sx = int(hill["x"] * camera_zoom + ox)
        sy = int(hill["y"] * camera_zoom + oy)

        hill_size = hill["size"] * camera_zoom

        points = [
            (sx, sy - hill_size * 0.65),
            (sx - hill_size * 0.9, sy + hill_size * 0.1),
            (sx + hill_size * 0.9, sy + hill_size * 0.1),
        ]

        pygame.draw.polygon(
            screen,
            hill["color"],
            points
        )

        pygame.draw.polygon(
            screen,
            (
                max(0, hill["color"][0] - 8),
                max(0, hill["color"][1] - 8),
                max(0, hill["color"][2] - 8)
            ),
            [
                (sx, sy + hill_size * 0.25),
                (sx - hill_size * 0.45, sy + hill_size * 0.55),
                (sx + hill_size * 0.45, sy + hill_size * 0.55),
            ]
        )


# endregion

# region GAME SYSTEMS
def fire_aaa():

    future_x = plane_x
    future_y = plane_y

    if aircraft_type == "JET":

        future_x += math.cos(
            plane_angle
        ) * plane_speed * random.uniform(
            8,
            20
        )

        future_y += math.sin(
            plane_angle
        ) * plane_speed * random.uniform(
            8,
            20
        )

    else:

        future_x += (
            heli_velocity_x
            * random.uniform(8, 18)
        )

        future_y += (
            heli_velocity_y
            * random.uniform(8, 18)
        )

    dx = future_x - aaa_position[0]
    dy = future_y - aaa_position[1]

    angle = math.atan2(dy, dx)

    angle += random.uniform(
        -0.30,
        0.30
    )

    speed = random.uniform(
        6,
        9
    )

    fuse_time = random.randint(
        40,
        80
    )

    aaa_bullets.append({

        "x": aaa_position[0],
        "y": aaa_position[1],

        "vx": math.cos(angle) * speed,
        "vy": math.sin(angle) * speed,

        "life": fuse_time
    })

# =========================================================
# EXPLOSION
# =========================================================

def create_explosion(
    x,
    y,
    color,
    radius=5
):
    explosion_sound.play()

    explosions.append({

        "x": x,
        "y": y,

        "radius": radius,

        "life": 30,

        "color": color
    })

# =========================================================
# SPAWN MISSILE
# =========================================================

def spawn_missile(missile_type):
    spawn_side = random.randint(0, 3)
    half_w = WIDTH * 0.5 + 40
    half_h = HEIGHT * 0.5 + 40
    half = max(half_w, half_h)
    mult = 6 if missile_type == "IR" else 12
    spawn_offset_x = half * mult
    spawn_offset_y = half * mult

    if missile_type == "STATIONARY_RADAR":
        spawn_x, spawn_y = aaa_position
    else:
        if spawn_side == 0:
            spawn_x = plane_x + random.randint(-int(spawn_offset_x), int(spawn_offset_x))
            spawn_y = plane_y - spawn_offset_y
        elif spawn_side == 1:
            spawn_x = plane_x + spawn_offset_x
            spawn_y = plane_y + random.randint(-int(spawn_offset_y), int(spawn_offset_y))
        elif spawn_side == 2:
            spawn_x = plane_x + random.randint(-int(spawn_offset_x), int(spawn_offset_x))
            spawn_y = plane_y + spawn_offset_y
        else:
            spawn_x = plane_x - spawn_offset_x
            spawn_y = plane_y + random.randint(-int(spawn_offset_y), int(spawn_offset_y))

    if missile_type == "STATIONARY_RADAR":
        init_fuel = FOX1_FUEL
        init_speed = FOX1_MISSILE_SPEED
    elif missile_type == "RADAR":
        init_fuel = FOX3_FUEL
        init_speed = FOX3_MISSILE_SPEED
    elif missile_type == "IR":
        init_fuel = IR_FUEL
        init_speed = IR_MISSILE_SPEED
    else:
        init_fuel = OPTICAL_FUEL
        init_speed = OPTICAL_MISSILE_SPEED

    spawn_angle = math.atan2(
        plane_y - spawn_y,
        plane_x - spawn_x
    )

    missiles.append({
        "type": missile_type,
        "x": spawn_x,
        "y": spawn_y,
        "angle": spawn_angle,
        "vx": math.cos(spawn_angle) * init_speed,
        "vy": math.sin(spawn_angle) * init_speed,
        "track_x": plane_x,
        "track_y": plane_y,
        "trail": [],
        "flare_bias": random.uniform(
            0.15,
            0.4
        ),
        "chaff_bias": random.uniform(
            0.45,
            0.85
        ),
        "lock_strength": 0.0,
        "is_decoyed": False,
        "decoy_pos": [0, 0],
        "fuel": init_fuel,
        "max_fuel": init_fuel,
        "speed": init_speed,
        "max_speed": init_speed
    })

# =========================================================
# FLARES
# =========================================================

# endregion

# region COUNTERMEASURE ACTIONS
def deploy_flares():

    flare_sound.play()

    for i in range(2):

        angle = (
            plane_angle
            + math.radians(
                random.uniform(
                    150,
                    210
                )
            )
        )

        speed = random.uniform(
            4,
            7
        )

        flares.append({

            "x": plane_x,
            "y": plane_y,

            "vx": math.cos(angle)
            * speed,

            "vy": math.sin(angle)
            * speed,

            "life": 60
        })

# =========================================================
# CHAFF
# =========================================================

# endregion

# region GUN AND EFFECTS
def deploy_chaff():

    chaff_sound.play()

    for i in range(16):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            1,
            4
        )

        chaff_clouds.append({

            "x": plane_x,
            "y": plane_y,

            "vx": math.cos(angle)
            * speed,

            "vy": math.sin(angle)
            * speed,

            "life": 180
        })

# =========================================================
# SMOKE
# =========================================================

# endregion

# region MAIN LOOP
def deploy_smoke():

    for i in range(24):

        angle = random.uniform(
            0,
            math.pi * 2
        )

        speed = random.uniform(
            0.5,
            2.5
        )

        smoke_clouds.append({

            "x": plane_x,
            "y": plane_y,

            "vx": math.cos(angle)
            * speed,

            "vy": math.sin(angle)
            * speed,

            "life": 220,

            "radius": random.randint(
                18,
                35
            )
        })

# =========================================================
# FIRE GUN
# =========================================================

# endregion

# region INPUT AND UPDATE
def fire_gun():

    global gun_fire_timer

    if gun_fire_timer > 0:
        return

    if aircraft_type == "JET":

        fire_rate = VULCAN_FIRE_RATE
        speed = VULCAN_SPEED
        spread = 0.03
        color = YELLOW

    else: 
 
        fire_rate = CHAIN_GUN_FIRE_RATE
        speed = CHAIN_SPEED
        spread = 0.07
        color = ORANGE

    gun_fire_timer = fire_rate

    gun_sound.play()

    angle = plane_angle + random.uniform(
        -spread,
        spread

    )

    spawn_x = (
        plane_x
        + math.cos(angle) * 35
    )

    spawn_y = (
        plane_y
        + math.sin(angle) * 35
    )
   
    if aircraft_type == "JET":
        player_vx = math.cos(plane_angle) * plane_speed
        player_vy = math.sin(plane_angle) * plane_speed
    else:
        player_vx = heli_velocity_x
        player_vy = heli_velocity_y

    bullets.append({

        "x": spawn_x,
        "y": spawn_y,

        "vx": math.cos(angle) * speed + player_vx,
        "vy": math.sin(angle) * speed + player_vy,

        "init_speed": speed,

        "life": 80,

        "color": color
    })

# =========================================================
# MAIN LOOP
# =========================================================

# endregion

# region MAIN LOOP
running = True

while running:

    clock.tick(60)

    # =====================================================
    # EVENTS
    # =====================================================

    rwr_state = "NONE"

    lwr_warning = False

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_p:
                paused = not paused

            if (
                event.key == pygame.K_LSHIFT
                or event.key == pygame.K_RSHIFT
            ):
                deploy_flares()

            if (
                event.key == pygame.K_LCTRL
                or event.key == pygame.K_RCTRL
            ):
                deploy_chaff()

            if event.key == pygame.K_c:
                deploy_smoke()

            if event.key == pygame.K_1:
                ground_radar_enabled = not ground_radar_enabled
                if not ground_radar_enabled:
                    ground_radar_lock = 0.0

            if event.key == pygame.K_2:
                ir_launch_sound.play()
                spawn_missile("IR")
      
            if event.key == pygame.K_3:
                radar_launch_sound.play()
                spawn_missile("RADAR")

            if event.key == pygame.K_z:
                aaa_enabled = not aaa_enabled

            if event.key == pygame.K_h:
                show_controls = not show_controls

            if event.key == pygame.K_BACKSPACE:
                reset_plane()

            if event.key == pygame.K_g:
                enemy_ai_active = not enemy_ai_active
                if not enemy_ai_active:
                    enemy_state = "ORBIT"

            if event.key == pygame.K_r:
                radar_enabled = not radar_enabled


    keys = pygame.key.get_pressed()
    alt_held = keys[pygame.K_LALT] or keys[pygame.K_RALT]

    # radar cursor control
    if radar_enabled and alt_held:
        if keys[pygame.K_a]:
            radar_cursor_angle -= 0.02
        if keys[pygame.K_d]:
            radar_cursor_angle += 0.02
        if keys[pygame.K_w]:
            radar_cursor_dist = min(1.0, radar_cursor_dist + 0.01)
        if keys[pygame.K_s]:
            radar_cursor_dist = max(0.1, radar_cursor_dist - 0.01)
        radar_cursor_angle = max(-1.0, min(1.0, radar_cursor_angle))

    # =====================================================
    # CAMERA ZOOM (always computed first for frame-consistency)
    # =====================================================
    if keys[pygame.K_o]:
        camera_zoom = max(MIN_ZOOM, camera_zoom / 1.03)
    if keys[pygame.K_i]:
        camera_zoom = min(MAX_ZOOM, camera_zoom * 1.03)

    # --- PRE-CALCULATE CAMERA CONSTANTS ---
    inv_zoom = 1.0 / max(camera_zoom, 0.001)
    view_w = (WIDTH * 0.5) * inv_zoom
    view_h = (HEIGHT * 0.5) * inv_zoom
    v_min_x, v_max_x = plane_x - view_w, plane_x + view_w
    v_min_y, v_max_y = plane_y - view_h, plane_y + view_h
    cam_ox = -plane_x * camera_zoom + WIDTH * 0.5
    cam_oy = -plane_y * camera_zoom + HEIGHT * 0.5

    fx_surface.fill((0, 0, 0, 0))
    screen.fill(BG)

    draw_environment(v_min_x, v_max_x, v_min_y, v_max_y, cam_ox, cam_oy)

    if not paused:

        # =================================================
        # GROUND RADAR LOGIC
        # =================================================
        prev_radar_sweep = radar_sweep
        radar_sweep = math.sin(pygame.time.get_ticks() * 0.003)
        if ground_radar_enabled:
            ground_radar_sweep = radar_sweep
            
            dx = plane_x - aaa_position[0]
            dy = plane_y - aaa_position[1]
            dist = math.hypot(dx, dy)
            
            if dist < FOX1_RADAR_RANGE:
                # Check for existing stationary radar missile specifically
                stationary_active = any(m["type"] == "STATIONARY_RADAR" for m in missiles)
                if not stationary_active and abs(ground_radar_sweep) < 0.25:
                    ground_radar_lock = min(1.0, ground_radar_lock + 0.05)
                
                if ground_radar_lock >= 1.0 and not stationary_active:
                    radar_launch_sound.play()
                    spawn_missile("STATIONARY_RADAR")
                    ground_radar_lock = 0.0
            else:
                ground_radar_lock = max(0.0, ground_radar_lock - 0.01)

        # =================================================
        # SONIC BOOM DETECTION
        # =================================================
        if aircraft_type == "JET":
            # Trigger sonic boom effect when crossing Mach 1 (approx 18.5 internal units)
            if prev_plane_speed < 18.5 and plane_speed >= 18.5:
                sonic_booms.append({
                    "x": plane_x,
                    "y": plane_y,
                    "angle": plane_angle,
                    "life": 25
                })
            prev_plane_speed = plane_speed

            # Wingtip Vortex Generation (Only above 400 knots and during turns)
            if 6.0 < plane_speed < 13.5 and abs(applied_turn) > 0.006:
                side_off = 39
                back_off = 10
                perp = plane_angle + math.pi/2
                for i, side in enumerate([-1, 1]):
                    wx = plane_x - math.cos(plane_angle) * back_off + math.cos(perp) * (side * side_off)
                    wy = plane_y - math.sin(plane_angle) * back_off + math.sin(perp) * (side * side_off)
                    
                    if last_vortex_pos[i] is not None:
                        vortex_points.append({
                            "x1": wx, "y1": wy,
                            "x2": last_vortex_pos[i][0], "y2": last_vortex_pos[i][1],
                            "life": 20
                        })
                    last_vortex_pos[i] = (wx, wy)
            else:
                last_vortex_pos = [None, None]


        # =================================================
        # FIRE GUN 
        # =================================================

        if keys[pygame.K_f]:
 
             fire_gun()

        # =================================================
        # MESSAGE TIMER
        # =================================================

        if result_timer > 0:

            result_timer -= 1

            if result_timer <= 0:
                result_text = ""

        # =================================================
        # JET CONTROLS
        # =================================================

        if aircraft_type == "JET":

            # Dynamic turn speed: 0 at speed 0, peaks early, then decreases as speed increases
            # This satisfies the requirement: "higher the speed the slower the aircraft turns"
            # while ensuring at 0 it cannot turn.
            actual_turn = turn_speed * (plane_speed / (1.0 + plane_speed**2 * 0.1))

            applied_turn = 0
            if keys[pygame.K_a] and not alt_held:
                applied_turn = -actual_turn

            if keys[pygame.K_d] and not alt_held:
                applied_turn = actual_turn
            plane_angle += applied_turn

            if keys[pygame.K_w] and not alt_held:
                # Check for 79% detent when accelerating
                if plane_throttle < 79 and plane_throttle + 1.0 >= 79:
                    plane_throttle = 79.0
                    detent_timer = 0
                    detent_target = 1 # Blocked going UP
                elif plane_throttle == 79 and detent_target == 1:
                    detent_timer += 1
                    if detent_timer >= 30: # 0.5 second hold to push into AB
                        plane_throttle = min(100.0, plane_throttle + 1.0)
                        detent_target = 0
                else:
                    plane_throttle = min(100.0, plane_throttle + 1.0)
                    detent_timer = 0
                    detent_target = 0
            elif keys[pygame.K_s] and not alt_held:
                plane_throttle = max(0.0, plane_throttle - 1.0)
                detent_timer = 0
                detent_target = 0
            else:
                detent_timer = 0

            # Smoother acceleration logic: Non-AB is now stronger, and AB provides a better boost
            if plane_throttle >= 80:
                # AB starts at 1.2x MIL peak and ends at 1.5x MIL peak
                # MIL peak = 0.0309375 * 1.25 = 0.038671875
                thrust = 0.04640625 + ((plane_throttle - 80) / 20.0) * 0.03
            else:
                thrust = (plane_throttle / 80.0) * 0.06

            # Drag increases with speed; Turn bleed only applies when the player is actually turning
            drag = (plane_speed / max_speed) * 0.08
            if plane_throttle == 0 and keys[pygame.K_s] and not alt_held:
                drag *= 2.0
                if plane_speed * 66.6 < 40:
                    plane_speed -= 0.015 # Extra braking force to reach 0 faster

            turn_bleed = abs(applied_turn) * 0.375

            plane_speed += thrust - drag - turn_bleed

            plane_speed = max(
                0,
                min(max_speed, plane_speed)
            )

            plane_x += (
                math.cos(plane_angle)
                * plane_speed
            )

            plane_y += (
                math.sin(plane_angle)
                * plane_speed
            )

        # =================================================
        # HELICOPTER CONTROLS
        # =================================================

        else:

            move_speed = 0.22

            if keys[pygame.K_q]:
                plane_angle -= 0.05

            if keys[pygame.K_e]:
                plane_angle += 0.05

            if keys[pygame.K_w] and not alt_held:

                heli_velocity_x += (
                    math.cos(plane_angle)
                    * move_speed
                )

                heli_velocity_y += (
                    math.sin(plane_angle)
                    * move_speed
                )

            if keys[pygame.K_s] and not alt_held:

                heli_velocity_x -= (
                    math.cos(plane_angle)
                    * move_speed * 0.7
                )

                heli_velocity_y -= (
                    math.sin(plane_angle)
                    * move_speed * 0.7
                )

            if keys[pygame.K_a] and not alt_held:

                heli_velocity_x += (
                    math.cos(
                        plane_angle - math.pi / 2
                    )
                    * move_speed
                )

                heli_velocity_y += (
                    math.sin(
                        plane_angle - math.pi / 2
                    )
                    * move_speed
                )

            if keys[pygame.K_d] and not alt_held:

                heli_velocity_x += (
                    math.cos(
                        plane_angle + math.pi / 2
                    )
                    * move_speed
                )

                heli_velocity_y += (
                    math.sin(
                        plane_angle + math.pi / 2
                    )
                    * move_speed
                )

            heli_velocity_x *= 0.94
            heli_velocity_y *= 0.94

            plane_x += heli_velocity_x
            plane_y += heli_velocity_y

        # =================================================
        # ENEMY AIRCRAFT UPDATE (AI or orbit)
        # =================================================

        if enemy_ai_active:
            dx_to_player = plane_x - enemy_x
            dy_to_player = plane_y - enemy_y
            dist_to_player = math.hypot(dx_to_player, dy_to_player)
            desired_enemy_heading = math.atan2(dy_to_player, dx_to_player)

            # threat detection
            threat_angle = None
            threat_is_bullet = False
            threat_vx = 0
            threat_vy = 0
            threat_x = 0
            threat_y = 0
            for missile in missiles:
                dx_m = missile["x"] - enemy_x
                dy_m = missile["y"] - enemy_y
                if math.hypot(dx_m, dy_m) < 4000:
                    to_enemy_angle = math.atan2(-dy_m, -dx_m)
                    if missile["type"] == "IR":
                        m_angle = math.atan2(missile["vy"], missile["vx"])
                    else:
                        m_angle = missile["angle"]
                    angle_diff = abs(to_enemy_angle - m_angle)
                    while angle_diff > math.pi:
                        angle_diff -= 2 * math.pi
                    if abs(angle_diff) < math.radians(60):
                        threat_angle = math.atan2(dy_m, dx_m)
                        break
            if threat_angle is None:
                dx_pe = enemy_x - plane_x
                dy_pe = enemy_y - plane_y
                dist_pe = math.hypot(dx_pe, dy_pe)
                if dist_pe < 3000 and len(bullets) > 0:
                    to_enemy_angle = math.atan2(dy_pe, dx_pe)
                    angle_diff = abs(to_enemy_angle - plane_angle)
                    while angle_diff > math.pi:
                        angle_diff -= 2 * math.pi
                    while angle_diff < -math.pi:
                        angle_diff += 2 * math.pi
                    if abs(angle_diff) < math.radians(30):
                        threat_angle = math.atan2(-dy_pe, -dx_pe)
                        threat_is_bullet = True
                        threat_vx = math.cos(plane_angle)
                        threat_vy = math.sin(plane_angle)
                        threat_x = plane_x
                        threat_y = plane_y

            if threat_angle is not None:
                enemy_state = "DODGE"
            elif dist_to_player < 6000:
                enemy_state = "ENGAGE"
            else:
                enemy_state = "ORBIT"

            # throttle per state
            if enemy_state == "ENGAGE" or enemy_state == "DODGE":
                target_throttle = 100.0
            else:
                target_throttle = 70.0
            if enemy_throttle < target_throttle:
                enemy_throttle = min(target_throttle, enemy_throttle + 3.0)
            elif enemy_throttle > target_throttle:
                enemy_throttle = max(target_throttle, enemy_throttle - 1.0)

            # desired turn direction
            if enemy_state == "ENGAGE":
                target_heading = desired_enemy_heading
            elif enemy_state == "DODGE":
                if threat_is_bullet:
                    cross = threat_vx * (enemy_y - threat_y) - threat_vy * (enemy_x - threat_x)
                    bullet_heading = math.atan2(threat_vy, threat_vx)
                    if cross > 0:
                        target_heading = bullet_heading + math.pi * 0.5
                    else:
                        target_heading = bullet_heading - math.pi * 0.5
                else:
                    target_heading = threat_angle + math.pi
            else:
                target_orbit_angle = math.atan2(enemy_y - enemy_cy, enemy_x - enemy_cx)
                enemy_orbit_angle = target_orbit_angle
                target_heading = target_orbit_angle + math.pi * 0.5

            heading_diff = target_heading - enemy_heading
            while heading_diff > math.pi:
                heading_diff -= 2 * math.pi
            while heading_diff < -math.pi:
                heading_diff += 2 * math.pi

            # physics model (same as player jet)
            actual_turn = enemy_turn_speed * (enemy_speed / (1.0 + enemy_speed**2 * 0.1))
            if heading_diff > 0:
                applied_enemy_turn = min(actual_turn, heading_diff)
            else:
                applied_enemy_turn = max(-actual_turn, heading_diff)
            enemy_heading += applied_enemy_turn

            if enemy_throttle >= 80:
                thrust = 0.04640625 + ((enemy_throttle - 80) / 20.0) * 0.03
            else:
                thrust = (enemy_throttle / 80.0) * 0.06
            drag = (enemy_speed / enemy_max_speed) * 0.08
            turn_bleed = abs(applied_enemy_turn) * 0.375
            enemy_speed += thrust - drag - turn_bleed
            enemy_speed = max(0, min(enemy_max_speed, enemy_speed))

            enemy_x += math.cos(enemy_heading) * enemy_speed
            enemy_y += math.sin(enemy_heading) * enemy_speed

            # orbit drift correction
            if enemy_state == "ORBIT":
                orbit_dx = (enemy_cx + math.cos(target_orbit_angle) * ENEMY_ORBIT_RADIUS) - enemy_x
                orbit_dy = (enemy_cy + math.sin(target_orbit_angle) * ENEMY_ORBIT_RADIUS) - enemy_y
                enemy_x += orbit_dx * 0.02
                enemy_y += orbit_dy * 0.02

            # fire when roughly aligned in engage
            if enemy_state == "ENGAGE" and abs(heading_diff) < 0.2:
                enemy_gun_timer -= 1
                if enemy_gun_timer <= 0:
                    spread = 0.03
                    gun_angle = enemy_heading + random.uniform(-spread, spread)
                    spawn_x = enemy_x + math.cos(gun_angle) * 35
                    spawn_y = enemy_y + math.sin(gun_angle) * 35
                    enemy_gun_timer = VULCAN_FIRE_RATE * 2
                    enemy_vx = math.cos(enemy_heading) * enemy_speed
                    enemy_vy = math.sin(enemy_heading) * enemy_speed
                    enemy_bullets.append({
                        "x": spawn_x,
                        "y": spawn_y,
                        "vx": math.cos(gun_angle) * VULCAN_SPEED * 0.8 + enemy_vx,
                        "vy": math.sin(gun_angle) * VULCAN_SPEED * 0.8 + enemy_vy,
                        "life": 40,
                        "init_speed": VULCAN_SPEED * 0.8,
                        "owner": "enemy"
                    })
        else:
            enemy_orbit_angle += 0.015
            enemy_x = enemy_cx + math.cos(enemy_orbit_angle) * ENEMY_ORBIT_RADIUS
            enemy_y = enemy_cy + math.sin(enemy_orbit_angle) * ENEMY_ORBIT_RADIUS
            enemy_heading = enemy_orbit_angle + math.pi * 0.5

        heat_x = (
            plane_x
            + math.cos(plane_angle)
            * heat_offset
        )

        heat_y = (
            plane_y
            + math.sin(plane_angle)
            * heat_offset
        )

        # =================================================
        # COUNTERMEASURES
        # =================================================

        for flare in flares:

            flare["life"] -= 1

            flare["x"] += flare["vx"]
            flare["y"] += flare["vy"]

        flares = [
            f for f in flares
            if f["life"] > 0
        ]

        for chaff in chaff_clouds:

            chaff["life"] -= 1

            chaff["x"] += chaff["vx"]
            chaff["y"] += chaff["vy"]

        chaff_clouds = [
            c for c in chaff_clouds
            if c["life"] > 0
        ]

        for smoke in smoke_clouds:

            smoke["life"] -= 1

            smoke["x"] += smoke["vx"]
            smoke["y"] += smoke["vy"]

        smoke_clouds = [
            s for s in smoke_clouds
            if s["life"] > 0
        ]

        # =================================================
        # BOFORS UPDATE
        # =================================================

        if aaa_enabled:

            aaa_timer += 1

            if aaa_timer >= AAA_FIRE_RATE:

                aaa_timer = 0

                fire_aaa()

        for bullet in aaa_bullets:

            bullet["life"] -= 1

            bullet["x"] += bullet["vx"]
            bullet["y"] += bullet["vy"]

            if bullet["life"] <= 0:

                bofors_flak.append({

                    "x": bullet["x"],
                    "y": bullet["y"],

                    "radius": random.randint(10, 18),
 
                    "life": random.randint(40, 65),

                    "smoke": random.uniform(
                        20,
                        40
                    )
                })

        aaa_bullets = [

            b for b in aaa_bullets

            if b["life"] > 0
        ]

        # =================================================
        # FLAK BURSTS
        # =================================================

        for flak in bofors_flak:

            flak["life"] -= 1

            flak["radius"] += 0.7

            flak["smoke"] += 0.35

        bofors_flak = [

            f for f in bofors_flak

            if f["life"] > 0
        ]

        # =================================================
        # MISSILE UPDATE
        # =================================================

        RESULT_DISPLAY_TIME = 100

        missiles_to_remove = []

        for missile in missiles:

            flare_targeted = False
            chaff_targeted = False
            smoke_blocked = False

            if missile["type"] == "IR":

                target_x = heat_x
                target_y = heat_y

                angle_to_player = math.atan2(plane_y - missile["y"], plane_x - missile["x"])

                # Check if the decoy flare still exists within IRCCM sanity gate
                if missile["is_decoyed"]:
                    decoy_still_visible = False
                    for flare in flares:
                        dx_f = flare["x"] - missile["decoy_pos"][0]
                        dy_f = flare["y"] - missile["decoy_pos"][1]
                        if dx_f * dx_f + dy_f * dy_f < 62500:  # 250^2
                            decoy_still_visible = True
                            missile["decoy_pos"] = [flare["x"], flare["y"]]
                            break
                    if decoy_still_visible:
                        # IRCCM: break decoy if flare drifts far from player's line of sight
                        angle_to_decoy = math.atan2(missile["decoy_pos"][1] - missile["y"], missile["decoy_pos"][0] - missile["x"])
                        angle_diff_dp = (angle_to_decoy - angle_to_player + math.pi) % (math.pi * 2) - math.pi
                        if abs(angle_diff_dp) > math.radians(IRCCM_BREAK_ANGLE):
                            missile["is_decoyed"] = False
                    else:
                        missile["is_decoyed"] = False

                if missile["is_decoyed"]:
                    target_x = missile["decoy_pos"][0]
                    target_y = missile["decoy_pos"][1]
                    flare_targeted = True
                # Flares only distract when afterburner is OFF (throttle < 80)
                elif plane_throttle < 80:
                    for flare in flares:
                        dx_f = missile["x"] - flare["x"]
                        dy_f = missile["y"] - flare["y"]
                        dist_sq = dx_f*dx_f + dy_f*dy_f

                        if dist_sq < 4000000: # 2000^2
                            flare_dist = math.sqrt(dist_sq)

                            # IRCCM: probability-based — angle smoothly reduces distraction chance
                            angle_to_flare = math.atan2(flare["y"] - missile["y"], flare["x"] - missile["x"])
                            angle_diff_fp = (angle_to_flare - angle_to_player + math.pi) % (math.pi * 2) - math.pi
                            angle_factor = max(0.0, 1.0 - abs(angle_diff_fp) / math.radians(IRCCM_MAX_ANGLE))
                            ratio = flare_dist / 2000
                            probability = (
                                missile["flare_bias"]
                                * (
                                    (1 - ratio) ** 2
                                )
                                * angle_factor
                            )

                            if random.random() < probability:
                                missile["is_decoyed"] = True
                                missile["decoy_pos"] = [flare["x"], flare["y"]]
                                target_x = flare["x"]
                                target_y = flare["y"]
                                flare_targeted = True

                # Lead pursuit for IR
                if not missile["is_decoyed"]:
                    if aircraft_type == "JET":
                        pvx = math.cos(plane_angle) * plane_speed
                        pvy = math.sin(plane_angle) * plane_speed
                    else:
                        pvx = heli_velocity_x
                        pvy = heli_velocity_y
                    dx_p = missile["x"] - plane_x
                    dy_p = missile["y"] - plane_y
                    dist_to_target = math.hypot(dx_p, dy_p)
                    pv_toward = (pvx * (-dx_p) + pvy * (-dy_p)) / (dist_to_target + 0.001)
                    closing = missile["speed"] - pv_toward
                    t_intercept = min(dist_to_target / max(closing, 1.0), 180)
                    target_lx = plane_x + pvx * t_intercept
                    target_ly = plane_y + pvy * t_intercept
                    # Clamp to forward hemisphere
                    vx = target_lx - missile["x"]
                    vy = target_ly - missile["y"]
                    dx = plane_x - missile["x"]
                    dy = plane_y - missile["y"]
                    if vx * dx + vy * dy < 0:
                        target_lx = plane_x
                        target_ly = plane_y
                    if "lead_x" not in missile:
                        missile["lead_x"] = target_lx
                        missile["lead_y"] = target_ly
                    else:
                        missile["lead_x"] += (target_lx - missile["lead_x"]) * 0.2
                        missile["lead_y"] += (target_ly - missile["lead_y"]) * 0.2
                else:
                    missile.pop("lead_x", None)
                    missile.pop("lead_y", None)

                missile_speed = IR_MISSILE_SPEED
                turn_rate = IR_TURN_RATE

            elif missile["type"] == "STATIONARY_RADAR":
                chaff_targeted = False
                target_x = missile["track_x"]
                target_y = missile["track_y"]
                source_x, source_y = aaa_position
                
                # Check if the decoy is still valid (chaff cloud still exists at track point)
                if missile["is_decoyed"]:
                    decoy_still_visible = False
                    for chaff in chaff_clouds:
                        dx_dc = chaff["x"] - missile["track_x"]
                        dy_dc = chaff["y"] - missile["track_y"]
                        if dx_dc * dx_dc + dy_dc * dy_dc < 62500: # 250^2 area
                            decoy_still_visible = True
                            # Update decoy position to follow the moving chaff
                            missile["decoy_pos"] = [chaff["x"], chaff["y"]]
                            break
                    if not decoy_still_visible:
                        missile["is_decoyed"] = False

                dx_t = plane_x - missile["track_x"]
                dy_t = plane_y - missile["track_y"]
                dist_to_track = math.sqrt(dx_t*dx_t + dy_t*dy_t)
                # Only re-acquire if not decoyed, or if player flies very close to the seeker's current track
                can_reacquire = not missile["is_decoyed"] or dist_to_track < 100

                dx_p = missile["x"] - plane_x
                dy_p = missile["y"] - plane_y
                dist_to_plane = math.sqrt(dx_p*dx_p + dy_p*dy_p)
                if dist_to_plane > 500: rwr_state = "SEARCH"
                elif dist_to_plane > 220: rwr_state = "TRACK"
                else: rwr_state = "MISSILE"

                # Radar cone detection from GROUND STATION
                angle_to_player = math.atan2(plane_y - source_y, plane_x - source_x)
                radar_angle = math.atan2(missile["track_y"] - source_y, missile["track_x"] - source_x)
                angle_diff = angle_to_player - radar_angle
                angle_diff = (angle_diff + math.pi) % (math.pi * 2) - math.pi

                # Stationary Radar only exists when tracking; use narrow 5-degree beam for detection
                player_in_cone = abs(angle_diff) <= math.radians(5.0 / 2)
                dx_gp = plane_x - source_x
                dy_gp = plane_y - source_y
                dist_ground_to_plane_sq = dx_gp*dx_gp + dy_gp*dy_gp
                dist_ground_to_plane = math.sqrt(dist_ground_to_plane_sq)
                radar_range_sq = FOX1_RADAR_RANGE ** 2
                
                if player_in_cone and dist_ground_to_plane_sq < radar_range_sq and can_reacquire:
                    missile["is_decoyed"] = False
                    if aircraft_type == "JET":
                        pvx, pvy = math.cos(plane_angle) * plane_speed, math.sin(plane_angle) * plane_speed
                    else:
                        pvx, pvy = heli_velocity_x, heli_velocity_y

                    # Calculate Radial Velocity (Closure Rate) relative to the ground station
                    # Flying perpendicular to the radar beam (notching) reduces this value to zero
                    dx_p, dy_p = plane_x - source_x, plane_y - source_y
                    radial_vel = abs((pvx * dx_p + pvy * dy_p) / dist_ground_to_plane) if dist_ground_to_plane > 0.001 else 0
                    
                    missile["lock_strength"] = min(1.0, radial_vel / 10) #notch sensitivity, lower is harder to notch
                    target_x, target_y = plane_x, plane_y

                    # Lead pursuit for SARH missile
                    mdx = missile["x"] - plane_x
                    mdy = missile["y"] - plane_y
                    dist_m_to_p = math.sqrt(mdx*mdx + mdy*mdy)
                    if dist_m_to_p > 0.001:
                        pv_toward = (pvx * (-mdx) + pvy * (-mdy)) / dist_m_to_p
                        closing = FOX1_MISSILE_SPEED - pv_toward
                        t_intercept = min(dist_m_to_p / max(closing, 1.0), 180)
                        target_lx = plane_x + pvx * t_intercept
                        target_ly = plane_y + pvy * t_intercept
                        vx = target_lx - missile["x"]
                        vy = target_ly - missile["y"]
                        dx = plane_x - missile["x"]
                        dy = plane_y - missile["y"]
                        if vx * dx + vy * dy < 0:
                            target_lx = plane_x
                            target_ly = plane_y
                        if "lead_x" not in missile:
                            missile["lead_x"] = target_lx
                            missile["lead_y"] = target_ly
                        else:
                            missile["lead_x"] += (target_lx - missile["lead_x"]) * 0.2
                            missile["lead_y"] += (target_ly - missile["lead_y"]) * 0.2

                else:
                    if missile["is_decoyed"]:
                        target_x, target_y = missile["decoy_pos"]
                    missile["lock_strength"] = 0.0
                    missile.pop("lead_x", None)
                    missile.pop("lead_y", None)

                # Seeker logic: check for chaff distraction within the beam
                if dist_ground_to_plane_sq < radar_range_sq:
                    for chaff in chaff_clouds:
                        # Radar cone check from ground source
                        dx_gc = chaff["x"] - source_x
                        dy_gc = chaff["y"] - source_y
                        if dx_gc*dx_gc + dy_gc*dy_gc > radar_range_sq:
                            continue
                            
                        angle_to_chaff = math.atan2(chaff["y"] - source_y, chaff["x"] - source_x)
                        angle_diff_chaff = angle_to_chaff - radar_angle
                        angle_diff_chaff = (angle_diff_chaff + math.pi) % (math.pi * 2) - math.pi

                        # Only see chaff within the narrow tracking beam
                        if abs(angle_diff_chaff) <= math.radians(5.0 / 2):
                            dx_cp = chaff["x"] - plane_x
                            dy_cp = chaff["y"] - plane_y
                            dist_cp_sq = dx_cp*dx_cp + dy_cp*dy_cp
                            if dist_cp_sq < 722500: # 850^2
                                dist_chaff_to_plane = math.sqrt(dist_cp_sq)
                                probability = missile["chaff_bias"] * ((1.0 - missile["lock_strength"])**2) * (1.0 - dist_chaff_to_plane / 850)
                                if random.random() < probability:
                                    missile["is_decoyed"] = True
                                    missile["decoy_pos"] = [chaff["x"], chaff["y"]]
                                    target_x, target_y = chaff["x"], chaff["y"]
                                    break

                if missile["is_decoyed"]:
                    chaff_targeted = True

                missile_speed = FOX1_MISSILE_SPEED
                turn_rate = FOX1_TURN_RATE

            elif missile["type"] == "RADAR":

                chaff_targeted = False

                target_x = missile["track_x"] # Default to current track if player not in cone
                target_y = missile["track_y"]

                dx_p = missile["x"] - plane_x
                dy_p = missile["y"] - plane_y
                dist_p_sq = dx_p*dx_p + dy_p*dy_p
                distance_to_plane = math.sqrt(dist_p_sq)
                
                if distance_to_plane > 500:
                    rwr_state = "SEARCH"

                elif distance_to_plane > 220:
                    rwr_state = "TRACK"

                else:
                    rwr_state = "MISSILE"

                # Check if the decoy is still valid (chaff cloud still exists at track point)
                if missile["is_decoyed"]:
                    decoy_still_visible = False
                    for chaff in chaff_clouds:
                        dx_dc = chaff["x"] - missile["track_x"]
                        dy_dc = chaff["y"] - missile["track_y"]
                        if dx_dc * dx_dc + dy_dc * dy_dc < 62500: # 250^2 area
                            decoy_still_visible = True
                            # Update decoy position to follow the moving chaff
                            missile["decoy_pos"] = [chaff["x"], chaff["y"]]
                            break
                    if not decoy_still_visible:
                        missile["is_decoyed"] = False
                        missile["lock_broken"] = True

                # Passive acquisition: only re-acquire plane if not decoyed or plane is near current track
                dx_t = plane_x - missile["track_x"]
                dy_t = plane_y - missile["track_y"]
                dist_to_track = math.sqrt(dx_t*dx_t + dy_t*dy_t)

                # Radar cone detection
                angle_to_player = math.atan2(plane_y - missile["y"], plane_x - missile["x"])
                angle_diff = (angle_to_player - missile["angle"] + math.pi) % (math.pi * 2) - math.pi

                # Seeker gimbal: physical seeker head tracks within gimbal limits
                gimbal_limit = math.radians(FOX3_GIMBAL_ANGLE / 2)
                if missile.get("lock_broken"):
                    seeker_angle = missile["angle"]  # Seeker locked forward when lock broken
                else:
                    seeker_angle = missile["angle"] + max(-gimbal_limit, min(gimbal_limit, angle_diff))

                # Active Radar seeker: Acquire in wide cone, track/re-acquire in narrow beam
                player_in_acq_cone = abs(angle_diff) <= math.radians(FOX3_CONE_ANGLE / 2)
                angle_to_player_from_seeker = (angle_to_player - seeker_angle + math.pi) % (math.pi * 2) - math.pi
                player_in_track_fov = abs(angle_to_player_from_seeker) <= math.radians(FOX3_TRACK_FOV / 2)
                player_in_gimbal = abs(angle_diff) <= gimbal_limit
                can_see_player = player_in_gimbal and (player_in_track_fov if (missile["is_decoyed"] or missile.get("lock_broken")) else player_in_acq_cone)
                can_reacquire = (not missile["is_decoyed"] and not missile.get("lock_broken")) or dist_to_track < 300 or (missile.get("lock_broken") and player_in_track_fov)
                
                # Compute target velocity for lead pursuit (unconditional for smooth updates)
                if aircraft_type == "JET":
                    pvx, pvy = math.cos(plane_angle) * plane_speed, math.sin(plane_angle) * plane_speed
                else:
                    pvx, pvy = heli_velocity_x, heli_velocity_y
                
                if can_see_player and dist_p_sq < RADAR_CONE_RANGE ** 2 and can_reacquire: # detection range
                    missile["is_decoyed"] = False
                    missile["lock_broken"] = False
                    # Calculate lock strength based on relative velocity (Closure Rate)
                    mvx, mvy = math.cos(missile["angle"]) * missile["speed"], math.sin(missile["angle"]) * missile["speed"]
                    
                    rel_vel = math.hypot(pvx - mvx, pvy - mvy)
                    # 12.5 normalization factor makes the seeker twice as sensitive to closure rate
                    missile["lock_strength"] = min(1.0, rel_vel / 35)
                    
                    target_x = plane_x
                    target_y = plane_y
                else:
                    missile["lock_strength"] = 0.0
                    missile.pop("lead_x", None)
                    missile.pop("lead_y", None)
                    if missile["is_decoyed"] or missile.get("lock_broken"):
                        target_x, target_y = missile["decoy_pos"]
                
                # Lead pursuit: time-to-intercept based on closing speed (only when tracking player)
                if not missile.get("is_decoyed") and not missile.get("lock_broken"):
                    dist_to_target = math.sqrt(dist_p_sq)
                    # Plane velocity component toward/away from missile
                    pv_toward = (pvx * (-dx_p) + pvy * (-dy_p)) / (dist_to_target + 0.001)
                    closing = FOX3_MISSILE_SPEED - pv_toward  # positive when closing
                    t_intercept = min(dist_to_target / max(closing, 1.0), 180)
                    # Smooth gimbal margin: continuous function with no hard branch
                    angle_ratio = abs(angle_diff) / gimbal_limit
                    gimbal_margin = max(0.0, 1.0 - (angle_ratio ** 6))
                    lead_factor = t_intercept * gimbal_margin
                    # Target lead position based on current plane position (always smooth)
                    target_lx = plane_x + pvx * lead_factor
                    target_ly = plane_y + pvy * lead_factor
                    # Clamp lead to forward hemisphere so missile never aims behind itself
                    vx = target_lx - missile["x"]
                    vy = target_ly - missile["y"]
                    dx = plane_x - missile["x"]
                    dy = plane_y - missile["y"]
                    if vx * dx + vy * dy < 0:
                        target_lx = plane_x
                        target_ly = plane_y
                    # Smooth the lead via exponential filter to prevent snap/oscillation
                    if "lead_x" not in missile:
                        missile["lead_x"] = target_lx
                        missile["lead_y"] = target_ly
                    else:
                        lead_filter = 0.2
                        missile["lead_x"] += (target_lx - missile["lead_x"]) * lead_filter
                        missile["lead_y"] += (target_ly - missile["lead_y"]) * lead_filter

                # Seeker logic: check for chaff distraction
                for chaff in chaff_clouds:
                    dx_mc = chaff["x"] - missile["x"]
                    dy_mc = chaff["y"] - missile["y"]
                    dist_mc_sq = dx_mc*dx_mc + dy_mc*dy_mc
                    if dist_mc_sq > RADAR_CONE_RANGE ** 2: # detection range
                        continue
                        
                    angle_to_chaff = math.atan2(chaff["y"] - missile["y"], chaff["x"] - missile["x"])
                    angle_diff_chaff = (angle_to_chaff - missile["angle"] + math.pi) % (math.pi * 2) - math.pi

                    # Seeker distracted only by chaff within the narrow forward track beam
                    if abs(angle_diff_chaff) <= math.radians(FOX3_TRACK_FOV / 2):
                        dx_cp = chaff["x"] - plane_x
                        dy_cp = chaff["y"] - plane_y
                        dist_cp_sq = dx_cp*dx_cp + dy_cp*dy_cp
                        if dist_cp_sq < 722500: # 850^2
                            dist_chaff_to_plane = math.sqrt(dist_cp_sq)
                            probability = (
                                missile["chaff_bias"]
                                * ((1.0 - missile["lock_strength"])**2)
                                * (1.0 - dist_chaff_to_plane / 850)
                            )
                            if random.random() < probability:
                                missile["is_decoyed"] = True
                                missile["decoy_pos"] = [chaff["x"], chaff["y"]]
                                target_x, target_y = chaff["x"], chaff["y"]
                                break
                
                if missile["is_decoyed"]:
                    chaff_targeted = True

                missile_speed = FOX3_MISSILE_SPEED
                turn_rate = FOX3_TURN_RATE

            else:

                dx_p = missile["x"] - plane_x
                dy_p = missile["y"] - plane_y
                distance_to_plane = math.sqrt(dx_p*dx_p + dy_p*dy_p)
                
                if distance_to_plane < 450:
                    lwr_warning = True

                target_x = plane_x
                target_y = plane_y

                # Optimized smoke check
                for smoke in smoke_clouds[::2]: # Check half the smoke for performance

                    dx_s = missile["x"] - smoke["x"]
                    dy_s = missile["y"] - smoke["y"]
                    radius_sum = smoke["radius"] + 40
                    # Use squared distance to avoid expensive square root (math.hypot)
                    if dx_s*dx_s + dy_s*dy_s < radius_sum * radius_sum:

                        smoke_blocked = True
                        target_x = smoke["x"]
                        target_y = smoke["y"]

                        break

                missile_speed = OPTICAL_MISSILE_SPEED
                turn_rate = OPTICAL_TURN_RATE

            track_response = 1.0
            missile["track_x"] += (
                target_x
                - missile["track_x"]
            ) * track_response

            missile["track_y"] += (
                target_y
                - missile["track_y"]
            ) * track_response

            # Use per-missile speed (affected by fuel and turn bleed)
            missile_speed = missile["speed"]
            # Scale turn rate by speed ratio (slower missile = less agile)
            speed_ratio = missile["speed"] / missile["max_speed"]
            turn_rate *= speed_ratio

            # Lead pursuit: steer toward predicted intercept point
            if missile["type"] in ("RADAR", "STATIONARY_RADAR", "IR") and "lead_x" in missile and not missile["is_decoyed"]:
                dx = missile["lead_x"] - missile["x"]
                dy = missile["lead_y"] - missile["y"]
            else:
                dx = (
                    missile["track_x"]
                    - missile["x"]
                )

                dy = (
                    missile["track_y"]
                    - missile["y"]
                )

            desired_angle = math.atan2(
                dy,
                dx
            )

            angle_diff = (
                desired_angle
                - missile["angle"]
            )

            while angle_diff > math.pi:
                angle_diff -= math.pi * 2

            while angle_diff < -math.pi:
                angle_diff += math.pi * 2

            if angle_diff > turn_rate:
                angle_diff = turn_rate

            if angle_diff < -turn_rate:
                angle_diff = -turn_rate

            missile["angle"] += angle_diff

            if missile["type"] == "IR":
                missile["vx"] = (missile["vx"] + IR_THRUST * math.cos(missile["angle"])) * IR_DRAG
                missile["vy"] = (missile["vy"] + IR_THRUST * math.sin(missile["angle"])) * IR_DRAG
                missile["x"] += missile["vx"]
                missile["y"] += missile["vy"]
                missile["speed"] = math.hypot(missile["vx"], missile["vy"])
            else:
                missile["x"] += math.cos(missile["angle"]) * missile_speed
                missile["y"] += math.sin(missile["angle"]) * missile_speed

            # Fuel burn: base burn + extra for turning
            fuel_burn = 1.0 + abs(angle_diff) * 10
            missile["fuel"] = max(0, missile["fuel"] - fuel_burn)

            if missile["fuel"] > 0:
                # Motor compensates for turn drag — no speed bleed while burning
                pass
            else:
                # Coasting: speed bleed from turning and gradual drag
                bleed = abs(angle_diff) * missile_speed * 0.3
                missile["speed"] = max(missile_speed - bleed, missile_speed * 0.95)
                missile["speed"] = max(missile["speed"] * 0.99975, 0.5)

            missile["trail"].append(
                (
                    missile["x"],
                    missile["y"]
                )
            )

            if len(missile["trail"]) > 100:
                missile["trail"].pop(0)

            # Self-destruct: no fuel and distance to tracked target keeps increasing (falling behind)
            if missile["fuel"] <= 0:
                if missile.get("is_decoyed"):
                    tx, ty = missile["decoy_pos"]
                else:
                    tx, ty = plane_x, plane_y
                m_dx = missile["x"] - tx
                m_dy = missile["y"] - ty
                cur_dist = math.hypot(m_dx, m_dy)
                last_dist = missile.get("last_dist", cur_dist)
                missile["last_dist"] = cur_dist
                if cur_dist > last_dist:
                    missile["falling_behind"] = missile.get("falling_behind", 0) + 1
                else:
                    missile["falling_behind"] = 0
                # Also require missile to be 2x slower than the target
                if missile.get("is_decoyed"):
                    too_slow = True
                    if cur_dist < 100:
                        create_explosion(missile["x"], missile["y"], GREY, radius=8)
                        missiles_to_remove.append(missile)
                        continue
                else:
                    if aircraft_type == "JET":
                        target_spd = plane_speed
                    else:
                        target_spd = math.hypot(heli_velocity_x, heli_velocity_y)
                    too_slow = missile_speed < target_spd * 0.5
                if missile["falling_behind"] >= 30 and cur_dist > 45 and too_slow:
                    create_explosion(missile["x"], missile["y"], GREY, radius=8)
                    missiles_to_remove.append(missile)
                    continue

            distance = math.hypot(missile["track_x"] - missile["x"], missile["track_y"] - missile["y"])

            # CPA proxy fuse: detonate when distance starts increasing after CPA within trigger range
            prev_dist = missile.get("cpa_last_dist", float('inf'))
            if distance > prev_dist and prev_dist < 180:

                countermeasure_hit = False

                if (
                    missile["type"] == "IR"
                    and flare_targeted
                ):

                    create_explosion(
                        missile["x"],
                        missile["y"],
                        YELLOW,
                        radius=15
                    )

                    result_text = (
                        "IR MISSILE DECOYED"
                    )

                    result_timer = RESULT_DISPLAY_TIME

                    countermeasure_hit = True

                elif (
                    "RADAR" in missile["type"]
                    and chaff_targeted
                ):

                    create_explosion(
                        missile["x"],
                        missile["y"],
                        CYAN,
                        radius=15
                    )

                    result_text = (
                        "RADAR MISSILE DECOYED"
                    )

                    result_timer = RESULT_DISPLAY_TIME

                    countermeasure_hit = True

                elif (
                    missile["type"] == "OPTICAL"
                    and smoke_blocked
                ):

                    create_explosion(
                        missile["x"],
                        missile["y"],
                        GREY
                    )

                    result_text = (
                        "OPTICAL LOST LOCK"
                    )

                    result_timer = RESULT_DISPLAY_TIME

                    countermeasure_hit = True

                if not countermeasure_hit:
                    lethal_radius = 150
                    dx_p = missile["x"] - plane_x
                    dy_p = missile["y"] - plane_y
                    # Optimized proximity check using squared distance
                    if (dx_p*dx_p + dy_p*dy_p) < (lethal_radius * lethal_radius):
                        # Player caught in proximity fuse
                        create_explosion(missile["x"], missile["y"], RED, radius=int(lethal_radius))
                        create_explosion(plane_x, plane_y, RED, radius=10)
                        
                        result_text = f"{missile['type']} MISSILE HIT"
                        result_timer = RESULT_DISPLAY_TIME
                        reset_plane()
                    else:
                        # Missile detonated safely (Visualizing the miss)
                        create_explosion(
                            missile["x"], 
                            missile["y"], 
                            GREY, 
                            radius=int(lethal_radius)
                        )

                missiles_to_remove.append(
                    missile
                )

            missile["cpa_last_dist"] = distance

        for missile in missiles_to_remove:

            if missile in missiles:
                missiles.remove(missile)

        # =================================================
        # FLAK DAMAGE
        # =================================================

        for flak in bofors_flak:

            dist = math.hypot(

                flak["x"] - plane_x,

                flak["y"] - plane_y
            )

            if dist < flak["radius"] + 18:

                create_explosion(
                    plane_x,
                    plane_y,
                    ORANGE,
                    radius=20
                )

                result_text = "40MM FLAK HIT"

                result_timer = 300

                reset_plane()

                bofors_flak.remove(flak)

                break

        # =================================================
        # BULLETS
        # =================================================

        gun_fire_timer = max(0, gun_fire_timer - 1)

        bullets_to_remove = []

        for bullet in bullets:

            bullet["x"] += bullet["vx"]
            bullet["y"] += bullet["vy"]

            bullet["vx"] *= 0.985
            bullet["vy"] *= 0.985

            bullet["life"] -= 1

            

            if bullet["life"] <= 0:

                 bullets_to_remove.append(
                     bullet
                 )

        for bullet in bullets_to_remove:

            if bullet in bullets:
                bullets.remove(bullet)

        # player bullets hit enemy
        for bullet in bullets[:]:
            dx_be = bullet["x"] - enemy_x
            dy_be = bullet["y"] - enemy_y
            if (dx_be*dx_be + dy_be*dy_be) < 3600:
                bullets.remove(bullet)
                enemy_health -= 10
                damage_pct = 1.0 - (enemy_health / enemy_max_health)
                explosion_radius = int(10 + damage_pct * 80)
                result_text = "HIT"
                result_timer = RESULT_DISPLAY_TIME
                create_explosion(enemy_x, enemy_y, RED, radius=explosion_radius)
                if enemy_health <= 0:
                    create_explosion(enemy_x, enemy_y, RED, radius=80)
                    enemy_health = enemy_max_health
                    enemy_speed = 0.0
                    enemy_throttle = 0.0
                    enemy_heading = math.pi * 0.5
                    enemy_x = enemy_cx + ENEMY_ORBIT_RADIUS
                    enemy_y = enemy_cy

        # enemy bullets update
        for b in enemy_bullets:
            b["x"] += b["vx"]
            b["y"] += b["vy"]
            b["life"] -= 1

        # player hit by enemy bullets
        for b in enemy_bullets[:]:
            dx_ep = b["x"] - plane_x
            dy_ep = b["y"] - plane_y
            if (dx_ep*dx_ep + dy_ep*dy_ep) < 400:
                enemy_bullets.remove(b)
                create_explosion(plane_x, plane_y, RED, radius=10)
                result_text = "ENEMY GUN HIT"
                result_timer = RESULT_DISPLAY_TIME
                reset_plane()

        enemy_bullets = [b for b in enemy_bullets if b["life"] > 0]

        # =================================================
        # SONIC BOOMS
        # =================================================
        for sb in sonic_booms:
            sb["life"] -= 1
            # Attach the boom effect to the plane's current coordinates
            sb["x"] = plane_x
            sb["y"] = plane_y
            sb["angle"] = plane_angle
        sonic_booms = [sb for sb in sonic_booms if sb["life"] > 0]

        for vp in vortex_points:
            vp["life"] -= 1
        vortex_points = [vp for vp in vortex_points if vp["life"] > 0]

        # =================================================
        # EXPLOSIONS
        # =================================================

        for explosion in explosions:

            explosion["life"] -= 1

        explosions = [
            e for e in explosions
            if e["life"] > 0
        ]

    # =====================================================
    # DRAW TRAILS
    # =====================================================

    for missile in missiles:

        trail_color = ORANGE

        if "RADAR" in missile["type"]:
            trail_color = LIGHT_BLUE

        if missile["type"] == "OPTICAL":
            trail_color = PURPLE

        # Optimization: Only process trails if the missile or its recent path might be visible
        if len(missile["trail"]) > 1 and (v_min_x - 1000 < missile["x"] < v_max_x + 1000 and 
                                         v_min_y - 1000 < missile["y"] < v_max_y + 1000):
            # Sub-sample trails based on zoom level to drastically reduce loop overhead
            t_step = 1 if camera_zoom > 1.2 else (2 if camera_zoom > 0.6 else 4)
            screen_pts = [
                (int(p[0] * camera_zoom + cam_ox), int(p[1] * camera_zoom + cam_oy))
                for p in missile["trail"][::t_step]
            ]
            if len(screen_pts) > 1:
                pygame.draw.lines(screen, trail_color, False, screen_pts, 2)

    # =====================================================
    # DRAW EFFECTS
    # =====================================================

    effect_scale = max(0.6, camera_zoom)
    # Pre-calculated bounds for effect culling
    m_v_min_x, m_v_max_x = v_min_x - 100, v_max_x + 100
    m_v_min_y, m_v_max_y = v_min_y - 100, v_max_y + 100

    for flare in flares:
        if not (m_v_min_x < flare["x"] < m_v_max_x and m_v_min_y < flare["y"] < m_v_max_y):
            continue
        sx = int(flare["x"] * camera_zoom + cam_ox)
        sy = int(flare["y"] * camera_zoom + cam_oy)

        pygame.draw.circle(
            screen,
            YELLOW,
            (sx, sy),
            max(1, int(4 * effect_scale))
        )

    for chaff in chaff_clouds:
        if not (m_v_min_x < chaff["x"] < m_v_max_x and m_v_min_y < chaff["y"] < m_v_max_y):
            continue
        sx = int(chaff["x"] * camera_zoom + cam_ox)
        sy = int(chaff["y"] * camera_zoom + cam_oy)

        pygame.draw.circle(
            screen,
            LIGHT_BLUE,
            (sx, sy),
            max(1, int(3 * effect_scale))
        )

    for smoke in smoke_clouds:
        if not (m_v_min_x - 50 < smoke["x"] < m_v_max_x + 50 and m_v_min_y - 50 < smoke["y"] < m_v_max_y + 50):
            continue
        sx = int(smoke["x"] * camera_zoom + cam_ox)
        sy = int(smoke["y"] * camera_zoom + cam_oy)

        pygame.draw.circle(
            screen,
            GREY,
            (sx, sy),
            max(1, int(smoke["radius"] * effect_scale))
        )

    # =====================================================
    # DRAW VORTICES
    # =====================================================
    if vortex_points:
        for vp in vortex_points:
            alpha = int((vp["life"] / 20) * 110)
            p1 = world_to_screen(vp["x1"], vp["y1"])
            p2 = world_to_screen(vp["x2"], vp["y2"])
            pygame.draw.line(fx_surface, (220, 220, 220, alpha), p1, p2, max(1, int(2 * camera_zoom)))

    # =====================================================
    # DRAW SONIC BOOMS
    # =====================================================
    for sb in sonic_booms:
        alpha = int((sb["life"] / 25) * 120)
        
        # World space dimensions for the vapor cone
        dist_back = 10 # Moved closer to middle (was 47)
        spread = 60    # Width of the cone base
        length = 40    # Depth of the cone
        
        # Vertex of the cone (at the tail)
        tail_x = sb["x"] - math.cos(sb["angle"]) * dist_back
        tail_y = sb["y"] - math.sin(sb["angle"]) * dist_back
        
        # Base center point
        bc_x = tail_x - math.cos(sb["angle"]) * length
        bc_y = tail_y - math.sin(sb["angle"]) * length
        
        # Base edge points perpendicular to flight path
        perp = sb["angle"] + math.pi/2
        p1_x = bc_x - math.cos(perp) * spread
        p1_y = bc_y - math.sin(perp) * spread
        p2_x = bc_x + math.cos(perp) * spread
        p2_y = bc_y + math.sin(perp) * spread
        
        pts = [world_to_screen(tail_x, tail_y), world_to_screen(p1_x, p1_y), world_to_screen(p2_x, p2_y)]
        pygame.draw.polygon(fx_surface, (200, 200, 200, alpha), pts)

    for explosion in explosions:

        sx, sy = world_to_screen(
            explosion["x"],
            explosion["y"]
        )

        pygame.draw.circle(
            screen,
            ORANGE,
            (sx, sy),
            int(explosion["radius"] * camera_zoom)
        )

    # =====================================================
    # DRAW TRACK DOTS
    # =====================================================

    for missile in missiles:
        line_color = GREY
        dot_color = GREEN

        if missile["type"] == "IR":
            line_color = RED
            dot_color = ORANGE

        if "RADAR" in missile["type"]:
            line_color = LIGHT_BLUE
            dot_color = CYAN

        if missile["type"] == "OPTICAL":
            line_color = PURPLE
            dot_color = PURPLE

        msx, msy = int(missile["x"] * camera_zoom + cam_ox), int(missile["y"] * camera_zoom + cam_oy)
        mtx, mty = int(missile["track_x"] * camera_zoom + cam_ox), int(missile["track_y"] * camera_zoom + cam_oy)

        pygame.draw.line(
            screen,
            line_color,
            (msx, msy),
            (mtx, mty),
            1
        )

        sx, sy = mtx, mty

        pygame.draw.circle(
            screen,
            dot_color,
            (sx, sy),
            6
        )

        # Draw yellow lead dot for missiles in lead pursuit
        if missile["type"] in ("RADAR", "STATIONARY_RADAR", "IR") and "lead_x" in missile and not missile["is_decoyed"]:
            lx = int(missile["lead_x"] * camera_zoom + cam_ox)
            ly = int(missile["lead_y"] * camera_zoom + cam_oy)
            pygame.draw.circle(screen, YELLOW, (lx, ly), 4)

        # Draw CPA detection radius (180 units)
        pygame.draw.circle(
            fx_surface,
            (255, 255, 100, 60),
            (msx, msy),
            int(180 * camera_zoom)
        )

    # =====================================================
    # DRAW BOFORS
    # =====================================================

    if aaa_enabled:
        draw_aaa()

    for bullet in aaa_bullets:

        sx, sy = world_to_screen(
            bullet["x"],
            bullet["y"]
        )

        pygame.draw.circle(
            screen,
            ORANGE,
            (sx, sy),
            4
        )

    for flak in bofors_flak:
        alpha = max(0, min(180, flak["life"] * 3))
        sx, sy = world_to_screen(flak["x"], flak["y"])
        # Optimization: Draw flak smoke directly to screen or fx_surface without per-frame allocation
        pygame.draw.circle(fx_surface, (45, 45, 45, alpha), (sx, sy), int(flak["smoke"] * camera_zoom))
    # =====================================================
    # DRAW BULLETS
    # =====================================================

    for bullet in bullets:
        spd = math.hypot(bullet["vx"], bullet["vy"])
        ratio = min(1.0, spd / bullet["init_speed"])
        # YELLOW -> ORANGE -> RED
        r = 255
        g = int(100 + 100 * ratio)
        b = 0
        bullet_color = (r, g, b)
    
        pygame.draw.line(
            screen,
            bullet_color,
            world_to_screen(bullet["x"], bullet["y"]),
            world_to_screen(
                bullet["x"] - bullet["vx"] * 2,
                bullet["y"] - bullet["vy"] * 2
            ),
            3
        )

    for b in enemy_bullets:
        spd = math.hypot(b["vx"], b["vy"])
        ratio = min(1.0, spd / b["init_speed"])
        r = 255
        g = int(100 + 100 * ratio)
        b_color = (r, g, 0)
        pygame.draw.line(
            screen,
            b_color,
            world_to_screen(b["x"], b["y"]),
            world_to_screen(
                b["x"] - b["vx"] * 2,
                b["y"] - b["vy"] * 2
            ),
            3
        )

    # =====================================================
    # THREAT DETECTION CONES (H to toggle)
    # =====================================================
    if show_controls and enemy_ai_active:
        cone_length = 40
        dx_pe = enemy_x - plane_x
        dy_pe = enemy_y - plane_y
        dist_pe = math.hypot(dx_pe, dy_pe)
        if dist_pe < 3000:
            psx, psy = world_to_screen(plane_x, plane_y)
            to_enemy_angle = math.atan2(dy_pe, dx_pe)
            angle_diff = abs(to_enemy_angle - plane_angle)
            while angle_diff > math.pi:
                angle_diff -= 2 * math.pi
            detected = abs(angle_diff) < math.radians(30) and len(bullets) > 0
            color = GREEN if detected else RED
            for sign in (-1, 1):
                cone_ang = plane_angle + sign * math.radians(30)
                end_x = psx + math.cos(cone_ang) * cone_length * 5
                end_y = psy + math.sin(cone_ang) * cone_length * 5
                pygame.draw.line(screen, color, (psx, psy), (end_x, end_y), 1)

        for missile in missiles:
            dx_m = missile["x"] - enemy_x
            dy_m = missile["y"] - enemy_y
            dist_m = math.hypot(dx_m, dy_m)
            if dist_m < 4000:
                mx_s, my_s = world_to_screen(missile["x"], missile["y"])
                to_enemy_angle = math.atan2(-dy_m, -dx_m)
                if missile["type"] == "IR":
                    m_angle = math.atan2(missile["vy"], missile["vx"])
                else:
                    m_angle = missile["angle"]
                angle_diff = abs(to_enemy_angle - m_angle)
                while angle_diff > math.pi:
                    angle_diff -= 2 * math.pi
                detected = abs(angle_diff) < math.radians(60)
                color = GREEN if detected else RED
                for sign in (-1, 1):
                    cone_ang = m_angle + sign * math.radians(60)
                    end_x = mx_s + math.cos(cone_ang) * cone_length
                    end_y = my_s + math.sin(cone_ang) * cone_length
                    pygame.draw.line(screen, color, (mx_s, my_s), (end_x, end_y), 1)

    # =====================================================
    # DRAW AIRCRAFT + MISSILES
    # =====================================================

    jet_turn = applied_turn if aircraft_type == "JET" else 0
    draw_plane(plane_x, plane_y, plane_angle, jet_turn if not paused else 0)

    # Player radar cone
    if radar_enabled:
        cone_range = 4000
        half_angle = math.radians(45)
        psx, psy = world_to_screen(plane_x, plane_y)
        pts = [(psx, psy)]
        segments = 12
        for i in range(segments + 1):
            ang = plane_angle - half_angle + (half_angle * 2 * (i / segments))
            px = psx + math.cos(ang) * cone_range * camera_zoom
            py = psy + math.sin(ang) * cone_range * camera_zoom
            pts.append((px, py))
        pygame.draw.polygon(screen, GREEN, pts, 2)

        sweep_ang = plane_angle + radar_sweep * half_angle
        lx = psx + math.cos(sweep_ang) * cone_range * camera_zoom
        ly = psy + math.sin(sweep_ang) * cone_range * camera_zoom
        pygame.draw.line(screen, (0, 255, 120), (psx, psy), (lx, ly), 2)

    # Draw enemy aircraft
    enemy_zoom = MIN_ZOOM * 1.5 if camera_zoom <= MIN_ZOOM * 1.01 else camera_zoom
    if enemy_image is not None:
        esx, esy = world_to_screen(enemy_x, enemy_y)
        sprite = pygame.transform.scale(
            enemy_image,
            (max(1, int(enemy_image.get_width() * enemy_zoom)),
             max(1, int(enemy_image.get_height() * enemy_zoom)))
        )
        rotated = pygame.transform.rotate(sprite, -math.degrees(enemy_heading))
        rect = rotated.get_rect(center=(esx, esy))
        screen.blit(rotated, rect)
    else:
        esx, esy = world_to_screen(enemy_x, enemy_y)
        pygame.draw.circle(screen, RED, (esx, esy), 18)

    # Speed UI underneath player (numbers only)
    speed_sx, speed_sy = world_to_screen(plane_x, plane_y)
    current_spd = plane_speed if aircraft_type == "JET" else math.hypot(heli_velocity_x, heli_velocity_y)
    speed_txt = font.render(str(int(current_spd * 66.6)), True, GREEN)
    screen.blit(speed_txt, (speed_sx - speed_txt.get_width() // 2, speed_sy + int(60 * camera_zoom + 15))) #45

    for missile in missiles:
        # Visibility check for missile body
        if (v_min_x - 50 < missile["x"] < v_max_x + 50 and 
            v_min_y - 50 < missile["y"] < v_max_y + 50):
            msx, msy = int(missile["x"] * camera_zoom + cam_ox), int(missile["y"] * camera_zoom + cam_oy)
            draw_missile(
                msx,
                msy,
                missile["angle"],
                missile["type"]
            )

            # Fuel bar under missile
            bar_w = 30
            bar_h = 4
            bar_x = msx - bar_w // 2
            bar_y = msy + 14
            fuel_ratio = missile["fuel"] / missile["max_fuel"]
            fuel_color = (int(255 * (1 - fuel_ratio)), int(255 * fuel_ratio), 0)
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, fuel_color, (bar_x, bar_y, int(bar_w * fuel_ratio), bar_h))

            # Speed text above missile
            speed_kt = int(missile["speed"] * 66.6)
            spd_txt = font_small.render(str(speed_kt), True, (200, 220, 255))
            screen.blit(spd_txt, (msx - spd_txt.get_width() // 2, msy - 22))

    # =====================================================
    # DRAW RADAR MISSILE SEEKER CONES
    # =====================================================

    # Check if a ground-based radar missile is already in the air
    stationary_radar_active = any(m["type"] == "STATIONARY_RADAR" for m in missiles)
    
    v_cone_range = RADAR_CONE_RANGE

    if ground_radar_enabled and not stationary_radar_active:
        ax, ay = aaa_position
        sx = int(ax * camera_zoom + cam_ox)
        sy = int(ay * camera_zoom + cam_oy)
        
        angle_to_player = math.atan2(plane_y - aaa_position[1], plane_x - aaa_position[0])
        # Narrow the cone as lock builds up (from 60 deg down to 5 deg)
        dynamic_angle = FOX1_CONE_ANGLE - ((FOX1_CONE_ANGLE - 5) * ground_radar_lock)
        half_cone = math.radians(dynamic_angle / 2)
        
        # Draw Ground Radar Cone
        cone_pts = [(sx, sy)]
        segments = 10
        for i in range(segments + 1):
            ang = (angle_to_player - half_cone) + (half_cone * 2 * (i / segments))
            px = int((ax + math.cos(ang) * FOX1_RADAR_RANGE) * camera_zoom + cam_ox)
            py = int((ay + math.sin(ang) * FOX1_RADAR_RANGE) * camera_zoom + cam_oy)
            cone_pts.append((px, py))
        
        alpha = 30 + int(ground_radar_lock * 50)
        pygame.draw.polygon(fx_surface, (0, 180, 255, alpha), cone_pts)
        
        # Draw Scanning Line
        sweep_ang = angle_to_player + ground_radar_sweep * half_cone
        lx = int((ax + math.cos(sweep_ang) * FOX1_RADAR_RANGE) * camera_zoom + cam_ox)
        ly = int((ay + math.sin(sweep_ang) * FOX1_RADAR_RANGE) * camera_zoom + cam_oy)
        pygame.draw.line(fx_surface, (0, 255, 120, 220), (sx, sy), (lx, ly), 2)

    for missile in missiles:
        if "RADAR" in missile["type"]:
            # Only draw cones for missiles near enough to be visible
            if not (v_min_x - v_cone_range < missile["x"] < v_max_x + v_cone_range and 
                    v_min_y - v_cone_range < missile["y"] < v_max_y + v_cone_range):
                continue
                
            ls = missile.get("lock_strength", 0)
            
            if missile["type"] == "STATIONARY_RADAR":
                cone_angle_rad = math.radians(5.0 / 2)
                source_x, source_y = aaa_position
                msx = int(source_x * camera_zoom + cam_ox)
                msy = int(source_y * camera_zoom + cam_oy)
                ref_angle = math.atan2(missile["track_y"] - source_y, missile["track_x"] - source_x)
            else:
                # FOX 3: Show gimbal limits and track beam
                msx = int(missile["x"] * camera_zoom + cam_ox)
                msy = int(missile["y"] * camera_zoom + cam_oy)
                ref_angle = missile["angle"]
                
                # Draw Gimbal Cone (Physical seeker tracking limit) — outline only
                g_half = math.radians(FOX3_GIMBAL_ANGLE / 2)
                g_end_l = int((missile["x"] + math.cos(ref_angle - g_half) * v_cone_range) * camera_zoom + cam_ox), \
                          int((missile["y"] + math.sin(ref_angle - g_half) * v_cone_range) * camera_zoom + cam_oy)
                g_end_r = int((missile["x"] + math.cos(ref_angle + g_half) * v_cone_range) * camera_zoom + cam_ox), \
                          int((missile["y"] + math.sin(ref_angle + g_half) * v_cone_range) * camera_zoom + cam_oy)
                ls = missile.get("lock_strength", 0)
                gimbal_alpha = int(120 + ls * 80)
                gimbal_color = (0, 200, 80, gimbal_alpha)
                pygame.draw.line(fx_surface, gimbal_color, (msx, msy), g_end_l, 1)
                pygame.draw.line(fx_surface, gimbal_color, (msx, msy), g_end_r, 1)
                # Arc at the far end
                arc_pts = []
                for i in range(5):
                    a = (ref_angle - g_half) + (g_half * 2 * (i / 4))
                    arc_pts.append((int((missile["x"] + math.cos(a) * v_cone_range) * camera_zoom + cam_ox),
                                    int((missile["y"] + math.sin(a) * v_cone_range) * camera_zoom + cam_oy)))
                pygame.draw.lines(fx_surface, gimbal_color, False, arc_pts, 1)
                
                # Track FOV cone follows the seeker gimbal angle, clamped within gimbal limits
                dx_t = missile["track_x"] - missile["x"]
                dy_t = missile["track_y"] - missile["y"]
                angle_to_track = math.atan2(dy_t, dx_t)
                angle_diff_track = (angle_to_track - missile["angle"] + math.pi) % (math.pi * 2) - math.pi
                track_seeker_angle = missile["angle"] + max(-g_half, min(g_half, angle_diff_track))
                
                cone_angle_rad = math.radians(FOX3_TRACK_FOV / 2)
                ref_angle = track_seeker_angle

            cone_range = FOX1_RADAR_RANGE if missile["type"] == "STATIONARY_RADAR" else v_cone_range
            points = [(msx, msy)]
            segments = 6
            for i in range(segments + 1):
                step_angle = (ref_angle - cone_angle_rad) + (cone_angle_rad * 2 * (i / segments))
                origin_x = aaa_position[0] if missile["type"] == "STATIONARY_RADAR" else missile["x"]
                origin_y = aaa_position[1] if missile["type"] == "STATIONARY_RADAR" else missile["y"]
                spx = int((origin_x + math.cos(step_angle) * cone_range) * camera_zoom + cam_ox)
                spy = int((origin_y + math.sin(step_angle) * cone_range) * camera_zoom + cam_oy)
                points.append((spx, spy))

            ls = missile.get("lock_strength", 0)
            dynamic_cone_color = (int(255 * ls), int(255 * (1.0 - ls)), 0, 80)

            pygame.draw.polygon(
                fx_surface,
                dynamic_cone_color,
                points
            )

    # --- Optimized RWR Screen Flash ---
    if rwr_state == "MISSILE":
        # Sync the border flash with the RWR text oscillation (every 150ms)
        if (pygame.time.get_ticks() // 150) % 2 == 0:
            border_color = (255, 0, 0, 90)
            thickness = 18
            # Draw directly to fx_surface to avoid allocating a new full-screen surface every frame
            pygame.draw.rect(fx_surface, border_color, (0, 0, WIDTH, thickness))
            pygame.draw.rect(fx_surface, border_color, (0, HEIGHT - thickness, WIDTH, thickness))
            pygame.draw.rect(fx_surface, border_color, (0, 0, thickness, HEIGHT))
            pygame.draw.rect(fx_surface, border_color, (WIDTH - thickness, 0, thickness, HEIGHT))

    screen.blit(fx_surface, (0, 0))

    # =====================================================
    # WARNING SYSTEMS
    # =====================================================

    warning_y = HEIGHT - 120

    if rwr_state != "NONE":

        display_color = GREEN

        if rwr_state == "TRACK":
            display_color = YELLOW

        elif rwr_state == "MISSILE":

            if (pygame.time.get_ticks() // 150) % 2 == 0:
                display_color = RED
            else:
                display_color = WHITE

        txt = big_font.render(
            f"RWR: {rwr_state}",
            True,
            display_color
        )

        screen.blit(
            txt,
            (
                WIDTH - 380,
                warning_y
            )
        )

    if lwr_warning:

        if (pygame.time.get_ticks() // 180) % 2 == 0:
            optical_color = PURPLE
        else:
            optical_color = WHITE

        txt = big_font.render(
            "OPTICAL WARNING",
            True,
            optical_color
        )

        screen.blit(
            txt,
            (
                WIDTH - 500,
                warning_y - 70
            )
        )

# endregion

# region UI
# =====================================================
    # UI
    # =====================================================
    # RADAR UI
    # =====================================================

    if radar_enabled:
        ax = WIDTH - 230
        ay = HEIGHT // 2 + 150
        radius = 248
        half_angle = math.radians(45)
        cone_range = 4000

        # detect sweep crossing enemy
        dx_e = enemy_x - plane_x
        dy_e = enemy_y - plane_y
        dist_e = math.hypot(dx_e, dy_e)
        if dist_e < cone_range:
            target_angle = math.atan2(dy_e, dx_e)
            rel_angle = target_angle - plane_angle
            while rel_angle > math.pi:
                rel_angle -= 2 * math.pi
            while rel_angle < -math.pi:
                rel_angle += 2 * math.pi
            if abs(rel_angle) < half_angle:
                target_sweep = rel_angle / half_angle
                if (prev_radar_sweep < target_sweep and radar_sweep >= target_sweep) or \
                   (prev_radar_sweep > target_sweep and radar_sweep <= target_sweep):
                    now = pygame.time.get_ticks()
                    radar_dots.append({
                        "angle": -math.pi / 2 + rel_angle,
                        "time": now,
                        "dist": dist_e
                    })

        # draw wedge
        pts = [(ax, ay)]
        segments = 12
        for i in range(segments + 1):
            ang = -math.pi / 2 - half_angle + (half_angle * 2 * (i / segments))
            px = ax + math.cos(ang) * radius
            py = ay + math.sin(ang) * radius
            pts.append((px, py))
        pygame.draw.polygon(screen, (0, 80, 0), pts)
        pygame.draw.polygon(screen, GREEN, pts, 2)

        # sweep line
        sweep_ang = -math.pi / 2 + radar_sweep * half_angle
        lx = ax + math.cos(sweep_ang) * radius
        ly = ay + math.sin(sweep_ang) * radius
        pygame.draw.line(screen, (0, 255, 120), (ax, ay), (lx, ly), 2)

        # dots with fade
        now = pygame.time.get_ticks()
        radar_dots = [d for d in radar_dots if now - d["time"] < 1000]
        for d in radar_dots:
            elapsed = now - d["time"]
            alpha = int(255 * (1.0 - elapsed / 1000))
            dot_radius = 20 + (d["dist"] / cone_range) * (radius - 30)
            dot_radius = min(radius - 10, max(20, dot_radius))
            dx = ax + math.cos(d["angle"]) * dot_radius
            dy = ay + math.sin(d["angle"]) * dot_radius
            dot_surf = pygame.Surface((16, 4), pygame.SRCALPHA)
            dot_surf.set_alpha(alpha)
            dot_surf.fill((0, 255, 0))
            screen.blit(dot_surf, (int(dx) - 8, int(dy) - 2))

        # radar cursor
        cursor_radius = 20 + radar_cursor_dist * (radius - 30)
        cursor_ang = -math.pi / 2 + radar_cursor_angle * half_angle
        cx = ax + math.cos(cursor_ang) * cursor_radius
        cy = ay + math.sin(cursor_ang) * cursor_radius
        perp = cursor_ang + math.pi / 2
        for offset in (-6, 6):
            px = cx + math.cos(perp) * offset
            py = cy + math.sin(perp) * offset
            p1x = px + math.cos(cursor_ang) * -8
            p1y = py + math.sin(cursor_ang) * -8
            p2x = px + math.cos(cursor_ang) * 8
            p2y = py + math.sin(cursor_ang) * 8
            pygame.draw.line(screen, YELLOW, (p1x, p1y), (p2x, p2y), 2)

    # =====================================================

    if show_controls:
        controls = [

            "JET:",
            "W/S = THROTTLE",
            "A/D = TURN",

            "",

            "HELI:",
            "W/S = FORWARD/BACK",
            "A/D = STRAFE",
            "Q/E = ROTATE",

            "",

            "SHIFT = FLARES",
            "CTRL = CHAFF",
            "C = SMOKE",
            "F = FIRE GUN",

            "",

        f"1 = GROUND RADAR: {int(ground_radar_lock * 100)}%" if ground_radar_enabled else "1 = GROUND RADAR: OFF",
            "2 = IR MISSILE",
            "3 = MOBILE RADAR MISSILE",

            "",

            "Z = TOGGLE 40MM BOFORS",
            "H = TOGGLE UI",

            "",

            f"AIRCRAFT: {aircraft_type}",
            f"ACTIVE MISSILES: {len(missiles)}"
        ]

        y = 20

        for text in controls:

            render = font.render(
                text,
                True,
                WHITE
            )

            screen.blit(
                render,
                (20, y)
            )

            y += 24

        # --- PERFORMANCE OVERLAY (Bottom Right) ---
        raw_ms = clock.get_rawtime()  # Time spent in the loop before the tick delay
        cpu_load = min(100, int((raw_ms / 16.67) * 100))

        perf_text = f"FPS: {int(clock.get_fps()):3} | FT: {raw_ms:2}ms | LOAD: {cpu_load:3}%"
        perf_surf = font.render(perf_text, True, WHITE)
        screen.blit(perf_surf, (WIDTH - perf_surf.get_width() - 20, HEIGHT - 40))


    throttle_pct = int(plane_throttle)

    gauge_x = 80
    gauge_y = HEIGHT - 410
    gauge_w = 112
    gauge_h = 328
    marker_h = 56
    # Calculate marker_y so that 0% is at the bottom and 100% is at the top
    marker_y = (gauge_y + gauge_h - marker_h) - int((throttle_pct / 100) * (gauge_h - marker_h))

    # Vertical center line (always visible)
    pygame.draw.line(
        screen,
        BLACK,
        (gauge_x + gauge_w // 2, gauge_y + 4),
        (gauge_x + gauge_w // 2, gauge_y + gauge_h - 4),
        8
    )

    # Indicator marker
    pygame.draw.rect(
        screen,
        BLACK,
        (gauge_x + 8, marker_y, gauge_w - 16, marker_h)
    )

    label = None
    if throttle_pct == 100:
        label = "AB MAX"
    elif throttle_pct >= 80:
        label = "AB"
    elif throttle_pct == 79:
        label = "MIL"
    elif throttle_pct == 0:
        label = "AIRBRK" if keys[pygame.K_s] else "IDLE"

    if label:
        ab_txt = font.render(label, True, WHITE)
        # Center the text inside the moving black indicator square
        text_x = (gauge_x + 8) + (gauge_w - 16 - ab_txt.get_width()) // 2
        text_y = marker_y + (marker_h - ab_txt.get_height()) // 2
        screen.blit(ab_txt, (text_x, text_y))


    if enemy_ai_active:
        ai_txt = font.render(f"AI: {enemy_state}", True, CYAN)
        screen.blit(
            ai_txt,
            (WIDTH - ai_txt.get_width() - 10, 30)
        )

    # enemy health bar (world-space above enemy)
    if enemy_health < enemy_max_health:
        esx, esy = world_to_screen(enemy_x, enemy_y)
        bar_w = 60
        bar_h = 6
        bar_x = esx - bar_w // 2
        bar_y = esy - 30
        fill_w = int(bar_w * (enemy_health / enemy_max_health))
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h))
        if fill_w > 0:
            health_color = GREEN if enemy_health > 50 else YELLOW if enemy_health > 25 else RED
            pygame.draw.rect(screen, health_color, (bar_x, bar_y, fill_w, bar_h))

    if result_text != "":
        if result_text == "HIT":
            txt = font.render(result_text, True, WHITE)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 4))
        else:
            txt = big_font.render(
                result_text,
                True,
                RED
            )

            screen.blit(
                txt,
                (
                    WIDTH // 2
                    - txt.get_width() // 2,
                    HEIGHT // 2 - 40
                )
            )
    pygame.display.flip()

pygame.quit()
