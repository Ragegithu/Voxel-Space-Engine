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


int main()
{
		
	sf::RenderWindow window(sf::VideoMode(WIDTH, HEIGHT), "Voxel Space");
	sf::Clock clock;

	Map map;
	fPlayer player;
	player.SnapToGround(map.mapWidth,map.mapHeight,map.heightMap);

	map.addEntity(0,0,"../assets/entity.png");
	
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
		
		if(targetHeight > player.cameraHeight + maxStep)
		{
			player.pposition.x = player.lastX;
    		player.pposition.y = player.lastY;
		}
		else
		{
			player.cameraHeight = nlerp(player.cameraHeight, targetHeight, deltaTimeSeconds * 10);
		}
		
		//render here
		map.clearBuffer();
		map.render(player.pposition, player.pangle, player.cameraHeight,player.horizon,2000,2000,WIDTH,HEIGHT,window);
		map.updateTexture();
		window.clear();
		window.draw(map.sprite);
        window.display();
		std::cout << 1.f / deltaTimeSeconds << std::endl;
    }

    return 0;
}