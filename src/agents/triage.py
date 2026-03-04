"""
Triage Agent for Document Intelligence Refinery.

The Triage Agent analyzes documents to determine their characteristics
for optimal extraction strategy routing.
"""

import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pdfplumber

from src.models.document_profile import (
    DocumentProfile,
    DomainHint,
    ExtractionCostHint,
    LayoutComplexity,
    OriginType,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PageAnalysis:
    """Analysis results for a single page."""
    page_number: int
    char_count: int
    char_density: float
    image_ratio: float
    bbox_area: float
    text_blocks: List[Dict] = field(default_factory=list)
    images: List[Dict] = field(default_factory=list)
    tables: int = 0
    has_embedded_fonts: bool = True


@dataclass
class TriageResult:
    """Result of triage analysis."""
    profile: DocumentProfile
    page_analyses: List[PageAnalysis]
    audit_log: List[Dict]


class DomainClassifier:
    """
    Keyword-based domain classifier.
    
    This is a simple rule-based classifier that can be extended
    with VLM-based classification in the future.
    """
    
    # Domain keyword patterns
    DOMAIN_KEYWORDS = {
        DomainHint.FINANCIAL: [
            r'\brevenue\b', r'\bbalance sheet\b', r'\bincome\b', r'\bfiscal\b',
            r'\bprofit\b', r'\bloss\b', r'\bassets\b', r'\bliabilities\b',
            r'\bequity\b', r'\bcash flow\b', r'\beps\b', r'\bebitda\b',
            r'\bquarterly\b', r'\bannual\b', r'\bfinancial\b', r'\bcapital\b',
        ],
        DomainHint.LEGAL: [
            r'\bplaintiff\b', r'\bdefendant\b', r'\bcourt\b', r'\bwhereas\b',
            r'\bhereby\b', r'\bcontract\b', r'\bagreement\b', r'\bclause\b',
            r'\bliability\b', r'\bindemnity\b', r'\bwarranty\b', r'\bremedy\b',
            r'\bjurisdiction\b', r'\barbitration\b', r'\blegal\b', r'\bstatute\b',
        ],
        DomainHint.TECHNICAL: [
            r'\balgorithm\b', r'\bspecification\b', r'\bsystem\b', r'\barchitecture\b',
            r'\bprotocol\b', r'\binterface\b', r'\bimplementation\b', r'\bapi\b',
            r'\bdatabase\b', r'\bsoftware\b', r'\bhardware\b', r'\bnetwork\b',
            r'\bconfiguration\b', r'\bdeployment\b', r'\btechnical\b', r'\benhancement\b',
        ],
        DomainHint.MEDICAL: [
            r'\bpatient\b', r'\bdiagnosis\b', r'\btreatment\b', r'\bsymptom\b',
            r'\btherapy\b', r'\bmedication\b', r'\bclinical\b', r'\bhealth\b',
            r'\bphysician\b', r'\bhospital\b', r'\bmedical\b', r'\b disease\b',
            r'\bcondition\b', r'\bprocedure\b', r'\bexamination\b', r'\bprescription\b',
        ],
    }
    
    def __init__(self):
        """Initialize the domain classifier with compiled regex patterns."""
        self._compiled_patterns: Dict[DomainHint, List[re.Pattern]] = {}
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            self._compiled_patterns[domain] = [
                re.compile(kw, re.IGNORECASE) for kw in keywords
            ]
    
    def classify(self, text: str) -> Tuple[DomainHint, float]:
        """
        Classify the domain of the given text.
        
        Returns:
            Tuple of (domain_hint, confidence_score)
        """
        if not text or len(text.strip()) < 50:
            return DomainHint.GENERAL, 0.0
        
        text_lower = text.lower()
        scores: Dict[DomainHint, int] = {d: 0 for d in DomainHint}
        
        for domain, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(text_lower)
                scores[domain] += len(matches)
        
        # Find the domain with the highest score
        max_score = max(scores.values())
        
        if max_score == 0:
            return DomainHint.GENERAL, 0.5
        
        # Calculate confidence based on score difference
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        top_domain = sorted_scores[0][0]
        second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0
        
        # Confidence calculation: higher when second place is far behind
        confidence = min(0.95, 0.5 + (max_score - second_score) * 0.05)
        
        return top_domain, confidence


class TriageAgent:
    """
    Triage Agent analyzes documents to determine their characteristics
    for routing decisions in the extraction pipeline.
    
    It performs the following classifications:
    - origin_type: How the document content was created
    - layout_complexity: Structural complexity of the document
    - domain_hint: Subject matter domain
    - extraction_cost_hint: Recommended extraction strategy
    """
    
    # Thresholds for classification (from DOMAIN_NOTES.md)
    CHAR_DENSITY_THRESHOLD = 0.001  # chars / page area
    CHAR_COUNT_MIN = 100  # minimum chars per page
    IMAGE_RATIO_THRESHOLD = 0.50  # >50% image suggests scanned
    
    def __init__(self, profiles_dir: str = ".refinery/profiles"):
        """
        Initialize the Triage Agent.
        
        Args:
            profiles_dir: Directory to save DocumentProfile outputs
        """
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self.domain_classifier = DomainClassifier()
    
    def analyze(self, file_path: str) -> TriageResult:
        """
        Analyze a document and return its profile.
        
        Args:
            file_path: Path to the document to analyze
            
        Returns:
            TriageResult containing the profile and analysis details
        """
        doc_id = self._generate_doc_id(file_path)
        logger.info(f"Analyzing document: {file_path} (doc_id: {doc_id})")
        
        audit_log = []
        
        # Analyze all pages
        page_analyses = self._analyze_pages(file_path)
        
        if not page_analyses:
            raise ValueError(f"No pages found in document: {file_path}")
        
        # Aggregate page-level metrics
        page_count = len(page_analyses)
        avg_char_density = sum(p.char_density for p in page_analyses) / page_count
        avg_image_ratio = sum(p.image_ratio for p in page_analyses) / page_count
        total_images = sum(len(p.images) for p in page_analyses)
        total_tables = sum(p.tables for p in page_analyses)
        
        audit_log.append({
            "step": "page_analysis",
            "page_count": page_count,
            "avg_char_density": avg_char_density,
            "avg_image_ratio": avg_image_ratio,
            "total_images": total_images,
            "total_tables": total_tables,
        })
        
        # Classify origin_type
        origin_type = self._classify_origin_type(page_analyses)
        audit_log.append({"step": "origin_type_classification", "result": origin_type})
        
        # Classify layout_complexity
        layout_complexity = self._classify_layout_complexity(page_analyses)
        audit_log.append({"step": "layout_classification", "result": layout_complexity})
        
        # Extract text for domain classification
        full_text = " ".join(
            p.text_blocks[0].get("text", "") 
            for p in page_analyses 
            if p.text_blocks
        )
        
        # Classify domain_hint
        domain_hint, domain_confidence = self.domain_classifier.classify(full_text)
        audit_log.append({
            "step": "domain_classification",
            "result": domain_hint,
            "confidence": domain_confidence
        })
        
        # Determine extraction_cost_hint
        extraction_cost_hint = self._determine_extraction_cost(
            origin_type, layout_complexity
        )
        audit_log.append({
            "step": "extraction_cost_determination",
            "result": extraction_cost_hint
        })
        
        # Estimate scanned vs native pages
        estimated_pages_scanned, estimated_pages_native = self._estimate_page_types(
            page_analyses
        )
        
        # Calculate overall confidence score
        confidence_score = self._calculate_confidence(
            avg_char_density, avg_image_ratio, domain_confidence
        )
        
        # Create the profile
        profile = DocumentProfile(
            doc_id=doc_id,
            file_path=file_path,
            origin_type=origin_type,
            layout_complexity=layout_complexity,
            domain_hint=domain_hint,
            extraction_cost_hint=extraction_cost_hint,
            page_count=page_count,
            estimated_pages_scanned=estimated_pages_scanned,
            estimated_pages_native=estimated_pages_native,
            char_density_avg=avg_char_density,
            image_ratio_avg=avg_image_ratio,
            confidence_score=confidence_score,
            has_tables=total_tables > 0,
            has_figures=total_images > 0,
        )
        
        # Save the profile
        self._save_profile(profile)
        
        logger.info(f"Triage complete: {origin_type.value}, {layout_complexity.value}, {domain_hint.value}")
        
        return TriageResult(
            profile=profile,
            page_analyses=page_analyses,
            audit_log=audit_log,
        )
    
    def _generate_doc_id(self, file_path: str) -> str:
        """Generate a unique document ID based on file path."""
        path_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        filename = Path(file_path).stem
        return f"doc_{filename}_{path_hash}"
    
    def _analyze_pages(self, file_path: str) -> List[PageAnalysis]:
        """Analyze all pages of the document."""
        analyses = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                analysis = self._analyze_page(page, page_num)
                analyses.append(analysis)
        
        return analyses
    
    def _analyze_page(self, page, page_num: int) -> PageAnalysis:
        """Analyze a single page."""
        # Get page dimensions
        width = page.width or 612  # default letter width in points
        height = page.height or 792  # default letter height in points
        bbox_area = width * height
        
        # Extract text
        text = page.extract_text() or ""
        char_count = len(text)
        char_density = char_count / bbox_area if bbox_area > 0 else 0
        
        # Extract text blocks with positions
        text_blocks = []
        words = page.extract_words() or []
        
        # Group words into blocks based on vertical position
        block_map: Dict[int, List[Dict]] = {}
        for word in words:
            top = int(word.get("top", 0))
            block_map.setdefault(top, []).append(word)
        
        for top, block_words in block_map.items():
            block_text = " ".join(w.get("text", "") for w in block_words)
            x0 = min(w.get("x0", 0) for w in block_words)
            x1 = max(w.get("x1", 0) for w in block_words)
            y0 = min(w.get("top", 0) for w in block_words)
            y1 = max(w.get("bottom", 0) for w in block_words)
            
            text_blocks.append({
                "text": block_text,
                "bbox": [x0, y0, x1, y1],
                "char_count": len(block_text),
            })
        
        # Extract images
        images = []
        page_images = page.images or []
        for img in page_images:
            img_bbox = img.get("bbox", [])
            if img_bbox:
                img_area = (img_bbox[2] - img_bbox[0]) * (img_bbox[3] - img_bbox[1])
                images.append({
                    "bbox": img_bbox,
                    "area": img_area,
                })
        
        # Calculate image ratio
        total_image_area = sum(img["area"] for img in images)
        image_ratio = total_image_area / bbox_area if bbox_area > 0 else 0
        
        # Detect tables
        tables = page.extract_tables() or []
        
        # Check for embedded fonts (simplified check)
        has_embedded_fonts = len(page.objects.get("fonts", [])) > 0
        
        return PageAnalysis(
            page_number=page_num,
            char_count=char_count,
            char_density=char_density,
            image_ratio=image_ratio,
            bbox_area=bbox_area,
            text_blocks=text_blocks,
            images=images,
            tables=len(tables),
            has_embedded_fonts=has_embedded_fonts,
        )
    
    def _classify_origin_type(self, analyses: List[PageAnalysis]) -> OriginType:
        """
        Classify the document origin type.
        
        - native_digital: High char density + embedded fonts
        - scanned_image: Low char density + high image ratio
        - mixed: Both characteristics present
        """
        native_indicators = 0
        scanned_indicators = 0
        
        for page in analyses:
            # Native digital indicators
            if page.char_density >= self.CHAR_DENSITY_THRESHOLD:
                native_indicators += 1
            if page.has_embedded_fonts:
                native_indicators += 0.5
            
            # Scanned image indicators
            if page.char_density < self.CHAR_DENSITY_THRESHOLD:
                scanned_indicators += 1
            if page.image_ratio > self.IMAGE_RATIO_THRESHOLD:
                scanned_indicators += 2
            if page.char_count < self.CHAR_COUNT_MIN:
                scanned_indicators += 1
        
        total_pages = len(analyses)
        
        # Determine origin type based on indicators
        if scanned_indicators > total_pages * 0.7:
            return OriginType.SCANNED_IMAGE
        elif native_indicators > total_pages * 0.7:
            return OriginType.NATIVE_DIGITAL
        elif native_indicators > 0 and scanned_indicators > 0:
            return OriginType.MIXED
        else:
            # Default to native digital if uncertain
            return OriginType.NATIVE_DIGITAL
    
    def _classify_layout_complexity(self, analyses: List[PageAnalysis]) -> LayoutComplexity:
        """
        Classify the layout complexity.
        
        Analyzes:
        - Column count using text block positions
        - Table presence via bounding box patterns
        - Figure presence via image objects
        """
        column_counts = []
        has_tables = False
        has_figures = False
        
        for page in analyses:
            # Detect columns by analyzing x-positions of text blocks
            if page.text_blocks:
                x_positions = []
                for block in page.text_blocks:
                    bbox = block.get("bbox", [])
                    if len(bbox) >= 4:
                        x_positions.extend([bbox[0], bbox[2]])  # x0 and x1
                
                # Estimate column count using x-position clustering
                if x_positions:
                    # Simple heuristic: count major x-position clusters
                    sorted_x = sorted(set(x_positions))
                    columns = 1
                    prev_x = sorted_x[0]
                    for x in sorted_x[1:]:
                        if x - prev_x > 100:  # threshold for column separation
                            columns += 1
                        prev_x = x
                    column_counts.append(min(columns, 4))  # cap at 4 columns
            
            if page.tables > 0:
                has_tables = True
            if len(page.images) > 0:
                has_figures = True
        
        # Determine dominant complexity
        if column_counts:
            avg_columns = sum(column_counts) / len(column_counts)
        else:
            avg_columns = 1
        
        # Classify based on analysis
        if has_tables and avg_columns >= 2:
            return LayoutComplexity.TABLE_HEAVY
        elif has_figures and avg_columns >= 2:
            return LayoutComplexity.FIGURE_HEAVY
        elif avg_columns >= 2:
            return LayoutComplexity.MULTI_COLUMN
        elif has_tables:
            return LayoutComplexity.TABLE_HEAVY
        elif has_figures:
            return LayoutComplexity.FIGURE_HEAVY
        else:
            return LayoutComplexity.SINGLE_COLUMN
    
    def _estimate_page_types(
        self, analyses: List[PageAnalysis]
    ) -> Tuple[int, int]:
        """Estimate the number of scanned vs native pages."""
        scanned = 0
        native = 0
        
        for page in analyses:
            if page.char_density < self.CHAR_DENSITY_THRESHOLD:
                scanned += 1
            else:
                native += 1
        
        return scanned, native
    
    def _determine_extraction_cost(
        self, origin_type: OriginType, layout_complexity: LayoutComplexity
    ) -> ExtractionCostHint:
        """
        Determine the recommended extraction cost hint.
        
        Based on the decision tree from DOMAIN_NOTES.md:
        - scanned_image → needs_vision_model
        - mixed → needs_layout_model  
        - native_digital + single_column → fast_text_sufficient
        - native_digital + complex → needs_layout_model
        """
        if origin_type == OriginType.SCANNED_IMAGE:
            return ExtractionCostHint.NEEDS_VISION_MODEL
        
        if origin_type == OriginType.MIXED:
            return ExtractionCostHint.NEEDS_LAYOUT_MODEL
        
        if origin_type == OriginType.NATIVE_DIGITAL:
            if layout_complexity == LayoutComplexity.SINGLE_COLUMN:
                return ExtractionCostHint.FAST_TEXT_SUFFICIENT
            else:
                return ExtractionCostHint.NEEDS_LAYOUT_MODEL
        
        # Default fallback
        return ExtractionCostHint.NEEDS_LAYOUT_MODEL
    
    def _calculate_confidence(
        self, 
        char_density: float, 
        image_ratio: float, 
        domain_confidence: float
    ) -> float:
        """Calculate overall confidence in the classification."""
        # Base confidence from character density
        if char_density >= self.CHAR_DENSITY_THRESHOLD:
            density_score = 1.0
        else:
            density_score = min(1.0, char_density / self.CHAR_DENSITY_THRESHOLD)
        
        # Low image ratio is good (suggests text-heavy document)
        if image_ratio <= self.IMAGE_RATIO_THRESHOLD:
            image_score = 1.0 - image_ratio
        else:
            image_score = 0.5
        
        # Weighted combination
        confidence = (
            0.4 * density_score +
            0.3 * image_score +
            0.3 * domain_confidence
        )
        
        return round(confidence, 2)
    
    def _save_profile(self, profile: DocumentProfile) -> None:
        """Save the profile to a JSON file."""
        output_path = self.profiles_dir / f"{profile.doc_id}.json"
        with open(output_path, "w") as f:
            json.dump(profile.model_dump(mode="json"), f, indent=2)
        logger.info(f"Profile saved to: {output_path}")


def triage_document(file_path: str, profiles_dir: str = ".refinery/profiles") -> DocumentProfile:
    """
    Convenience function to triage a document.
    
    Args:
        file_path: Path to the document
        profiles_dir: Directory to save profiles
        
    Returns:
        DocumentProfile with classification results
    """
    agent = TriageAgent(profiles_dir)
    result = agent.analyze(file_path)
    return result.profile


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.agents.triage <document_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    profile = triage_document(file_path)
    print(f"\nDocument Profile:")
    print(f"  ID: {profile.doc_id}")
    print(f"  Origin: {profile.origin_type}")
    print(f"  Layout: {profile.layout_complexity}")
    print(f"  Domain: {profile.domain_hint}")
    print(f"  Extraction: {profile.extraction_cost_hint}")
    print(f"  Pages: {profile.page_count}")
    print(f"  Confidence: {profile.confidence_score}")
