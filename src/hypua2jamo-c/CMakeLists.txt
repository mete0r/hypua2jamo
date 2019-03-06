cmake_minimum_required(VERSION 3.0.0)
project (HanyangPUA)
add_library(HanyangPUA STATIC p2jc-ucs4.cpp p2jc-ucs2.cpp p2jd-ucs4.cpp p2jd-ucs2.cpp jx2p.cpp jc2p.c jd2p.c)
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
