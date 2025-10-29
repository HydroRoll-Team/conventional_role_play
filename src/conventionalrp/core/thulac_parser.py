"""
基于清华 THULAC 的智能解析器

使用 THULAC (THU Lexical Analyzer for Chinese) 进行中文词法分析，
自动识别 TRPG 日志中的对话、动作、旁白等内容类型，
大幅简化规则配置。

THULAC 是清华大学自然语言处理与社会人文计算实验室研制推出的
一套中文词法分析工具包，具有中文分词和词性标注功能。

词性标注说明：
- n/名词 np/人名 ns/地名 ni/机构名 nz/其它专名
- m/数词 q/量词 mq/数量词 t/时间词 f/方位词 s/处所词
- v/动词 a/形容词 d/副词 
- h/前接成分 k/后接成分
- i/习语 j/简称 r/代词 c/连词 p/介词 
- u/助词 y/语气助词 e/叹词 o/拟声词
- g/语素 w/标点 x/其它
"""

import re
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

try:
    import thulac
    THULAC_AVAILABLE = True
except ImportError:
    THULAC_AVAILABLE = False
    logger.warning("THULAC not installed. Please install with: pip install thulac")
    


class THULACParser:
    # 默认分隔符配置（可通过 load_rules 覆盖）
    DEFAULT_DELIMITERS = {
        "dialogue": [
            ('"', '"'),      # 英文双引号
            ('"', '"'),      # 中文双引号
            ("'", "'"),      # 单引号
        ],
        "thought": [
            ("【", "】"),     # 中文方括号
            ("[", "]"),      # 英文方括号
        ],
        "action": [
            ("（", "）"),     # 中文括号
            ("(", ")"),      # 英文括号
            ("*", "*"),      # 星号
            ("**", "**"),    # 双星号
        ],
        "ooc": [
            ("//", "\n"),    # 双斜杠到行尾
            (">>", "\n"),    # 双右尖括号到行尾
        ]
    }
    
    POS_TYPE_MAPPING = {
        # 动词相关 -> 动作
        "v": "action",      # 动词
        
        # 名词相关 -> 旁白
        "n": "narration",   # 名词
        "np": "narration",  # 人名
        "ns": "narration",  # 地名
        "ni": "narration",  # 机构名
        "nz": "narration",  # 其它专名
        
        # 代词 -> 对话（第一人称/第二人称倾向于对话）
        "r": "dialogue",    # 代词
        
        # 副词/形容词 -> 旁白
        "d": "narration",   # 副词
        "a": "narration",   # 形容词
        
        # 量词/数词 -> 旁白
        "m": "narration",   # 数词
        "q": "narration",   # 量词
        "mq": "narration",  # 数量词
        
        # 时间/方位/处所 -> 旁白
        "t": "narration",   # 时间词
        "f": "narration",   # 方位词
        "s": "narration",   # 处所词
        
        # 语气词/叹词 -> 对话
        "y": "dialogue",    # 语气助词
        "e": "dialogue",    # 叹词
    }
    
    # 动作动词关键词（优先级更高）
    ACTION_VERBS = {
        "走", "跑", "看", "听", "摸", "拿", "放", "打开", "关闭",
        "推", "拉", "举", "扔", "跳", "爬", "坐", "站", "躺",
        "进入", "离开", "接近", "远离", "转身", "回头", "低头", "抬头",
        "微笑", "大笑", "哭", "喊", "叫", "说", "讲", "念", "读",
        "投掷", "检定", "攻击", "防御", "躲避"
    }
    
    # 对话相关关键词
    DIALOGUE_INDICATORS = {
        "我", "你", "他", "她", "我们", "你们", "他们",
        "吗", "呢", "啊", "哦", "嗯", "哼", "咦", "哎",
    }
    
    def __init__(self, seg_only: bool = False, user_dict: str = None):
        """
        初始化 THULAC 解析器
        
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
        
        self.seg_only = seg_only
        self.thulac = thulac.thulac(
            seg_only=seg_only,
            user_dict=user_dict if user_dict else None
        )
        
        self.delimiters = self.DEFAULT_DELIMITERS.copy()
        self.custom_words = {}
        self.statistics = {
            "total_parsed": 0,
            "dialogue_count": 0,
            "action_count": 0,
            "thought_count": 0,
            "narration_count": 0,
            "ooc_count": 0,
        }
        
        logger.info(f"THULACParser initialized with seg_only={seg_only}")
    
    def load_rules(self, rules_path: str = None, rules_dict: Dict = None):
        """
        加载简化的规则配置
        
        Args:
            rules_path: 规则文件路径（JSON5 格式）
            rules_dict: 直接传入规则字典
            
        规则格式示例：
        ```json
        {
            "delimiters": {
                "dialogue": [["\"", "\""], [""", """]],
                "action": [["(", ")"], ["*", "*"]],
                "thought": [["【", "】"]]
            },
            "custom_words": {
                "骰子": "n",
                "检定": "v",
                "守秘人": "np"
            }
        }
        ```
        """
        import json5
        from pathlib import Path
        
        if rules_path:
            if not Path(rules_path).exists():
                raise FileNotFoundError(f"Rules file not found: {rules_path}")
            with open(rules_path, "r", encoding="utf-8") as f:
                rules_dict = json5.load(f)
        
        if not rules_dict:
            logger.info("No rules provided, using default delimiters")
            return
        
        # 加载分隔符配置
        if "delimiters" in rules_dict:
            for content_type, delimiter_pairs in rules_dict["delimiters"].items():
                self.delimiters[content_type] = [tuple(pair) for pair in delimiter_pairs]
        
        # 加载自定义词汇（词 -> 词性）
        if "custom_words" in rules_dict:
            self.custom_words = rules_dict["custom_words"]
            logger.info(f"Loaded {len(self.custom_words)} custom words")
        
        logger.info("Rules loaded successfully")
    
    def _extract_delimited_content(self, text: str) -> List[Dict]:
        """
        提取分隔符标记的内容
        
        Returns:
            List of {type, content, start, end, delimiter}
        """
        results = []
        
        for content_type, delimiter_pairs in self.delimiters.items():
            for start_delim, end_delim in delimiter_pairs:
                # 转义正则特殊字符
                start_pattern = re.escape(start_delim)
                end_pattern = re.escape(end_delim)
                
                # 处理到行尾的情况
                if end_delim == "\n":
                    pattern = f"{start_pattern}(.+?)(?:\n|$)"
                else:
                    pattern = f"{start_pattern}(.+?){end_pattern}"
                
                for match in re.finditer(pattern, text):
                    results.append({
                        "type": content_type,
                        "content": match.group(1),
                        "start": match.start(),
                        "end": match.end(),
                        "delimiter": (start_delim, end_delim),
                        "confidence": 1.0  # 分隔符匹配的置信度为 100%
                    })
        
        results.sort(key=lambda x: x["start"])
        return results
    
    def _analyze_with_thulac(self, text: str) -> List[Dict]:
        """
        使用 THULAC 分析文本
        
        Returns:
            List of {type, content, words, tags, confidence}
        """
        result = self.thulac.cut(text, text=False)  # 返回 [(word, pos), ...]
        
        if not result:
            return [{
                "type": "narration",
                "content": text,
                "words": [],
                "tags": [],
                "confidence": 0.5,
                "method": "thulac"
            }]
        
        # 分离词和词性
        words = [item[0] for item in result]
        tags = [item[1] for item in result]
        
        # 应用自定义词性（如果有）
        for i, word in enumerate(words):
            if word in self.custom_words:
                tags[i] = self.custom_words[word]
        
        # 基于词性和内容推断类型
        content_type = self._infer_content_type(words, tags)
        confidence = self._calculate_confidence(words, tags, content_type)
        
        return [{
            "type": content_type,
            "content": text,
            "words": words,
            "tags": tags,
            "confidence": confidence,
            "method": "thulac"
        }]
    
    def _infer_content_type(self, words: List[str], tags: List[str]) -> str:
        """
        基于词性和内容推断内容类型
        
        策略：
        1. 检查是否包含动作动词 -> action
        2. 检查是否包含对话指示词 -> dialogue
        3. 统计主导词性 -> 按映射表判断
        """
        for word in words:
            if word in self.ACTION_VERBS:
                return "action"
        
        dialogue_indicators = sum(1 for w in words if w in self.DIALOGUE_INDICATORS)
        if dialogue_indicators >= 2:  # 至少2个对话指示词
            return "dialogue"
        
        pos_count = {}
        for tag in tags:
            if tag == "w":  # 忽略标点
                continue
            pos_count[tag] = pos_count.get(tag, 0) + 1
        
        if not pos_count:
            return "narration"
        
        # 找出最常见的词性
        dominant_pos = max(pos_count.items(), key=lambda x: x[1])[0]
        
        # 特殊规则：如果有动词，倾向于判断为动作
        if "v" in pos_count and pos_count["v"] >= len(words) * 0.3:
            return "action"
        
        # 根据主导词性映射
        return self.POS_TYPE_MAPPING.get(dominant_pos, "narration")
    
    def _calculate_confidence(self, words: List[str], tags: List[str], 
                            content_type: str) -> float:
        """
        计算分析置信度
        
        基于以下因素：
        1. 词性标注的一致性
        2. 关键词匹配度
        3. 文本长度
        """
        if not words or not tags:
            return 0.5
        
        base_confidence = 0.5
        
        if content_type == "action":
            action_word_count = sum(1 for w in words if w in self.ACTION_VERBS)
            if action_word_count > 0:
                base_confidence += 0.3
        elif content_type == "dialogue":
            dialogue_word_count = sum(1 for w in words if w in self.DIALOGUE_INDICATORS)
            if dialogue_word_count >= 2:
                base_confidence += 0.3

        unique_pos = len(set(tag for tag in tags if tag != "w"))
        if unique_pos == 1:
            base_confidence += 0.2
        elif unique_pos <= 3:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _merge_results(self, delimited: List[Dict], thulac_results: List[Dict], 
                      text: str) -> List[Dict]:
        """
        合并分隔符提取和 THULAC 分析结果
        
        优先级：分隔符标记 > THULAC 分析
        """
        if not delimited:
            return thulac_results
        
        results = []
        covered_ranges = set()
        
        for item in delimited:
            results.append(item)
            for i in range(item["start"], item["end"]):
                covered_ranges.add(i)
        
        uncovered_segments = []
        start = 0
        for i in range(len(text)):
            if i in covered_ranges:
                if start < i:
                    uncovered_segments.append((start, i))
                start = i + 1
        if start < len(text):
            uncovered_segments.append((start, len(text)))
        
        for start, end in uncovered_segments:
            segment = text[start:end].strip()
            if segment:
                thulac_result = self._analyze_with_thulac(segment)
                for item in thulac_result:
                    item["start"] = start
                    item["end"] = end
                    results.append(item)
        
        results.sort(key=lambda x: x.get("start", 0))
        return results
    
    def parse_line(self, line: str) -> Dict:
        """
        解析单行日志
        
        Args:
            line: 日志行
            
        Returns:
            {
                "metadata": {...},
                "content": [...]
            }
        """
        if not line or not line.strip():
            return {"metadata": {}, "content": []}
        
        # 提取元数据（时间戳、发言人等）
        metadata = self._extract_metadata(line)
        
        # 移除元数据后的内容
        content_text = self._remove_metadata(line, metadata)
        
        # 1. 提取分隔符标记的内容
        delimited = self._extract_delimited_content(content_text)
        
        # 2. 使用 THULAC 分析未标记的内容
        thulac_results = []
        if not delimited or len(delimited) == 0:
            thulac_results = self._analyze_with_thulac(content_text)
        
        # 3. 合并结果
        content = self._merge_results(delimited, thulac_results, content_text)
        
        # 更新统计
        self.statistics["total_parsed"] += 1
        for item in content:
            type_key = f"{item['type']}_count"
            if type_key in self.statistics:
                self.statistics[type_key] += 1
        
        return {
            "metadata": metadata,
            "content": content
        }
    
    def _extract_metadata(self, line: str) -> Dict:
        """提取元数据（时间戳、发言人）"""
        metadata = {}
        
        # 常见的元数据格式
        patterns = [
            r"^\[(.+?)\]\s*<(.+?)>",           # [时间] <发言人>
            r"^(.+?)\s*\|\s*(.+?)\s*:",        # 时间 | 发言人:
            r"^<(.+?)>\s*@\s*(.+?)$",          # <发言人> @ 时间
        ]
        
        for pattern in patterns:
            match = re.search(pattern, line)
            if match:
                metadata["timestamp"] = match.group(1)
                metadata["speaker"] = match.group(2)
                break
        
        return metadata
    
    def _remove_metadata(self, line: str, metadata: Dict) -> str:
        """移除元数据，返回纯内容"""
        if not metadata:
            return line
        
        # 移除匹配到的元数据部分
        patterns = [
            r"^\[.+?\]\s*<.+?>\s*",
            r"^.+?\s*\|\s*.+?\s*:\s*",
            r"^<.+?>\s*@\s*.+?\s*",
        ]
        
        for pattern in patterns:
            line = re.sub(pattern, "", line, count=1)
        
        return line.strip()
    
    def parse_log(self, log_path: str) -> List[Dict]:
        """
        解析完整的 TRPG 日志文件
        
        Args:
            log_path: 日志文件路径
            
        Returns:
            解析结果列表
        """
        from pathlib import Path
        
        if not Path(log_path).exists():
            raise FileNotFoundError(f"Log file not found: {log_path}")
        
        with open(log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        results = []
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            try:
                result = self.parse_line(line)
                result["line_number"] = i + 1
                results.append(result)
            except Exception as e:
                logger.error(f"Error parsing line {i+1}: {e}")
                results.append({
                    "line_number": i + 1,
                    "error": str(e),
                    "raw_line": line
                })
        
        logger.info(f"Parsed {len(results)} lines from {log_path}")
        return results
    
    def get_statistics(self) -> Dict:
        """获取解析统计信息"""
        return self.statistics.copy()
    
    def reset_statistics(self):
        """重置统计信息"""
        for key in self.statistics:
            self.statistics[key] = 0
