"""
自动分类解析器 (Auto Parser)
"""

from typing import List, Dict, Optional, Union, Set
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


try:
    import thulac
    THULAC_AVAILABLE = True
except ImportError:
    THULAC_AVAILABLE = False
    logger.warning("THULAC not installed. Please install with: pip install thulac")


class AutoParser:
    
    CONTENT_TYPES = [
        "dialogue",    # 对话
        "action",      # 动作
        "narration",   # 旁白
        "unknown",     # 未知
        "ooc",         # 场外讨论
    ]
    
    # THULAC 词性标注说明
    # n/名词 np/人名 ns/地名 ni/机构名 nz/其它专名
    # m/数词 q/量词 mq/数量词 t/时间词 f/方位词 s/处所词
    # v/动词 a/形容词 d/副词 
    # h/前接成分 k/后接成分
    # i/习语 j/简称 r/代词 c/连词 p/介词 
    # u/助词 y/语气助词 e/叹词 o/拟声词
    # g/语素 w/标点 x/其它
    
    # 词性到内容类型的映射策略
    POS_WEIGHTS = {
        # 动词相关 - 倾向于动作
        'v': {'action': 0.8, 'narration': 0.2},
        
        # 名词相关 - 倾向于旁白
        'n': {'narration': 0.7, 'dialogue': 0.3},
        'np': {'narration': 0.6, 'dialogue': 0.4},  # 人名可能出现在对话中
        'ns': {'narration': 0.8, 'dialogue': 0.2},  # 地名
        'ni': {'narration': 0.8, 'dialogue': 0.2},  # 机构名
        'nz': {'narration': 0.7, 'dialogue': 0.3},  # 其它专名
        
        # 代词 - 倾向于对话
        'r': {'dialogue': 0.7, 'narration': 0.3},
        
        # 形容词 - 倾向于旁白或对话
        'a': {'narration': 0.5, 'dialogue': 0.4, 'action': 0.1},
        
        # 副词 - 可以是任何类型
        'd': {'dialogue': 0.4, 'narration': 0.4, 'action': 0.2},
        
        # 助词、语气词 - 倾向于对话
        'u': {'dialogue': 0.8, 'narration': 0.2},
        'y': {'dialogue': 0.9, 'narration': 0.1},  # 语气助词
        'e': {'dialogue': 0.8, 'action': 0.2},     # 叹词
        
        # 量词、数词 - 倾向于旁白
        'm': {'narration': 0.8, 'dialogue': 0.2},
        'q': {'narration': 0.7, 'dialogue': 0.3},
        'mq': {'narration': 0.8, 'dialogue': 0.2},
        
        # 时间、方位、处所 - 倾向于旁白
        't': {'narration': 0.8, 'dialogue': 0.2},
        'f': {'narration': 0.7, 'dialogue': 0.3},
        's': {'narration': 0.8, 'dialogue': 0.2},
    }
    
    def __init__(self, seg_only: bool = False, user_dict: str = None):
        """
        初始化自动解析器
        
        Args:
            seg_only: 是否只进行分词（不标注词性）
            user_dict: 用户自定义词典路径
        """
        if not THULAC_AVAILABLE:
            raise ImportError(
                "THULAC is not installed. Please install with:\n"
                "pip install thulac\n"
                "Note: First installation may take a few minutes to download models."
            )
        
        self.thulac = thulac.thulac(
            seg_only=seg_only,
            user_dict=user_dict if user_dict else None
        )
        
        # 可选的自定义关键词列表
        self.custom_action_words: Set[str] = set()
        self.custom_dialogue_words: Set[str] = set()
        self.custom_narration_words: Set[str] = set()
        self.custom_ooc_words: Set[str] = set()
        
        # 统计信息
        self.statistics = {
            "total_lines": 0,
            "parsed_lines": 0,
            "error_lines": 0,
        }
        
        # 初始化每种类型的计数
        for content_type in self.CONTENT_TYPES:
            self.statistics[f"{content_type}_count"] = 0
        
        logger.info(f"AutoParser initialized with THULAC seg_only={seg_only}")
    
    def load_custom_keywords(self, 
                           action_words: Optional[List[str]] = None,
                           dialogue_words: Optional[List[str]] = None,
                           narration_words: Optional[List[str]] = None,
                           ooc_words: Optional[List[str]] = None):
        """
        加载自定义关键词列表
        
        Args:
            action_words: 动作关键词列表
            dialogue_words: 对话关键词列表
            narration_words: 旁白关键词列表
            ooc_words: OOC关键词列表
        """
        if action_words:
            self.custom_action_words.update(action_words)
            logger.info(f"Loaded {len(action_words)} custom action words")
        
        if dialogue_words:
            self.custom_dialogue_words.update(dialogue_words)
            logger.info(f"Loaded {len(dialogue_words)} custom dialogue words")
        
        if narration_words:
            self.custom_narration_words.update(narration_words)
            logger.info(f"Loaded {len(narration_words)} custom narration words")
        
        if ooc_words:
            self.custom_ooc_words.update(ooc_words)
            logger.info(f"Loaded {len(ooc_words)} custom ooc words")
    
    def load_keywords_from_file(self, file_path: Union[str, Path], 
                               content_type: str):
        """
        从文件加载关键词列表
        
        Args:
            file_path: 关键词文件路径，每行一个关键词
            content_type: 内容类型 ('action', 'dialogue', 'narration')
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Keywords file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
        
        if content_type == 'action':
            self.custom_action_words.update(keywords)
        elif content_type == 'dialogue':
            self.custom_dialogue_words.update(keywords)
        elif content_type == 'narration':
            self.custom_narration_words.update(keywords)
        elif content_type == 'ooc':
            self.custom_ooc_words.update(keywords)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
        
        logger.info(f"Loaded {len(keywords)} {content_type} keywords from {file_path}")
    
    def parse_line(self, line: str, line_number: int = None) -> Dict:
        """
        解析单行日志，返回包含分类信息的字典
        
        Args:
            line: 要解析的文本行
            line_number: 行号（可选）
        
        Returns:
            {
                "line_number": 1,
                "raw_text": "原始文本",
                "content": "内容文本",
                "content_type": "dialogue",
                "words": ["我", "喜欢", "你"],
                "pos_tags": ["r", "v", "r"],
                "confidence": 0.85,
                "analysis": {}  # 词法分析详情
            }
        """
        self.statistics["total_lines"] += 1
        
        # 基础结果结构
        result = {
            "line_number": line_number,
            "raw_text": line,
            "content": "",
            "content_type": "unknown",
            "words": [],
            "pos_tags": [],
            "confidence": 0.0,
            "analysis": {}
        }
        
        # 空行处理
        if not line or not line.strip():
            result["content_type"] = "unknown"
            return result
        
        text = line.strip()
        result["content"] = text
        
        # 使用 THULAC 进行词法分析
        try:
            # THULAC 返回 [(word, pos), (word, pos), ...]
            lac_result = self.thulac.cut(text, text=False)
            
            # 分离词和词性
            words = [item[0] for item in lac_result]
            pos_tags = [item[1] for item in lac_result]
            
            result["words"] = words
            result["pos_tags"] = pos_tags
            
            # 基于词法分析结果分类
            content_type, confidence, analysis = self._classify_by_thulac(words, pos_tags)
            
            result["content_type"] = content_type
            result["confidence"] = confidence
            result["analysis"] = analysis
            
            # 更新统计
            self.statistics["parsed_lines"] += 1
            self.statistics[f"{content_type}_count"] += 1
            
        except Exception as e:
            logger.error(f"Error analyzing line {line_number}: {e}")
            self.statistics["error_lines"] += 1
            result["analysis"]["error"] = str(e)
        
        return result
    
    def _classify_by_thulac(self, words: List[str], pos_tags: List[str]) -> tuple:
        """
        基于 THULAC 词法分析结果进行分类
        
        Args:
            words: 分词结果
            pos_tags: 词性标注结果
        
        Returns:
            (content_type, confidence, analysis_dict)
        """
        if not words or not pos_tags:
            return "unknown", 0.0, {}
        
        # 初始化类型分数（排除 unknown）
        type_scores = {content_type: 0.0 for content_type in self.CONTENT_TYPES if content_type != 'unknown'}
        
        # 分析详情
        analysis = {
            "word_count": len(words),
            "pos_distribution": {},
            "custom_matches": []
        }
        
        # 统计词性分布
        for pos in pos_tags:
            if pos != 'w':  # 忽略标点
                analysis["pos_distribution"][pos] = analysis["pos_distribution"].get(pos, 0) + 1
        
        # 基于词性加权计算类型分数
        for i, (word, pos) in enumerate(zip(words, pos_tags)):
            # 跳过标点
            if pos == 'w':
                continue
            
            # 检查自定义关键词（优先级最高）
            if word in self.custom_action_words:
                type_scores['action'] += 1.0
                analysis["custom_matches"].append({"word": word, "type": "action"})
            elif word in self.custom_dialogue_words:
                type_scores['dialogue'] += 1.0
                analysis["custom_matches"].append({"word": word, "type": "dialogue"})
            elif word in self.custom_narration_words:
                type_scores['narration'] += 1.0
                analysis["custom_matches"].append({"word": word, "type": "narration"})
            elif word in self.custom_ooc_words:
                type_scores['ooc'] += 1.0
                analysis["custom_matches"].append({"word": word, "type": "ooc"})
            
            # 应用词性权重
            if pos in self.POS_WEIGHTS:
                weights = self.POS_WEIGHTS[pos]
                for content_type, weight in weights.items():
                    type_scores[content_type] += weight
        
        # 归一化分数
        total_score = sum(type_scores.values())
        if total_score > 0:
            for content_type in type_scores:
                type_scores[content_type] /= total_score
        
        # 选择得分最高的类型
        if type_scores:
            content_type = max(type_scores.items(), key=lambda x: x[1])
            analysis["type_scores"] = type_scores
            
            # 如果最高分太低，标记为 unknown
            if content_type[1] < 0.3:
                return "unknown", content_type[1], analysis
            
            return content_type[0], content_type[1], analysis
        
        return "unknown", 0.0, analysis
    
    def parse_log_file(self, file_path: Union[str, Path]) -> List[Dict]:
        """
        批处理方法：按行解析日志文件
        
        Args:
            file_path: 日志文件路径
        
        Returns:
            包含所有解析结果的列表，每个元素都是一个 dict
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Log file not found: {file_path}")
        
        logger.info(f"Parsing log file: {file_path}")
        
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 批量处理以提高效率
            texts = [line.strip() for line in lines]
            
            for line_num, (line, text) in enumerate(zip(lines, texts), start=1):
                if not text:
                    # 跳过空行
                    continue
                
                try:
                    result = self.parse_line(text, line_number=line_num)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error parsing line {line_num}: {e}")
                    self.statistics["error_lines"] += 1
                    # 添加错误记录
                    results.append({
                        "line_number": line_num,
                        "raw_text": line.strip(),
                        "content": text,
                        "content_type": "unknown",
                        "words": [],
                        "pos_tags": [],
                        "confidence": 0.0,
                        "analysis": {"error": str(e)}
                    })
        
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
        
        logger.info(f"Successfully parsed {len(results)} lines from {file_path}")
        return results
    
    def parse_text_batch(self, lines: List[str]) -> List[Dict]:
        """
        批处理方法：解析文本行列表
        
        Args:
            lines: 文本行列表
        
        Returns:
            包含所有解析结果的列表
        """
        results = []
        
        for line_num, line in enumerate(lines, start=1):
            try:
                result = self.parse_line(line, line_number=line_num)
                results.append(result)
            except Exception as e:
                logger.error(f"Error parsing line {line_num}: {e}")
                self.statistics["error_lines"] += 1
                results.append({
                    "line_number": line_num,
                    "raw_text": line,
                    "content": line.strip(),
                    "content_type": "unknown",
                    "words": [],
                    "pos_tags": [],
                    "confidence": 0.0,
                    "analysis": {"error": str(e)}
                })
        
        return results
    
    def get_statistics(self) -> Dict:
        """获取解析统计信息"""
        stats = self.statistics.copy()
        
        # 计算成功率
        if stats["total_lines"] > 0:
            stats["success_rate"] = stats["parsed_lines"] / stats["total_lines"]
            stats["error_rate"] = stats["error_lines"] / stats["total_lines"]
        else:
            stats["success_rate"] = 0.0
            stats["error_rate"] = 0.0
        
        return stats
    
    def reset_statistics(self):
        """重置统计信息"""
        for key in self.statistics:
            self.statistics[key] = 0
    
    def get_content_types(self) -> List[str]:
        """获取所有支持的内容类型"""
        return self.CONTENT_TYPES.copy()
    
    def filter_by_type(self, parsed_data: List[Dict], 
                      content_type: str) -> List[Dict]:
        """
        按内容类型过滤解析结果
        
        Args:
            parsed_data: 解析结果列表
            content_type: 要过滤的内容类型
        
        Returns:
            过滤后的结果列表
        """
        if content_type not in self.CONTENT_TYPES:
            logger.warning(f"Unknown content type: {content_type}")
            return []
        
        return [item for item in parsed_data if item["content_type"] == content_type]
    
    def group_by_type(self, parsed_data: List[Dict]) -> Dict[str, List[Dict]]:
        """
        按内容类型分组
        
        Args:
            parsed_data: 解析结果列表
        
        Returns:
            按类型分组的字典
        """
        grouped = {content_type: [] for content_type in self.CONTENT_TYPES}
        
        for item in parsed_data:
            content_type = item.get("content_type", "unknown")
            if content_type in grouped:
                grouped[content_type].append(item)
        
        return grouped
