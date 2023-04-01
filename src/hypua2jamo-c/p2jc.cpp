#include <stdio.h>
#include <stddef.h>
#include <string.h>

#include "config.h"

#ifdef HAVE_STDINT_H
#include <stdint.h>
#else
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#endif

#include "p2jc-table.h"


template <typename codepoint_t>
inline size_t p2jc_calcsize(const codepoint_t *src, size_t srclen) {
	const unsigned short *jamo_seq;
	size_t ret = 0;
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
inline size_t p2jc_encode(const codepoint_t *src, size_t srclen, codepoint_t *dst) {
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


extern "C" size_t hypua_p2jc_ucs2_calcsize(const uint16_t *src, size_t srclen) {
	return p2jc_calcsize(src, srclen);
}


extern "C" size_t hypua_p2jc_ucs2_encode(const uint16_t *src, size_t srclen, uint16_t *dst) {
	return p2jc_encode(src, srclen, dst);
}


extern "C" size_t hypua_p2jc_ucs4_calcsize(const uint32_t *src, size_t srclen) {
	return p2jc_calcsize(src, srclen);
}


extern "C" size_t hypua_p2jc_ucs4_encode(const uint32_t *src, size_t srclen, uint32_t *dst) {
	return p2jc_encode(src, srclen, dst);
}
