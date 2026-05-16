#include <SFML/Graphics.hpp>
#include <iostream>
#include <chrono>
#include <math.h>

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

	map.addEntity(512,512,"entity.png");
	map.addEntity(512,312,"buildingcolor.png");

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

		//handle FPS camera MOVE TO CAMERA CLASS
		int mx = (int)player.pposition.x % map.mapWidth;
		int my = (int)player.pposition.y % map.mapHeight;
		if (mx < 0) mx += map.mapWidth;
		if (my < 0) my += map.mapHeight;
		float cameraHeight = map.heightMap[my * map.mapWidth + mx] + 2.f;
        
		//UPDATE
		player.Update(deltaTimeSeconds,window);

		
		//render here
		map.clearBuffer();
		map.render(player.pposition, player.pangle, cameraHeight,player.horizon,3000,4000,WIDTH,HEIGHT,window);
		map.updateTexture();
		window.clear();
		window.draw(map.sprite);
        window.display();
		//std::cout << 1.f / deltaTimeSeconds << std::endl;
    }

    return 0;
}