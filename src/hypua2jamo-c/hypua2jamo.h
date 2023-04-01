#ifndef __hypua2jamo_h__
#define __hypua2jamo_h__

#include <stddef.h>

#ifdef _MSC_VER
#  if _MSC_VER < 1600
   typedef unsigned short    uint16_t;
   typedef unsigned int      uint32_t;
#  else
#  include <stdint.h>
#  endif
#else
#  include <stdint.h>
#endif

/* encoder */

size_t hypua_c2d_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_c2d_ucs4_encode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_c2d_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_c2d_ucs2_encode(const uint16_t *src, size_t srclen, uint16_t *dst);
size_t hypua_p2jc_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_p2jc_ucs4_encode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_p2jc_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_p2jc_ucs2_encode(const uint16_t *src, size_t srclen, uint16_t *dst);
size_t hypua_p2jd_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_p2jd_ucs4_encode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_p2jd_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_p2jd_ucs2_encode(const uint16_t *src, size_t srclen, uint16_t *dst);

/* decoder */

size_t hypua_d2c_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_d2c_ucs4_decode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_d2c_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_d2c_ucs2_decode(const uint16_t *src, size_t srclen, uint16_t *dst);
size_t hypua_jc2p_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_jc2p_ucs4_decode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_jc2p_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_jc2p_ucs2_decode(const uint16_t *src, size_t srclen, uint16_t *dst);
size_t hypua_jd2p_ucs4_calcsize(const uint32_t *src, size_t srclen);
size_t hypua_jd2p_ucs4_decode(const uint32_t *src, size_t srclen, uint32_t *dst);
size_t hypua_jd2p_ucs2_calcsize(const uint16_t *src, size_t srclen);
size_t hypua_jd2p_ucs2_decode(const uint16_t *src, size_t srclen, uint16_t *dst);

/* decoder generic */

int hypua_decoder_alloc_size();
void hypua_decoder_init_d2c(void *decoder);
void hypua_decoder_init_jc2p(void *decoder);
void hypua_decoder_init_jd2p(void *decoder);
void hypua_decoder_init(
		void *decoder,
		const void *root,
		const void *nodelist,
		int nodelistLen
);
int hypua_decoder_getstate(void *decoder);
int hypua_decoder_setstate(void *decoder, int state);
size_t hypua_decoder_calcsize_ucs2(void *decoder, const uint16_t *src, size_t srclen);
size_t hypua_decoder_calcsize_ucs4(void *decoder, const uint32_t *src, size_t srclen);
size_t hypua_decoder_calcsize_flush(void *decoder);
size_t hypua_decoder_decode_ucs2(
		void *decoder,
		uint16_t *src,
		size_t srclen,
		uint16_t *dst
);
size_t hypua_decoder_decode_ucs4(
		void *decoder,
		uint32_t *src,
		size_t srclen,
		uint32_t *dst
);
size_t hypua_decoder_decode_flush_ucs2(void *decoder, void *dst);
size_t hypua_decoder_decode_flush_ucs4(void *decoder, void *dst);

#endif
