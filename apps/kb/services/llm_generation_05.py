from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


class LocalModel:
    # Initiate the model
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:3b", temperature=0)

    def prompt_model(self, question: str, content: str):
        # generate a prompt using the provided question and context
        prompt = ChatPromptTemplate.from_template("""
                You are a helpful assistant.
                Use the knowledge-base to improve your answer when useful, but respond naturally.

                Question:
                {question}

                Context:
                {content}

                Answer:
        """)

        normalized_prompt = prompt.format_messages(question=question, content=content)
        response = self.llm.invoke(normalized_prompt)
        return response


local_model = LocalModel()
