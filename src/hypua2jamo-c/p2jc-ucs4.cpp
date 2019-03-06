#include <string.h>

#include "config.h"

#ifdef HAVE_INTTYPES_H
#include <inttypes.h>
#else
typedef unsigned int uint32_t;
#endif


typedef uint32_t codepoint_t;

#include "p2jc-table.h"
#include "p2jx.hpp"


extern "C" int hypua_p2jc_ucs4_calcsize(const codepoint_t *src, int srclen) {
	return calcsize(src, srclen);
}


extern "C" int hypua_p2jc_ucs4_encode(const codepoint_t *src, int srclen, codepoint_t *dst) {
	return encode(src, srclen, dst);
}
