#include <SFML/Graphics.hpp>
#include <iostream>
#include <chrono>
#include <cmath>

#include "ntypes.h"
#include "map.h"
#include "player.h"

#include "imgui.h"
#include "imgui-SFML.h"
#include "imguiThemes.h"

bool level = 0;
float stime = 0;

int main()
{
	sf::RenderWindow window(sf::VideoMode(WIDTH, HEIGHT), "Voxel Space");

	sf::Clock clock;

	Map map;

	map.loadImageArray(map.heightMapImg,map.heightMap,"../assets/heightmap1.png",true);
	map.loadImageArray(map.colorMapImg,map.colorMap,"../assets/colormap1.png",false);
	map.loadImageArray(map.buildingColorImg,map.bcolor,"../assets/buildingcolor1.png",false);
	map.loadImageArray(map.materialMapImg,map.materialMap,"../assets/materialmap1.png",false);

	fPlayer player;
	player.SnapToGround(map.mapWidth,map.mapHeight,map.heightMap);

	map.addEntity(10,10,"../assets/entity.png");

    while (window.isOpen())
    {
        sf::Event event;
        while (window.pollEvent(event))
        {
            if (event.type == sf::Event::Closed || sf::Keyboard::isKeyPressed(sf::Keyboard::Escape))
                window.close();
            else if (event.type == sf::Event::Resized)
            {
                sf::FloatRect visibleArea(0, 0, event.size.width, event.size.height);
                window.setView(sf::View(visibleArea));

            }
        }

		
        sf::Time deltaTime = clock.restart();
        float deltaTimeSeconds = std::min(std::max(deltaTime.asSeconds(), 0.f), 1.f);
		window.setMouseCursorVisible(false);
		window.setMouseCursorGrabbed(true);

		stime += deltaTimeSeconds;
		
		if(sf::Keyboard::isKeyPressed(sf::Keyboard::H) && level && stime > 1)
		{
			map.loadImageArray(map.heightMapImg,map.heightMap,"../assets/heightmap1.png",true);
			map.loadImageArray(map.colorMapImg,map.colorMap,"../assets/colormap1.png",false);
			map.loadImageArray(map.buildingColorImg,map.bcolor,"../assets/buildingcolor1.png",false);
			map.loadImageArray(map.materialMapImg,map.materialMap,"../assets/materialmap1.png",false);

			level = false;
			stime = 0;
		}
		else if(sf::Keyboard::isKeyPressed(sf::Keyboard::H) && !level && stime > 1)
		{
			map.loadImageArray(map.heightMapImg,map.heightMap,"../assets/heightmap.png",true);
			map.loadImageArray(map.colorMapImg,map.colorMap,"../assets/colormap.png",false);
			map.loadImageArray(map.buildingColorImg,map.bcolor,"../assets/buildingcolor1.png",false);
			map.loadImageArray(map.materialMapImg,map.materialMap,"../assets/materialmap.png",false);

			level = true;
			stime = 0;
		}
        
		//UPDATE
		player.Update(deltaTimeSeconds,window);


		//handle FPS camera MOVE TO Player CLASS
		int mx = (int)player.pposition.x % map.mapWidth;
		int my = (int)player.pposition.y % map.mapHeight;
		if (mx < 0) mx += map.mapWidth;
		if (my < 0) my += map.mapHeight;
		
		float offset = 2.f;
		float maxStep = 3.f;

		float targetHeight = map.heightMap[my * map.mapWidth + mx] + offset;
		player.cameraHeight = nlerp(player.cameraHeight, targetHeight, deltaTimeSeconds * 10);
		
		if(targetHeight > player.cameraHeight + maxStep)
		{
			player.pposition.x = player.lastX;
    		player.pposition.y = player.lastY;
		}
		else
		{
		}
		
		//render here
		map.skyColor = {10,10,25};
		map.clearBuffer();
		map.render(player.pposition, player.pangle, player.cameraHeight,player.horizon,2000,4000,320,180,window);
		map.updateTexture();

		map.sprite.setScale(WIDTH / 320, HEIGHT / 180);
		

		window.clear();
		window.draw(map.sprite);
		
        window.display();
		std::cout << 1.f / deltaTimeSeconds << std::endl;
    }

    return 0;
}