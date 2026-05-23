"""
总结服务类，用户提问，搜索参考资料
"""
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from rag.vector_store import VectorStore
from utils.prompts_loader import load_rag_prompts


class RagSummarizerService(object):
    def __init__(self):
        self.vector_store = VectorStore()
        self.retriver = self.vector_store.get_retriver()
        self.prompt_txt = load_rag_prompts()
        self.prompt_template = PromptTemplate.from_template(self.prompt_txt)
        self.model = chat_model
        self.chain = self.__init__chain()

    def __init__chain(self):
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    def retriver_docs(self,query:str) -> list[Document]:
        return self.retriver.invoke(query)

    def rag_summarize(self,query:str) -> str:
        context_docs = self.retriver.invoke(query)

        context = ""

        counter = 0

        for doc in context_docs:
            counter +=1
            context += f"【参考资料{counter}】: 参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"

        return self.chain.invoke(
            {
                "input": query,
                "context": context,
            }
        )


if __name__ == '__main__':
    rag_service = RagSummarizerService()
    print(rag_service.rag_summarize("小户型适合哪些扫地机器人"))
