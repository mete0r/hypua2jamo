#include <stdio.h>
#include <string.h>

#include "config.h"

#ifdef HAVE_INTTYPES_H
#include <inttypes.h>
#else
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#endif


#include "p2jd-table.h"
#include "p2jx.hpp"


extern "C" int hypua_p2jd_ucs2_calcsize(const uint16_t *src, int srclen) {
	return calcsize(src, srclen);
}


extern "C" int hypua_p2jd_ucs2_encode(const uint16_t *src, int srclen, uint16_t *dst) {
	printf("hypua_p2jd_ucs2_encode\n");
	return encode(src, srclen, dst);
}


extern "C" int hypua_p2jd_ucs4_calcsize(const uint32_t *src, int srclen) {
	return calcsize(src, srclen);
}


extern "C" int hypua_p2jd_ucs4_encode(const uint32_t *src, int srclen, uint32_t *dst) {
	return encode(src, srclen, dst);
}
