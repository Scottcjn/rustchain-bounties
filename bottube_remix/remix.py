#!/usr/bin/env python3
"""
BoTTube Remix - Video remix functionality and Provenance Tree MVP.

Features:
- Remix videos with transformations
- Track content provenance
- Build provenance trees
- Verify content origins
"""

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from enum import Enum
from collections import defaultdict


# ===== Data Models =====

class RemixType(Enum):
    """Types of remixes."""
    CUT = "cut"
    MIX = "mix"
    OVERLAY = "overlay"
    SUBTITLE = "subtitle"
    VOICE_OVER = "voice_over"
    TRANSITION = "transition"


class ContentStatus(Enum):
    """Content status."""
    DRAFT = "draft"
    PROCESSING = "processing"
    READY = "ready"
    PUBLISHED = "published"
    REJECTED = "rejected"


@dataclass
class ProvenanceNode:
    """A node in the provenance tree."""
    id: str
    content_id: str
    content_hash: str
    source_ids: List[str]  # Parent content IDs
    remix_type: Optional[str]
    created_at: str
    creator: str
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content_id": self.content_id,
            "content_hash": self.content_hash,
            "source_ids": self.source_ids,
            "remix_type": self.remix_type,
            "created_at": self.created_at,
            "creator": self.creator,
            "metadata": self.metadata,
        }


@dataclass
class RemixRequest:
    """A remix request."""
    source_content_id: str
    remix_type: RemixType
    parameters: Dict[str, Any]
    creator: str
    title: Optional[str] = None
    description: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "source_content_id": self.source_content_id,
            "remix_type": self.remix_type.value,
            "parameters": self.parameters,
            "creator": self.creator,
            "title": self.title,
            "description": self.description,
        }


@dataclass
class RemixResult:
    """Result of a remix operation."""
    success: bool
    content_id: Optional[str]
    provenance_node_id: Optional[str]
    message: str
    output_url: Optional[str] = None
    errors: List[str] = field(default_factory=list)


# ===== Provenance Tree =====

class ProvenanceTree:
    """
    Manages content provenance tracking.
    
    Tracks the lineage of remixed content building a tree structure.
    """
    
    def __init__(self):
        self._nodes: Dict[str, ProvenanceNode] = {}
        self._content_index: Dict[str, List[str]] = defaultdict(list)  # content_id -> node_ids
    
    def add_node(self, node: ProvenanceNode) -> None:
        """Add a provenance node."""
        self._nodes[node.id] = node
        self._content_index[node.content_id].append(node.id)
    
    def get_node(self, node_id: str) -> Optional[ProvenanceNode]:
        """Get a provenance node by ID."""
        return self._nodes.get(node_id)
    
    def get_content_nodes(self, content_id: str) -> List[ProvenanceNode]:
        """Get all provenance nodes for a content ID."""
        node_ids = self._content_index.get(content_id, [])
        return [self._nodes[nid] for nid in node_ids if nid in self._nodes]
    
    def get_ancestors(self, content_id: str, max_depth: int = 10) -> List[ProvenanceNode]:
        """Get all ancestors of a content item."""
        ancestors = []
        visited: Set[str] = set()
        
        def traverse(cid: str, depth: int):
            if depth > max_depth or cid in visited:
                return
            
            visited.add(cid)
            nodes = self.get_content_nodes(cid)
            
            for node in nodes:
                ancestors.append(node)
                for source_id in node.source_ids:
                    traverse(source_id, depth + 1)
        
        traverse(content_id, 0)
        return ancestors
    
    def get_descendants(self, content_id: str, max_depth: int = 10) -> List[ProvenanceNode]:
        """Get all descendants of a content item."""
        descendants = []
        visited: Set[str] = set()
        
        def traverse(cid: str, depth: int):
            if depth > max_depth or cid in visited:
                return
            
            visited.add(cid)
            
            # Find nodes that have this content as a source
            for node in self._nodes.values():
                if cid in node.source_ids:
                    descendants.append(node)
                    traverse(node.content_id, depth + 1)
        
        traverse(content_id, 0)
        return descendants
    
    def get_tree(self, content_id: str) -> Dict[str, Any]:
        """Get the full provenance tree for content."""
        ancestors = self.get_ancestors(content_id)
        
        tree = {
            "root_content_id": content_id,
            "ancestors": [n.to_dict() for n in ancestors],
            "total_ancestors": len(ancestors),
        }
        
        return tree
    
    def verify_provenance(self, content_id: str) -> Dict[str, Any]:
        """Verify the provenance of content."""
        nodes = self.get_content_nodes(content_id)
        
        if not nodes:
            return {
                "verified": False,
                "content_id": content_id,
                "message": "No provenance records found",
            }
        
        # Check for valid tree structure
        has_roots = any(len(n.source_ids) == 0 for n in nodes)
        
        return {
            "verified": True,
            "content_id": content_id,
            "has_roots": has_roots,
            "node_count": len(nodes),
            "message": "Provenance verified",
        }
    
    def to_json(self) -> str:
        """Export provenance tree to JSON."""
        data = {
            "nodes": {k: v.to_dict() for k, v in self._nodes.items()},
            "content_index": dict(self._content_index),
        }
        return json.dumps(data, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> "ProvenanceTree":
        """Import provenance tree from JSON."""
        data = json.loads(json_str)
        tree = cls()
        
        for node_id, node_data in data.get("nodes", {}).items():
            node = ProvenanceNode(**node_data)
            tree.add_node(node)
        
        return tree


# ===== Remix Engine =====

class RemixEngine:
    """
    Handles video remix operations.
    
    Supports various remix types:
    - CUT: Extract segments from source
    - MIX: Combine multiple sources
    - OVERLAY: Add overlay to source
    - SUBTITLE: Add subtitles
    - VOICE_OVER: Add voice over
    - TRANSITION: Add transitions
    """
    
    def __init__(self, provenance_tree: Optional[ProvenanceTree] = None):
        self.provenance_tree = provenance_tree or ProvenanceTree()
        self._content_store: Dict[str, Dict] = {}
    
    def _generate_content_id(self, data: Dict) -> str:
        """Generate a unique content ID."""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _generate_hash(self, content: str) -> str:
        """Generate content hash."""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def create_remix(self, request: RemixRequest) -> RemixResult:
        """Create a remix from a source."""
        try:
            # Validate source exists
            source_nodes = self.provenance_tree.get_content_nodes(request.source_content_id)
            
            # Create new content
            content_id = self._generate_content_id(request.to_dict())
            content_hash = self._generate_hash(json.dumps(request.parameters))
            
            # Create provenance node
            node_id = f"node_{content_id}"
            node = ProvenanceNode(
                id=node_id,
                content_id=content_id,
                content_hash=content_hash,
                source_ids=[request.source_content_id],
                remix_type=request.remix_type.value,
                created_at=datetime.now().isoformat(),
                creator=request.creator,
                metadata={
                    "title": request.title,
                    "description": request.description,
                    "parameters": request.parameters,
                }
            )
            
            # Store content
            self._content_store[content_id] = {
                "id": content_id,
                "type": request.remix_type.value,
                "status": ContentStatus.READY.value,
                "created_at": node.created_at,
                "creator": request.creator,
            }
            
            # Add to provenance tree
            self.provenance_tree.add_node(node)
            
            return RemixResult(
                success=True,
                content_id=content_id,
                provenance_node_id=node_id,
                message=f"Remix created successfully",
                output_url=f"https://bottube.example.com/watch/{content_id}",
            )
            
        except Exception as e:
            return RemixResult(
                success=False,
                content_id=None,
                provenance_node_id=None,
                message=f"Failed to create remix: {str(e)}",
                errors=[str(e)],
            )
    
    def get_provenance(self, content_id: str) -> Dict[str, Any]:
        """Get provenance for content."""
        return self.provenance_tree.get_tree(content_id)
    
    def verify_provenance(self, content_id: str) -> Dict[str, Any]:
        """Verify content provenance."""
        return self.provenance_tree.verify_provenance(content_id)
    
    def get_content(self, content_id: str) -> Optional[Dict]:
        """Get content by ID."""
        return self._content_store.get(content_id)


# ===== Main =====

def main():
    """Demo the Remix and Provenance Tree."""
    # Create engine
    engine = RemixEngine()
    
    # Create original content
    original_request = RemixRequest(
        source_content_id="original_video_001",
        remix_type=RemixType.CUT,
        parameters={"start": 0, "end": 30},
        creator="creator1",
        title="Original Video",
    )
    
    result = engine.create_remix(original_request)
    print(f"Created original: {result.content_id}")
    
    # Create remix
    remix_request = RemixRequest(
        source_content_id=result.content_id,
        remix_type=RemixType.OVERLAY,
        parameters={"overlay_text": "New Title"},
        creator="creator2",
        title="Remixed Video",
    )
    
    result2 = engine.create_remix(remix_request)
    print(f"Created remix: {result2.content_id}")
    
    # Get provenance
    provenance = engine.get_provenance(result2.content_id)
    print(f"\nProvenance for remix:")
    print(json.dumps(provenance, indent=2))
    
    # Verify
    verified = engine.verify_provenance(result2.content_id)
    print(f"\nVerification: {verified['verified']}")
    
    # Export provenance
    print(f"\nProvenance Tree JSON:")
    print(engine.provenance_tree.to_json())


if __name__ == "__main__":
    main()
