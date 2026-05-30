#pragma once
#include <iostream>


struct point{float x, y;};
struct point3D{float x,y,z;};

inline float nlerp(float a, float b, float t)
{
    return a + (b - a) * t;
}