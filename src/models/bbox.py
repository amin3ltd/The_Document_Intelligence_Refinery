"""Bounding Box schema for spatial metadata with geometric operations.


"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class BBox(BaseModel):
    """
    Bounding Box representation with validation and geometric operations.
    
    Coordinates are in the format [x0, y0, x1, y1] where:
    - x0, y0: Top-left corner
    - x1, y1: Bottom-right corner
    
    All coordinates are in PDF point units (72 DPI).
    """
    x0: float = Field(..., description="Left edge coordinate")
    y0: float = Field(..., description="Top edge coordinate")
    x1: float = Field(..., description="Right edge coordinate")
    y1: float = Field(..., description="Bottom edge coordinate")
    
    @field_validator('x1')
    @classmethod
    def x1_must_be_greater_than_x0(cls, v: float, info) -> float:
        """Validate that x1 > x0."""
        if 'x0' in info.data and v <= info.data['x0']:
            raise ValueError(f"x1 ({v}) must be greater than x0 ({info.data['x0']})")
        return v
    
    @field_validator('y1')
    @classmethod
    def y1_must_be_greater_than_y0(cls, v: float, info) -> float:
        """Validate that y1 > y0."""
        if 'y0' in info.data and v <= info.data['y0']:
            raise ValueError(f"y1 ({v}) must be greater than y0 ({info.data['y0']})")
        return v
    
    @property
    def width(self) -> float:
        """Calculate width of the bounding box (right - left)."""
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        """Calculate height of the bounding box (bottom - top)."""
        return self.y1 - self.y0
    
    @property
    def area(self) -> float:
        """Calculate area of the bounding box."""
        return self.width * self.height
    
    @property
    def center(self) -> tuple[float, float]:
        """Get center point of the bounding box."""
        return ((self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2)
    
    @property
    def left(self) -> float:
        """Left x-coordinate (alias for x0)."""
        return self.x0
    
    @property
    def top(self) -> float:
        """Top y-coordinate (alias for y0)."""
        return self.y0
    
    @property
    def right(self) -> float:
        """Right x-coordinate (alias for x1)."""
        return self.x1
    
    @property
    def bottom(self) -> float:
        """Bottom y-coordinate (alias for y1)."""
        return self.y1
    
    def to_list(self) -> List[float]:
        """Convert to list format [x0, y0, x1, y1]."""
        return [self.x0, self.y0, self.x1, self.y1]
    
    @classmethod
    def from_list(cls, coords: List[float]) -> "BBox":
        """Create BBox from list [x0, y0, x1, y1]."""
        if len(coords) != 4:
            raise ValueError(f"BBox requires 4 coordinates, got {len(coords)}")
        return cls(x0=coords[0], y0=coords[1], x1=coords[2], y1=coords[3])
    
    @classmethod
    def from_tuple(cls, coords: tuple[float, float, float, float]) -> "BBox":
        """Create BBox from tuple (left, top, right, bottom)."""
        return cls(x0=coords[0], y0=coords[1], x1=coords[2], y1=coords[3])
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if a point is within this bounding box."""
        return self.x0 <= x <= self.x1 and self.y0 <= y <= self.y1
    
    def overlaps_with(self, other: "BBox") -> bool:
        """Check if this bounding box overlaps with another."""
        return not (
            self.x1 < other.x0 or 
            other.x1 < self.x0 or 
            self.y1 < other.y0 or 
            other.y1 < self.y0
        )
    
    def contains(self, other: "BBox") -> bool:
        """
        Check if this bounding box contains another bounding box.
        
        Returns True if other is completely within self.
        """
        return (other.x0 >= self.x0 and 
                other.x1 <= self.x1 and 
                other.y0 >= self.y0 and 
                other.y1 <= self.y1)
    
    def _calculate_intersection_area(self, other: "BBox") -> float:
        """Calculate the intersection area between this bounding box and another."""
        left = max(self.x0, other.x0)
        top = max(self.y0, other.y0)
        right = min(self.x1, other.x1)
        bottom = min(self.y1, other.y1)
        
        if left < right and top < bottom:
            return (right - left) * (bottom - top)
        return 0.0
    
    def iou(self, other: "BBox") -> float:
        """
        Calculate Intersection over Union (IOU) between two bounding boxes.
        
        Returns a value between 0.0 and 1.0:
        - 1.0 means perfect overlap
        - 0.0 means no overlap
        """
        intersection_area = self._calculate_intersection_area(other)
        
        if intersection_area == 0:
            return 0.0
        
        union_area = self.area + other.area - intersection_area
        
        if union_area == 0:
            return 0.0
        
        return intersection_area / union_area
    
    def intersection_ratio(self, other: "BBox") -> float:
        """
        Calculate the intersection ratio between two bounding boxes.
        
        Returns the ratio of intersection area to the smaller box's area.
        Value between 0.0 and 1.0.
        """
        intersection_area = self._calculate_intersection_area(other)
        
        if intersection_area == 0:
            return 0.0
        
        smaller_area = min(self.area, other.area)
        
        if smaller_area == 0:
            return 0.0
        
        return intersection_area / smaller_area
    
    def merge(self, other: "BBox") -> "BBox":
        """
        Merge this bounding box with another, creating a box that contains both.
        
        The resulting box has:
        - left = min(self.left, other.left)
        - top = min(self.top, other.top)
        - right = max(self.right, other.right)
        - bottom = max(self.bottom, other.bottom)
        """
        return BBox(
            x0=min(self.x0, other.x0),
            y0=min(self.y0, other.y0),
            x1=max(self.x1, other.x1),
            y1=max(self.y1, other.y1)
        )
    
    def relaxed_iou(self, other: "BBox", relaxation: float = 10.0) -> float:
        """
        Calculate a relaxed IOU with an expansion factor.
        
        This expands both boxes by the relaxation factor before calculating IOU,
        which helps with boxes that are slightly misaligned but still represent
        the same content.
        
        Args:
            other: The other bounding box
            relaxation: Pixels to expand each side (default 10.0)
        
        Returns:
            Relaxed IOU value between 0.0 and 1.0
        """
        self_width = self.width
        self_height = self.height
        
        # Calculate proportional relaxation (percentage of box size)
        self_expansion = relaxation
        other_expansion = relaxation
        
        # Expand boxes
        expanded_self = BBox(
            x0=max(0.0, self.x0 - self_expansion),
            y0=max(0.0, self.y0 - self_expansion),
            x1=self.x1 + self_expansion,
            y1=self.y1 + self_expansion
        )
        
        expanded_other = BBox(
            x0=max(0.0, other.x0 - other_expansion),
            y0=max(0.0, other.y0 - other_expansion),
            x1=other.x1 + other_expansion,
            y1=other.y1 + other_expansion
        )
        
        return expanded_self.iou(expanded_other)
    
    def weighted_distance(self, other: "BBox") -> float:
        """
        Calculate the weighted distance between two bounding boxes.
        
        Uses center points and relative size difference.
        Lower values indicate more similar boxes.
        """
        (self_center_x, self_center_y) = self.center
        (other_center_x, other_center_y) = other.center
        
        # Distance between centers
        center_distance = ((self_center_x - other_center_x) ** 2 + 
                         (self_center_y - other_center_y) ** 2) ** 0.5
        
        # Size difference ratio
        size_ratio = max(self.area, other.area) / max(min(self.area, other.area), 1e-6)
        
        # Normalize by typical document dimensions (assuming 8.5x11 inch at 72 DPI)
        normalized_distance = center_distance / 612.0  # 8.5 * 72
        
        return normalized_distance * size_ratio
    
    def expand(self, amount: float) -> "BBox":
        """
        Expand the bounding box by a uniform amount in all directions.
        
        Args:
            amount: Amount to expand each side by (in points)
        
        Returns:
            New expanded BBox
        """
        return BBox(
            x0=max(0.0, self.x0 - amount),
            y0=max(0.0, self.y0 - amount),
            x1=self.x1 + amount,
            y1=self.y1 + amount
        )
    
    def scale(self, factor: float) -> "BBox":
        """
        Scale the bounding box by a factor from origin (0, 0).
        
        Args:
            factor: Scale factor (e.g., 2.0 doubles the size)
        
        Returns:
            New scaled BBox
        """
        return BBox(
            x0=self.x0 * factor,
            y0=self.y0 * factor,
            x1=self.x1 * factor,
            y1=self.y1 * factor
        )
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "x0": 50.0,
                "y0": 100.0,
                "x1": 500.0,
                "y1": 280.0
            }
        }
