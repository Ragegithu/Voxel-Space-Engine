from PIL import Image
import numpy as np
from scipy.spatial import KDTree

# --- Settings ---
WIDTH, HEIGHT = 1024 * 4, 1024 * 4
SCALE       = 2048.0
OCTAVES     = 12
PERSISTENCE = 0.4
LACUNARITY  = 2.0
SEED        = np.random.randint(0, 9999)

# --- Toggle ---
GENERATE_CITY = True
TERRAIN_FLAT  = True

# --- City Settings ---
N_CITY_SEEDS      = 60
CITY_BLOCK_HEIGHT = (20, 80)
CITY_TERRAIN_MIN  = 108
CITY_TERRAIN_MAX  = 160

# --- Road Settings ---
ROAD_WIDTH        = 50
ROAD_COLOR        = (45, 43, 40)
SIDEWALK_COLOR    = (80, 77, 72)

# --- Material IDs ---
MAT_TERRAIN  = 0
MAT_BUILDING = 1
MAT_ROAD     = 2
MAT_SIDEWALK = 3

print(f"Seed: {SEED}")
print(f"City generation: {'ON' if GENERATE_CITY else 'OFF'}")
print(f"Flat terrain: {'ON' if TERRAIN_FLAT else 'OFF'}")
rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------ #
#  Noise
# ------------------------------------------------------------------ #
def smooth_noise(width, height, scale, rng):
    grid_w = int(width / scale) + 2
    grid_h = int(height / scale) + 2
    grid = rng.random((grid_h, grid_w))
    grid[-1, :] = grid[0, :]
    grid[:, -1] = grid[:, 0]

    xs = np.linspace(0, grid_w - 1, width)
    ys = np.linspace(0, grid_h - 1, height)

    x0 = np.floor(xs).astype(int)
    x1 = np.minimum(x0 + 1, grid_w - 1)
    y0 = np.floor(ys).astype(int)
    y1 = np.minimum(y0 + 1, grid_h - 1)

    fx = xs - np.floor(xs)
    fy = ys - np.floor(ys)
    fx = fx * fx * (3 - 2 * fx)
    fy = fy * fy * (3 - 2 * fy)
    fx = fx[np.newaxis, :]
    fy = fy[:, np.newaxis]

    top    = grid[np.ix_(y0, x0)] * (1 - fx) + grid[np.ix_(y0, x1)] * fx
    bottom = grid[np.ix_(y1, x0)] * (1 - fx) + grid[np.ix_(y1, x1)] * fx
    return top * (1 - fy) + bottom * fy

if TERRAIN_FLAT:
    print("Flat terrain mode — skipping noise generation...")
    noise = np.full((HEIGHT, WIDTH), 130, dtype=np.uint8)
else:
    print("Generating terrain noise...")
    noise     = np.zeros((HEIGHT, WIDTH))
    amplitude = 20.0
    frequency = 1.0
    max_val   = 0.0

    for _ in range(OCTAVES):
        noise   += smooth_noise(WIDTH, HEIGHT, SCALE / frequency, rng) * amplitude
        max_val += amplitude
        amplitude *= PERSISTENCE
        frequency *= LACUNARITY

    noise_f = noise / max_val
    noise_f = np.power(noise_f, 0.7)
    noise   = (noise_f * 255).astype(np.uint8)

# ------------------------------------------------------------------ #
#  Colormap helper
# ------------------------------------------------------------------ #
SUN_X        = 1.0
SUN_Y        = -1.5
SUN_STRENGTH = 1

def make_colormap(h):
    ramp = [
        (0,   (15,  30,  60)),
        (85,  (20,  45,  80)),
        (105, (30,  55,  90)),
        (112, (180, 160, 100)),
        (118, (155, 140, 85)),
        (125, (85,  90,  50)),
        (145, (60,  80,  35)),
        (165, (45,  65,  25)),
        (185, (55,  60,  30)),
        (200, (90,  75,  50)),
        (212, (100, 85,  60)),
        (222, (110, 100, 80)),
        (235, (130, 120, 105)),
        (247, (190, 185, 175)),
        (255, (210, 210, 210)),
    ]
    h_f   = h.astype(np.float32)
    color = np.zeros((*h.shape, 3), dtype=np.float32)
    for i in range(len(ramp) - 1):
        h0, c0 = ramp[i]
        h1, c1 = ramp[i + 1]
        mask = (h_f >= h0) & (h_f < h1)
        t = (h_f - h0) / (h1 - h0)
        for ch in range(3):
            color[..., ch] += mask * (c0[ch] + t * (c1[ch] - c0[ch]))

    h_f32 = h.astype(np.float32)
    dx    = np.roll(h_f32, -1, axis=1) - np.roll(h_f32, 1, axis=1)
    dy    = np.roll(h_f32, -1, axis=0) - np.roll(h_f32, 1, axis=0)
    shade = dx * SUN_X + dy * SUN_Y
    shade = shade / (np.max(np.abs(shade)) + 1e-6)
    shade = np.clip(shade * SUN_STRENGTH + 1.0, 0.3, 1.3)
    color *= shade[..., np.newaxis]
    return np.clip(color, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ #
#  No city — pure terrain
# ------------------------------------------------------------------ #
if not GENERATE_CITY:
    print("Skipping city generation...")
    print("Generating colormap...")
    final_color  = make_colormap(noise)
    material_map = np.full((HEIGHT, WIDTH), MAT_TERRAIN, dtype=np.uint8)

    print("Saving...")
    Image.fromarray(noise,        mode="L").save("heightmap.png")
    Image.fromarray(final_color,  mode="RGB").save("colormap.png")
    Image.fromarray(material_map, mode="L").save("materialmap.png")
    print(f"Done! (seed: {SEED})")
    exit()

# ------------------------------------------------------------------ #
#  City zone mask
# ------------------------------------------------------------------ #
print("Generating city zones...")
city_mask = (noise >= CITY_TERRAIN_MIN) & (noise <= CITY_TERRAIN_MAX)
city_zone = city_mask

# ------------------------------------------------------------------ #
#  Manhattan Voronoi
# ------------------------------------------------------------------ #
print(f"Computing Manhattan Voronoi ({N_CITY_SEEDS} seeds, {WIDTH}x{HEIGHT} map)...")

seed_xy = rng.random((N_CITY_SEEDS, 2)) * np.array([WIDTH, HEIGHT])
tree    = KDTree(seed_xy)

cell_heights = rng.integers(CITY_BLOCK_HEIGHT[0], CITY_BLOCK_HEIGHT[1], size=N_CITY_SEEDS)

cell_type = rng.integers(0, 4, size=N_CITY_SEEDS)

concrete_r = rng.integers(110, 145, size=N_CITY_SEEDS)
concrete_g = rng.integers(110, 140, size=N_CITY_SEEDS)
concrete_b = rng.integers(115, 148, size=N_CITY_SEEDS)

glass_r    = rng.integers(100, 130, size=N_CITY_SEEDS)
glass_g    = rng.integers(120, 150, size=N_CITY_SEEDS)
glass_b    = rng.integers(130, 165, size=N_CITY_SEEDS)

brick_r    = rng.integers(130, 170, size=N_CITY_SEEDS)
brick_g    = rng.integers(85,  115, size=N_CITY_SEEDS)
brick_b    = rng.integers(65,  95,  size=N_CITY_SEEDS)

clad_r     = rng.integers(150, 185, size=N_CITY_SEEDS)
clad_g     = rng.integers(140, 170, size=N_CITY_SEEDS)
clad_b     = rng.integers(110, 140, size=N_CITY_SEEDS)

cell_r = np.where(cell_type == 0, concrete_r,
         np.where(cell_type == 1, glass_r,
         np.where(cell_type == 2, brick_r, clad_r))).astype(np.float32)
cell_g = np.where(cell_type == 0, concrete_g,
         np.where(cell_type == 1, glass_g,
         np.where(cell_type == 2, brick_g, clad_g))).astype(np.float32)
cell_b = np.where(cell_type == 0, concrete_b,
         np.where(cell_type == 1, glass_b,
         np.where(cell_type == 2, brick_b, clad_b))).astype(np.float32)

ys_grid, xs_grid = np.mgrid[0:HEIGHT, 0:WIDTH]
all_coords       = np.column_stack([xs_grid.ravel(), ys_grid.ravel()])

CHUNK = 2_000_000
n_px  = WIDTH * HEIGHT
cell_idx = np.empty(n_px, dtype=np.int32)

for start in range(0, n_px, CHUNK):
    end = min(start + CHUNK, n_px)
    _, cell_idx[start:end] = tree.query(all_coords[start:end], p=1)
    print(f"  {end:,} / {n_px:,} pixels", end="\r")

print()
cell_idx = cell_idx.reshape(HEIGHT, WIDTH)

# ------------------------------------------------------------------ #
#  Road network
# ------------------------------------------------------------------ #
print("Generating road network...")

edge = (
    (np.roll(cell_idx, -1, axis=1) != cell_idx) |
    (np.roll(cell_idx,  1, axis=1) != cell_idx) |
    (np.roll(cell_idx, -1, axis=0) != cell_idx) |
    (np.roll(cell_idx,  1, axis=0) != cell_idx)
)

road_core = edge & city_zone

def dilate(mask, iters):
    m = mask.copy()
    for _ in range(iters):
        m = (m |
             np.roll(m,  1, axis=0) | np.roll(m, -1, axis=0) |
             np.roll(m,  1, axis=1) | np.roll(m, -1, axis=1))
    return m

road_wide      = dilate(road_core, ROAD_WIDTH)     & city_zone
sidewalk_strip = dilate(road_core, ROAD_WIDTH + 2) & city_zone & ~road_wide

# ------------------------------------------------------------------ #
#  Apply buildings to heightmap
# ------------------------------------------------------------------ #
voronoi_heights = cell_heights[cell_idx]

final_height = noise.astype(np.float32).copy()

building_pixels = city_mask & ~road_wide & ~sidewalk_strip
final_height[building_pixels] += voronoi_heights[building_pixels]

final_height[road_wide]      = noise[road_wide].astype(np.float32) - 1
final_height[sidewalk_strip] = noise[sidewalk_strip].astype(np.float32)

final_height = np.clip(final_height, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ #
#  Colormap
# ------------------------------------------------------------------ #
print("Generating colormap...")
terrain_color = make_colormap(final_height)

building_r = cell_r[cell_idx]
building_g = cell_g[cell_idx]
building_b = cell_b[cell_idx]

h_f32  = final_height.astype(np.float32)
dx     = np.roll(h_f32, -1, axis=1) - np.roll(h_f32, 1, axis=1)
dy     = np.roll(h_f32, -1, axis=0) - np.roll(h_f32, 1, axis=0)
shade  = dx * SUN_X + dy * SUN_Y
shade  = shade / (np.max(np.abs(shade)) + 1e-6)
shade  = np.clip(shade * SUN_STRENGTH + 1.0, 0.3, 1.3)

building_color = np.stack([
    np.clip(building_r * shade, 0, 255).astype(np.uint8),
    np.clip(building_g * shade, 0, 255).astype(np.uint8),
    np.clip(building_b * shade, 0, 255).astype(np.uint8),
], axis=-1)

final_color = terrain_color.copy()
final_color[building_pixels] = building_color[building_pixels]

swalk_shade = np.clip(shade[sidewalk_strip], 0.5, 1.2)
final_color[sidewalk_strip] = np.stack([
    np.clip(160 * swalk_shade, 0, 255),
    np.clip(155 * swalk_shade, 0, 255),
    np.clip(148 * swalk_shade, 0, 255),
], axis=-1).astype(np.uint8)

road_shade = np.clip(shade[road_wide], 0.6, 1.1)
final_color[road_wide] = np.stack([
    np.clip(ROAD_COLOR[0] * road_shade, 0, 255),
    np.clip(ROAD_COLOR[1] * road_shade, 0, 255),
    np.clip(ROAD_COLOR[2] * road_shade, 0, 255),
], axis=-1).astype(np.uint8)

# ------------------------------------------------------------------ #
#  Material map
# ------------------------------------------------------------------ #
print("Generating material map...")
material_map = np.full((HEIGHT, WIDTH), MAT_TERRAIN, dtype=np.uint8)
material_map[building_pixels] = MAT_BUILDING
material_map[road_wide]       = MAT_ROAD
material_map[sidewalk_strip]  = MAT_SIDEWALK

# ------------------------------------------------------------------ #
#  Save
# ------------------------------------------------------------------ #
print("Saving...")
Image.fromarray(final_height, mode="L").save("../assets/heightmap.png")
Image.fromarray(final_color,  mode="RGB").save("../assets/colormap.png")
Image.fromarray(material_map, mode="L").save("../assets/materialmap.png")
print(f"Done! heightmap.png + colormap.png + materialmap.png saved.  (seed: {SEED})")