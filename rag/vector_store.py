import os
from langchain_core.documents import Document
from utils.path_tool import get_abs_path
from langchain_chroma import Chroma
from utils.config_handler import chroma_config,rag_config
from model.factory import embedding_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.file_handler import txt_loader,pdf_loader,listdir_with_allowed_type,get_file_md5_hex
from utils.logger_handler import logger


class VectorStore:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name= chroma_config['collection_name'],
            embedding_function= embedding_model,
            persist_directory= chroma_config['persist_directory']
        )

        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size= chroma_config['chunk_size'],
            chunk_overlap= chroma_config['chunk_overlap'],
            separators = chroma_config['separators'],
            length_function= len,
        )

    def get_retriver(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_config["k"]})
    def load_document(self):
        def check_md5_hex(md5_hex_check:str):

            if not os.path.exists(get_abs_path(chroma_config["md5_hex_store"])):
                open(get_abs_path(chroma_config["md5_hex_store"]),'w',encoding='utf-8')
                return False
            with open(get_abs_path(chroma_config["md5_hex_store"]),'r',encoding='utf-8') as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_hex_check:
                        return True
                return False

        def save_md5_hex(md5_hex_save):
            with open(get_abs_path(chroma_config["md5_hex_store"]),'a',encoding='utf-8') as f:
                f.write(md5_hex_save + "\n")


        #加载文件
        def get_file_docunments(read_path:str):
            #如果是txt文件，就用txt函数加载
            if read_path.endswith('txt'):
                return txt_loader(read_path)
            #如果是pdf文件，就用pdf函数加载
            if read_path.endswith('pdf'):
                return pdf_loader(read_path)
            #返回空列表，表示什么都没有获取到
            return []


        allowed_file_path = listdir_with_allowed_type(
            get_abs_path(chroma_config["data_path"]),
            tuple(chroma_config["allow_knowledge_file_type"]),
        )

        for file_path in allowed_file_path:
            #获取文件的md5
            md5_hex = get_file_md5_hex(file_path)

            if check_md5_hex(md5_hex):
                logger.info(f"{file_path}已经存在知识库内")
                continue

            try:
                document: list[Document] = get_file_docunments(file_path)

                if not document:
                    logger.warning(f"{file_path}知识库内没有有效内容")
                    continue

                split_document: list[document] = self.spliter.split_documents(document)

                if not split_document:
                    logger.warning(f"{file_path}分片后没有有效内容")
                    continue

                self.vector_store.add_documents(split_document)

                save_md5_hex(md5_hex)

                logger.info(f"{file_path}内容加载成功")
            except Exception as e:
                logger.error(f"{file_path}内容加载失败，{str(e)}")

if __name__ == '__main__':
    vs = VectorStore()
    vs.load_document()
    retriver = vs.get_retriver()
    res = retriver.invoke("迷路")
    for r in res:
        print(r.page_content)
        print('*'*20)