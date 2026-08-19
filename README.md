# VoxelSpace Engine

A software voxel renderer inspired by the terrain engine behind Novalogic's  
Comanche (1992) — one of the most creative rendering hacks in game history.  
Built in C++ with SFML, with procedural terrain and city generation.

## What it does

- First-person voxel space renderer using column casting — the same core  
  trick Comanche used to render terrain on a 486 in 1992
- Procedural heightmap-based terrain and city generation via a Python script
- Textured terrain with manually written UV mapping
- Fog and culling for performance and atmosphere

## Tech

- **Language:** C++
- **Library:** SFML (texture loading, windowing)
- **Renderer:** Software — no GPU pipeline, all CPU column casting
- **Generation:** Python heightmap generator feeding into the engine

## Building

```bash
# clone the repo
git clone --recurse-submodules https://github.com/Ragegithu/Voxel-Space-Engine
cd Voxel-Space-Engine

# build (cmake)
cmake -S . -B buildfolder
cmake --build buildfolder

#run
cd buildfolder ./mygame
```

## Why Comanche

I've always been obsessed with how old games did so much with so little.  
Comanche shipped a first person terrain renderer in 1992 on hardware that  
could barely run a spreadsheet. Recreating that with a modern twist —  
procedural generation, textures, city environments — felt like the right  
kind of challenge.

## Screenshots
<img width="1169" height="664" alt="Screenshot_20260819_025949" src="https://github.com/user-attachments/assets/fb8657f5-2c17-4383-8f3c-1fb66d80d008" />
<img width="736" height="733" alt="Screenshot_20260819_025927" src="https://github.com/user-attachments/assets/c799fbef-fc24-47df-b1c2-c5f50fab6e86" />
<img width="731" height="738" alt="Screenshot_20260819_025913" src="https://github.com/user-attachments/assets/64c0558b-3aac-4219-a4ca-2cc9de8439cd" />
<img width="1281" height="724" alt="Screenshot_20260819_025840" src="https://github.com/user-attachments/assets/0378495b-7652-4218-b239-d27b8c2db0e6" />
