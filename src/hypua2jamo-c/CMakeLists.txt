cmake_minimum_required(VERSION 3.0.0)
project (HanyangPUA)
add_library(HanyangPUA STATIC p2jc4.c p2jd4.c p2jc2.c p2jd2.c)
set_property(TARGET HanyangPUA PROPERTY POSITION_INDEPENDENT_CODE ON)
