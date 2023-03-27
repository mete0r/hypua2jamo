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
#include "d2c-tree.inc"


void hypua_decoder_init_d2c(void *decoder) {
	hypua_decoder_init(
			decoder,
			&node_root,
			nodelist,
			sizeof(nodelist) / sizeof(nodelist[0])
	);
}


size_t hypua_d2c_ucs2_calcsize(const uint16_t *src, size_t srclen) {
	size_t dstlen = 0;
	struct Decoder decoder;
	hypua_decoder_init_d2c(&decoder);
	dstlen += hypua_decoder_calcsize_ucs2(&decoder, src, srclen);
	dstlen += hypua_decoder_calcsize_flush(&decoder);
	return dstlen;
}


size_t hypua_d2c_ucs2_decode(const uint16_t *src, size_t srclen, uint16_t *dst) {
	struct Decoder decoder;
	uint16_t *dst_begin = dst;

	hypua_decoder_init_d2c(&decoder);
	dst += hypua_decoder_decode_ucs2(&decoder, src, srclen, dst);
	dst += hypua_decoder_decode_flush_ucs2(&decoder, dst);
	return dst - dst_begin;
}


size_t hypua_d2c_ucs4_calcsize(const uint32_t *src, size_t srclen) {
	size_t dstlen = 0;
	struct Decoder decoder;
	hypua_decoder_init_d2c(&decoder);
	dstlen += hypua_decoder_calcsize_ucs4(&decoder, src, srclen);
	dstlen += hypua_decoder_calcsize_flush(&decoder);
	return dstlen;
}


size_t hypua_d2c_ucs4_decode(const uint32_t *src, size_t srclen, uint32_t *dst) {
	struct Decoder decoder;
	uint32_t *dst_begin = dst;

	hypua_decoder_init_d2c(&decoder);
	dst += hypua_decoder_decode_ucs4(&decoder, src, srclen, dst);
	dst += hypua_decoder_decode_flush_ucs4(&decoder, dst);
	return dst - dst_begin;
}
