#include <string.h>

#include "config.h"

#ifdef HAVE_INTTYPES_H
#include <inttypes.h>
#else
typedef unsigned short uint16_t;
#endif


typedef uint16_t codepoint_t;

#include "p2jd-table.h"


int hypua_p2jd2_translate_calcsize(const codepoint_t *src, int srclen) {
	const codepoint_t *jamo_seq;
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


int hypua_p2jd2_translate(const codepoint_t *src, int srclen, codepoint_t *dst) {
	const codepoint_t *jamo_seq;
	int jamo_len;
	const codepoint_t *src_end = src + srclen;
	const codepoint_t *dst_start = dst;
	for (; src < src_end; ++src) {
		jamo_seq = lookup(*src);
		if (jamo_seq == NULL) {
			*(dst++) = *src;
		} else {
			jamo_len = *(jamo_seq++);
			memcpy(dst, jamo_seq, jamo_len * sizeof(codepoint_t));
			dst += jamo_len;
		}
	}
	return dst - dst_start;
}
