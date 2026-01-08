from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from typing import List


class MockPGVector(VectorStore):
    """
    模拟 PGVector 向量存储，用于存储和检索数据库架构信息。
    
    注意：这是一个简化的实现，仅用于演示目的。
    生产环境应使用真实的向量数据库（如 PGVector）。
    """

    def __init__(self, docs: List[Document]):
        """
        初始化向量存储。
        
        Args:
            docs: 文档列表
        """
        self.docs = docs

    def similarity_search(self, query: str, k: int = 4, **kwargs) -> List[Document]:
        """
        基于关键词匹配的相似度搜索（简化实现）。
        
        Args:
            query: 查询字符串
            k: 返回的文档数量
            **kwargs: 其他可选参数（兼容基类接口）
            
        Returns:
            匹配的文档列表
        """
        results = []
        for doc in self.docs:
            if any(word in doc.page_content.lower()
                   for word in query.lower().split()):
                results.append(doc)
        return results[:k]

    @classmethod
    def from_texts(cls, texts: List[str], **kwargs) -> "MockPGVector":
        """
        从文本列表创建 MockPGVector 实例（实现抽象方法）。
        
        Args:
            texts: 文本列表
            **kwargs: 其他可选参数
            
        Returns:
            MockPGVector 实例
        """
        from langchain_core.documents import Document
        docs = [Document(page_content=text) for text in texts]
        return cls(docs=docs)


schema_docs = [
    Document(page_content="""
Table: teachers
Columns:
- teacher_id (int, primary key)
- name (varchar)
- department (varchar)
"""),
    Document(page_content="""
Table: students
Columns:
- student_id (int, primary key)
- name (varchar)
- age (int)
- major (varchar)
"""),
    Document(page_content="""
Table: courses
Columns:
- course_id (int, primary key)
- course_name (varchar)
- teacher_id (int, foreign key -> teachers.teacher_id)
"""),
    Document(page_content="""
Table: enrollments
Columns:
- student_id (int, foreign key -> students.student_id)
- course_id (int, foreign key -> courses.course_id)
"""),
]

vector_store = MockPGVector(schema_docs)
