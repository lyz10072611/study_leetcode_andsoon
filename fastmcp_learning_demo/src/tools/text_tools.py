"""
文本处理工具示例

这个模块展示了FastMCP的高级文本处理功能，包括文本分析、情感分析、
关键词提取、文本摘要等功能。这些工具展示了如何处理复杂的文本数据。
"""

from fastmcp import FastMCP
from typing import List, Dict, Optional, Any
import re
import json
from collections import Counter
import unicodedata


class TextTools:
    """文本处理工具类，包含各种文本分析和处理工具"""
    
    def __init__(self, mcp: FastMCP):
        """
        初始化文本处理工具
        
        Args:
            mcp: FastMCP服务器实例
        """
        self.mcp = mcp
        self._register_tools()
    
    def _register_tools(self):
        """注册所有文本处理工具"""
        # 基础文本分析
        self.mcp.tool()(self.analyze_text)
        self.mcp.tool()(self.count_words)
        self.mcp.tool()(self.count_characters)
        self.mcp.tool()(self.count_sentences)
        self.mcp.tool()(self.count_paragraphs)
        
        # 文本清洗和预处理
        self.mcp.tool()(self.clean_text)
        self.mcp.tool()(self.remove_special_chars)
        self.mcp.tool()(self.normalize_unicode)
        self.mcp.tool()(self.remove_extra_whitespace)
        
        # 文本转换
        self.mcp.tool()(self.to_uppercase)
        self.mcp.tool()(self.to_lowercase)
        self.mcp.tool()(self.to_title_case)
        self.mcp.tool()(self.reverse_text)
        
        # 文本搜索和替换
        self.mcp.tool()(self.find_occurrences)
        self.mcp.tool()(self.replace_text)
        self.mcp.tool()(self.extract_emails)
        self.mcp.tool()(self.extract_urls)
        self.mcp.tool()(self.extract_phone_numbers)
        
        # 文本分析
        self.mcp.tool()(self.extract_keywords)
        self.mcp.tool()(self.analyze_sentiment)
        self.mcp.tool()(self.detect_language)
        self.mcp.tool()(self.calculate_readability)
        
        # 高级文本处理
        self.mcp.tool()(self.generate_summary)
        self.mcp.tool()(self.tokenize_text)
        self.mcp.tool()(self.find_similar_words)
        self.mcp.tool()(self.detect_plagiarism)
        
        # 格式化工具
        self.mcp.tool()(self.format_text)
        self.mcp.tool()(self.wrap_text)
        self.mcp.tool()(self.indent_text)
        self.mcp.tool()(self.align_text)
    
    # ===== 基础文本分析工具 =====
    
    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        全面分析文本
        
        Args:
            text: 要分析的文本
            
        Returns:
            包含各种文本统计信息的字典
            
        Example:
            >>> analyze_text("Hello world! This is a test.")
            {
                "total_characters": 27,
                "total_words": 6,
                "total_sentences": 2,
                "total_paragraphs": 1,
                "average_word_length": 4.5,
                "average_sentence_length": 13.5,
                "unique_words": 6,
                "most_common_words": [("hello", 1), ("world", 1)]
            }
        """
        if not text or not text.strip():
            return {"error": "文本不能为空"}
        
        # 基础统计
        total_chars = len(text)
        total_words = len(text.split())
        
        # 句子数量（基于标点符号）
        sentences = re.split(r'[.!?]+', text)
        total_sentences = len([s for s in sentences if s.strip()])
        
        # 段落数量（基于空行）
        paragraphs = text.split('\n\n')
        total_paragraphs = len([p for p in paragraphs if p.strip()])
        
        # 单词分析
        words = text.lower().split()
        words_clean = [re.sub(r'[^\w]', '', word) for word in words]
        words_clean = [word for word in words_clean if word]
        
        if words_clean:
            avg_word_length = sum(len(word) for word in words_clean) / len(words_clean)
            unique_words = len(set(words_clean))
            word_counts = Counter(words_clean)
            most_common = word_counts.most_common(5)
        else:
            avg_word_length = 0
            unique_words = 0
            most_common = []
        
        # 句子长度分析
        if total_sentences > 0:
            avg_sentence_length = total_chars / total_sentences
        else:
            avg_sentence_length = 0
        
        return {
            "total_characters": total_chars,
            "total_words": total_words,
            "total_sentences": max(1, total_sentences),  # 至少1个句子
            "total_paragraphs": max(1, total_paragraphs),  # 至少1个段落
            "average_word_length": round(avg_word_length, 2),
            "average_sentence_length": round(avg_sentence_length, 2),
            "unique_words": unique_words,
            "most_common_words": most_common
        }
    
    def count_words(self, text: str) -> int:
        """
        统计文本中的单词数量
        
        Args:
            text: 要统计的文本
            
        Returns:
            单词数量
        """
        return len(text.split()) if text.strip() else 0
    
    def count_characters(self, text: str, include_spaces: bool = True) -> int:
        """
        统计文本中的字符数量
        
        Args:
            text: 要统计的文本
            include_spaces: 是否包含空格，默认为True
            
        Returns:
            字符数量
        """
        if include_spaces:
            return len(text)
        else:
            return len(text.replace(" ", ""))
    
    def count_sentences(self, text: str) -> int:
        """
        统计文本中的句子数量
        
        Args:
            text: 要统计的文本
            
        Returns:
            句子数量
        """
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])
    
    def count_paragraphs(self, text: str) -> int:
        """
        统计文本中的段落数量
        
        Args:
            text: 要统计的文本
            
        Returns:
            段落数量
        """
        paragraphs = text.split('\n\n')
        return len([p for p in paragraphs if p.strip()])
    
    # ===== 文本清洗和预处理工具 =====
    
    def clean_text(self, text: str, remove_urls: bool = True, 
                   remove_emails: bool = True, remove_numbers: bool = False) -> str:
        """
        清洗文本，移除不需要的内容
        
        Args:
            text: 要清洗的文本
            remove_urls: 是否移除URL，默认为True
            remove_emails: 是否移除邮箱地址，默认为True
            remove_numbers: 是否移除数字，默认为False
            
        Returns:
            清洗后的文本
        """
        cleaned = text
        
        if remove_urls:
            cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned)
        
        if remove_emails:
            cleaned = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', cleaned)
        
        if remove_numbers:
            cleaned = re.sub(r'\d+', '', cleaned)
        
        # 移除多余的空白字符
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def remove_special_chars(self, text: str, keep_chars: str = "") -> str:
        """
        移除特殊字符，只保留字母、数字和指定字符
        
        Args:
            text: 要处理的文本
            keep_chars: 要保留的特殊字符
            
        Returns:
            处理后的文本
        """
        # 构建正则表达式模式
        pattern = f'[^\w{re.escape(keep_chars)}\s]'
        return re.sub(pattern, '', text)
    
    def normalize_unicode(self, text: str) -> str:
        """
        标准化Unicode文本
        
        Args:
            text: 要标准化的文本
            
        Returns:
            标准化后的文本
        """
        return unicodedata.normalize('NFKD', text)
    
    def remove_extra_whitespace(self, text: str) -> str:
        """
        移除多余的空白字符
        
        Args:
            text: 要处理的文本
            
        Returns:
            处理后的文本
        """
        # 移除行首行尾空白，合并多个空白字符
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            cleaned_line = re.sub(r'\s+', ' ', line.strip())
            if cleaned_line:
                cleaned_lines.append(cleaned_line)
        return '\n'.join(cleaned_lines)
    
    # ===== 文本转换工具 =====
    
    def to_uppercase(self, text: str) -> str:
        """将文本转换为大写"""
        return text.upper()
    
    def to_lowercase(self, text: str) -> str:
        """将文本转换为小写"""
        return text.lower()
    
    def to_title_case(self, text: str) -> str:
        """将文本转换为标题格式"""
        return text.title()
    
    def reverse_text(self, text: str) -> str:
        """反转文本"""
        return text[::-1]
    
    # ===== 文本搜索和替换工具 =====
    
    def find_occurrences(self, text: str, pattern: str, case_sensitive: bool = True) -> Dict[str, Any]:
        """
        查找文本中模式的出现位置
        
        Args:
            text: 要搜索的文本
            pattern: 要查找的模式
            case_sensitive: 是否区分大小写，默认为True
            
        Returns:
            包含搜索结果的字典
        """
        flags = 0 if case_sensitive else re.IGNORECASE
        matches = list(re.finditer(pattern, text, flags))
        
        return {
            "pattern": pattern,
            "total_occurrences": len(matches),
            "positions": [(match.start(), match.end()) for match in matches],
            "matched_text": [match.group() for match in matches]
        }
    
    def replace_text(self, text: str, old_pattern: str, new_text: str, 
                     case_sensitive: bool = True, use_regex: bool = False) -> str:
        """
        替换文本中的内容
        
        Args:
            text: 原始文本
            old_pattern: 要替换的模式
            new_text: 新文本
            case_sensitive: 是否区分大小写，默认为True
            use_regex: 是否使用正则表达式，默认为False
            
        Returns:
            替换后的文本
        """
        if use_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            return re.sub(old_pattern, new_text, text, flags=flags)
        else:
            if case_sensitive:
                return text.replace(old_pattern, new_text)
            else:
                # 不区分大小写的替换
                pattern = re.compile(re.escape(old_pattern), re.IGNORECASE)
                return pattern.sub(new_text, text)
    
    def extract_emails(self, text: str) -> List[str]:
        """
        提取文本中的邮箱地址
        
        Args:
            text: 要提取的文本
            
        Returns:
            邮箱地址列表
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, text)
    
    def extract_urls(self, text: str) -> List[str]:
        """
        提取文本中的URL
        
        Args:
            text: 要提取的文本
            
        Returns:
            URL列表
        """
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)
    
    def extract_phone_numbers(self, text: str) -> List[str]:
        """
        提取文本中的电话号码
        
        Args:
            text: 要提取的文本
            
        Returns:
            电话号码列表
        """
        # 支持多种电话号码格式
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 123-456-7890 或 123.456.7890
            r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',     # (123) 456-7890
            r'\b\d{3}\s\d{3}\s\d{4}\b',        # 123 456 7890
        ]
        
        phone_numbers = []
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phone_numbers.extend(matches)
        
        return list(set(phone_numbers))  # 去重
    
    # ===== 文本分析工具 =====
    
    def extract_keywords(self, text: str, max_keywords: int = 10, 
                        min_length: int = 3) -> List[Dict[str, int]]:
        """
        提取文本中的关键词
        
        Args:
            text: 要分析的文本
            max_keywords: 最大关键词数量，默认为10
            min_length: 最小关键词长度，默认为3
            
        Returns:
            关键词列表，每个关键词包含单词和频率
        """
        # 转换为小写并提取单词
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # 过滤短词
        words = [word for word in words if len(word) >= min_length]
        
        # 统计词频
        word_counts = Counter(words)
        
        # 获取最常见的关键词
        most_common = word_counts.most_common(max_keywords)
        
        return [{"keyword": word, "frequency": count} for word, count in most_common]
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        简单的情感分析（基于关键词匹配）
        
        Args:
            text: 要分析的文本
            
        Returns:
            情感分析结果
        """
        # 简单的情感词典
        positive_words = {
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'love', 'like', 'happy', 'joy', 'perfect', 'awesome', 'brilliant',
            'outstanding', 'superb', 'magnificent', 'marvelous', 'terrific'
        }
        
        negative_words = {
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike',
            'sad', 'angry', 'disappointed', 'frustrated', 'annoying',
            'worst', 'disgusting', 'pathetic', 'useless', 'boring'
        }
        
        # 转换为小写并分词
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total_words = len(words)
        
        # 计算情感分数
        if total_words > 0:
            positive_ratio = positive_count / total_words
            negative_ratio = negative_count / total_words
            
            if positive_ratio > negative_ratio:
                sentiment = "positive"
                confidence = positive_ratio
            elif negative_ratio > positive_ratio:
                sentiment = "negative"
                confidence = negative_ratio
            else:
                sentiment = "neutral"
                confidence = 0.5
        else:
            sentiment = "neutral"
            confidence = 0.0
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 3),
            "positive_words": positive_count,
            "negative_words": negative_count,
            "total_words": total_words
        }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        简单的语言检测（基于字符特征）
        
        Args:
            text: 要检测的文本
            
        Returns:
            语言检测结果
        """
        if not text.strip():
            return {"language": "unknown", "confidence": 0.0}
        
        # 简单的语言特征
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        japanese_chars = len(re.findall(r'[\u3040-\u309f\u30a0-\u30ff]', text))
        korean_chars = len(re.findall(r'[\uac00-\ud7af]', text))
        arabic_chars = len(re.findall(r'[\u0600-\u06ff]', text))
        cyrillic_chars = len(re.findall(r'[\u0400-\u04ff]', text))
        
        total_chars = len(text)
        
        languages = {
            "chinese": chinese_chars / total_chars if total_chars > 0 else 0,
            "japanese": japanese_chars / total_chars if total_chars > 0 else 0,
            "korean": korean_chars / total_chars if total_chars > 0 else 0,
            "arabic": arabic_chars / total_chars if total_chars > 0 else 0,
            "cyrillic": cyrillic_chars / total_chars if total_chars > 0 else 0,
        }
        
        # 如果检测到非拉丁字符，选择比例最高的
        non_latin_ratio = sum(languages.values())
        if non_latin_ratio > 0.1:
            detected_lang = max(languages.items(), key=lambda x: x[1])
            return {
                "language": detected_lang[0],
                "confidence": round(detected_lang[1], 3),
                "script_ratio": round(non_latin_ratio, 3)
            }
        
        # 否则认为是英文或其他拉丁语系
        return {
            "language": "latin/english",
            "confidence": round(1 - non_latin_ratio, 3),
            "script_ratio": round(non_latin_ratio, 3)
        }
    
    def calculate_readability(self, text: str) -> Dict[str, float]:
        """
        计算文本的可读性分数（简化版Flesch Reading Ease）
        
        Args:
            text: 要分析的文本
            
        Returns:
            可读性分析结果
        """
        if not text.strip():
            return {"error": "文本不能为空"}
        
        # 计算句子数
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # 计算单词数
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        word_count = len(words)
        
        # 计算音节数（简化版：每个元音组算一个音节）
        syllable_count = 0
        for word in words:
            word_syllables = len(re.findall(r'[aeiouAEIOU]+', word))
            if word_syllables == 0:
                word_syllables = 1  # 每个单词至少有一个音节
            syllable_count += word_syllables
        
        if sentence_count == 0 or word_count == 0:
            return {"error": "无法计算可读性：没有有效的句子或单词"}
        
        # 计算Flesch Reading Ease分数
        avg_sentence_length = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count
        
        flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        
        # 确定阅读级别
        if flesch_score >= 90:
            grade_level = "5th grade"
            difficulty = "Very easy to read"
        elif flesch_score >= 80:
            grade_level = "6th grade"
            difficulty = "Easy to read"
        elif flesch_score >= 70:
            grade_level = "7th grade"
            difficulty = "Fairly easy to read"
        elif flesch_score >= 60:
            grade_level = "8th & 9th grade"
            difficulty = "Plain English"
        elif flesch_score >= 50:
            grade_level = "10th to 12th grade"
            difficulty = "Fairly difficult to read"
        elif flesch_score >= 30:
            grade_level = "College level"
            difficulty = "Difficult to read"
        else:
            grade_level = "Graduate level"
            difficulty = "Very difficult to read"
        
        return {
            "flesch_reading_ease": round(flesch_score, 2),
            "grade_level": grade_level,
            "difficulty": difficulty,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_syllables_per_word": round(avg_syllables_per_word, 2),
            "sentence_count": sentence_count,
            "word_count": word_count,
            "syllable_count": syllable_count
        }
    
    # ===== 高级文本处理工具 =====
    
    def generate_summary(self, text: str, max_sentences: int = 3) -> str:
        """
        生成文本摘要（基于句子重要性）
        
        Args:
            text: 要总结的文本
            max_sentences: 最大句子数，默认为3
            
        Returns:
            文本摘要
        """
        if not text.strip():
            return ""
        
        # 分割句子
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= max_sentences:
            return text
        
        # 计算每个句子的关键词得分
        keywords = self.extract_keywords(text, max_keywords=10)
        keyword_set = set(kw["keyword"] for kw in keywords)
        
        sentence_scores = []
        for sentence in sentences:
            score = 0
            words = re.findall(r'\b[a-zA-Z]+\b', sentence.lower())
            
            # 关键词匹配得分
            for word in words:
                if word in keyword_set:
                    score += 1
            
            # 句子长度惩罚（过短或过长的句子得分降低）
            word_count = len(words)
            if word_count < 3 or word_count > 30:
                score *= 0.5
            
            # 位置得分（开头的句子更重要）
            position_score = 1.0 / (sentences.index(sentence) + 1)
            score *= (1 + position_score)
            
            sentence_scores.append((sentence, score))
        
        # 选择得分最高的句子
        sentence_scores.sort(key=lambda x: x[1], reverse=True)
        selected_sentences = [s[0] for s in sentence_scores[:max_sentences]]
        
        # 按原文顺序排列
        summary_sentences = []
        for sentence in sentences:
            if sentence in selected_sentences:
                summary_sentences.append(sentence)
        
        return '. '.join(summary_sentences) + '.'
    
    def tokenize_text(self, text: str, method: str = "word") -> List[str]:
        """
        文本分词
        
        Args:
            text: 要分词的文本
            method: 分词方法，可选"word"、"sentence"、"character"
            
        Returns:
            分词结果列表
        """
        if method == "word":
            return re.findall(r'\b[a-zA-Z]+\b', text.lower())
        elif method == "sentence":
            sentences = re.split(r'[.!?]+', text)
            return [s.strip() for s in sentences if s.strip()]
        elif method == "character":
            return list(text)
        else:
            return ["error: 不支持的分词方法"]
    
    def find_similar_words(self, text: str, target_word: str, 
                          similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        查找文本中与目标词相似的单词（基于编辑距离）
        
        Args:
            text: 要搜索的文本
            target_word: 目标词
            similarity_threshold: 相似度阈值，默认为0.7
            
        Returns:
            相似词列表
        """
        def levenshtein_distance(s1: str, s2: str) -> int:
            """计算编辑距离"""
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
            
            if len(s2) == 0:
                return len(s1)
            
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        def similarity(s1: str, s2: str) -> float:
            """计算相似度"""
            distance = levenshtein_distance(s1.lower(), s2.lower())
            max_len = max(len(s1), len(s2))
            if max_len == 0:
                return 1.0
            return 1 - (distance / max_len)
        
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        target_lower = target_word.lower()
        
        similar_words = []
        for word in set(words):  # 去重
            if word != target_lower:
                sim_score = similarity(word, target_lower)
                if sim_score >= similarity_threshold:
                    similar_words.append({
                        "word": word,
                        "similarity": round(sim_score, 3),
                        "frequency": words.count(word)
                    })
        
        # 按相似度排序
        similar_words.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similar_words
    
    def detect_plagiarism(self, text1: str, text2: str, 
                         similarity_threshold: float = 0.8) -> Dict[str, Any]:
        """
        检测两个文本之间的相似性（简化版）
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            similarity_threshold: 相似度阈值，默认为0.8
            
        Returns:
            相似性检测结果
        """
        def get_ngrams(text: str, n: int = 3) -> set:
            """获取n-gram集合"""
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
            ngrams = set()
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                ngrams.add(ngram)
            return ngrams
        
        # 获取3-gram
        ngrams1 = get_ngrams(text1, 3)
        ngrams2 = get_ngrams(text2, 3)
        
        if not ngrams1 or not ngrams2:
            return {
                "similarity": 0.0,
                "common_ngrams": 0,
                "total_ngrams": 0,
                "plagiarism_detected": False,
                "common_phrases": []
            }
        
        # 计算共同n-gram
        common_ngrams = ngrams1.intersection(ngrams2)
        total_ngrams = ngrams1.union(ngrams2)
        
        # 计算Jaccard相似度
        similarity = len(common_ngrams) / len(total_ngrams) if total_ngrams else 0
        
        return {
            "similarity": round(similarity, 3),
            "common_ngrams": len(common_ngrams),
            "total_ngrams": len(total_ngrams),
            "plagiarism_detected": similarity >= similarity_threshold,
            "common_phrases": list(common_ngrams)[:10]  # 最多显示10个
        }
    
    # ===== 格式化工具 =====
    
    def format_text(self, text: str, width: int = 80, justify: str = "left") -> str:
        """
        格式化文本
        
        Args:
            text: 要格式化的文本
            width: 每行宽度，默认为80
            justify: 对齐方式，可选"left"、"right"、"center"、"justify"
            
        Returns:
            格式化后的文本
        """
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            if not line.strip():
                formatted_lines.append("")
                continue
            
            words = line.split()
            if justify == "justify" and len(words) > 1:
                # 两端对齐处理
                current_line = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + len(current_line) <= width:
                        current_line.append(word)
                        current_length += len(word)
                    else:
                        if len(current_line) > 1:
                            # 在单词间插入空格以实现两端对齐
                            total_spaces = width - current_length
                            spaces_between = len(current_line) - 1
                            base_space = total_spaces // spaces_between
                            extra_spaces = total_spaces % spaces_between
                            
                            justified_line = current_line[0]
                            for i, word in enumerate(current_line[1:], 1):
                                spaces = base_space + (1 if i <= extra_spaces else 0)
                                justified_line += ' ' * spaces + word
                            
                            formatted_lines.append(justified_line)
                        else:
                            formatted_lines.append(current_line[0].ljust(width))
                        
                        current_line = [word]
                        current_length = len(word)
                
                if current_line:
                    formatted_lines.append(' '.join(current_line).ljust(width))
            else:
                # 其他对齐方式
                if justify == "left":
                    formatted_lines.append(line.ljust(width))
                elif justify == "right":
                    formatted_lines.append(line.rjust(width))
                elif justify == "center":
                    formatted_lines.append(line.center(width))
                else:
                    formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def wrap_text(self, text: str, width: int = 80) -> str:
        """
        自动换行
        
        Args:
            text: 要处理的文本
            width: 每行宽度，默认为80
            
        Returns:
            自动换行后的文本
        """
        import textwrap
        return textwrap.fill(text, width=width)
    
    def indent_text(self, text: str, spaces: int = 4) -> str:
        """
        缩进文本
        
        Args:
            text: 要处理的文本
            spaces: 缩进空格数，默认为4
            
        Returns:
            缩进后的文本
        """
        indent = ' ' * spaces
        lines = text.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)
    
    def align_text(self, text: str, width: int = 80, alignment: str = "center") -> str:
        """
        对齐文本
        
        Args:
            text: 要对齐的文本
            width: 宽度，默认为80
            alignment: 对齐方式，可选"left"、"right"、"center"
            
        Returns:
            对齐后的文本
        """
        lines = text.split('\n')
        aligned_lines = []
        
        for line in lines:
            if alignment == "left":
                aligned_lines.append(line.ljust(width))
            elif alignment == "right":
                aligned_lines.append(line.rjust(width))
            elif alignment == "center":
                aligned_lines.append(line.center(width))
            else:
                aligned_lines.append(line)
        
        return '\n'.join(aligned_lines)