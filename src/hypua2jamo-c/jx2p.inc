static struct Node* find_child(struct Node* node, uint16_t jamo_code) {
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


#define codepoint_t			uint32_t
#define TRANSLATOR_CALCSIZE		TRANSLATOR(u4_calcsize)
#define TRANSLATOR_CALCSIZE_FLUSH	TRANSLATOR(u4_calcsize_flush)
#define TRANSLATOR_TRANSLATE		TRANSLATOR(u4_translate)
#define TRANSLATOR_TRANSLATE_FLUSH	TRANSLATOR(u4_translate_flush)
#include "jx2p-translator-methods.inc"

#undef codepoint_t
#undef TRANSLATOR_CALCSIZE
#undef TRANSLATOR_CALCSIZE_FLUSH
#undef TRANSLATOR_TRANSLATE
#undef TRANSLATOR_TRANSLATE_FLUSH


#define codepoint_t			uint16_t
#define TRANSLATOR_CALCSIZE		TRANSLATOR(u2_calcsize)
#define TRANSLATOR_CALCSIZE_FLUSH	TRANSLATOR(u2_calcsize_flush)
#define TRANSLATOR_TRANSLATE		TRANSLATOR(u2_translate)
#define TRANSLATOR_TRANSLATE_FLUSH	TRANSLATOR(u2_translate_flush)
#include "jx2p-translator-methods.inc"
