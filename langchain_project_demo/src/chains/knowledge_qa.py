"""
知识库问答链模块
提供基于文档的智能问答功能
"""

import os
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import hashlib
from loguru import logger

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, 
    TextLoader, 
    UnstructuredWordDocumentLoader,
    UnstructuredMarkdownLoader
)
from langchain.schema import Document

from src.config.settings import config
from src.config.prompts import get_prompt_template
from src.models.llm_factory import create_chat_model, create_embedding_model
from src.utils.logger import get_logger


@dataclass
class DocumentInfo:
    """文档信息"""
    doc_id: str
    filename: str
    file_path: str
    file_type: str
    file_size: int
    upload_time: float
    content_hash: str
    metadata: Dict[str, Any]


@dataclass
class QAResponse:
    """问答响应"""
    answer: str
    confidence: float
    source_documents: List[Document]
    metadata: Dict[str, Any]


class KnowledgeBaseManager:
    """
    知识库管理器
    
    提供以下功能：
    1. 文档上传和预处理
    2. 文本分块和向量化
    3. 向量存储管理
    4. 相似度搜索
    5. 文档生命周期管理
    """
    
    def __init__(
        self,
        vector_store_path: str = None,
        embedding_model = None,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        初始化知识库管理器
        
        Args:
            vector_store_path: 向量存储路径
            embedding_model: 嵌入模型
            chunk_size: 文本块大小
            chunk_overlap: 文本块重叠大小
        """
        self.vector_store_path = vector_store_path or config.vector_db.persist_directory
        self.embedding_model = embedding_model or create_embedding_model()
        self.chunk_size = chunk_size or config.embedding.chunk_size
        self.chunk_overlap = chunk_overlap or config.embedding.chunk_overlap
        
        # 初始化文本分割器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?", "，", ",", " ", ""]
        )
        
        # 初始化向量存储
        self.vector_store = self._initialize_vector_store()
        
        # 文档信息存储
        self.documents: Dict[str, DocumentInfo] = {}
        
        self.logger = get_logger(__name__)
        self.logger.info(f"知识库管理器初始化完成 - 存储路径: {self.vector_store_path}")
    
    def _initialize_vector_store(self) -> Chroma:
        """初始化向量存储"""
        try:
            vector_store = Chroma(
                persist_directory=self.vector_store_path,
                embedding_function=self.embedding_model,
                collection_name=config.vector_db.collection_name
            )
            
            self.logger.info("向量存储初始化成功")
            return vector_store
            
        except Exception as e:
            self.logger.error(f"向量存储初始化失败: {e}")
            raise
    
    def upload_document(self, file_path: str, metadata: Dict[str, Any] = None) -> DocumentInfo:
        """
        上传文档到知识库
        
        Args:
            file_path: 文档路径
            metadata: 文档元数据
            
        Returns:
            DocumentInfo: 文档信息
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 检查文件类型
            file_type = file_path.suffix.lower()
            if file_type not in ['.pdf', '.txt', '.md', '.docx']:
                raise ValueError(f"不支持的文件类型: {file_type}")
            
            # 加载文档
            documents = self._load_document(file_path)
            
            # 生成文档ID
            doc_id = str(uuid.uuid4())
            
            # 计算内容哈希
            content_hash = self._calculate_content_hash(documents)
            
            # 检查是否已存在相同内容的文档
            existing_doc = self._find_duplicate_document(content_hash)
            if existing_doc:
                self.logger.info(f"文档已存在，跳过上传: {existing_doc.filename}")
                return existing_doc
            
            # 添加元数据
            for doc in documents:
                doc.metadata.update({
                    "doc_id": doc_id,
                    "filename": file_path.name,
                    "file_path": str(file_path),
                    "file_type": file_type,
                    "upload_time": time.time(),
                    "content_hash": content_hash,
                    **(metadata or {})
                })
            
            # 文本分块
            split_docs = self.text_splitter.split_documents(documents)
            
            # 添加到向量存储
            self.vector_store.add_documents(split_docs)
            
            # 保存文档信息
            doc_info = DocumentInfo(
                doc_id=doc_id,
                filename=file_path.name,
                file_path=str(file_path),
                file_type=file_type,
                file_size=file_path.stat().st_size,
                upload_time=time.time(),
                content_hash=content_hash,
                metadata=metadata or {}
            )
            
            self.documents[doc_id] = doc_info
            
            self.logger.info(f"文档上传成功: {file_path.name} ({len(split_docs)} 个文本块)")
            return doc_info
            
        except Exception as e:
            self.logger.error(f"文档上传失败: {e}")
            raise
    
    def _load_document(self, file_path: Path) -> List[Document]:
        """加载文档"""
        file_type = file_path.suffix.lower()
        
        if file_type == '.pdf':
            loader = PyPDFLoader(str(file_path))
        elif file_type == '.txt':
            loader = TextLoader(str(file_path), encoding='utf-8')
        elif file_type == '.md':
            loader = UnstructuredMarkdownLoader(str(file_path))
        elif file_type == '.docx':
            loader = UnstructuredWordDocumentLoader(str(file_path))
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")
        
        return loader.load()
    
    def _calculate_content_hash(self, documents: List[Document]) -> str:
        """计算文档内容哈希"""
        content = ""
        for doc in documents:
            content += doc.page_content
        
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _find_duplicate_document(self, content_hash: str) -> Optional[DocumentInfo]:
        """查找重复文档"""
        for doc_info in self.documents.values():
            if doc_info.content_hash == content_hash:
                return doc_info
        return None
    
    def search_similar_documents(
        self, 
        query: str, 
        k: int = 5,
        score_threshold: float = 0.7
    ) -> List[Tuple[Document, float]]:
        """
        搜索相似文档
        
        Args:
            query: 查询文本
            k: 返回结果数量
            score_threshold: 相似度阈值
            
        Returns:
            相似文档列表，包含文档和相似度分数
        """
        try:
            results = self.vector_store.similarity_search_with_score(
                query=query,
                k=k
            )
            
            # 过滤低于阈值的文档
            filtered_results = [
                (doc, score) for doc, score in results 
                if score >= score_threshold
            ]
            
            self.logger.debug(f"搜索完成: '{query}' - 找到 {len(filtered_results)} 个相关文档")
            return filtered_results
            
        except Exception as e:
            self.logger.error(f"文档搜索失败: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """
        删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        try:
            if doc_id not in self.documents:
                return False
            
            # 从向量存储中删除
            # 注意：Chroma的删除功能需要基于metadata过滤
            self.vector_store._collection.delete(
                where={"doc_id": doc_id}
            )
            
            # 从文档列表中删除
            del self.documents[doc_id]
            
            self.logger.info(f"文档删除成功: {doc_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"文档删除失败: {e}")
            return False
    
    def get_document_info(self, doc_id: str) -> Optional[DocumentInfo]:
        """
        获取文档信息
        
        Args:
            doc_id: 文档ID
            
        Returns:
            文档信息或None
        """
        return self.documents.get(doc_id)
    
    def get_all_documents(self) -> List[DocumentInfo]:
        """获取所有文档信息"""
        return list(self.documents.values())
    
    def get_document_stats(self) -> Dict[str, Any]:
        """获取文档统计信息"""
        total_docs = len(self.documents)
        total_size = sum(doc.file_size for doc in self.documents.values())
        
        file_type_counts = {}
        for doc in self.documents.values():
            file_type = doc.file_type
            file_type_counts[file_type] = file_type_counts.get(file_type, 0) + 1
        
        return {
            "total_documents": total_docs,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "file_type_distribution": file_type_counts,
            "average_size_bytes": total_size / total_docs if total_docs > 0 else 0
        }


class KnowledgeQAChain:
    """
    知识库问答链
    
    提供基于文档的智能问答功能
    """
    
    def __init__(
        self,
        knowledge_base: Optional[KnowledgeBaseManager] = None,
        llm: Optional[BaseLanguageModel] = None,
        enable_citations: bool = True,
        confidence_threshold: float = 0.7
    ):
        """
        初始化知识库问答链
        
        Args:
            knowledge_base: 知识库管理器
            llm: 语言模型
            enable_citations: 是否启用引用
            confidence_threshold: 置信度阈值
        """
        self.knowledge_base = knowledge_base or KnowledgeBaseManager()
        self.llm = llm or create_chat_model()
        self.enable_citations = enable_citations
        self.confidence_threshold = confidence_threshold
        
        # 创建问答链
        self.qa_chain = self._create_qa_chain()
        self.answer_quality_chain = self._create_answer_quality_chain()
        
        self.logger = get_logger(__name__)
        self.logger.info("知识库问答链初始化完成")
    
    def _create_qa_chain(self) -> ChatPromptTemplate:
        """创建问答链"""
        system_template = """你是一个知识库问答助手，基于提供的文档内容回答问题。

回答原则：
1. 准确性：只基于提供的文档内容回答问题
2. 完整性：尽可能提供详细和全面的答案
3. 诚实性：如果文档中没有相关信息，明确说明
4. 引用性：在回答中引用具体的文档内容
5. 清晰性：用清晰易懂的语言表达

回答格式：
1. 直接答案：首先给出问题的直接答案
2. 详细解释：然后提供更详细的解释和背景信息
3. 引用来源：最后引用相关的文档内容

注意事项：
- 不要编造文档中没有的信息
- 不要添加个人观点或推测
- 保持客观和中立的态度
- 如果不确定，明确说明

当前时间: {current_time}
"""
        
        human_template = """
基于以下文档内容回答问题：

参考文档：
{context}

问题：{question}

请提供准确、详细的答案：
"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("human", human_template)
        ])
        
        return prompt | self.llm | StrOutputParser()
    
    def _create_answer_quality_chain(self) -> ChatPromptTemplate:
        """创建答案质量评估链"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """你是一个答案质量评估专家，评估问答答案的质量。

评估维度：
1. 准确性：答案是否准确基于提供的文档
2. 完整性：答案是否完整回答了问题
3. 相关性：答案是否与问题高度相关
4. 清晰度：答案是否清晰易懂

输出格式：
{"accuracy": 0.95, "completeness": 0.90, "relevance": 0.95, "clarity": 0.92, "overall_confidence": 0.93}

评分标准：
- 0.9-1.0: 优秀
- 0.7-0.89: 良好
- 0.5-0.69: 一般
- 0.0-0.49: 较差
"""),
            ("human", """
问题：{question}
参考文档：{context}
答案：{answer}

请评估答案质量：""")
        ])
        
        return prompt | self.llm | JsonOutputParser()
    
    def answer_question(
        self, 
        question: str, 
        k: int = 5,
        score_threshold: float = None,
        return_metadata: bool = False
    ) -> Union[str, QAResponse]:
        """
        回答问题
        
        Args:
            question: 用户问题
            k: 检索文档数量
            score_threshold: 相似度阈值，如果为None则使用默认值
            return_metadata: 是否返回完整元数据
            
        Returns:
            答案文本或完整响应对象
        """
        try:
            start_time = time.time()
            
            # 使用默认阈值
            if score_threshold is None:
                score_threshold = self.confidence_threshold
            
            # 搜索相关文档
            similar_docs = self.knowledge_base.search_similar_documents(
                query=question,
                k=k,
                score_threshold=score_threshold
            )
            
            if not similar_docs:
                response = QAResponse(
                    answer="抱歉，知识库中没有找到相关信息。请尝试其他关键词或联系人工客服。",
                    confidence=0.0,
                    source_documents=[],
                    metadata={
                        "search_time": time.time() - start_time,
                        "documents_found": 0,
                        "threshold_used": score_threshold
                    }
                )
                return response if return_metadata else response.answer
            
            # 构建上下文
            context_parts = []
            for i, (doc, score) in enumerate(similar_docs):
                context_parts.append(f"[文档{i+1}] (相似度: {score:.3f})\n{doc.page_content}")
            
            context = "\n\n".join(context_parts)
            
            # 生成答案
            answer = self.qa_chain.invoke({
                "context": context,
                "question": question,
                "current_time": self._get_current_time()
            })
            
            # 评估答案质量
            quality_score = self.answer_quality_chain.invoke({
                "question": question,
                "context": context,
                "answer": answer
            })
            
            # 构建响应
            response = QAResponse(
                answer=answer,
                confidence=quality_score["overall_confidence"],
                source_documents=[doc for doc, _ in similar_docs],
                metadata={
                    "quality_scores": quality_score,
                    "search_time": time.time() - start_time,
                    "documents_found": len(similar_docs),
                    "threshold_used": score_threshold,
                    "source_count": len(similar_docs)
                }
            )
            
            self.logger.info(
                f"问答完成 - 问题: '{question[:50]}...', "
                f"置信度: {quality_score['overall_confidence']:.3f}, "
                f"找到文档: {len(similar_docs)}, "
                f"耗时: {time.time() - start_time:.2f}s"
            )
            
            return response if return_metadata else response.answer
            
        except Exception as e:
            self.logger.error(f"问答处理失败: {e}")
            error_response = "抱歉，处理您的问题时出现了错误。请稍后再试。"
            
            if return_metadata:
                return QAResponse(
                    answer=error_response,
                    confidence=0.0,
                    source_documents=[],
                    metadata={"error": str(e)}
                )
            else:
                return error_response
    
    def add_document(self, file_path: str, metadata: Dict[str, Any] = None) -> DocumentInfo:
        """
        添加文档到知识库
        
        Args:
            file_path: 文档路径
            metadata: 文档元数据
            
        Returns:
            DocumentInfo: 文档信息
        """
        return self.knowledge_base.upload_document(file_path, metadata)
    
    def delete_document(self, doc_id: str) -> bool:
        """
        从知识库删除文档
        
        Args:
            doc_id: 文档ID
            
        Returns:
            是否删除成功
        """
        return self.knowledge_base.delete_document(doc_id)
    
    def get_document_info(self, doc_id: str) -> Optional[DocumentInfo]:
        """
        获取文档信息
        
        Args:
            doc_id: 文档ID
            
        Returns:
            文档信息或None
        """
        return self.knowledge_base.get_document_info(doc_id)
    
    def get_all_documents(self) -> List[DocumentInfo]:
        """获取所有文档信息"""
        return self.knowledge_base.get_all_documents()
    
    def get_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        return self.knowledge_base.get_document_stats()
    
    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")


# 便捷函数
def create_knowledge_qa_chain(**kwargs) -> KnowledgeQAChain:
    """
    创建知识库问答链
    
    Args:
        **kwargs: 传递给KnowledgeQAChain的参数
        
    Returns:
        KnowledgeQAChain: 知识库问答链实例
    """
    return KnowledgeQAChain(**kwargs)


def answer_from_knowledge_base(
    question: str,
    knowledge_base_path: str = None,
    **kwargs
) -> str:
    """
    便捷函数：从知识库回答问题
    
    Args:
        question: 用户问题
        knowledge_base_path: 知识库路径
        **kwargs: 其他参数
        
    Returns:
        str: 答案
    """
    # 创建知识库问答链（如果不存在）
    if not hasattr(answer_from_knowledge_base, '_chain'):
        kb_manager = KnowledgeBaseManager(
            vector_store_path=knowledge_base_path
        )
        answer_from_knowledge_base._chain = create_knowledge_qa_chain(
            knowledge_base=kb_manager,
            **kwargs
        )
    
    return answer_from_knowledge_base._chain.answer_question(question)