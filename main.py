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

turn_speed = 0.0225

camera_zoom = 1.0
MIN_ZOOM = 0.35
MAX_ZOOM = 3.2
ZOOM_STEP = 1.20 #1.08
GRASS_SPAWN_MIN_X = -12000
GRASS_SPAWN_MAX_X = 12000
GRASS_SPAWN_MIN_Y = -12000
GRASS_SPAWN_MAX_Y = 12000

heat_offset = -30

# endregion

# region HELICOPTER
# =========================================================
# HELICOPTER
# =========================================================

heli_velocity_x = 0
heli_velocity_y = 0

# endregion

# region IMAGES
# =========================================================
# IMAGES
# =========================================================

PLANE_IMAGE_PATH = resource_path(
    "plane.png"
)

HELI_IMAGE_PATH = resource_path(
    "helicopter.png"
)

plane_image = None
heli_image = None

if os.path.exists(PLANE_IMAGE_PATH):

    plane_image = pygame.image.load(
        PLANE_IMAGE_PATH
    ).convert_alpha()

    plane_image = pygame.transform.scale(
        plane_image,
        (60, 60)
    )

if os.path.exists(HELI_IMAGE_PATH):

    heli_image = pygame.image.load(
        HELI_IMAGE_PATH
    ).convert_alpha()

    heli_image = pygame.transform.scale(
        heli_image,
        (120, 120)
    )

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

IR_MISSILE_SPEED = 6.5
IR_TURN_RATE = 0.09

RADAR_CONE_ANGLE_DEGREES = 60
RADAR_CONE_RANGE = 5000 # Range for visual cone and detection

RADAR_MISSILE_SPEED = 9
RADAR_TURN_RATE = 0.055

OPTICAL_MISSILE_SPEED = 3.8
OPTICAL_TURN_RATE = 0.1

# endregion

# region GUN SYSTEM
# =========================================================
# GUN SYSTEM
# =========================================================

bullets = []

gun_fire_timer = 0

VULCAN_FIRE_RATE = 2
CHAIN_GUN_FIRE_RATE = 9

VULCAN_SPEED = 18
CHAIN_SPEED = 12

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

road_manager = None


# endregion

# region ROAD SYSTEM
class RoadManager:

    def __init__(self, start_x, start_y):

        self.chunk_length = 480
        self.chunk_width = 90
        self.max_chunks = 240
        self.chunks = []

        self.last_x = start_x
        self.last_y = start_y
        self.heading = random.uniform(-0.10, 0.10)

        for _ in range(6):
            self.spawn_chunk()

    def spawn_chunk(self):

        end_x = self.last_x + math.cos(self.heading) * self.chunk_length
        end_y = self.last_y + math.sin(self.heading) * self.chunk_length

        self.chunks.append({
            "x1": self.last_x,
            "y1": self.last_y,
            "x2": end_x,
            "y2": end_y,
            "width": self.chunk_width,
        })

        self.last_x = end_x
        self.last_y = end_y

        self.heading += random.uniform(-0.08, 0.08)

        if len(self.chunks) > self.max_chunks:
            self.chunks.pop(0)

    def update(self, player_x, player_y):

        while len(self.chunks) < 80:
            self.spawn_chunk()

        if math.hypot(player_x - self.last_x, player_y - self.last_y) < self.chunk_length * 0.45:
            self.spawn_chunk()

        far_distance = max(40000, 120000 * (1.0 / max(camera_zoom, 0.35)))

        self.chunks = [
            chunk for chunk in self.chunks
            if math.hypot(player_x - chunk["x2"], player_y - chunk["y2"]) < far_distance
        ]

    def draw(self):

        for chunk in self.chunks:

            sx1, sy1 = world_to_screen(chunk["x1"], chunk["y1"])
            sx2, sy2 = world_to_screen(chunk["x2"], chunk["y2"])

            if sx1 < -400 and sx2 < -400:
                continue

            if sx1 > WIDTH + 400 and sx2 > WIDTH + 400:
                continue

            if sy1 < -400 and sy2 < -400:
                continue

            if sy1 > HEIGHT + 400 and sy2 > HEIGHT + 400:
                continue

            pygame.draw.line(
                screen,
                ROAD_EDGE,
                (sx1, sy1),
                (sx2, sy2),
                18
            )

            pygame.draw.line(
                screen,
                ROAD,
                (sx1, sy1),
                (sx2, sy2),
                10
            )


road_manager = RoadManager(plane_x, plane_y)


# endregion

# region TERRAIN
def generate_mountains():

    global mountains

    while len(mountains) < 18:

        mountains.append({
            "x": plane_x + random.randint(-6000, 6000),
            "y": plane_y + random.randint(-5000, 5000),
            "size": random.randint(360, 660),
            "color": MOUNTAIN if len(mountains) % 2 == 0 else MOUNTAIN_ALT
        })

    mountains = [
        hill for hill in mountains
        if abs(hill["x"] - plane_x) < 14000
        and abs(hill["y"] - plane_y) < 14000
    ]


generate_mountains()

grass_blades = []

for _ in range(1200):

    gx = random.randint(-12000, 12000)
    gy = random.randint(-12000, 12000)

    blade_len = random.randint(18, 42)
    center_len = blade_len + random.randint(4, 10)
    spread = random.randint(4, 9)
    angle = random.uniform(0.08, 0.22)

    grass_blades.append({
        "x": gx,
        "y": gy,
        "blade_len": blade_len,
        "center_len": center_len,
        "spread": spread,
        "angle": angle,
    })

# =========================================================
# FONT
# =========================================================

font = pygame.font.SysFont(
    "consolas",
    22
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
    global road_manager

    global plane_speed
    global plane_throttle
    global detent_timer
    global detent_target

    global plane_angle

    global heli_velocity_x
    global heli_velocity_y

    plane_x = WIDTH * 0.5
    plane_y = HEIGHT * 0.5

    plane_speed = 0
    plane_throttle = 0.0
    detent_timer = 0
    detent_target = 0

    plane_angle = 0

    heli_velocity_x = 0
    heli_velocity_y = 0

    road_manager = RoadManager(plane_x, plane_y)

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
def draw_plane(x, y, angle):

    global aircraft_type

    sx, sy = world_to_screen(x, y)

    if aircraft_type == "JET":

        if plane_image is not None:

            sprite = pygame.transform.scale(
                plane_image,
                (
                    max(1, int(plane_image.get_width() * camera_zoom)),
                    max(1, int(plane_image.get_height() * camera_zoom))
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
                    max(1, int(heli_image.get_width() * camera_zoom)),
                    max(1, int(heli_image.get_height() * camera_zoom))
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
    x,
    y,
    angle,
    missile_type
):

    points = [
        (10, 0),
        (-6, -3),
        (-2, 0),
        (-6, 3)
    ]

    rotated = []

    for px, py in points:

        rx = (
            px * math.cos(angle)
            - py * math.sin(angle)
        )

        ry = (
            px * math.sin(angle)
            + py * math.cos(angle)
        )

        rotated.append(
            (x + rx, y + ry)
        )

    color = RED

    if missile_type == "RADAR":
        color = CYAN

    if missile_type == "OPTICAL":
        color = PURPLE

    screen_points = [
        world_to_screen(rx, ry)
        for rx, ry in rotated
    ]

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
def draw_environment():

    screen.fill(WATER)

    left = max(GRASS_SPAWN_MIN_X, plane_x - WIDTH / (2 * max(camera_zoom, 0.001)))
    right = min(GRASS_SPAWN_MAX_X, plane_x + WIDTH / (2 * max(camera_zoom, 0.001)))
    top = max(GRASS_SPAWN_MIN_Y, plane_y - HEIGHT / (2 * max(camera_zoom, 0.001)))
    bottom = min(GRASS_SPAWN_MAX_Y, plane_y + HEIGHT / (2 * max(camera_zoom, 0.001)))

    if left < right and top < bottom:

        sx1, sy1 = world_to_screen(left, top)
        sx2, sy2 = world_to_screen(right, bottom)

        pygame.draw.rect(
            screen,
            GRASS,
            (
                min(sx1, sx2),
                min(sy1, sy2),
                max(1, abs(sx2 - sx1)),
                max(1, abs(sy2 - sy1))
            )
        )

    grass_scale = max(0.35, camera_zoom)

    for blade in grass_blades:

        sx, sy = world_to_screen(blade["x"], blade["y"])

        if sx < -80 or sx > WIDTH + 80 or sy < -80 or sy > HEIGHT + 80:
            continue

        blade_len = int(blade["blade_len"] * grass_scale)
        center_len = int(blade["center_len"] * grass_scale)
        spread = max(1, int(blade["spread"] * grass_scale))
        angle = blade["angle"]

        pygame.draw.line(
            screen,
            GRASS_LIGHT,
            (sx, sy + 2),
            (sx, sy - center_len),
            max(1, int(3 * grass_scale))
        )

        left_x1 = sx - spread
        left_y1 = sy + 2
        left_x2 = sx - spread - int(math.cos(angle) * 8 * grass_scale)
        left_y2 = sy - blade_len + int(math.sin(angle) * 6 * grass_scale)

        right_x1 = sx + spread
        right_y1 = sy + 2
        right_x2 = sx + spread + int(math.cos(angle) * 8 * grass_scale)
        right_y2 = sy - blade_len - int(math.sin(angle) * 6 * grass_scale)

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

    if road_manager is not None:
        road_manager.draw()

    for hill in mountains:

        sx, sy = world_to_screen(hill["x"], hill["y"])

        if sx < -300 or sx > WIDTH + 300 or sy < -300 or sy > HEIGHT + 300:
            continue

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

def spawn_missile(
    missile_type
):

    spawn_side = random.randint(0, 3)

    half_w = WIDTH * 0.5 + 40
    half_h = HEIGHT * 0.5 + 40

    # Scale spawn distance by 3x
    spawn_offset_x = half_w * 3
    spawn_offset_y = half_h * 3

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

    missiles.append({

        "type": missile_type,

        "x": spawn_x,
        "y": spawn_y,

        "angle": math.atan2(
            plane_y - spawn_y,
            plane_x - spawn_x
        ),

        "track_x": plane_x,
        "track_y": plane_y,

        "trail": [],

        "flare_bias": random.uniform(
            0.35,
            0.75
        ),

        "chaff_bias": random.uniform(
            0.45,
            0.85
        )
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

            "life": 120
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
   
    bullets.append({

        "x": spawn_x,
        "y": spawn_y,
 
        "vx": math.cos(angle) * speed,
        "vy": math.sin(angle) * speed,

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

    screen.fill(BG)

    draw_environment()

    rwr_state = "NONE"

    lwr_warning = False

    # =====================================================
    # EVENTS
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:
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

                ir_launch_sound.play()

                spawn_missile("IR")

            if event.key == pygame.K_2:
                
                radar_launch_sound.play()

                spawn_missile("RADAR")
      
            if event.key == pygame.K_3:

                optical_launch_sound.play()

                spawn_missile("OPTICAL")

            if event.key == pygame.K_z:
                aaa_enabled = not aaa_enabled

            if event.key == pygame.K_o:
                camera_zoom = max(MIN_ZOOM, round(camera_zoom / ZOOM_STEP, 2))

            if event.key == pygame.K_i:
                camera_zoom = min(MAX_ZOOM, round(camera_zoom * ZOOM_STEP, 2))

            if event.key == pygame.K_h:

                if aircraft_type == "JET":
                    aircraft_type = "HELICOPTER"
                else:
                    aircraft_type = "JET"

    keys = pygame.key.get_pressed()

    if not paused:

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
            if keys[pygame.K_a]:
                applied_turn = -actual_turn

            if keys[pygame.K_d]:
                applied_turn = actual_turn
            plane_angle += applied_turn

            if keys[pygame.K_w]:
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
            elif keys[pygame.K_s]:
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
            if plane_throttle == 0 and keys[pygame.K_s]:
                drag *= 2.0

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

            if keys[pygame.K_w]:

                heli_velocity_x += (
                    math.cos(plane_angle)
                    * move_speed
                )

                heli_velocity_y += (
                    math.sin(plane_angle)
                    * move_speed
                )

            if keys[pygame.K_s]:

                heli_velocity_x -= (
                    math.cos(plane_angle)
                    * move_speed * 0.7
                )

                heli_velocity_y -= (
                    math.sin(plane_angle)
                    * move_speed * 0.7
                )

            if keys[pygame.K_a]:

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

            if keys[pygame.K_d]:

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

        road_manager.update(plane_x, plane_y)

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

        generate_mountains()

        if mountain_refresh_timer <= 0:
            generate_mountains()
            mountain_refresh_timer = 10
        else:
            mountain_refresh_timer -= 1

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

                for flare in flares:

                    flare_dist = math.hypot(
                        missile["x"] - flare["x"],
                        missile["y"] - flare["y"]
                    )

                    if flare_dist < 220:

                        probability = (
                            missile["flare_bias"]
                            * (
                                1
                                - flare_dist / 220
                            )
                        )

                        if random.random() < probability:

                            target_x = flare["x"]
                            target_y = flare["y"]

                            flare_targeted = True

                missile_speed = IR_MISSILE_SPEED
                turn_rate = IR_TURN_RATE

            elif missile["type"] == "RADAR":

                chaff_targeted = False

                target_x = missile["track_x"] # Default to current track if player not in cone
                target_y = missile["track_y"]

                distance_to_plane = math.hypot(
                    missile["x"] - plane_x,
                    missile["y"] - plane_y
                )

                if distance_to_plane > 500:
                    rwr_state = "SEARCH"

                elif distance_to_plane > 220:
                    rwr_state = "TRACK"

                else:
                    rwr_state = "MISSILE"

                # Radar cone detection
                angle_to_player = math.atan2(plane_y - missile["y"], plane_x - missile["x"])
                angle_diff = angle_to_player - missile["angle"]
                while angle_diff > math.pi:
                    angle_diff -= math.pi * 2
                while angle_diff < -math.pi:
                    angle_diff += math.pi * 2

                # Reduce internal detection angle by 2 degrees to perfectly align with visual cone edges
                player_in_cone = abs(angle_diff) <= math.radians((RADAR_CONE_ANGLE_DEGREES - 2) / 2)
                
                # Only track player if within cone and range
                if player_in_cone and distance_to_plane < RADAR_CONE_RANGE:
                    target_x = plane_x
                    target_y = plane_y

                for chaff in chaff_clouds:

                    chaff_dist = math.hypot(
                        missile["x"] - chaff["x"],
                        missile["y"] - chaff["y"]
                    )

                    if chaff_dist < 260:
                        # Seeker cone check for chaff
                        angle_to_chaff = math.atan2(chaff["y"] - missile["y"], chaff["x"] - missile["x"])
                        angle_diff_chaff = angle_to_chaff - missile["angle"]
                        while angle_diff_chaff > math.pi: angle_diff_chaff -= math.pi * 2
                        while angle_diff_chaff < -math.pi: angle_diff_chaff += math.pi * 2

                        if abs(angle_diff_chaff) <= math.radians((RADAR_CONE_ANGLE_DEGREES - 2) / 2):
                            probability = (
                                missile["chaff_bias"]
                                * (
                                    1
                                    - chaff_dist / 260
                                )
                            )

                            if random.random() < probability:
                                target_x = chaff["x"]
                                target_y = chaff["y"]
                                chaff_targeted = True

                missile_speed = RADAR_MISSILE_SPEED
                turn_rate = RADAR_TURN_RATE

            else:

                distance_to_plane = math.hypot(
                    missile["x"] - plane_x,
                    missile["y"] - plane_y
                )

                if distance_to_plane < 450:
                    lwr_warning = True

                target_x = plane_x
                target_y = plane_y

                for smoke in smoke_clouds:

                    smoke_dist = math.hypot(
                        missile["x"] - smoke["x"],
                        missile["y"] - smoke["y"]
                    )

                    if smoke_dist < smoke["radius"] + 40:

                        smoke_blocked = True

                        target_x = smoke["x"]
                        target_y = smoke["y"]

                        break

                missile_speed = OPTICAL_MISSILE_SPEED
                turn_rate = OPTICAL_TURN_RATE

            missile["track_x"] += (
                target_x
                - missile["track_x"]
            ) * 0.10

            missile["track_y"] += (
                target_y
                - missile["track_y"]
            ) * 0.10

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

            missile["x"] += (
                math.cos(missile["angle"])
                * missile_speed
            )

            missile["y"] += (
                math.sin(missile["angle"])
                * missile_speed
            )

            missile["trail"].append(
                (
                    missile["x"],
                    missile["y"]
                )
            )

            if len(missile["trail"]) > 220:
                missile["trail"].pop(0)

            distance = math.hypot(dx, dy)

            if distance < 18:

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
                    missile["type"] == "RADAR"
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
                    # Scale lethal radius with zoom to maintain visual screen-space consistency
                    # This ensures the danger zone is always ~45 pixels on screen
                    lethal_radius = 45 / camera_zoom
                    dist_to_player = math.hypot(missile["x"] - plane_x, missile["y"] - plane_y)

                    if dist_to_player < lethal_radius:
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

            bullet["life"] -= 1

            

            if bullet["life"] <= 0:

                 bullets_to_remove.append(
                     bullet
                 )

        for bullet in bullets_to_remove:

            if bullet in bullets:
                bullets.remove(bullet)

        # =================================================
        # EXPLOSIONS
        # =================================================

        for explosion in explosions:

            explosion["radius"] += 2
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

        if missile["type"] == "RADAR":
            trail_color = LIGHT_BLUE

        if missile["type"] == "OPTICAL":
            trail_color = PURPLE

        for i in range(
            len(missile["trail"]) - 1
        ):

            pygame.draw.line(
                screen,
                trail_color,
                world_to_screen(*missile["trail"][i]),
                world_to_screen(*missile["trail"][i + 1]),
                2
            )

    # =====================================================
    # DRAW EFFECTS
    # =====================================================

    effect_scale = max(0.6, camera_zoom)

    for flare in flares:

        sx, sy = world_to_screen(
            flare["x"],
            flare["y"]
        )

        pygame.draw.circle(
            screen,
            YELLOW,
            (sx, sy),
            max(1, int(4 * effect_scale))
        )

    for chaff in chaff_clouds:

        sx, sy = world_to_screen(
            chaff["x"],
            chaff["y"]
        )

        pygame.draw.circle(
            screen,
            LIGHT_BLUE,
            (sx, sy),
            max(1, int(3 * effect_scale))
        )

    for smoke in smoke_clouds:

        sx, sy = world_to_screen(
            smoke["x"],
            smoke["y"]
        )

        pygame.draw.circle(
            screen,
            GREY,
            (sx, sy),
            max(1, int(smoke["radius"] * effect_scale))
        )

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

        if missile["type"] == "RADAR":

            line_color = LIGHT_BLUE
            dot_color = CYAN

        if missile["type"] == "OPTICAL":

            line_color = PURPLE
            dot_color = PURPLE

        pygame.draw.line(
            screen,
            line_color,
            world_to_screen(missile["x"], missile["y"]),
            world_to_screen(missile["track_x"], missile["track_y"]),
            1
        )

        sx, sy = world_to_screen(
            missile["track_x"],
            missile["track_y"]
        )

        pygame.draw.circle(
            screen,
            dot_color,
            (sx, sy),
            6
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
 
        smoke_surface = pygame.Surface(
            (
                int(flak["smoke"] * 2),
                int(flak["smoke"] * 2)
            ),
            pygame.SRCALPHA
        )
 
        alpha = max(
            0,
            min(
                180,
                flak["life"] * 3
            )
        )

        pygame.draw.circle(
   
            smoke_surface,

            (
                45,
                45,
                45,
                alpha
            ),

            (
                int(flak["smoke"]),
                int(flak["smoke"])
            ),

            int(flak["smoke"])
        )

        sx, sy = world_to_screen(
            flak["x"],
            flak["y"]
        )

        screen.blit(
            smoke_surface,
            (
                sx - flak["smoke"],
                sy - flak["smoke"]
            )
        )
    # =====================================================
    # DRAW BULLETS
    # =====================================================

    for bullet in bullets:
    
        pygame.draw.line(
            screen,
            bullet["color"],
            world_to_screen(bullet["x"], bullet["y"]),
            world_to_screen(
                bullet["x"] - bullet["vx"] * 2,
                bullet["y"] - bullet["vy"] * 2
            ),
            3
        )

    # =====================================================
    # DRAW AIRCRAFT + MISSILES
    # =====================================================

    draw_plane(
        plane_x,
        plane_y,
        plane_angle
    )

    # Speed UI underneath player (numbers only)
    speed_sx, speed_sy = world_to_screen(plane_x, plane_y)
    current_spd = plane_speed if aircraft_type == "JET" else math.hypot(heli_velocity_x, heli_velocity_y)
    speed_txt = font.render(str(int(current_spd * (1300 / 19.5))), True, GREEN)
    screen.blit(speed_txt, (speed_sx - speed_txt.get_width() // 2, speed_sy + 40))

    for missile in missiles:

        draw_missile(
            missile["x"],
            missile["y"],
            missile["angle"],
            missile["type"]
        )

    # =====================================================
    # DRAW RADAR MISSILE SEEKER CONES
    # =====================================================
    cone_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    cone_angle_rad = math.radians(RADAR_CONE_ANGLE_DEGREES / 2)

    for missile in missiles:
        if missile["type"] == "RADAR":
            # Missile's position in screen coordinates
            msx, msy = world_to_screen(missile["x"], missile["y"])

            # Points for the cone extending from the missile
            p1x = missile["x"] + math.cos(missile["angle"] - cone_angle_rad) * RADAR_CONE_RANGE
            p1y = missile["y"] + math.sin(missile["angle"] - cone_angle_rad) * RADAR_CONE_RANGE
            p2x = missile["x"] + math.cos(missile["angle"] + cone_angle_rad) * RADAR_CONE_RANGE
            p2y = missile["y"] + math.sin(missile["angle"] + cone_angle_rad) * RADAR_CONE_RANGE

            sp1x, sp1y = world_to_screen(p1x, p1y)
            sp2x, sp2y = world_to_screen(p2x, p2y)

            pygame.draw.polygon(
                cone_surface,
                LIGHT_BLUE_ALPHA,
                [(msx, msy), (sp1x, sp1y), (sp2x, sp2y)]
            )
    screen.blit(cone_surface, (0, 0))

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

            flash = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            border_color = (255, 0, 0, 90)
            thickness = 18

            pygame.draw.rect(flash, border_color, (0, 0, WIDTH, thickness))
            pygame.draw.rect(flash, border_color, (0, HEIGHT - thickness, WIDTH, thickness))
            pygame.draw.rect(flash, border_color, (0, 0, thickness, HEIGHT))
            pygame.draw.rect(flash, border_color, (WIDTH - thickness, 0, thickness, HEIGHT))

            screen.blit(flash, (0, 0))

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

        "1 = IR MISSILE",
        "2 = RADAR MISSILE",
        "3 = OPTICAL MISSILE",

        "",

        "Z = TOGGLE 40MM BOFORS",
        "H = SWITCH AIRCRAFT",

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


    if result_text != "":

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
