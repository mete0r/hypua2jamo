int TRANSLATOR_CALCSIZE(void *translator, const codepoint_t *src, int srclen) {
	struct Translator *t = translator;
	struct Node const* child_node;
	int dstlen = 0;
	const uint16_t *src_reserved;
	const codepoint_t *src_end = src + srclen;
	codepoint_t jamo_code;

	while (src < src_end) {
		jamo_code = *src;
		child_node = find_child(t->node, jamo_code);
		if (child_node == NULL) {
			if (t->node == &node_root) {
				/* flush current jamo and return to the root state */
				dstlen += 1;
				t->node = &node_root;
				src += 1;
				continue;
			} else if (t->node->pua_code != 0) {
				/* flush current node and return to the root state */
				dstlen += 1;

				t->node = &node_root;
				continue;
			} else {
				/* flush reserved jamo and return to the root state */
				dstlen += t->node->jamo_seq_len;
				for (	src_reserved = t->node->jamo_seq;
					src_reserved < t->node->jamo_seq + t->node->jamo_seq_len;
					src_reserved ++)
				{
				}

				t->node = &node_root;
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


int TRANSLATOR_CALCSIZE_FLUSH(void *translator) {
	struct Translator *t = translator;
	int dstlen = 0;
	const uint16_t *src_reserved;

	if (t->node == &node_root) {
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

	t->node = &node_root;

	return dstlen;
}


int TRANSLATOR_TRANSLATE(void *translator, const codepoint_t *src, int srclen, codepoint_t *dst) {
	struct Translator *t = translator;
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
			if (t->node == &node_root) {
				/* flush current jamo and return to the root state */
				dstlen += 1;
				*(dst++) = jamo_code;

				t->node = &node_root;
				src += 1;
				continue;
			} else if (t->node->pua_code != 0) {
				/* flush current node and return to the root state */
				dstlen += 1;
				*(dst++) = t->node->pua_code;

				t->node = &node_root;
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

				t->node = &node_root;
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


int TRANSLATOR_TRANSLATE_FLUSH(void *translator, codepoint_t *dst) {
	struct Translator *t = translator;
	int dstlen = 0;
	codepoint_t *dst_begin = dst;
	const uint16_t *src_reserved;

	if (t->node == &node_root) {
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

	t->node = &node_root;

	return dst - dst_begin;
}


