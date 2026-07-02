from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate


class LocalModel:
    # Initiate the model
    def __init__(self):
        self.llm = ChatOllama(model="qwen2.5:7b", temperature=0)

    def generate_query(self, query, prev_user_queries):
        user_query_prompt = ChatPromptTemplate.from_template("""
            You are an expert Query Rewriter for a Retrieval-Augmented Generation (RAG) system.
            
            Your task is to transform a user question into a short, high-signal search query optimized for vector retrieval.
            
            User Question:
            {query}
            
            Conversation History:
            {prev_user_queries}
            
            Rules:
            
            1. Produce a SINGLE search query only.
            2. The query MUST be short (max 8–15 words).
            3. Preserve the exact meaning and intent of the user question.
            4. Resolve all pronouns or ambiguous references using the conversation history.
            5. Remove filler words, polite phrases, and conversational language.
            6. Keep only essential keywords: entities, technical terms, symptoms, actions, objects, or constraints.
            7. Prefer keyword-style queries over full sentences.
            8. Add minimal useful synonyms only if they improve retrieval (not verbosity).
            9. Do NOT answer the question.
            10. Do NOT explain anything.
            11. Do NOT include quotes, punctuation noise, or formatting.
            
            Output ONLY the optimized query.
            
            Examples:
            
            Input:
            "What are the symptoms?"
            
            History:
            ["Tell me about Ebola"]
            
            Output:
            Ebola symptoms clinical signs presentation
            
            Input:
            "How is it treated?"
            
            History:
            ["What is postpartum hemorrhage?"]
            
            Output:
            Postpartum hemorrhage treatment management
            
            Input:
            "What is the dosage?"
            
            History:
            ["Amoxicillin for pneumonia"]
            
            Output:
            Amoxicillin pneumonia dosage adult pediatric
        """)
        normalized_prompt = user_query_prompt.format_messages(query=query, prev_user_queries=prev_user_queries)
        response = self.llm.invoke(normalized_prompt)
        return response.content

    def prompt_model(self, question: str, content: str, conversation_history):

        # generate a prompt using the provided question and context
        prompt = ChatPromptTemplate.from_template("""
           You are a helpful assistant.
                Use the knowledge-base to improve your answer when useful, but respond naturally.
                
                - make sure the results will render well in HTML with all essential tags.

                Question:
                {question}

                Context:
                {content}
                
                conversation_history:
                {conversation_history}

                Answer:
        """)

        normalized_prompt = prompt.format_messages(question=question, content=content, conversation_history=conversation_history)
        response = self.llm.invoke(normalized_prompt)
        return response


local_model = LocalModel()
