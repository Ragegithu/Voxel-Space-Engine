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

    void CameraPosition(int mx, int my);
    void Update(float deltaTimeSeconds, sf::RenderWindow& window);

    float pspeed =  300.f;
    float psens  = 0.003f;


    point pposition = {0,0};
    float pangle = 0;
    sf::Vector2i mousePos;
    float cameraHeight;
	float horizon = 0;
};