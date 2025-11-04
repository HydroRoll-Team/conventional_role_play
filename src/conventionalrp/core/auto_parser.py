"""
自动分类解析器 (Auto Parser)

使用 HanLP 进行智能文本分析和分类
HanLP 提供了更准确的中文分词、词性标注、命名实体识别和依存句法分析
"""

from typing import List, Dict, Optional, Union, Set
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


try:
    import hanlp
    HANLP_AVAILABLE = True
except ImportError:
    HANLP_AVAILABLE = False
    logger.warning("HanLP not installed. Please install with: pip install hanlp")


class AutoParser:
    
    CONTENT_TYPES = [
        "dialogue",    # 对话
        "action",      # 动作
        "narration",   # 旁白
        "unknown",     # 未知
        "ooc",         # 场外讨论
    ]
    
    # HanLP 词性标注说明（CTB 标注集）
    # 名词: NN-普通名词 NR-人名 NS-地名 NT-机构名 NP-专有名词
    # 动词: VV-动词 VA-动作动词 VC-系动词 VE-有 
    # 形容词: JJ-形容词
    # 代词: PN-代词
    # 副词: AD-副词
    # 数量: CD-数词 OD-序数词 M-量词
    # 介词/连词: P-介词 CC-并列连词 CS-从属连词
    # 助词: DEC-的 DEG-的 DER-得 DEV-地 AS-了/着/过 SP-句末助词
    # 语气词: IJ-感叹词
    # 标点: PU-标点
    
    # 词性到内容类型的映射策略（基于 HanLP CTB 标注）
    POS_WEIGHTS = {
        # 动词相关 - 倾向于动作
        'VV': {'action': 0.8, 'narration': 0.2},      # 动词
        'VA': {'action': 0.85, 'narration': 0.15},    # 动作动词（更倾向于动作）
        'VC': {'dialogue': 0.5, 'narration': 0.5},    # 系动词（是/为等）
        'VE': {'narration': 0.6, 'dialogue': 0.4},    # 有
        
        # 名词相关 - 倾向于旁白
        'NN': {'narration': 0.7, 'dialogue': 0.3},    # 普通名词
        'NR': {'narration': 0.6, 'dialogue': 0.4},    # 人名（可能出现在对话中）
        'NS': {'narration': 0.8, 'dialogue': 0.2},    # 地名
        'NT': {'narration': 0.8, 'dialogue': 0.2},    # 机构名
        'NP': {'narration': 0.7, 'dialogue': 0.3},    # 专有名词
        
        # 代词 - 倾向于对话
        'PN': {'dialogue': 0.75, 'narration': 0.25},  # 代词（我/你/他等）
        
        # 形容词 - 倾向于旁白或对话
        'JJ': {'narration': 0.5, 'dialogue': 0.4, 'action': 0.1},
        
        # 副词 - 可以是任何类型
        'AD': {'dialogue': 0.4, 'narration': 0.4, 'action': 0.2},
        
        # 助词 - 倾向于对话
        'DEC': {'dialogue': 0.7, 'narration': 0.3},   # 的（结构助词）
        'DEG': {'dialogue': 0.7, 'narration': 0.3},   # 的（关联助词）
        'DER': {'dialogue': 0.6, 'action': 0.4},      # 得（动补）
        'DEV': {'action': 0.7, 'narration': 0.3},     # 地（状中）
        'AS': {'dialogue': 0.6, 'narration': 0.4},    # 了/着/过
        'SP': {'dialogue': 0.85, 'narration': 0.15},  # 句末助词（吗/呢/吧等）
        
        # 感叹词 - 强烈倾向于对话
        'IJ': {'dialogue': 0.9, 'action': 0.1},       # 感叹词（啊/哦/唉等）
        
        # 数量词 - 倾向于旁白
        'CD': {'narration': 0.8, 'dialogue': 0.2},    # 数词
        'OD': {'narration': 0.8, 'dialogue': 0.2},    # 序数词
        'M': {'narration': 0.7, 'dialogue': 0.3},     # 量词
        
        # 介词/连词 - 中性
        'P': {'narration': 0.5, 'dialogue': 0.5},     # 介词
        'CC': {'narration': 0.5, 'dialogue': 0.5},    # 并列连词
        'CS': {'narration': 0.6, 'dialogue': 0.4},    # 从属连词
    }
    
    def __init__(self, model: str = 'SMALL', tasks: Optional[List[str]] = None, 
                 use_gpu: bool = False, devices: Optional[List[int]] = None):
        """
        初始化自动解析器
        
        Args:
            model: HanLP 模型规模
                - 'SMALL': 小型模型（快速，适合日常使用）
                - 'LARGE': 大型模型（更准确，需要更多资源）
                - 'MULTI_TASK': 多任务模型
                - 或自定义模型路径
            tasks: 要加载的任务列表，如 ['tok', 'pos', 'ner', 'dep']
                - tok: 分词
                - pos: 词性标注
                - ner: 命名实体识别
                - dep: 依存句法分析
                - None: 使用默认任务（分词+词性标注）
            use_gpu: 是否使用 GPU 加速
            devices: GPU 设备 ID 列表
        """
        if not HANLP_AVAILABLE:
            raise ImportError(
                "HanLP is not installed. Please install with:\n"
                "pip install hanlp\n"
                "Note: First installation may take a few minutes to download models."
            )
        
        logger.info(f"Initializing HanLP AutoParser with model={model}, tasks={tasks}")
        
        # 初始化 HanLP 流水线
        try:
            # 根据任务需求选择合适的预训练模型
            if tasks is None:
                # 默认使用分词和词性标注
                tasks = ['tok/fine', 'pos/ctb']
            
            # 加载 HanLP 多任务模型
            if model == 'SMALL':
                # 使用小型预训练模型
                self.hanlp = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_SMALL_ZH)
            elif model == 'LARGE':
                # 使用大型预训练模型
                self.hanlp = hanlp.load(hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)
            elif model == 'MULTI_TASK':
                # 使用完整多任务模型
                self.hanlp = hanlp.load(hanlp.pretrained.mtl.UD_ONTONOTES_TOK_POS_LEM_FEA_NER_SRL_DEP_SDP_CON_XLMR_BASE)
            else:
                # 使用自定义模型路径或名称
                self.hanlp = hanlp.load(model)
            
            # 配置设备
            if use_gpu and devices:
                self.hanlp.to(f'cuda:{devices[0]}')
            elif use_gpu:
                self.hanlp.to('cuda')
            
            logger.info("HanLP model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load HanLP model: {e}")
            # 降级到基础分词模型
            logger.warning("Falling back to basic tokenizer")
            self.hanlp = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
        
        # 可选的自定义关键词列表
        self.custom_action_words: Set[str] = set()
        self.custom_dialogue_words: Set[str] = set()
        self.custom_narration_words: Set[str] = set()
        self.custom_ooc_words: Set[str] = set()
        
        # 动作动词关键词库（用于增强识别）
        self.action_verbs = {
            '走', '跑', '看', '听', '摸', '拿', '放', '打开', '关闭',
            '推', '拉', '举', '扔', '跳', '爬', '坐', '站', '躺',
            '进入', '离开', '接近', '远离', '转身', '回头', '低头', '抬头',
            '微笑', '大笑', '哭', '喊', '叫', '念', '读',
            '投掷', '检定', '攻击', '防御', '躲避', '施法', '释放',
            '握', '抓', '松开', '敲', '踢', '打', '砍', '刺',
        }
        
        # 对话标志词
        self.dialogue_markers = {
            '说', '讲', '道', '问', '答', '回答', '询问', '告诉',
            '我', '你', '他', '她', '我们', '你们', '他们',
            '吗', '呢', '吧', '啊', '哦', '嗯', '唉', '哎',
        }
        
        # 统计信息
        self.statistics = {
            "total_lines": 0,
            "parsed_lines": 0,
            "error_lines": 0,
        }
        
        # 初始化每种类型的计数
        for content_type in self.CONTENT_TYPES:
            self.statistics[f"{content_type}_count"] = 0
        
        logger.info(f"AutoParser initialized successfully")
    
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
                "pos_tags": ["PN", "VV", "PN"],
                "confidence": 0.85,
                "entities": [...],  # 命名实体
                "dependencies": [...],  # 依存关系（如果可用）
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
            "entities": [],
            "dependencies": [],
            "confidence": 0.0,
            "analysis": {}
        }
        
        # 空行处理
        if not line or not line.strip():
            result["content_type"] = "unknown"
            return result
        
        text = line.strip()
        result["content"] = text
        
        # 使用 HanLP 进行词法分析
        try:
            # HanLP 返回字典，包含多个任务的结果
            hanlp_result = self.hanlp(text)
            
            # 提取分词结果
            if 'tok/fine' in hanlp_result or 'tok' in hanlp_result:
                words = hanlp_result.get('tok/fine') or hanlp_result.get('tok', [])
            else:
                # 如果没有分词结果，尝试使用第一个可用的分词任务
                words = []
                for key in hanlp_result.keys():
                    if 'tok' in key.lower():
                        words = hanlp_result[key]
                        break
            
            # 提取词性标注结果
            if 'pos/ctb' in hanlp_result or 'pos' in hanlp_result:
                pos_tags = hanlp_result.get('pos/ctb') or hanlp_result.get('pos', [])
            else:
                # 如果没有词性结果，尝试使用第一个可用的词性任务
                pos_tags = []
                for key in hanlp_result.keys():
                    if 'pos' in key.lower():
                        pos_tags = hanlp_result[key]
                        break
            
            # 提取命名实体识别结果（如果可用）
            if 'ner' in hanlp_result or 'ner/ontonotes' in hanlp_result:
                entities = hanlp_result.get('ner/ontonotes') or hanlp_result.get('ner', [])
                result["entities"] = entities
            
            # 提取依存句法分析结果（如果可用）
            if 'dep' in hanlp_result:
                result["dependencies"] = hanlp_result.get('dep', [])
            
            result["words"] = words
            result["pos_tags"] = pos_tags
            
            # 基于词法分析结果分类
            content_type, confidence, analysis = self._classify_by_hanlp(
                words, pos_tags, result.get("entities", []), text
            )
            
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
    
    def _classify_by_hanlp(self, words: List[str], pos_tags: List[str], 
                          entities: List, text: str) -> tuple:
        """
        基于 HanLP 词法分析结果进行分类
        
        Args:
            words: 分词结果
            pos_tags: 词性标注结果
            entities: 命名实体识别结果
            text: 原始文本
        
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
            "custom_matches": [],
            "key_features": [],
            "entity_count": len(entities) if entities else 0,
        }
        
        # 统计词性分布
        for pos in pos_tags:
            if pos != 'PU':  # 忽略标点
                analysis["pos_distribution"][pos] = analysis["pos_distribution"].get(pos, 0) + 1
        
        # 基于词性加权计算类型分数
        for i, (word, pos) in enumerate(zip(words, pos_tags)):
            # 跳过标点
            if pos == 'PU':
                continue
            
            # 检查自定义关键词（优先级最高，权重 2.0）
            if word in self.custom_action_words:
                type_scores['action'] += 2.0
                analysis["custom_matches"].append({"word": word, "type": "action", "weight": 2.0})
            elif word in self.custom_dialogue_words:
                type_scores['dialogue'] += 2.0
                analysis["custom_matches"].append({"word": word, "type": "dialogue", "weight": 2.0})
            elif word in self.custom_narration_words:
                type_scores['narration'] += 2.0
                analysis["custom_matches"].append({"word": word, "type": "narration", "weight": 2.0})
            elif word in self.custom_ooc_words:
                type_scores['ooc'] += 2.0
                analysis["custom_matches"].append({"word": word, "type": "ooc", "weight": 2.0})
            
            # 检查内置关键词库（权重 1.5）
            if word in self.action_verbs:
                type_scores['action'] += 1.5
                analysis["key_features"].append({"word": word, "type": "action_verb"})
            elif word in self.dialogue_markers:
                type_scores['dialogue'] += 1.5
                analysis["key_features"].append({"word": word, "type": "dialogue_marker"})
            
            # 应用词性权重
            if pos in self.POS_WEIGHTS:
                weights = self.POS_WEIGHTS[pos]
                for content_type, weight in weights.items():
                    type_scores[content_type] += weight
            else:
                # 未知词性，根据前缀做简单判断
                if pos.startswith('V'):  # 动词类
                    type_scores['action'] += 0.5
                elif pos.startswith('N'):  # 名词类
                    type_scores['narration'] += 0.5
        
        # 句末助词检测（强对话信号）
        if pos_tags and pos_tags[-1] == 'SP':
            type_scores['dialogue'] += 1.0
            analysis["key_features"].append({"feature": "sentence_particle", "position": "end"})
        
        # 感叹词检测（强对话信号）
        if 'IJ' in pos_tags:
            type_scores['dialogue'] += 1.2
            analysis["key_features"].append({"feature": "interjection"})
        
        # 人称代词检测（对话信号）
        pronoun_count = sum(1 for pos in pos_tags if pos == 'PN')
        if pronoun_count >= 2:
            type_scores['dialogue'] += 0.8
            analysis["key_features"].append({"feature": "multiple_pronouns", "count": pronoun_count})
        
        # 命名实体检测（旁白信号）
        if entities and len(entities) > 0:
            type_scores['narration'] += 0.5 * len(entities)
            analysis["key_features"].append({"feature": "named_entities", "count": len(entities)})
        
        # 动词占比检测（动作信号）
        verb_count = sum(1 for pos in pos_tags if pos.startswith('V'))
        if len(pos_tags) > 0:
            verb_ratio = verb_count / len(pos_tags)
            if verb_ratio > 0.3:
                type_scores['action'] += verb_ratio
                analysis["key_features"].append({"feature": "high_verb_ratio", "ratio": verb_ratio})
        
        # 文本长度特征
        if len(text) < 10:
            # 短文本更可能是对话或动作
            type_scores['dialogue'] += 0.3
            type_scores['action'] += 0.2
        elif len(text) > 50:
            # 长文本更可能是旁白
            type_scores['narration'] += 0.3
        
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
    
    def parse_log_file(self, file_path: Union[str, Path], batch_size: int = 32) -> List[Dict]:
        """
        批处理方法：按行解析日志文件
        
        Args:
            file_path: 日志文件路径
            batch_size: 批处理大小，HanLP 支持批量处理以提高效率
        
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
            
            # 过滤空行并保留行号
            non_empty_lines = [(i+1, line.strip()) for i, line in enumerate(lines) if line.strip()]
            
            # 批量处理以提高效率
            for i in range(0, len(non_empty_lines), batch_size):
                batch = non_empty_lines[i:i+batch_size]
                
                try:
                    # 提取文本
                    texts = [text for _, text in batch]
                    
                    # HanLP 批量处理
                    hanlp_results = self.hanlp(texts)
                    
                    # 处理每个结果
                    for j, (line_num, text) in enumerate(batch):
                        try:
                            # 提取当前文本的分析结果
                            result = self._process_hanlp_batch_result(
                                text, hanlp_results, j, line_num
                            )
                            results.append(result)
                            
                            # 更新统计
                            self.statistics["parsed_lines"] += 1
                            self.statistics[f"{result['content_type']}_count"] += 1
                            
                        except Exception as e:
                            logger.error(f"Error processing line {line_num}: {e}")
                            self.statistics["error_lines"] += 1
                            results.append({
                                "line_number": line_num,
                                "raw_text": text,
                                "content": text,
                                "content_type": "unknown",
                                "words": [],
                                "pos_tags": [],
                                "entities": [],
                                "confidence": 0.0,
                                "analysis": {"error": str(e)}
                            })
                
                except Exception as e:
                    logger.error(f"Error in batch processing: {e}")
                    # 回退到逐行处理
                    for line_num, text in batch:
                        try:
                            result = self.parse_line(text, line_number=line_num)
                            results.append(result)
                        except Exception as e2:
                            logger.error(f"Error parsing line {line_num}: {e2}")
                            self.statistics["error_lines"] += 1
        
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
        
        logger.info(f"Successfully parsed {len(results)} lines from {file_path}")
        return results
    
    def _process_hanlp_batch_result(self, text: str, hanlp_results: Dict, 
                                    index: int, line_num: int) -> Dict:
        """
        处理 HanLP 批量分析的单个结果
        
        Args:
            text: 原始文本
            hanlp_results: HanLP 批量处理返回的结果字典
            index: 当前文本在批次中的索引
            line_num: 行号
        
        Returns:
            解析结果字典
        """
        self.statistics["total_lines"] += 1
        
        result = {
            "line_number": line_num,
            "raw_text": text,
            "content": text,
            "content_type": "unknown",
            "words": [],
            "pos_tags": [],
            "entities": [],
            "dependencies": [],
            "confidence": 0.0,
            "analysis": {}
        }
        
        try:
            # 提取分词结果
            if 'tok/fine' in hanlp_results:
                words = hanlp_results['tok/fine'][index]
            elif 'tok' in hanlp_results:
                words = hanlp_results['tok'][index]
            else:
                words = []
            
            # 提取词性标注结果
            if 'pos/ctb' in hanlp_results:
                pos_tags = hanlp_results['pos/ctb'][index]
            elif 'pos' in hanlp_results:
                pos_tags = hanlp_results['pos'][index]
            else:
                pos_tags = []
            
            # 提取命名实体
            entities = []
            if 'ner/ontonotes' in hanlp_results:
                entities = hanlp_results['ner/ontonotes'][index]
            elif 'ner' in hanlp_results:
                entities = hanlp_results['ner'][index]
            
            # 提取依存句法
            if 'dep' in hanlp_results:
                result["dependencies"] = hanlp_results['dep'][index]
            
            result["words"] = words
            result["pos_tags"] = pos_tags
            result["entities"] = entities
            
            # 分类
            content_type, confidence, analysis = self._classify_by_hanlp(
                words, pos_tags, entities, text
            )
            
            result["content_type"] = content_type
            result["confidence"] = confidence
            result["analysis"] = analysis
            
        except Exception as e:
            logger.error(f"Error processing result for line {line_num}: {e}")
            result["analysis"]["error"] = str(e)
        
        return result
    
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
    
    def extract_entities(self, parsed_data: List[Dict]) -> Dict[str, List]:
        """
        提取所有命名实体
        
        Args:
            parsed_data: 解析结果列表
        
        Returns:
            按实体类型分组的实体列表
        """
        entities_by_type = {}
        
        for item in parsed_data:
            entities = item.get("entities", [])
            if entities:
                for entity in entities:
                    if isinstance(entity, tuple) and len(entity) >= 2:
                        entity_text, entity_type = entity[0], entity[1]
                        if entity_type not in entities_by_type:
                            entities_by_type[entity_type] = []
                        entities_by_type[entity_type].append({
                            "text": entity_text,
                            "line_number": item.get("line_number"),
                            "context": item.get("content")
                        })
        
        return entities_by_type
    
    def get_word_frequency(self, parsed_data: List[Dict], 
                          min_length: int = 2,
                          exclude_pos: Optional[List[str]] = None) -> Dict[str, int]:
        """
        统计词频
        
        Args:
            parsed_data: 解析结果列表
            min_length: 最小词长度
            exclude_pos: 要排除的词性列表（如 ['PU'] 排除标点）
        
        Returns:
            词频字典
        """
        if exclude_pos is None:
            exclude_pos = ['PU']  # 默认排除标点
        
        word_freq = {}
        
        for item in parsed_data:
            words = item.get("words", [])
            pos_tags = item.get("pos_tags", [])
            
            for word, pos in zip(words, pos_tags):
                if len(word) >= min_length and pos not in exclude_pos:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # 按频率排序
        return dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True))
    
    def analyze_dialogue_patterns(self, parsed_data: List[Dict]) -> Dict:
        """
        分析对话模式
        
        Args:
            parsed_data: 解析结果列表
        
        Returns:
            对话分析统计
        """
        dialogue_items = self.filter_by_type(parsed_data, "dialogue")
        
        analysis = {
            "total_dialogues": len(dialogue_items),
            "avg_length": 0.0,
            "common_patterns": {},
            "pronoun_usage": {},
            "sentence_particles": {},
        }
        
        if not dialogue_items:
            return analysis
        
        total_length = 0
        
        for item in dialogue_items:
            words = item.get("words", [])
            pos_tags = item.get("pos_tags", [])
            
            total_length += len(item.get("content", ""))
            
            # 统计代词使用
            for word, pos in zip(words, pos_tags):
                if pos == 'PN':
                    analysis["pronoun_usage"][word] = analysis["pronoun_usage"].get(word, 0) + 1
                elif pos == 'SP':
                    analysis["sentence_particles"][word] = analysis["sentence_particles"].get(word, 0) + 1
        
        analysis["avg_length"] = total_length / len(dialogue_items)
        
        return analysis
    
    def export_to_json(self, parsed_data: List[Dict], 
                      output_path: Union[str, Path]) -> None:
        """
        导出解析结果为 JSON 文件
        
        Args:
            parsed_data: 解析结果列表
            output_path: 输出文件路径
        """
        import json
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(parsed_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Exported {len(parsed_data)} items to {output_path}")
    
    def get_summary(self, parsed_data: List[Dict]) -> Dict:
        """
        获取解析结果摘要
        
        Args:
            parsed_data: 解析结果列表
        
        Returns:
            摘要统计信息
        """
        type_counts = {content_type: 0 for content_type in self.CONTENT_TYPES}
        confidence_sum = {content_type: 0.0 for content_type in self.CONTENT_TYPES}
        
        total_words = 0
        total_entities = 0
        
        for item in parsed_data:
            content_type = item.get("content_type", "unknown")
            confidence = item.get("confidence", 0.0)
            
            type_counts[content_type] += 1
            confidence_sum[content_type] += confidence
            
            total_words += len(item.get("words", []))
            total_entities += len(item.get("entities", []))
        
        # 计算平均置信度
        avg_confidence = {}
        for content_type in self.CONTENT_TYPES:
            if type_counts[content_type] > 0:
                avg_confidence[content_type] = confidence_sum[content_type] / type_counts[content_type]
            else:
                avg_confidence[content_type] = 0.0
        
        return {
            "total_items": len(parsed_data),
            "type_distribution": type_counts,
            "avg_confidence": avg_confidence,
            "total_words": total_words,
            "total_entities": total_entities,
            "avg_words_per_item": total_words / len(parsed_data) if parsed_data else 0.0,
        }
