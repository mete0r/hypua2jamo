struct Node {
	int index;
	int jamo_seq_len;
	const uint16_t *jamo_seq;
	uint16_t jamo_code;
	uint16_t pua_code;
	int childrenLen;
	const struct Node** children;
	const char* node_name;
};


struct Decoder {
	const struct Node *root;
	const struct Node *node;
	const struct Node **nodelist;
	int nodelistLen;
};


#ifdef __cplusplus
extern "C" {
#endif

int hypua_decoder_alloc_size();
void hypua_decoder_init(
		struct Decoder *decoder,
		const struct Node *root,
		const struct Node **nodelist,
		int nodelistLen
);
int hypua_decoder_getstate(const struct Decoder *decoder);
int hypua_decoder_setstate(struct Decoder *decoder, int state);
size_t hypua_decoder_calcsize_ucs2(struct Decoder *decoder, const uint16_t *src, size_t srclen);
size_t hypua_decoder_calcsize_ucs4(struct Decoder *decoder, const uint32_t *src, size_t srclen);
size_t hypua_decoder_calcsize_flush(struct Decoder *decoder);
size_t hypua_decoder_decode_ucs2(
		struct Decoder *decoder,
		const uint16_t *src,
		size_t srclen,
		uint16_t *dst
);
size_t hypua_decoder_decode_ucs4(
		struct Decoder *decoder,
		const uint32_t *src,
		size_t srclen,
		uint32_t *dst
);
size_t hypua_decoder_decode_flush_ucs2(struct Decoder *decoder, uint16_t *dst);
size_t hypua_decoder_decode_flush_ucs4(struct Decoder *decoder, uint32_t *dst);


#ifdef __cplusplus
}
#endif
