#include <string.h>

#include "codepoints_p2j.h"


int hypua2jamo_calc_translation(const codepoint_t *src, int srclen) {
	codepoint_t *jamo_seq;
	int ret = 0;
	const codepoint_t *src_end = src + srclen;
	while (src++ < src_end) {
		jamo_seq = lookup(*src);
		if (jamo_seq != NULL) {
			ret += jamo_seq[0];
		}
	}
	return ret;
}


int hypua2jamo_translate_codepoints(const codepoint_t *src, int srclen, codepoint_t *dst) {
	codepoint_t *jamo_seq;
	int jamo_len;
	const codepoint_t *src_end = src + srclen;
	while (src++ < src_end) {
		jamo_seq = lookup(*src);
		if (jamo_seq == NULL) {
			*(dst++) = *src;
		} else {
			jamo_len = *(jamo_seq++);
			memcpy(dst, jamo_seq, jamo_len * sizeof(codepoint_t));
			dst += jamo_len;
		}
	}
	return 0;
}
