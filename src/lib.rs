use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use regex::Regex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub enum TokenType {
    Metadata,
    DiceRoll,
    Dialogue,
    Action,
    Ooc,
    System,
    Text,
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[pyclass]
pub struct Token {
    #[pyo3(get, set)]
    pub token_type: String,
    #[pyo3(get, set)]
    pub content: String,
    #[pyo3(get, set)]
    pub metadata: HashMap<String, String>,
}

#[pymethods]
impl Token {
    #[new]
    fn new(token_type: String, content: String) -> Self {
        Token {
            token_type,
            content,
            metadata: HashMap::new(),
        }
    }

    fn add_metadata(&mut self, key: String, value: String) {
        self.metadata.insert(key, value);
    }

    fn get_metadata(&self, key: &str) -> Option<String> {
        self.metadata.get(key).cloned()
    }
    fn to_dict(&self, py: Python) -> PyResult<Py<PyAny>> {
        let dict = PyDict::new(py);
        dict.set_item("type", &self.token_type)?;
        dict.set_item("content", &self.content)?;
        
        let metadata_dict = PyDict::new(py);
        for (k, v) in &self.metadata {
            metadata_dict.set_item(k, v)?;
        }
        dict.set_item("metadata", metadata_dict)?;
        
        Ok(dict.into())
    }

    fn __repr__(&self) -> String {
        format!("Token(type={}, content={})", self.token_type, self.content)
    }
}

#[pyclass]
pub struct RegexRule {
    pattern: Regex,
    #[pyo3(get, set)]
    pub rule_type: String,
    #[pyo3(get, set)]
    pub priority: i32,
}

#[pymethods]
impl RegexRule {
    #[new]
    fn new(pattern: String, rule_type: String, priority: i32) -> PyResult<Self> {
        let regex = Regex::new(&pattern)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid regex pattern: {}", e)
            ))?;
        
        Ok(RegexRule {
            pattern: regex,
            rule_type,
            priority,
        })
    }

    fn matches(&self, text: &str) -> bool {
        self.pattern.is_match(text)
    }


    fn extract(&self, text: &str) -> Option<Vec<String>> {
        self.pattern.captures(text).map(|caps| {
            caps.iter()
                .skip(1) // 跳过完整匹配
                .filter_map(|m| m.map(|m| m.as_str().to_string()))
                .collect()
        })
    }

    fn find_all(&self, text: &str, py: Python) -> PyResult<Py<PyAny>> {
        let matches: Vec<(usize, usize, String)> = self.pattern
            .find_iter(text)
            .map(|m| (m.start(), m.end(), m.as_str().to_string()))
            .collect();
        
        let list = PyList::empty(py);
        for (start, end, matched) in matches {
            let dict = PyDict::new(py);
            dict.set_item("start", start)?;
            dict.set_item("end", end)?;
            dict.set_item("text", matched)?;
            list.append(dict)?;
        }
        
        Ok(list.into())
    }
}

#[pyclass]
pub struct TextParser {
    rules: Vec<(Regex, String, i32)>, // (pattern, type, priority)
}

#[pymethods]
impl TextParser {
    #[new]
    fn new() -> Self {
        TextParser { rules: Vec::new() }
    }

    fn add_rule(&mut self, pattern: String, rule_type: String, priority: i32) -> PyResult<()> {
        let regex = Regex::new(&pattern)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid regex: {}", e)
            ))?;
        
        self.rules.push((regex, rule_type, priority));
        self.rules.sort_by(|a, b| b.2.cmp(&a.2));
        
        Ok(())
    }

    fn parse_line(&self, text: &str) -> Vec<(String, String, usize, usize)> {
        let mut results = Vec::new();
        let mut processed_ranges: Vec<(usize, usize)> = Vec::new();
        for (pattern, rule_type, _priority) in &self.rules {
            for mat in pattern.find_iter(text) {
                let start = mat.start();
                let end = mat.end();

                let overlaps = processed_ranges.iter().any(|(s, e)| {
                    (start >= *s && start < *e) || (end > *s && end <= *e) || (start <= *s && end >= *e)
                });

                if !overlaps {
                    results.push((
                        rule_type.clone(),
                        mat.as_str().to_string(),
                        start,
                        end,
                    ));
                    processed_ranges.push((start, end));
                }
            }
        }

        results.sort_by_key(|r| r.2);
        results
    }
    fn parse_lines(&self, lines: Vec<String>, py: Python) -> PyResult<Py<PyAny>> {
        let list = PyList::empty(py);
        
        for line in lines {
            let parsed = self.parse_line(&line);
            let line_result = PyList::empty(py);
            
            for (rule_type, content, start, end) in parsed {
                let dict = PyDict::new(py);
                dict.set_item("type", rule_type)?;
                dict.set_item("content", content)?;
                dict.set_item("start", start)?;
                dict.set_item("end", end)?;
                line_result.append(dict)?;
            }
            
            list.append(line_result)?;
        }
        
        Ok(list.into())
    }

    fn clear_rules(&mut self) {
        self.rules.clear();
    }

    fn rule_count(&self) -> usize {
        self.rules.len()
    }
}

#[pyclass]
pub struct FastMatcher {
    patterns: Vec<String>,
}

#[pymethods]
impl FastMatcher {
    #[new]
    fn new(patterns: Vec<String>) -> Self {
        FastMatcher { patterns }
    }


    fn contains_any(&self, text: &str) -> bool {
        self.patterns.iter().any(|p| text.contains(p))
    }


    fn find_matches(&self, text: &str) -> Vec<String> {
        self.patterns
            .iter()
            .filter(|p| text.contains(*p))
            .cloned()
            .collect()
    }

    fn count_matches(&self, text: &str, py: Python) -> PyResult<Py<PyAny>> {
        let dict = PyDict::new(py);
        for pattern in &self.patterns {
            let count = text.matches(pattern.as_str()).count();
            dict.set_item(pattern, count)?;
        }
        Ok(dict.into())
    }
}

#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // 添加类
    m.add_class::<Token>()?;
    m.add_class::<RegexRule>()?;
    m.add_class::<TextParser>()?;
    m.add_class::<FastMatcher>()?;
    
    Ok(())
}