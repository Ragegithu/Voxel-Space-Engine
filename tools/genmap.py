from PIL import Image
import numpy as np

# --- Settings ---
WIDTH, HEIGHT = 1024 * 4, 1024 * 4
SEED        = np.random.randint(0, 9999)

# --- Toggles ---
GENERATE_CITY = False   # False = pure terrain, no buildings or roads
TERRAIN_FLAT  = False  # False = generate noise-based heightmap terrain

# --- Material IDs ---
MAT_TERRAIN    = 0
MAT_BUILDING_X = 1  # X-facing face (front/back) → use mx for texX
MAT_ROAD       = 2
MAT_SIDEWALK   = 3
MAT_BUILDING_Y = 4  # Y-facing face (left/right) → use my for texX
MAT_LAMP       = 5  # lamp post (pole + head)

# --- Road / Block grid settings ---
BLOCK_MIN       = 300    # min city block size (pixels) before road
BLOCK_MAX       = 600    # max city block size
ROAD_WIDTH      = 100    # half-width of road (total = 2x)
SIDEWALK_WIDTH  = 12     # sidewalk margin inside block before buildings start

# --- Building settings ---
BUILDING_MIN_W  = 60     # min building footprint width
BUILDING_MAX_W  = 220    # max building footprint width
BUILDING_MIN_H  = 20     # min height added to terrain
BUILDING_MAX_H  = 110    # max height added to terrain
BUILDING_GAP    = 10     # min gap between buildings in same block
BASE_TERRAIN    = 130    # flat terrain height value

# --- Lamp post settings ---
LAMP_SPACING   = 400     # pixels between posts along a road
LAMP_POLE_SIZE = 6       # pole footprint (pixels square)
LAMP_HEAD_SIZE = 6       # light-head footprint (pixels square)
LAMP_POLE_H    = 20      # pole height above BASE_TERRAIN
LAMP_HEAD_H    = 1       # extra height of light head above pole
POLE_COLOR     = (105, 105, 110)
LIGHT_COLOR    = (255, 200, 80)

# --- Colors ---
ROAD_COLOR      = (45,  43,  40)
SIDEWALK_COLOR  = (160, 155, 148)
SUN_X           = 1.0
SUN_Y           = -1.5

print(f"Seed: {SEED}")
print(f"City generation: {'ON' if GENERATE_CITY else 'OFF'}")
print(f"Flat terrain: {'ON' if TERRAIN_FLAT else 'OFF'}")
rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------ #
#  Terrain base
# ------------------------------------------------------------------ #
if TERRAIN_FLAT:
    print("Flat terrain mode...")
    noise = np.full((HEIGHT, WIDTH), BASE_TERRAIN, dtype=np.uint8)
else:
    print("Generating terrain noise...")
    OCTAVES     = 12
    PERSISTENCE = 0.4
    LACUNARITY  = 2.0
    SCALE       = 2048.0

    def smooth_noise(width, height, scale, rng):
        grid_w = int(width  / scale) + 2
        grid_h = int(height / scale) + 2
        grid   = rng.random((grid_h, grid_w))
        grid[-1, :] = grid[0, :]
        grid[:, -1] = grid[:, 0]
        xs = np.linspace(0, grid_w - 1, width,  endpoint=False)
        ys = np.linspace(0, grid_h - 1, height, endpoint=False)
        x0 = np.floor(xs).astype(int); x1 = np.minimum(x0 + 1, grid_w - 1)
        y0 = np.floor(ys).astype(int); y1 = np.minimum(y0 + 1, grid_h - 1)
        fx = xs - np.floor(xs); fx = fx * fx * (3 - 2 * fx)
        fy = ys - np.floor(ys); fy = fy * fy * (3 - 2 * fy)
        fx = fx[np.newaxis, :]; fy = fy[:, np.newaxis]
        top    = grid[np.ix_(y0, x0)] * (1 - fx) + grid[np.ix_(y0, x1)] * fx
        bottom = grid[np.ix_(y1, x0)] * (1 - fx) + grid[np.ix_(y1, x1)] * fx
        return top * (1 - fy) + bottom * fy

    n = np.zeros((HEIGHT, WIDTH))
    amp, freq, max_val = 20.0, 1.0, 0.0
    for _ in range(OCTAVES):
        n      += smooth_noise(WIDTH, HEIGHT, SCALE / freq, rng) * amp
        max_val += amp; amp *= PERSISTENCE; freq *= LACUNARITY
    n = np.power(n / max_val, 0.7)
    noise = (n * 255).astype(np.uint8)

final_height = noise.astype(np.float32).copy()
material_map = np.full((HEIGHT, WIDTH), MAT_TERRAIN, dtype=np.uint8)

# ------------------------------------------------------------------ #
#  Shared color noise function
# ------------------------------------------------------------------ #
def color_noise(w, h, scale, rng_):
    gw = int(w / scale) + 2
    gh = int(h / scale) + 2
    g  = rng_.random((gh, gw))
    g[-1, :] = g[0, :]
    g[:, -1] = g[:, 0]
    xs = np.linspace(0, gw - 1, w, endpoint=False)
    ys = np.linspace(0, gh - 1, h, endpoint=False)
    x0 = np.floor(xs).astype(int); x1 = np.minimum(x0 + 1, gw - 1)
    y0 = np.floor(ys).astype(int); y1 = np.minimum(y0 + 1, gh - 1)
    fx = xs - np.floor(xs); fx = fx * fx * (3 - 2 * fx); fx = fx[np.newaxis, :]
    fy = ys - np.floor(ys); fy = fy * fy * (3 - 2 * fy); fy = fy[:, np.newaxis]
    top    = g[np.ix_(y0, x0)] * (1 - fx) + g[np.ix_(y0, x1)] * fx
    bottom = g[np.ix_(y1, x0)] * (1 - fx) + g[np.ix_(y1, x1)] * fx
    return top * (1 - fy) + bottom * fy

TERRAIN_RAMP = [
    (0.00, ( 30,  38,  18)),   # dark soil / deep valley
    (0.15, ( 45,  58,  25)),   # lowland grass
    (0.35, ( 62,  82,  35)),   # mid grass
    (0.55, ( 75,  90,  42)),   # lighter grass
    (0.70, ( 90,  85,  55)),   # scrubland / dry grass
    (0.82, (110,  98,  72)),   # rocky dirt
    (0.92, (130, 118,  95)),   # bare rock
    (1.00, (200, 195, 185)),   # snow / peak rock
]

# ------------------------------------------------------------------ #
#  No city - pure terrain early exit
# ------------------------------------------------------------------ #
if not GENERATE_CITY:
    print("Skipping city generation...")
    h_f32 = final_height.astype(np.float32)
    dx    = np.roll(h_f32, -1, axis=1) - np.roll(h_f32, 1, axis=1)
    dy    = np.roll(h_f32, -1, axis=0) - np.roll(h_f32, 1, axis=0)
    shade = dx * SUN_X + dy * SUN_Y
    shade = shade / (np.max(np.abs(shade)) + 1e-6)
    shade = np.clip(shade + 1.0, 0.3, 1.4)

    cn  = color_noise(WIDTH, HEIGHT, 512, rng) * 0.5
    cn += color_noise(WIDTH, HEIGHT, 128, rng) * 0.3
    cn += color_noise(WIDTH, HEIGHT,  32, rng) * 0.2
    cn  = (cn - cn.min()) / (cn.max() - cn.min())

    h_norm = (h_f32 - h_f32.min()) / (h_f32.max() - h_f32.min() + 1e-6)
    blend  = cn * 0.55 + h_norm * 0.45
    blend  = (blend - blend.min()) / (blend.max() - blend.min())

    terrain_color = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
    for i in range(len(TERRAIN_RAMP) - 1):
        t0, c0 = TERRAIN_RAMP[i]
        t1, c1 = TERRAIN_RAMP[i + 1]
        seg_mask = (blend >= t0) & (blend < t1)
        t = np.where(seg_mask, (blend - t0) / (t1 - t0), 0.0)
        for ch in range(3):
            terrain_color[:, :, ch] += seg_mask * (c0[ch] + t * (c1[ch] - c0[ch]))

    final_color = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for ch in range(3):
        final_color[:, :, ch] = np.clip(
            terrain_color[:, :, ch] * shade, 0, 255
        ).astype(np.uint8)

    print("Saving...")
    Image.fromarray(final_height.astype(np.uint8), mode="L").save("../assets/heightmap.png")
    Image.fromarray(final_color, mode="RGB").save("../assets/colormap.png")
    Image.fromarray(material_map, mode="L").save("../assets/materialmap.png")
    print(f"Done! (seed: {SEED})")
    exit()

# ------------------------------------------------------------------ #
#  Generate grid street lines
# ------------------------------------------------------------------ #
print("Generating street grid...")

def make_grid_lines(total, block_min, block_max, rng):
    lines = []
    pos   = 0
    while pos < total:
        gap  = int(rng.integers(block_min, block_max))
        pos += gap
        if pos < total:
            lines.append(pos)
    return lines

x_roads = make_grid_lines(WIDTH,  BLOCK_MIN, BLOCK_MAX, rng)
y_roads = make_grid_lines(HEIGHT, BLOCK_MIN, BLOCK_MAX, rng)

road_mask     = np.zeros((HEIGHT, WIDTH), dtype=bool)
sidewalk_mask = np.zeros((HEIGHT, WIDTH), dtype=bool)

for cx in x_roads:
    r0 = max(0, cx - ROAD_WIDTH);  r1 = min(WIDTH,  cx + ROAD_WIDTH)
    road_mask[:, r0:r1] = True
    s0 = max(0, cx - ROAD_WIDTH - SIDEWALK_WIDTH)
    s1 = min(WIDTH, cx + ROAD_WIDTH + SIDEWALK_WIDTH)
    sidewalk_mask[:, s0:s1] = True

for cy in y_roads:
    r0 = max(0, cy - ROAD_WIDTH);  r1 = min(HEIGHT, cy + ROAD_WIDTH)
    road_mask[r0:r1, :] = True
    s0 = max(0, cy - ROAD_WIDTH - SIDEWALK_WIDTH)
    s1 = min(HEIGHT, cy + ROAD_WIDTH + SIDEWALK_WIDTH)
    sidewalk_mask[s0:s1, :] = True

sidewalk_mask &= ~road_mask

# ------------------------------------------------------------------ #
#  Collect blocks
# ------------------------------------------------------------------ #
def get_blocks(road_lines, total, road_w, swalk_w):
    edges = [0] + road_lines + [total]
    blocks = []
    for i in range(len(edges) - 1):
        a = edges[i]; b = edges[i + 1]
        inner_a = a + (road_w + swalk_w if i > 0 else 0)
        inner_b = b - (road_w + swalk_w if i < len(edges) - 2 else 0)
        if inner_b - inner_a > BUILDING_MIN_W * 2:
            blocks.append((inner_a, inner_b))
    return blocks

x_blocks = get_blocks(x_roads, WIDTH,  ROAD_WIDTH, SIDEWALK_WIDTH)
y_blocks = get_blocks(y_roads, HEIGHT, ROAD_WIDTH, SIDEWALK_WIDTH)

# ------------------------------------------------------------------ #
#  Building material color pools
# ------------------------------------------------------------------ #
BUILDING_PALETTES = [
    ((110, 145), (110, 140), (115, 148)),  # concrete
    ((100, 130), (120, 150), (130, 165)),  # glass
    ((130, 170), (85,  115), (65,   95)),  # brick
    ((150, 185), (140, 170), (110, 140)),  # cladding
]

building_color_map = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

# ------------------------------------------------------------------ #
#  Place rectangular buildings
# ------------------------------------------------------------------ #
print(f"Placing buildings in {len(x_blocks) * len(y_blocks)} blocks...")

building_mask = np.zeros((HEIGHT, WIDTH), dtype=bool)

for (bx0, bx1) in x_blocks:
    for (by0, by1) in y_blocks:

        x_cursor = bx0
        while x_cursor < bx1:
            avail_x = bx1 - x_cursor
            if avail_x < BUILDING_MIN_W:
                break
            bw = int(rng.integers(BUILDING_MIN_W, min(BUILDING_MAX_W, avail_x) + 1))

            y_cursor = by0
            while y_cursor < by1:
                avail_y = by1 - y_cursor
                if avail_y < BUILDING_MIN_W:
                    break
                bh = int(rng.integers(BUILDING_MIN_W, min(BUILDING_MAX_W, avail_y) + 1))

                height_val = int(rng.integers(BUILDING_MIN_H, BUILDING_MAX_H))
                pal   = BUILDING_PALETTES[rng.integers(0, len(BUILDING_PALETTES))]
                col_r = int(rng.integers(*pal[0]))
                col_g = int(rng.integers(*pal[1]))
                col_b = int(rng.integers(*pal[2]))

                rx0, rx1 = x_cursor, x_cursor + bw
                ry0, ry1 = y_cursor, y_cursor + bh

                final_height[ry0:ry1, rx0:rx1] = BASE_TERRAIN + height_val
                building_mask[ry0:ry1, rx0:rx1] = True
                building_color_map[ry0:ry1, rx0:rx1] = (col_r, col_g, col_b)

                material_map[ry0:ry1, rx0:rx1] = MAT_BUILDING_X
                material_map[ry0,     rx0:rx1] = MAT_BUILDING_X
                material_map[ry1-1,   rx0:rx1] = MAT_BUILDING_X
                material_map[ry0:ry1, rx0    ] = MAT_BUILDING_Y
                material_map[ry0:ry1, rx1-1  ] = MAT_BUILDING_Y

                y_cursor += bh + BUILDING_GAP

            x_cursor += bw + BUILDING_GAP

# ------------------------------------------------------------------ #
#  Apply roads / sidewalks to heightmap
# ------------------------------------------------------------------ #
final_height[road_mask]     = BASE_TERRAIN - 1
final_height[sidewalk_mask] = BASE_TERRAIN
final_height[building_mask & road_mask]     = BASE_TERRAIN + BUILDING_MIN_H
final_height[building_mask & sidewalk_mask] = BASE_TERRAIN + BUILDING_MIN_H
final_height = np.clip(final_height, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ #
#  Lamp posts
# ------------------------------------------------------------------ #
print("Placing lamp posts...")

lamp_pole_mask = np.zeros((HEIGHT, WIDTH), dtype=bool)
lamp_head_mask = np.zeros((HEIGHT, WIDTH), dtype=bool)
lamp_color_map = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

_sw_offset = ROAD_WIDTH + SIDEWALK_WIDTH // 2   # centre of sidewalk strip

def _place_lamp(cx, cy):
    # --- pole ---
    px0 = max(0, cx - LAMP_POLE_SIZE // 2)
    px1 = min(WIDTH,  px0 + LAMP_POLE_SIZE)
    py0 = max(0, cy - LAMP_POLE_SIZE // 2)
    py1 = min(HEIGHT, py0 + LAMP_POLE_SIZE)
    final_height[py0:py1, px0:px1] = BASE_TERRAIN + LAMP_POLE_H
    lamp_pole_mask[py0:py1, px0:px1] = True
    lamp_color_map[py0:py1, px0:px1] = POLE_COLOR
    # --- light head (sits on top of pole) ---
    hx0 = max(0, cx - LAMP_HEAD_SIZE // 2)
    hx1 = min(WIDTH,  hx0 + LAMP_HEAD_SIZE)
    hy0 = max(0, cy - LAMP_HEAD_SIZE // 2)
    hy1 = min(HEIGHT, hy0 + LAMP_HEAD_SIZE)
    final_height[hy0:hy1, hx0:hx1] = BASE_TERRAIN + LAMP_POLE_H + LAMP_HEAD_H
    lamp_head_mask[hy0:hy1, hx0:hx1] = True
    lamp_color_map[hy0:hy1, hx0:hx1] = LIGHT_COLOR

# Along every vertical road (x_roads): posts on both sidewalk sides
# Skip y positions that fall inside a horizontal road zone (intersection)
_road_zone = ROAD_WIDTH + SIDEWALK_WIDTH
for cx in x_roads:
    for y in range(0, HEIGHT, LAMP_SPACING):
        if any(abs(y - cy) < _road_zone for cy in y_roads):
            continue
        for lx in (cx - _sw_offset, cx + _sw_offset):
            if 0 < lx < WIDTH:
                _place_lamp(int(lx), y)

# Along every horizontal road (y_roads): posts on both sidewalk sides
# Skip x positions that fall inside a vertical road zone (intersection)
for cy in y_roads:
    for x in range(0, WIDTH, LAMP_SPACING):
        if any(abs(x - cx) < _road_zone for cx in x_roads):
            continue
        for ly in (cy - _sw_offset, cy + _sw_offset):
            if 0 < ly < HEIGHT:
                _place_lamp(x, int(ly))

lamp_mask = lamp_pole_mask | lamp_head_mask

# ------------------------------------------------------------------ #
#  Material map
# ------------------------------------------------------------------ #
print("Building material map...")
material_map[road_mask     & ~building_mask] = MAT_ROAD
material_map[sidewalk_mask & ~building_mask] = MAT_SIDEWALK
material_map[lamp_mask]                      = MAT_LAMP

# ------------------------------------------------------------------ #
#  Shading
# ------------------------------------------------------------------ #
print("Computing shading...")
h_f32 = final_height.astype(np.float32)
dx    = np.roll(h_f32, -1, axis=1) - np.roll(h_f32, 1, axis=1)
dy    = np.roll(h_f32, -1, axis=0) - np.roll(h_f32, 1, axis=0)
shade = dx * SUN_X + dy * SUN_Y
shade = shade / (np.max(np.abs(shade)) + 1e-6)
shade = np.clip(shade * 1.0 + 1.0, 0.3, 1.4)

# ------------------------------------------------------------------ #
#  Colormap
# ------------------------------------------------------------------ #
print("Generating colormap...")
final_color = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

terrain_px = ~building_mask & ~road_mask & ~sidewalk_mask & ~lamp_mask

cn  = color_noise(WIDTH, HEIGHT, 512, rng) * 0.5
cn += color_noise(WIDTH, HEIGHT, 128, rng) * 0.3
cn += color_noise(WIDTH, HEIGHT,  32, rng) * 0.2
cn  = (cn - cn.min()) / (cn.max() - cn.min())

h_norm = (h_f32 - h_f32.min()) / (h_f32.max() - h_f32.min() + 1e-6)
blend  = cn * 0.55 + h_norm * 0.45
blend  = (blend - blend.min()) / (blend.max() - blend.min())

terrain_color = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
for i in range(len(TERRAIN_RAMP) - 1):
    t0, c0 = TERRAIN_RAMP[i]
    t1, c1 = TERRAIN_RAMP[i + 1]
    mask = (blend >= t0) & (blend < t1)
    t = np.where(mask, (blend - t0) / (t1 - t0), 0.0)
    for ch in range(3):
        terrain_color[:,:,ch] += mask * (c0[ch] + t*(c1[ch]-c0[ch]))

for ch in range(3):
    final_color[terrain_px, ch] = np.clip(terrain_color[terrain_px, ch] * shade[terrain_px], 0, 255).astype(np.uint8)

for ch in range(3):
    final_color[building_mask, ch] = np.clip(
        building_color_map[building_mask, ch].astype(np.float32) * shade[building_mask], 0, 255
    ).astype(np.uint8)

road_px = road_mask & ~building_mask
for i, c in enumerate(ROAD_COLOR):
    final_color[road_px, i] = np.clip(c * shade[road_px], 0, 255).astype(np.uint8)

swalk_px = sidewalk_mask & ~building_mask
for i, c in enumerate(SIDEWALK_COLOR):
    final_color[swalk_px, i] = np.clip(c * shade[swalk_px], 0, 255).astype(np.uint8)

# Lamp poles — shaded grey (engine overrides color via MAT_LAMP, but colormap still written for reference)
pole_only = lamp_pole_mask & ~lamp_head_mask
for ch in range(3):
    final_color[pole_only, ch] = np.clip(
        lamp_color_map[pole_only, ch].astype(np.float32) * shade[pole_only], 0, 255
    ).astype(np.uint8)

# Light heads — pure unshaded white
final_color[lamp_head_mask] = LIGHT_COLOR

# ------------------------------------------------------------------ #
#  Save
# ------------------------------------------------------------------ #
print("Saving...")
Image.fromarray(final_height, mode="L").save("../assets/heightmap.png")
Image.fromarray(final_color,  mode="RGB").save("../assets/colormap.png")
Image.fromarray(material_map, mode="L").save("../assets/materialmap.png")
print(f"Done! Seed: {SEED}")
print(f"  x_roads: {len(x_roads)} streets, y_roads: {len(y_roads)} streets")
print(f"  blocks:  {len(x_blocks)} x {len(y_blocks)} = {len(x_blocks)*len(y_blocks)}")