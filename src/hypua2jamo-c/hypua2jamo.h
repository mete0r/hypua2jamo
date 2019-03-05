#ifndef __hypua2jamo_h__
#define __hypua2jamo_h__

/* encoder */
int hypua_p2jc4_translate_calcsize(const unsigned int *src, int srclen);
int hypua_p2jc4_translate(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_p2jd4_translate_calcsize(const unsigned int *src, int srclen);
int hypua_p2jd4_translate(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_p2jc2_translate_calcsize(const unsigned short *src, int srclen);
int hypua_p2jc2_translate(const unsigned short *src, int srclen, unsigned short *dst);
int hypua_p2jd2_translate_calcsize(const unsigned int *src, int srclen);
int hypua_p2jd2_translate(const unsigned short *src, int srclen, unsigned short *dst);

int hypua_jc2p4_translate_calcsize(const unsigned int *src, int srclen);
int hypua_jc2p4_translate(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_jc2p2_translate_calcsize(const unsigned short *src, int srclen);
int hypua_jc2p2_translate(const unsigned short *src, int srclen, unsigned short *dst);
int hypua_jd2p4_translate_calcsize(const unsigned int *src, int srclen);
int hypua_jd2p4_translate(const unsigned int *src, int srclen, unsigned int *dst);
int hypua_jd2p2_translate_calcsize(const unsigned short *src, int srclen);
int hypua_jd2p2_translate(const unsigned short *src, int srclen, unsigned short *dst);

/* decoder */
int hypua_jc2p_translator_size();
int hypua_jc2p_translator_init(void *);
int hypua_jc2p_translator_getstate(void *);
int hypua_jc2p_translator_setstate(void *, int);
int hypua_jc2p_translator_u2_calcsize(void *, const unsigned short *src, int srclen);
int hypua_jc2p_translator_u2_calcsize_flush(void *);
int hypua_jc2p_translator_u2_translate(void *, const unsigned short *src, int srclen, unsigned short *dst);
int hypua_jc2p_translator_u2_translate_flush(void *, unsigned short *dst);
int hypua_jc2p_translator_u4_calcsize(void *, const unsigned int *src, int srclen);
int hypua_jc2p_translator_u4_calcsize_flush(void *);
int hypua_jc2p_translator_u4_translate(void *, const unsigned int *src, int srclen, unsigned int *dst);
int hypua_jc2p_translator_u4_translate_flush(void *, unsigned int *dst);

int hypua_jd2p_translator_size();
int hypua_jd2p_translator_init(void *);
int hypua_jd2p_translator_getstate(void *);
int hypua_jd2p_translator_setstate(void *, int);
int hypua_jd2p_translator_u2_calcsize(void *, const unsigned short *src, int srclen);
int hypua_jd2p_translator_u2_calcsize_flush(void *);
int hypua_jd2p_translator_u2_translate(void *, const unsigned short *src, int srclen, unsigned short *dst);
int hypua_jd2p_translator_u2_translate_flush(void *, unsigned short *dst);
int hypua_jd2p_translator_u4_calcsize(void *, const unsigned int *src, int srclen);
int hypua_jd2p_translator_u4_calcsize_flush(void *);
int hypua_jd2p_translator_u4_translate(void *, const unsigned int *src, int srclen, unsigned int *dst);
int hypua_jd2p_translator_u4_translate_flush(void *, unsigned int *dst);

#endif
