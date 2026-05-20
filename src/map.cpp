#include "map.h"

Map::Map()
{   

    pixel.resize(width * height * 4, 0);

	if (!texture.create(width, height)) {
		std::cout << "failed to create pixel buffer" << std::endl;
	}
	sprite.setTexture(texture);



	loadImageArray(heightMapImg,heightMap,"../assets/heightmap.png");
	loadImageArray(colorMapImg,colorMap,"../assets/colormap.png");
	loadImageArray(buildingColorImg,bcolor,"../assets/buildingcolor.png");
	loadImageArray(materialMapImg,materialMap,"../assets/materialmap.png");

	mapWidth = heightMapImg.getSize().x;
	mapHeight = heightMapImg.getSize().y;
}

void Map::addEntity(float xpos, float ypos, std::string imageName)
{
	Entity e;
	e.ex = xpos;
	e.ey = ypos;
	e.imageName = imageName;
	loadImageArray(e.entityImg,e.entityColor,imageName);
	entities.push_back(e);
}

void Map::set_pixel(std::vector<std::uint8_t>& pixel, int x, int y, std::uint8_t r, std::uint8_t g,std::uint8_t b)
{
	
    if(x < 0 || x >= width || y < 0 || y >= height)
    {
        std::cout << "set_pixel out of bounds: " << x << " " << y << std::endl;
        return;
    }
	int index = (y * width + x) * 4;
	pixel[index + 0] = r;
	pixel[index + 1] = g;
	pixel[index + 2] = b;
	pixel[index + 3] = 255;
}
void Map::DrawVerticalLine(int x, int top, int bottom, int screen_height, sf::Color color, int mx, int my,float dx, float dy, std::vector<Entity>& es)
{
	int topb = top;
    if (top < 0)
	{
		top = 0;
	}
    if (bottom > screen_height) bottom = screen_height; 

	uint8_t mat = materialMap[my * mapWidth + mx];

	int columnHeight = bottom - top;

    for (int y = top; y < bottom; y++)
	{
		bool blocked = false;
		for(Entity& e : es)
		{
			if(e.entityRendered &&x >= e.entityLeft && x < e.entityRight && y >= e.entityTop && y < e.entityBottom)
			{	
				blocked = true;
				break;
			}
		}
		if(blocked) continue;
		if(mat == 1 || mat == 4)
		{
			float t = (columnHeight > 0) ? (float)(y - (bottom)) / columnHeight : 0.0f;
			
			//int texX = mx / 1 % 128;//(std::abs(dx) > std::abs(dy)) ? mx % 128 : my % 128;
			int texX = (mat == 4) ? my % 128 : mx % 128;
			int texY = (int)(heightMap[my * mapWidth + mx] + t * 128) % 128;
            sf::Color texColor = bcolor[texY * 128 + texX];
			set_pixel(pixel, x, y, texColor.r, texColor.g, texColor.b);
		}
		else
		{
			//terrain
			set_pixel(pixel, x, y, color.r, color.g, color.b);
		}
	}
}
void Map::render(point p, float angle, float height, float horizon, float scale_height, int distance, int screen_width, int screen_height, sf::RenderWindow& window)
{
	point pleft,pright;
	float dx,dy;
	float heightOnScreen;


	std::vector<int> ybuffer(screen_width, screen_height);
	std::vector<float> zbuffer(screen_width, (float) distance);
	std::vector<bool> entityPixel(screen_width * screen_height, false);

	float cosine = cos(angle);
	float sine = sin(angle);

	float step = 1.0f;

	
	// precompute Entities
	for(Entity& e : entities){
		e.rdx = e.ex - p.x;
		e.rdy = e.ey - p.y;
		e.entityDepth = -(e.rdx * sine) - (e.rdy * cosine);

		e.mex = (int)e.ex % mapWidth;
    	e.mey = (int)e.ey % mapHeight;

	
	
    	e.pl_x = (-cosine * e.entityDepth - sine * e.entityDepth) + p.x;
    	e.pr_x = ( cosine * e.entityDepth - sine * e.entityDepth) + p.x;
    	e.ddx   = (e.pr_x - e.pl_x) / screen_width;
    
    	e.spriteSize = (int)(e.entityWorldSize / e.entityDepth * scale_height);
		e.entityWorldZ = heightMap[e.mey * mapWidth + e.mex] + 0.5;
    	e.screen_x = (int)((e.ex - e.pl_x) / e.ddx);

    	e.screen_y = (int)((height - e.entityWorldZ) / e.entityDepth * scale_height + horizon);


    	e.entityLeft   = e.screen_x - e.spriteSize / 2;
    	e.entityRight  = e.screen_x + e.spriteSize / 2;
    	e.entityTop    = e.screen_y - e.spriteSize;
    	e.entityBottom = e.screen_y;
	}

	for(float i = 1; i < distance; i+= step)
	{
		//fov 
		pleft.x = (-cosine * i - sine * i) + p.x;
		pleft.y = (sine * i - cosine * i ) + p.y;

		pright.x = ( cosine * i - sine*i) + p.x;
		pright.y = (-sine * i - cosine*i) + p.y;

		dx = (pright.x - pleft.x) / screen_width;
		dy = (pright.y - pleft.y) / screen_width;
 
		for(int j = 0; j < screen_width; j++)
		{	
			
			int mx = ((int)pleft.x) % heightMapImg.getSize().x;
			int my = ((int)pleft.y) % heightMapImg.getSize().y;
			if (mx < 0) mx += heightMapImg.getSize().x;
			if (my < 0) my += heightMapImg.getSize().y;
			
			heightOnScreen = (height - heightMap[my * mapWidth + mx]) / i * scale_height + horizon;
			int top = (int)heightOnScreen;

			if(top < ybuffer[j])
			{
    			DrawVerticalLine(j, top, ybuffer[j], screen_height, colorMap[my * mapWidth + mx],mx,my,dx,dy,entities);
				ybuffer[j] = top;
			}
			zbuffer[j] = i;
			
			pleft.x += dx;
			pleft.y += dy;
		}

		//ENTITY RENDERING-------------------------------------------------------------------------
		for(Entity& e : entities){
			if(e.entityDepth > 0.5f && i >= e.entityDepth - step && i <= e.entityDepth + step)
			{
				for(int col = e.entityLeft; col < e.entityRight; col++)
				{
					if(col < 0 || col >= screen_width) continue;
					if(e.entityDepth < zbuffer[col])
					{
						for(int y = e.entityTop; y < e.entityBottom; y++)
						{
							if(y < 0 || y >= screen_height) continue;
							if(y < ybuffer[col])
							{
								int idx = y * screen_width + col;
								if(entityPixel[idx]) continue;
								int texX = (col - e.entityLeft) * 128 / e.spriteSize;
								int texY = (y - e.entityTop) * 128 / e.spriteSize;
								sf::Color eTex = e.entityColor[texX * 128 + texY];
								set_pixel(pixel,col,y,eTex.r,eTex.g,eTex.b);
								entityPixel[idx] = true;
							}
							e.entityRendered = true;
						}
					}
				}
			}
		}

		step += 0.03f ;
	}
}

void Map::clearBuffer()
{    for(int i = 0; i < width * height * 4; i += 4) {
        pixel[i+0] = 20;
        pixel[i+1] = 20;
        pixel[i+2] = 30;
        pixel[i+3] = 255;
    }
	for(Entity& e : entities)
		e.entityRendered = false;
}

void Map::updateTexture()
{
    texture.update(pixel.data());
}