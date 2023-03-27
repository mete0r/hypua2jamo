#ifndef __hypua2jamo_h__
#define __hypua2jamo_h__

#include <stddef.h>

/* encoder */

size_t hypua_c2d_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_c2d_ucs4_encode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_c2d_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_c2d_ucs2_encode(const unsigned short *src, size_t srclen, unsigned short *dst);
size_t hypua_p2jc_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_p2jc_ucs4_encode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_p2jc_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_p2jc_ucs2_encode(const unsigned short *src, size_t srclen, unsigned short *dst);
size_t hypua_p2jd_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_p2jd_ucs4_encode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_p2jd_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_p2jd_ucs2_encode(const unsigned short *src, size_t srclen, unsigned short *dst);

/* decoder */

size_t hypua_d2c_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_d2c_ucs4_decode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_d2c_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_d2c_ucs2_decode(const unsigned short *src, size_t srclen, unsigned short *dst);
size_t hypua_jc2p_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_jc2p_ucs4_decode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_jc2p_ucs2_calcsize(const unsigned short *src, size_t srclen);
size_t hypua_jc2p_ucs2_decode(const unsigned short *src, size_t srclen, unsigned short *dst);
size_t hypua_jd2p_ucs4_calcsize(const unsigned int *src, size_t srclen);
size_t hypua_jd2p_ucs4_decode(const unsigned int *src, size_t srclen, unsigned int *dst);
size_t hypua_jd2p_calcsize_ucs2(const unsigned short *src, size_t srclen);
size_t hypua_jd2p_ucs2_decode(const unsigned short *src, size_t srclen, unsigned short *dst);

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
size_t hypua_decoder_calcsize_ucs2(void *decoder, void *src, size_t srclen);
size_t hypua_decoder_calcsize_ucs4(void *decoder, void *src, size_t srclen);
size_t hypua_decoder_calcsize_flush(void *t);
size_t hypua_decoder_decode_ucs2(
		void *decoder,
		void *src,
		size_t srclen,
		void *dst
);
size_t hypua_decoder_decode_ucs4(
		void *decoder,
		void *src,
		size_t srclen,
		void *dst
);
size_t hypua_decoder_decode_flush_ucs2(void *decoder, void *dst);
size_t hypua_decoder_decode_flush_ucs4(void *decoder, void *dst);

#endif
