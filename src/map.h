#pragma once

#include <SFML/Graphics.hpp>
#include <iostream>
#include <cstdint>
#include <math.h>
#include <string>

#include "ntypes.h"

struct Entity
{
friend class Map;
private:
	float rdx;
	float rdy;
	float entityDepth;

	int mex;
    int mey;

    float entityWorldSize = 20.f;
    float entityWorldZ;

    int spriteSize;

    float pl_x;
    float pr_x;
    float ddx;
    int screen_x;

    int screen_y;

    int entityLeft;
    int entityRight;
    int entityTop;
    int entityBottom;
    bool entityRendered;
    
    sf::Image entityImg;

    //entity values
public:
    std::string imageName;
    std::vector<sf::Color> entityColor;
    float ex,ey;
};

class Map
{
public:
    Map();

    void addEntity(float xpos, float ypos, std::string imageName);

    template<typename T>
    void loadImageArray(sf::Image& image, std::vector<T>& buffer, std::string imageName);
    
    void set_pixel(std::vector<std::uint8_t>& pixel, int x, int y, std::uint8_t r, std::uint8_t g,std::uint8_t b);

    void DrawVerticalLine(int x, int top,  int bottom, int screen_height, sf::Color color, int mx, int my, float dx, float dy,std::vector<Entity>& es);
    
    void render(point p, float angle, float height, float horizon, float scale_height, int distance, int screen_width, int screen_height, sf::RenderWindow& window);

    void clearBuffer();


    void updateTexture();

    std::vector<std::uint8_t> pixel; // pixel buffer

    int mapWidth;
    int mapHeight;

    int width = 800;
    int height = 800;

    sf::Image heightMapImg, colorMapImg, materialMapImg;

	sf::Image buildingColorImg;

    std::vector<float> heightMap;
    std::vector<sf::Color> colorMap;
    std::vector<uint8_t> materialMap;

	std::vector<sf::Color> bcolor;

	sf::Texture texture;
    sf::Sprite sprite;

    std::vector<Entity> entities;
};

template <typename T>
inline void Map::loadImageArray(sf::Image& image, std::vector<T>& buffer, std::string imageName)
{
    if(!image.loadFromFile(imageName))
    {
        std::cout << "couldnt find image: " << imageName << std::endl;
    }
    int w = image.getSize().x;
    int h = image.getSize().y;
    buffer.resize(w * h);

    for(int y = 0; y < h; y++)
    {
        for(int x = 0; x < w; x++)
        {
            if constexpr (std::is_same_v<T,sf::Color>)
            {
                buffer[y * w + x] = image.getPixel(x,y);
            }
            else
            {
                buffer[y * w + x] = image.getPixel(x,y).r;
            }
        }
    }
}
