#include <stddef.h>
#include <stdio.h>

#include "config.h"

#ifdef HAVE_INTTYPES_H
#include <inttypes.h>
#else
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#endif

#include "jx2p.h"
#include "jd2p-tree.inc"


void hypua_decoder_init_jd2p(void *decoder) {
	hypua_decoder_init(
			decoder,
			&node_root,
			nodelist,
			sizeof(nodelist) / sizeof(nodelist[0])
	);
}


int hypua_jd2p_ucs2_calcsize(const uint16_t *src, int srclen) {
	int dstlen = 0;
	struct Decoder decoder;
	hypua_decoder_init_jd2p(&decoder);
	dstlen += hypua_decoder_calcsize_ucs2(&decoder, src, srclen);
	dstlen += hypua_decoder_calcsize_flush(&decoder);
	return dstlen;
}


int hypua_jd2p_ucs2_decode(const uint16_t *src, int srclen, uint16_t *dst) {
	int dstlen = 0;
	struct Decoder decoder;
	uint16_t *dst_begin = dst;

	hypua_decoder_init_jd2p(&decoder);
	dst += hypua_decoder_decode_ucs2(&decoder, src, srclen, dst);
	dst += hypua_decoder_decode_flush_ucs2(&decoder, dst);
	return dst - dst_begin;
}


int hypua_jd2p_ucs4_calcsize(const uint32_t *src, int srclen) {
	int dstlen = 0;
	struct Decoder decoder;
	hypua_decoder_init_jd2p(&decoder);
	dstlen += hypua_decoder_calcsize_ucs4(&decoder, src, srclen);
	dstlen += hypua_decoder_calcsize_flush(&decoder);
	return dstlen;
}


int hypua_jd2p_ucs4_decode(const uint32_t *src, int srclen, uint32_t *dst) {
	int dstlen = 0;
	struct Decoder decoder;
	uint32_t *dst_begin = dst;

	hypua_decoder_init_jd2p(&decoder);
	dst += hypua_decoder_decode_ucs4(&decoder, src, srclen, dst);
	dst += hypua_decoder_decode_flush_ucs4(&decoder, dst);
	return dst - dst_begin;
}
