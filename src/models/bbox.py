"""Bounding Box schema for spatial metadata."""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class BBox(BaseModel):
    """
    Bounding Box representation with validation.
    
    Coordinates are in the format [x0, y0, x1, y1] where:
    - x0, y0: Top-left corner
    - x1, y1: Bottom-right corner
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
        """Calculate width of the bounding box."""
        return self.x1 - self.x0
    
    @property
    def height(self) -> float:
        """Calculate height of the bounding box."""
        return self.y1 - self.y0
    
    @property
    def area(self) -> float:
        """Calculate area of the bounding box."""
        return self.width * self.height
    
    @property
    def center(self) -> tuple[float, float]:
        """Get center point of the bounding box."""
        return ((self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2)
    
    def to_list(self) -> List[float]:
        """Convert to list format [x0, y0, x1, y1]."""
        return [self.x0, self.y0, self.x1, self.y1]
    
    @classmethod
    def from_list(cls, coords: List[float]) -> "BBox":
        """Create BBox from list [x0, y0, x1, y1]."""
        if len(coords) != 4:
            raise ValueError(f"BBox requires 4 coordinates, got {len(coords)}")
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
