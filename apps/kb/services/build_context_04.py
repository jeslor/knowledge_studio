import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")


def build_context(docs, max_token: int):
    context = []
    token_count = 0
    for doc in docs:
        text = doc.page_content if len(doc.page_content) > 0 else ""
        tokens = len(encoder.encode(text))
        if tokens > max_token:
            break
        context.append(text)
        token_count += tokens
    return context, token_count
