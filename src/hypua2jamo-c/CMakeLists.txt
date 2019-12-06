cmake_minimum_required(VERSION 2.8.12.2)
project (HanyangPUA)
add_library(HanyangPUA STATIC c2d.cpp p2jc.cpp d2c.c p2jd.cpp jx2p.cpp jc2p.c jd2p.c)
set_property(TARGET HanyangPUA PROPERTY POSITION_INDEPENDENT_CODE ON)

include(CheckIncludeFile)
include(CheckTypeSize)

check_include_file(inttypes.h HAVE_INTTYPES_H)
check_type_size(long TYPESIZE_LONG)
check_type_size(int TYPESIZE_INT)
check_type_size(short TYPESIZE_SHORT)
check_type_size(wchar_t TYPESIZE_WCHAR_T)

configure_file(config.h.in config.h)
include_directories(${CMAKE_CURRENT_BINARY_DIR})
