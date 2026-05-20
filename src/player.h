#pragma once

#include <SFML/Graphics.hpp>
#include <iostream>
#include <cmath>

#include "ntypes.h"
#include "conf.h"

class fPlayer
{
public:
    fPlayer();

    void Update(float deltaTimeSeconds, sf::RenderWindow& window);
    void SnapToGround(int mapWidth, int mapHeight, std::vector<float> heightMap);

    
    
    float pspeed =  300.f;
    float psens  = 0.003f;
    
    float offset = 2.0f;


    point pposition = {0,0};
    float pangle = 0;
    float cameraHeight;
	float horizon = 0;
    float lastX,lastY;
    
private:
    sf::Vector2i mousePos;
};