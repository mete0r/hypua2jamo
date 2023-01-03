#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "config.h"

#ifdef HAVE_INTTYPES_H
#include <inttypes.h>
#else
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#endif


#include "p2jd-table.h"


template <typename codepoint_t>
inline int p2jd_calcsize(const codepoint_t *src, int srclen) {
	const unsigned short *jamo_seq;
	int ret = 0;
	const codepoint_t *src_end = src + srclen;
	for (; src < src_end; ++src) {
		jamo_seq = lookup(*src);
		if (jamo_seq != NULL) {
			ret += jamo_seq[0];
		} else {
			ret += 1;
		}
	}
	return ret;
}


template <typename codepoint_t>
inline ptrdiff_t p2jd_encode(const codepoint_t *src, int srclen, codepoint_t *dst) {
	const unsigned short *jamo_seq;
	int jamo_len;
	const codepoint_t *src_end = src + srclen;
	const codepoint_t *dst_start = dst;
	for (; src < src_end; ++src) {
		jamo_seq = lookup(*src);
		if (jamo_seq == NULL) {
			*(dst++) = *src;
		} else {
			jamo_len = *(jamo_seq++);
			while (jamo_len-- > 0) {
				*(dst++) = *(jamo_seq++);
			}
		}
	}
	return dst - dst_start;
}


extern "C" int hypua_p2jd_ucs2_calcsize(const uint16_t *src, int srclen) {
	return p2jd_calcsize(src, srclen);
}


extern "C" ptrdiff_t hypua_p2jd_ucs2_encode(const uint16_t *src, int srclen, uint16_t *dst) {
	return p2jd_encode(src, srclen, dst);
}


extern "C" int hypua_p2jd_ucs4_calcsize(const uint32_t *src, int srclen) {
	return p2jd_calcsize(src, srclen);
}


extern "C" ptrdiff_t hypua_p2jd_ucs4_encode(const uint32_t *src, int srclen, uint32_t *dst) {
	return p2jd_encode(src, srclen, dst);
}
