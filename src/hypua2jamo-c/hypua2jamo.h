#ifndef __hypua2jamo_h__
#define __hypua2jamo_h__

/* encoder */

int hypua_p2jc_ucs4_calcsize(const unsigned int *src, int srclen);
int hypua_p2jc_ucs4_encode(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_p2jc_ucs2_calcsize(const unsigned short *src, int srclen);
int hypua_p2jc_ucs2_encode(const unsigned short *src, int srclen, unsigned short *dst);
int hypua_p2jd_ucs4_calcsize(const unsigned int *src, int srclen);
int hypua_p2jd_ucs4_encode(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_p2jd_ucs2_calcsize(const unsigned short *src, int srclen);
int hypua_p2jd_ucs2_encode(const unsigned short *src, int srclen, unsigned short *dst);

/* decoder */

int hypua_jc2p_ucs4_calcsize(const unsigned int *src, int srclen);
int hypua_jc2p_ucs4_decode(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_jc2p_ucs2_calcsize(const unsigned short *src, int srclen);
int hypua_jc2p_ucs2_decode(const unsigned short *src, int srclen, unsigned short *dst);
int hypua_jd2p_ucs4_calcsize(const unsigned int *src, int srclen);
int hypua_jd2p_ucs4_decode(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_jd2p_calcsize_ucs2(const unsigned short *src, int srclen);
int hypua_jd2p_ucs2_decode(const unsigned short *src, int srclen, unsigned short *dst);

/* decoder generic */

int hypua_decoder_alloc_size();
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
int hypua_decoder_calcsize_ucs2(void *decoder, void *src, int srclen);
int hypua_decoder_calcsize_ucs4(void *decoder, void *src, int srclen);
int hypua_decoder_calcsize_flush(void *t);
int hypua_decoder_decode_ucs2(
		void *decoder,
		void *src,
		int srclen,
		void *dst
);
int hypua_decoder_decode_ucs4(
		void *decoder,
		void *src,
		int srclen,
		void *dst
);
int hypua_decoder_decode_flush_ucs2(void *decoder, void *dst);
int hypua_decoder_decode_flush_ucs4(void *decoder, void *dst);

#endif
