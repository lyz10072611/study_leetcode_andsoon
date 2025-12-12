"""
链功能测试模块
"""

import pytest
from unittest.mock import Mock, patch
import json

from src.chains.customer_service import CustomerServiceChain, ConversationContext
from src.chains.knowledge_qa import KnowledgeQAChain
from src.config.settings import config


class TestCustomerServiceChain:
    """测试客服对话链"""
    
    @pytest.fixture
    def mock_llm(self):
        """模拟LLM"""
        mock = Mock()
        mock.invoke.return_value = "这是一个测试回复"
        return mock
    
    @pytest.fixture
    def customer_chain(self, mock_llm):
        """创建客服链实例"""
        return CustomerServiceChain(llm=mock_llm, enable_tools=False)
    
    def test_intent_recognition(self, customer_chain, mock_llm):
        """测试意图识别"""
        # 模拟意图识别结果
        mock_llm.invoke.side_effect = [
            json.dumps({"intent": "product_inquiry", "confidence": 0.9, "reason": "用户询问产品"}),
            "这是一个测试回复"
        ]
        
        context = ConversationContext(
            session_id="test_session",
            user_id="test_user", 
            user_message="你们的产品价格是多少？",
            chat_history=[]
        )
        
        response = customer_chain.process_message(context, return_metadata=True)
        
        assert response.intent == "product_inquiry"
        assert response.confidence == 0.9
        assert "测试回复" in response.response
    
    def test_sentiment_analysis(self, customer_chain, mock_llm):
        """测试情感分析"""
        mock_llm.invoke.side_effect = [
            json.dumps({"intent": "general_inquiry", "confidence": 0.8, "reason": "一般询问"}),
            json.dumps({"sentiment": "positive", "intensity": "moderate", "confidence": 0.85, "reason": "积极情感"}),
            "这是一个测试回复"
        ]
        
        context = ConversationContext(
            session_id="test_session",
            user_id="test_user",
            user_message="你们的服务真的很棒！",
            chat_history=[]
        )
        
        response = customer_chain.process_message(context, return_metadata=True)
        
        assert response.sentiment == "positive"
        assert response.confidence == 0.8
    
    def test_content_safety_filter(self, customer_chain, mock_llm):
        """测试内容安全过滤"""
        # 模拟内容安全检查失败
        with patch('src.chains.customer_service.ContentFilter') as mock_filter_class:
            mock_filter = Mock()
            mock_filter.check_content.return_value = Mock(
                is_safe=False,
                risk_level="high",
                violations=["包含不当内容"],
                confidence=0.9,
                reason="检测到不当内容",
                to_dict=lambda: {"is_safe": False, "risk_level": "high"}
            )
            mock_filter_class.return_value = mock_filter
            
            # 重新创建链以使用模拟的过滤器
            chain = CustomerServiceChain(llm=mock_llm, enable_tools=False)
            
            context = ConversationContext(
                session_id="test_session",
                user_id="test_user",
                user_message="不当内容测试",
                chat_history=[]
            )
            
            response = chain.process_message(context, return_metadata=True)
            
            assert "不当内容" in response.response
            assert response.metadata["safety_check"]["is_safe"] == False
    
    def test_escalation_detection(self, customer_chain, mock_llm):
        """测试人工转接检测"""
        mock_llm.invoke.side_effect = [
            json.dumps({"intent": "escalation", "confidence": 0.95, "reason": "需要转接"}),
            json.dumps({"sentiment": "negative", "intensity": "strong", "confidence": 0.9, "reason": "强烈负面"}),
            "这是一个测试回复"
        ]
        
        context = ConversationContext(
            session_id="test_session",
            user_id="test_user",
            user_message="我要投诉，转接人工客服！",
            chat_history=[]
        )
        
        response = customer_chain.process_message(context, return_metadata=True)
        
        assert response.requires_escalation == True
        assert response.intent == "escalation"
    
    def test_chat_history_integration(self, customer_chain, mock_llm):
        """测试对话历史集成"""
        mock_llm.invoke.return_value = "基于历史的回复"
        
        context = ConversationContext(
            session_id="test_session",
            user_id="test_user",
            user_message="继续刚才的话题",
            chat_history=[
                {"role": "user", "content": "你好"},
                {"role": "assistant", "content": "您好！有什么可以帮助您的吗？"},
                {"role": "user", "content": "我想了解产品信息"}
            ]
        )
        
        response = customer_chain.process_message(context)
        
        assert "基于历史的回复" in response


class TestKnowledgeQAChain:
    """测试知识库问答链"""
    
    @pytest.fixture
    def mock_llm(self):
        """模拟LLM"""
        mock = Mock()
        mock.invoke.return_value = "这是知识库中的答案"
        return mock
    
    @pytest.fixture
    def mock_knowledge_base(self):
        """模拟知识库"""
        mock = Mock()
        mock.search_similar_documents.return_value = [
            (Mock(page_content="相关文档内容1"), 0.9),
            (Mock(page_content="相关文档内容2"), 0.85)
        ]
        return mock
    
    @pytest.fixture
    def qa_chain(self, mock_llm, mock_knowledge_base):
        """创建问答链实例"""
        return KnowledgeQAChain(
            knowledge_base=mock_knowledge_base,
            llm=mock_llm
        )
    
    def test_successful_qa(self, qa_chain, mock_knowledge_base, mock_llm):
        """测试成功的问答"""
        # 模拟答案质量评估
        mock_llm.invoke.side_effect = [
            "这是知识库中的答案",
            json.dumps({
                "accuracy": 0.9,
                "completeness": 0.85,
                "relevance": 0.95,
                "clarity": 0.92,
                "overall_confidence": 0.93
            })
        ]
        
        response = qa_chain.answer_question(
            question="什么是LangChain？",
            return_metadata=True
        )
        
        assert "这是知识库中的答案" in response.answer
        assert response.confidence == 0.93
        assert len(response.source_documents) == 2
    
    def test_no_relevant_documents(self, qa_chain, mock_knowledge_base):
        """测试没有相关文档的情况"""
        mock_knowledge_base.search_similar_documents.return_value = []
        
        response = qa_chain.answer_question(
            question="无关问题",
            return_metadata=True
        )
        
        assert "没有找到相关信息" in response.answer
        assert response.confidence == 0.0
        assert len(response.source_documents) == 0
    
    def test_low_confidence_answer(self, qa_chain, mock_llm):
        """测试低置信度答案"""
        mock_llm.invoke.side_effect = [
            "不确定的答案",
            json.dumps({
                "accuracy": 0.3,
                "completeness": 0.4,
                "relevance": 0.5,
                "clarity": 0.6,
                "overall_confidence": 0.45
            })
        ]
        
        response = qa_chain.answer_question(
            question="复杂问题",
            return_metadata=True
        )
        
        assert response.confidence == 0.45
        assert response.confidence < qa_chain.confidence_threshold
    
    def test_document_upload(self, qa_chain, mock_knowledge_base):
        """测试文档上传"""
        mock_knowledge_base.upload_document.return_value = Mock(
            doc_id="test_doc_123",
            filename="test.pdf",
            file_size=1024,
            file_type=".pdf"
        )
        
        doc_info = qa_chain.add_document("/path/to/test.pdf")
        
        assert doc_info.doc_id == "test_doc_123"
        assert doc_info.filename == "test.pdf"
        mock_knowledge_base.upload_document.assert_called_once()
    
    def test_document_deletion(self, qa_chain, mock_knowledge_base):
        """测试文档删除"""
        mock_knowledge_base.delete_document.return_value = True
        
        result = qa_chain.delete_document("test_doc_123")
        
        assert result == True
        mock_knowledge_base.delete_document.assert_called_once_with("test_doc_123")
    
    def test_search_with_threshold(self, qa_chain, mock_knowledge_base):
        """测试带阈值的搜索"""
        # 模拟一些低于阈值的搜索结果
        mock_knowledge_base.search_similar_documents.return_value = [
            (Mock(page_content="低分文档1"), 0.6),  # 低于阈值
            (Mock(page_content="低分文档2"), 0.5),  # 低于阈值
        ]
        
        response = qa_chain.answer_question(
            question="测试问题",
            score_threshold=0.7,  # 设置较高阈值
            return_metadata=True
        )
        
        assert "没有找到相关信息" in response.answer
        assert response.metadata["documents_found"] == 0
        assert response.metadata["threshold_used"] == 0.7


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def integration_setup(self):
        """集成测试设置"""
        # 这里可以设置真实的LLM和数据库连接
        # 但在测试中我们通常使用模拟对象
        pass
    
    def test_end_to_end_conversation(self):
        """端到端对话测试"""
        # 这个测试需要真实的LLM API密钥
        # 通常只在集成测试环境中运行
        pytest.skip("需要真实的LLM API密钥")
    
    def test_knowledge_base_integration(self):
        """知识库集成测试"""
        # 测试文档上传、搜索、问答的完整流程
        pytest.skip("需要真实的数据库和文件系统")
    
    def test_performance_benchmark(self):
        """性能基准测试"""
        # 测试响应时间、内存使用等性能指标
        pytest.skip("需要性能测试环境")


# 测试工具函数
def test_create_customer_service_chain():
    """测试客服链创建函数"""
    from src.chains.customer_service import create_customer_service_chain
    
    chain = create_customer_service_chain(enable_tools=False)
    assert isinstance(chain, CustomerServiceChain)


def test_create_knowledge_qa_chain():
    """测试知识库问答链创建函数"""
    from src.chains.knowledge_qa import create_knowledge_qa_chain
    
    chain = create_knowledge_qa_chain()
    assert isinstance(chain, KnowledgeQAChain)


def test_process_customer_message():
    """测试便捷函数"""
    from src.chains.customer_service import process_customer_message
    
    # 这个测试需要真实的LLM，所以跳过
    pytest.skip("需要真实的LLM API密钥")


def test_answer_from_knowledge_base():
    """测试知识库问答便捷函数"""
    from src.chains.knowledge_qa import answer_from_knowledge_base
    
    # 这个测试需要真实的LLM和知识库，所以跳过
    pytest.skip("需要真实的LLM API密钥和知识库")