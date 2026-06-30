class Processor:
    def __init__(self):
        pass

    def process_query(self, query: str):
        query = query.lower()
        query = query.strip()
        query = " ".join(query.split())
        if "what is" in query:
            intent = "definition"
        elif "how" in query:
            intent = "explanation"
        else:
            intent = "general"

        return f"{query}, intent:{intent}"


processor_service = Processor()
