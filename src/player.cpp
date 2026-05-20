#include "player.h"

fPlayer::fPlayer()
{

}

void fPlayer::SnapToGround(int mapWidth, int mapHeight, std::vector<float> heightMap)
{
    int mx = (int)pposition.x % mapWidth;
    int my = (int)pposition.y % mapHeight;
    cameraHeight = heightMap[my * mapWidth + mx] + offset;
}

void fPlayer::Update(float deltaTimeSeconds, sf::RenderWindow &window)
{

	lastX = pposition.x;
	lastY = pposition.y;



	//keyboard movement
	if(sf::Keyboard::isKeyPressed(sf::Keyboard::W))
	{
    	pposition.x -= pspeed * sin(pangle) * deltaTimeSeconds;
    	pposition.y -= pspeed * cos(pangle) * deltaTimeSeconds;
	}
	if(sf::Keyboard::isKeyPressed(sf::Keyboard::S))
	{
    	pposition.x += pspeed * sin(pangle) * deltaTimeSeconds;
    	pposition.y += pspeed * cos(pangle) * deltaTimeSeconds;
	}
	if(sf::Keyboard::isKeyPressed(sf::Keyboard::A))
	{
    	pposition.x -= pspeed * cos(pangle) * deltaTimeSeconds;
    	pposition.y += pspeed * sin(pangle) * deltaTimeSeconds;
	}
	if(sf::Keyboard::isKeyPressed(sf::Keyboard::D))
	{
    	pposition.x += pspeed * cos(pangle) * deltaTimeSeconds;
    	pposition.y -= pspeed * sin(pangle) * deltaTimeSeconds;
	}


		//mouse position
	sf::Vector2i mousePos = sf::Mouse::getPosition(window);
	sf::Mouse::setPosition(sf::Vector2i(WIDTH / 2, HEIGHT / 2), window);

	int mouseDeltaX = mousePos.x - WIDTH / 2;
	int mouseDeltaY = mousePos.y - HEIGHT / 2;

	horizon-= mouseDeltaY * psens * 100;
	pangle -= mouseDeltaX * psens;
}