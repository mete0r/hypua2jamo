#include <stddef.h>
#include <stdio.h>

#include "config.h"

#ifdef HAVE_STDINT_H
#include <stdint.h>
#else
typedef unsigned short uint16_t;
typedef unsigned int uint32_t;
#endif

#include "jx2p.h"


int hypua_decoder_alloc_size() {
	return sizeof(struct Decoder);
}


void hypua_decoder_init(
		struct Decoder *decoder,
		const struct Node *root,
		const struct Node **nodelist,
		int nodelistLen
) {
	decoder->root = decoder->node = root;
	decoder->nodelist = nodelist;
	decoder->nodelistLen = nodelistLen;
}


int hypua_decoder_getstate(const struct Decoder *decoder) {
	return decoder->node->index;
}


int hypua_decoder_setstate(struct Decoder *decoder, int state) {
	int oldstate = decoder->node->index;
	if (state < 0 || state >= decoder->nodelistLen) {
		return -1;
	}
	decoder->node = decoder->nodelist[state];
	return oldstate;
}


static const struct Node* find_child(
		const struct Node* node,
		uint16_t jamo_code
) {
	const struct Node** childrenEnd;
	const struct Node** child;

	if (node->childrenLen == 0) {
		return NULL;
	}
	childrenEnd = node->children + node->childrenLen;

	for (child = node->children; child < childrenEnd; ++child) {
		if ((*child)->jamo_code == jamo_code) {
			return *child;
		}
	}

	return NULL;
}


template <typename codepoint_t>
size_t calcsize(struct Decoder *t, const codepoint_t *src, size_t srclen) {
	const struct Node *child_node;
	size_t dstlen = 0;
	const uint16_t *src_reserved;
	const codepoint_t *src_end = src + srclen;
	codepoint_t jamo_code;

	while (src < src_end) {
		jamo_code = *src;
		child_node = find_child(t->node, jamo_code);
		if (child_node == NULL) {
			if (t->node == t->root) {
				/* flush current jamo and return to the root state */
				dstlen += 1;
				t->node = t->root;
				src += 1;
				continue;
			} else if (t->node->pua_code != 0) {
				/* flush current node and return to the root state */
				dstlen += 1;

				t->node = t->root;
				continue;
			} else {
				/* flush reserved jamo and return to the root state */
				dstlen += t->node->jamo_seq_len;
				for (	src_reserved = t->node->jamo_seq;
					src_reserved < t->node->jamo_seq + t->node->jamo_seq_len;
					src_reserved ++)
				{
				}

				t->node = t->root;
				continue;
			}
		} else {
			/* reserve current jamo and make transition to next state */
			src += 1;

			t->node = child_node;
		}
	}

	return dstlen;
}


size_t hypua_decoder_calcsize_ucs2(struct Decoder *decoder, const uint16_t *src, size_t srclen) {
	return calcsize(decoder, src, srclen);
}

size_t hypua_decoder_calcsize_ucs4(struct Decoder *decoder, const uint32_t *src, size_t srclen) {
	return calcsize(decoder, src, srclen);
}


static size_t calcsize_flush(struct Decoder *t) {
	const uint16_t *src_reserved;
	size_t dstlen = 0;

	if (t->node == t->root) {
	} else {
		if (t->node->pua_code != 0) {
			/* flush current node */
			dstlen += 1;
		} else {
			/* flush reserved jamo */
			dstlen += t->node->jamo_seq_len;
			for (	src_reserved = t->node->jamo_seq;
				src_reserved < t->node->jamo_seq + t->node->jamo_seq_len;
				src_reserved ++)
			{
			}
		}
	}

	t->node = t->root;

	return dstlen;
}


size_t hypua_decoder_calcsize_flush(struct Decoder *decoder) {
	return calcsize_flush(decoder);
}


template <typename codepoint_t>
size_t decode(
		struct Decoder *t,
		const codepoint_t *src,
		size_t srclen,
		codepoint_t *dst
) {
	const struct Node* child_node;
	int dstlen = 0;
	const uint16_t *src_reserved;
	const codepoint_t *src_end = src + srclen;
	const codepoint_t *dst_begin = dst;
	codepoint_t jamo_code;

	while (src < src_end) {
		jamo_code = *src;
		child_node = find_child(t->node, jamo_code);
		if (child_node == NULL) {
			if (t->node == t->root) {
				/* flush current jamo and return to the root state */
				dstlen += 1;
				*(dst++) = jamo_code;

				t->node = t->root;
				src += 1;
				continue;
			} else if (t->node->pua_code != 0) {
				/* flush current node and return to the root state */
				dstlen += 1;
				*(dst++) = t->node->pua_code;

				t->node = t->root;
				continue;
			} else {
				/* flush reserved jamo and return to the root state */
				dstlen += t->node->jamo_seq_len;
				for (	src_reserved = t->node->jamo_seq;
					src_reserved < t->node->jamo_seq + t->node->jamo_seq_len;
					src_reserved ++
				) {
					*(dst++) = *(src_reserved);
				}

				t->node = t->root;
				continue;
			}
		} else {
			/* reserve current jamo and make transition to next state */
			src += 1;

			t->node = child_node;
		}
	}
	return dst - dst_begin;
}


size_t hypua_decoder_decode_ucs2(
		struct Decoder *decoder,
		const uint16_t *src,
		size_t srclen,
		uint16_t *dst
) {
	return decode(decoder, src, srclen, dst);
}


size_t hypua_decoder_decode_ucs4(
		struct Decoder *decoder,
		const uint32_t *src,
		size_t srclen,
		uint32_t *dst
) {
	return decode(decoder, src, srclen, dst);
}


template <typename codepoint_t>
static size_t decode_flush(struct Decoder *t, codepoint_t *dst) {
	int dstlen = 0;
	codepoint_t *dst_begin = dst;
	const uint16_t *src_reserved;

	if (t->node == t->root) {
	} else {
		if (t->node->pua_code != 0) {
			/* flush current node */
			dstlen += 1;
			*(dst++) = t->node->pua_code;
		} else {
			/* flush reserved jamo */
			dstlen += t->node->jamo_seq_len;
			for (	src_reserved = t->node->jamo_seq;
				src_reserved < t->node->jamo_seq + t->node->jamo_seq_len;
				src_reserved ++
			) {
				*(dst++) = *(src_reserved);
			}
		}
	}

	t->node = t->root;

	return dst - dst_begin;
}


size_t hypua_decoder_decode_flush_ucs2(struct Decoder *decoder, uint16_t *dst) {
	return decode_flush(decoder, dst);
}


size_t hypua_decoder_decode_flush_ucs4(struct Decoder *decoder, uint32_t *dst) {
	return decode_flush(decoder, dst);
}
