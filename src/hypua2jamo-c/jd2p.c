#include <stddef.h>
#include <stdio.h>

#include "config.h"

#ifdef HAVE_INTTYPES_H
#include <inttypes.h>
#else
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#endif

#include "jx2p-translator.h"
#include "jd2p-tree.inc"

#define TRANSLATOR(method)	hypua_jd2p_translator_ ## method

#include "jx2p.inc"


int hypua_jd2p_translator_size() {
	return sizeof(struct Translator);
}


void hypua_jd2p_translator_init(void *translator) {
	struct Translator *t = translator;
	t->node = &node_root;
}


int hypua_jd2p_translator_getstate(void *translator) {
	struct Translator *t = translator;
	return t->node->index;
}


int hypua_jd2p_translator_setstate(void *translator, int state) {
	struct Translator *t = translator;
	int oldstate = t->node->index;
	if (state < 0 || state >= sizeof(nodelist)/sizeof(nodelist[0])) {
		return -1;
	}
	t->node = nodelist[state];
	return oldstate;
}


int hypua_jd2p2_translate_calcsize(const uint16_t *src, int srclen) {
	int dstlen = 0;
	struct Translator translator;
	hypua_jd2p_translator_init(&translator);
	dstlen += hypua_jd2p_translator_u2_calcsize(&translator, src, srclen);
	dstlen += hypua_jd2p_translator_u2_calcsize_flush(&translator);
	return dstlen;
}


int hypua_jd2p2_translate(const uint16_t *src, int srclen, uint16_t *dst) {
	int dstlen = 0;
	struct Translator translator;
	uint16_t *dst_begin = dst;

	hypua_jd2p_translator_init(&translator);
	dst += hypua_jd2p_translator_u2_translate(&translator, src, srclen, dst);
	dst += hypua_jd2p_translator_u2_translate_flush(&translator, dst);
	return dst - dst_begin;
}


int hypua_jd2p4_translate_calcsize(const uint32_t *src, int srclen) {
	int dstlen = 0;
	struct Translator translator;
	hypua_jd2p_translator_init(&translator);
	dstlen += hypua_jd2p_translator_u4_calcsize(&translator, src, srclen);
	dstlen += hypua_jd2p_translator_u4_calcsize_flush(&translator);
	return dstlen;
}


int hypua_jd2p4_translate(const uint32_t *src, int srclen, uint32_t *dst) {
	int dstlen = 0;
	struct Translator translator;
	uint32_t *dst_begin = dst;

	hypua_jd2p_translator_init(&translator);
	dst += hypua_jd2p_translator_u4_translate(&translator, src, srclen, dst);
	dst += hypua_jd2p_translator_u4_translate_flush(&translator, dst);
	return dst - dst_begin;
}
