//! High-performance text processing utilities
//! 
//! This module provides fast text processing functions used by the
//! chunking engine, including parallel text splitting and keyword extraction.

use ahash::AHashSet;
use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;

/// A high-performance text chunk with metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TextChunk {
    pub text: String,
    pub start_idx: usize,
    pub end_idx: usize,
    pub chunk_type: String,
    pub word_count: usize,
}

/// High-performance text processor using Rayon for parallel processing
pub struct TextProcessor {
    max_chunk_size: usize,
    min_chunk_size: usize,
}

impl TextProcessor {
    pub fn new(max_chunk_size: usize, min_chunk_size: usize) -> Self {
        Self {
            max_chunk_size,
            min_chunk_size,
        }
    }

    /// Split text into chunks using parallel processing
    pub fn split_into_chunks(&self, text: &str) -> Vec<TextChunk> {
        // Split by paragraphs first (faster than regex)
        let paragraphs: Vec<&str> = text.split("\n\n").collect();
        
        // Process paragraphs in parallel
        paragraphs
            .par_iter()
            .flat_map(|para| self.split_paragraph(para))
            .collect()
    }

    /// Split a paragraph into smaller chunks if needed
    fn split_paragraph(&self, text: &str) -> Vec<TextChunk> {
        let text = text.trim();
        if text.is_empty() {
            return vec![];
        }

        let word_count = self.count_words(text);
        
        // If within limits, return as single chunk
        if word_count <= self.max_chunk_size / 5 {
            return vec![TextChunk {
                text: text.to_string(),
                start_idx: 0,
                end_idx: text.len(),
                chunk_type: "paragraph".to_string(),
                word_count,
            }];
        }

        // Split into smaller chunks
        let mut chunks = Vec::new();
        let words: Vec<&str> = text.split_whitespace().collect();
        let mut current_chunk = String::new();
        let mut current_words = 0;
        let mut start_idx = 0;

        for (i, word) in words.iter().enumerate() {
            if current_words > 0 && current_words * 5 >= self.max_chunk_size {
                // Start new chunk
                chunks.push(TextChunk {
                    text: current_chunk.trim().to_string(),
                    start_idx,
                    end_idx: start_idx + current_chunk.len(),
                    chunk_type: "paragraph".to_string(),
                    word_count: current_words,
                });
                start_idx += current_chunk.len();
                current_chunk = String::new();
                current_words = 0;
            }
            
            if !current_chunk.is_empty() {
                current_chunk.push(' ');
            }
            current_chunk.push_str(word);
            current_words += 1;
        }

        // Add remaining chunk
        if !current_chunk.is_empty() {
            chunks.push(TextChunk {
                text: current_chunk.trim().to_string(),
                start_idx,
                end_idx: start_idx + current_chunk.len(),
                chunk_type: "paragraph".to_string(),
                word_count: current_words,
            });
        }

        chunks
    }

    /// Count words efficiently
    #[inline]
    pub fn count_words(&self, text: &str) -> usize {
        text.split_whitespace().count()
    }

    /// Extract keywords using parallel processing
    pub fn extract_keywords(&self, texts: &[String], top_k: usize) -> Vec<(String, usize)> {
        // Count word frequencies in parallel
        let word_counts: AHashSet<String> = texts
            .par_iter()
            .flat_map(|text| {
                text.to_lowercase()
                    .split(|c: char| !c.is_alphanumeric())
                    .filter(|s| s.len() > 3)
                    .map(|s| s.to_string())
                    .collect::<Vec<_>>()
            })
            .fold(AHashSet::new, |mut acc, word| {
                *acc.entry(word).or_insert(0) += 1;
                acc
            })
            .reduce(AHashSet::new, |mut a, b| {
                for (word, count) in b {
                    *a.entry(word).or_insert(0) += count;
                }
                a
            });

        // Sort and return top k
        let mut words: Vec<(String, usize)> = word_counts.into_iter().collect();
        words.sort_by(|a, b| b.1.cmp(&a.1));
        words.truncate(top_k);
        words
    }

    /// Calculate text similarity using Jaccard index (fast)
    pub fn jaccard_similarity(&self, text1: &str, text2: &str) -> f64 {
        let set1: HashSet<&str> = text1.split_whitespace().collect();
        let set2: HashSet<&str> = text2.split_whitespace().collect();
        
        let intersection = set1.intersection(&set2).count();
        let union = set1.union(&set2).count();
        
        if union == 0 {
            return 0.0;
        }
        
        intersection as f64 / union as f64
    }
}

/// Fast bounding box operations
#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
pub struct BoundingBox {
    pub x0: f64,
    pub y0: f64,
    pub x1: f64,
    pub y1: f64,
}

impl BoundingBox {
    pub fn new(x0: f64, y0: f64, x1: f64, y1: f64) -> Self {
        Self { x0, y0, x1, y1 }
    }

    /// Calculate IOU (Intersection over Union) - highly optimized
    #[inline]
    pub fn iou(&self, other: &BoundingBox) -> f64 {
        // Calculate intersection
        let left = self.x0.max(other.x0);
        let top = self.y0.max(other.y0);
        let right = self.x1.min(other.x1);
        let bottom = self.y1.min(other.y1);

        if left >= right || top >= bottom {
            return 0.0;
        }

        let intersection = (right - left) * (bottom - top);
        let union = self.area() + other.area() - intersection;

        if union == 0.0 {
            return 0.0;
        }

        intersection / union
    }

    /// Area of the bounding box
    #[inline]
    pub fn area(&self) -> f64 {
        (self.x1 - self.x0) * (self.y1 - self.y0)
    }

    /// Check if boxes overlap
    #[inline]
    pub fn overlaps(&self, other: &BoundingBox) -> bool {
        self.x0 < other.x1 && other.x0 < self.x1 &&
        self.y0 < other.y1 && other.y0 < self.y1
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_text_processor() {
        let processor = TextProcessor::new(1000, 50);
        let text = "Hello world. This is a test. Another sentence here.";
        let chunks = processor.split_into_chunks(text);
        assert!(!chunks.is_empty());
    }

    #[test]
    fn test_bounding_box_iou() {
        let box1 = BoundingBox::new(0.0, 0.0, 10.0, 10.0);
        let box2 = BoundingBox::new(5.0, 5.0, 15.0, 15.0);
        
        let iou = box1.iou(&box2);
        assert!(iou > 0.0 && iou < 1.0);
    }
}
