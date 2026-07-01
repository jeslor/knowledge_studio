import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")


def build_context(docs, max_tokens):
    context = []
    citations = []
    token_count = 0

    for i, doc in enumerate(docs, start=1):
        text = doc.page_content or ""
        tokens = len(encoder.encode(text))

        if token_count + tokens > max_tokens:
            break

        token_count += tokens

        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "?")

        context.append(
            f"""
                [Document {i}]
                Source: {source}
                Page: {page}
                
                {text}
            """
        )

        citations.append({
            "id": i,
            "source": source,
            "page": page,
        })

    return "\n\n".join(context), citations