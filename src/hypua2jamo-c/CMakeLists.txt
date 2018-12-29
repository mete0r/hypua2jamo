cmake_minimum_required(VERSION 3.0.0)
project (HanyangPUA)
add_library(HanyangPUA STATIC p2jc4.c p2jd4.c p2jc2.c p2jd2.c)
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
