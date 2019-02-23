int TRANSLATOR_CALCSIZE(void *translator, const codepoint_t *src, int srclen) {
	struct Translator *t = translator;
	struct Node* child_node;
	int dstlen = 0;
	const uint16_t *src_reserved;
	const codepoint_t *src_end = src + srclen;
	codepoint_t jamo_code;

	fprintf(stderr, "-----------------------\n");
	fprintf(stderr, "node(%s/%04x)", t->node->node_name, t->node->pua_code);
	while (src < src_end) {
		jamo_code = *src;
		fprintf(stderr, " -%04x-> ", jamo_code);
		child_node = find_child(t->node, jamo_code);
		if (child_node == NULL) {
			if (t->node == &node_root) {
				/* flush current jamo and return to the root state */
				dstlen += 1;
				fprintf(stderr, "(+1=%d) %04x", dstlen, jamo_code);
				t->node = &node_root;
				fprintf(stderr, "\nnode(root)");
				src += 1;
				continue;
			} else if (t->node->pua_code != 0) {
				/* flush current node and return to the root state */
				dstlen += 1;
				fprintf(stderr, "(+1=%d) %04x", dstlen, t->node->pua_code);

				t->node = &node_root;
				fprintf(stderr, "\nnode(root)");
				continue;
			} else {
				/* flush reserved jamo and return to the root state */
				dstlen += t->node->jamo_seq_len;
				fprintf(stderr, "(+%d=%d)", t->node->jamo_seq_len, dstlen);
				for (	src_reserved = t->node->jamo_seq;
					src_reserved < t->node->jamo_seq + t->node->jamo_seq_len;
					src_reserved ++)
				{
					fprintf(stderr, " %04x", *src_reserved);
				}

				t->node = &node_root;
				fprintf(stderr, "\nnode(root)");
				continue;
			}
		} else {
			/* reserve current jamo and make transition to next state */
			src += 1;

			t->node = child_node;
			fprintf(stderr, "node(%s/%04x)", t->node->node_name, t->node->pua_code);
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
			fprintf(stderr, " -EOF -> (+1=%d) %04x", dstlen, t->node->pua_code);
		} else {
			/* flush reserved jamo */
			dstlen += t->node->jamo_seq_len;
			fprintf(stderr, " -EOF -> (+%d=%d)", t->node->jamo_seq_len, dstlen);
			for (	src_reserved = t->node->jamo_seq;
				src_reserved < t->node->jamo_seq + t->node->jamo_seq_len;
				src_reserved ++)
			{
				fprintf(stderr, " %04x", *src_reserved);
			}
		}
	}
	fprintf(stderr, "\n");

	t->node = &node_root;

	return dstlen;
}


int TRANSLATOR_TRANSLATE(void *translator, const codepoint_t *src, int srclen, codepoint_t *dst) {
	struct Translator *t = translator;
	struct Node* child_node;
	int dstlen = 0;
	const uint16_t *src_reserved;
	const codepoint_t *src_end = src + srclen;
	const codepoint_t *dst_begin = dst;
	codepoint_t jamo_code;

	fprintf(stderr, "-----------------------\n");
	fprintf(stderr, "node(%s/%04x)", t->node->node_name, t->node->pua_code);
	while (src < src_end) {
		jamo_code = *src;
		fprintf(stderr, " -%04x-> ", jamo_code);
		child_node = find_child(t->node, jamo_code);
		if (child_node == NULL) {
			if (t->node == &node_root) {
				/* flush current jamo and return to the root state */
				dstlen += 1;
				*(dst++) = jamo_code;

				fprintf(stderr, "(+1=%d) %04x", dstlen, jamo_code);
				t->node = &node_root;
				fprintf(stderr, "\nnode(root)");
				src += 1;
				continue;
			} else if (t->node->pua_code != 0) {
				/* flush current node and return to the root state */
				dstlen += 1;
				*(dst++) = t->node->pua_code;
				fprintf(stderr, "(+1=%d) %04x", dstlen, t->node->pua_code);

				t->node = &node_root;
				fprintf(stderr, "\nnode(root)");
				continue;
			} else {
				/* flush reserved jamo and return to the root state */
				dstlen += t->node->jamo_seq_len;
				fprintf(stderr, "(+%d=%d)", t->node->jamo_seq_len, dstlen);
				for (	src_reserved = t->node->jamo_seq;
					src_reserved < t->node->jamo_seq + t->node->jamo_seq_len;
					src_reserved ++
				) {
					fprintf(stderr, " %04x", *src_reserved);
					*(dst++) = *(src_reserved);
				}

				t->node = &node_root;
				fprintf(stderr, "\nnode(root)");
				continue;
			}
		} else {
			/* reserve current jamo and make transition to next state */
			src += 1;

			t->node = child_node;
			fprintf(stderr, "node(%s/%04x)", t->node->node_name, t->node->pua_code);
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
			fprintf(stderr, " -EOF -> (+1=%d) %04x", dstlen, t->node->pua_code);
		} else {
			/* flush reserved jamo */
			dstlen += t->node->jamo_seq_len;
			fprintf(stderr, " -EOF -> (+%d=%d)", t->node->jamo_seq_len, dstlen);
			for (	src_reserved = t->node->jamo_seq;
				src_reserved < t->node->jamo_seq + t->node->jamo_seq_len;
				src_reserved ++
			) {
				fprintf(stderr, " %04x", *src_reserved);
				*(dst++) = *(src_reserved);
			}
		}
	}
	fprintf(stderr, "\n");

	t->node = &node_root;

	return dst - dst_begin;
}


