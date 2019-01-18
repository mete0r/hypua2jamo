#include <string.h>

#include "config.h"

#ifdef HAVE_INTTYPES_H
#include <inttypes.h>
#else
typedef unsigned int uint32_t;
#endif


typedef uint32_t codepoint_t;

#include "jc2p-tree.h"


static struct Node* find_child(struct Node* node, codepoint_t jamo_code) {
	struct Node** childrenEnd;
	struct Node** child;

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


int hypua_jc2p4_translate_calcsize(const codepoint_t *src, int srclen) {
	struct Node* node = &node_root;
	struct Node* child_node;
	int dstlen = 0;
	const codepoint_t *src_consumed = src;
	const codepoint_t *src_end = src + srclen;
	codepoint_t jamo_code;

	for (; src < src_end; ++src) {
		jamo_code = *src;
		child_node = find_child(node, jamo_code);
		if (child_node == NULL) {
			if (node->pua_code != 0) {
				dstlen += 1;
			} else {
				dstlen += (src - src_consumed);
			}
			node = &node_root;
			src_consumed = src;
		}
	}
	return dstlen;
}
