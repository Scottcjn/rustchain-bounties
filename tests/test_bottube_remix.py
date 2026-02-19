#!/usr/bin/env python3
"""Tests for BoTTube Remix"""

import pytest
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bottube_remix.remix import (
    RemixEngine,
    ProvenanceTree,
    ProvenanceNode,
    RemixRequest,
    RemixResult,
    RemixType,
    ContentStatus,
)


class TestProvenanceNode:
    """Test ProvenanceNode"""

    def test_create_node(self):
        node = ProvenanceNode(
            id="node_1",
            content_id="content_1",
            content_hash="abc123",
            source_ids=["original_1"],
            remix_type="cut",
            created_at="2026-02-19T00:00:00Z",
            creator="user1"
        )
        assert node.id == "node_1"
        assert node.content_id == "content_1"
        assert node.remix_type == "cut"

    def test_to_dict(self):
        node = ProvenanceNode(
            id="node_1",
            content_id="content_1",
            content_hash="abc123",
            source_ids=["original_1"],
            remix_type="cut",
            created_at="2026-02-19T00:00:00Z",
            creator="user1"
        )
        data = node.to_dict()
        assert data["id"] == "node_1"
        assert data["remix_type"] == "cut"


class TestRemixType:
    """Test RemixType enum"""
    
    def test_values(self):
        assert RemixType.CUT.value == "cut"
        assert RemixType.MIX.value == "mix"
        assert RemixType.OVERLAY.value == "overlay"


class TestRemixRequest:
    """Test RemixRequest"""
    
    def test_create_request(self):
        request = RemixRequest(
            source_content_id="original_1",
            remix_type=RemixType.CUT,
            parameters={"start": 0, "end": 30},
            creator="user1"
        )
        assert request.source_content_id == "original_1"
        assert request.remix_type == RemixType.CUT
    
    def test_to_dict(self):
        request = RemixRequest(
            source_content_id="original_1",
            remix_type=RemixType.CUT,
            parameters={"start": 0},
            creator="user1"
        )
        data = request.to_dict()
        assert data["remix_type"] == "cut"


class TestRemixResult:
    """Test RemixResult"""
    
    def test_success_result(self):
        result = RemixResult(
            success=True,
            content_id="content_123",
            provenance_node_id="node_123",
            message="Success"
        )
        assert result.success is True
        assert result.content_id == "content_123"
    
    def test_error_result(self):
        result = RemixResult(
            success=False,
            content_id=None,
            provenance_node_id=None,
            message="Error",
            errors=["Something went wrong"]
        )
        assert result.success is False
        assert len(result.errors) == 1


class TestProvenanceTree:
    """Test ProvenanceTree"""
    
    def test_create_tree(self):
        tree = ProvenanceTree()
        assert len(tree._nodes) == 0
    
    def test_add_node(self):
        tree = ProvenanceTree()
        node = ProvenanceNode(
            id="node_1",
            content_id="content_1",
            content_hash="abc",
            source_ids=[],
            remix_type=None,
            created_at="2026-02-19T00:00:00Z",
            creator="user1"
        )
        tree.add_node(node)
        
        retrieved = tree.get_node("node_1")
        assert retrieved is not None
        assert retrieved.content_id == "content_1"
    
    def test_get_content_nodes(self):
        tree = ProvenanceTree()
        node = ProvenanceNode(
            id="node_1",
            content_id="content_1",
            content_hash="abc",
            source_ids=[],
            remix_type=None,
            created_at="2026-02-19T00:00:00Z",
            creator="user1"
        )
        tree.add_node(node)
        
        nodes = tree.get_content_nodes("content_1")
        assert len(nodes) == 1
    
    def test_get_ancestors(self):
        tree = ProvenanceTree()
        
        # Add original
        node1 = ProvenanceNode(
            id="node_1",
            content_id="original",
            content_hash="abc",
            source_ids=[],
            remix_type=None,
            created_at="2026-02-19T00:00:00Z",
            creator="user1"
        )
        
        # Add remix
        node2 = ProvenanceNode(
            id="node_2",
            content_id="remix_1",
            content_hash="def",
            source_ids=["original"],
            remix_type="cut",
            created_at="2026-02-19T00:01:00Z",
            creator="user2"
        )
        
        tree.add_node(node1)
        tree.add_node(node2)
        
        ancestors = tree.get_ancestors("remix_1")
        assert len(ancestors) == 2
    
    def test_verify_provenance_exists(self):
        tree = ProvenanceTree()
        node = ProvenanceNode(
            id="node_1",
            content_id="content_1",
            content_hash="abc",
            source_ids=[],
            remix_type=None,
            created_at="2026-02-19T00:00:00Z",
            creator="user1"
        )
        tree.add_node(node)
        
        verified = tree.verify_provenance("content_1")
        assert verified["verified"] is True
    
    def test_verify_provenance_not_exists(self):
        tree = ProvenanceTree()
        
        verified = tree.verify_provenance("nonexistent")
        assert verified["verified"] is False
    
    def test_to_json_from_json(self):
        tree = ProvenanceTree()
        node = ProvenanceNode(
            id="node_1",
            content_id="content_1",
            content_hash="abc",
            source_ids=[],
            remix_type=None,
            created_at="2026-02-19T00:00:00Z",
            creator="user1"
        )
        tree.add_node(node)
        
        json_str = tree.to_json()
        loaded_tree = ProvenanceTree.from_json(json_str)
        
        assert loaded_tree.get_node("node_1") is not None


class TestRemixEngine:
    """Test RemixEngine"""
    
    def test_create_engine(self):
        engine = RemixEngine()
        assert engine.provenance_tree is not None
    
    def test_create_remix(self):
        engine = RemixEngine()
        
        # First create original
        original = RemixRequest(
            source_content_id="original_video",
            remix_type=RemixType.CUT,
            parameters={"start": 0, "end": 30},
            creator="user1"
        )
        
        result = engine.create_remix(original)
        assert result.success is True
        assert result.content_id is not None
    
    def test_remix_chaining(self):
        engine = RemixEngine()
        
        # Create original
        original = RemixRequest(
            source_content_id="original_video",
            remix_type=RemixType.CUT,
            parameters={"start": 0, "end": 30},
            creator="user1"
        )
        
        result1 = engine.create_remix(original)
        
        # Create remix from original
        remix = RemixRequest(
            source_content_id=result1.content_id,
            remix_type=RemixType.OVERLAY,
            parameters={"text": "New Title"},
            creator="user2"
        )
        
        result2 = engine.create_remix(remix)
        
        # Check provenance
        provenance = engine.get_provenance(result2.content_id)
        assert provenance["total_ancestors"] >= 2
    
    def test_verify_provenance(self):
        engine = RemixEngine()
        
        request = RemixRequest(
            source_content_id="original",
            remix_type=RemixType.CUT,
            parameters={"start": 0},
            creator="user1"
        )
        
        result = engine.create_remix(request)
        
        verified = engine.verify_provenance(result.content_id)
        assert verified["verified"] is True
    
    def test_get_content(self):
        engine = RemixEngine()
        
        request = RemixRequest(
            source_content_id="original",
            remix_type=RemixType.CUT,
            parameters={"start": 0},
            creator="user1"
        )
        
        result = engine.create_remix(request)
        content = engine.get_content(result.content_id)
        
        assert content is not None
        assert content["type"] == "cut"


class TestIntegration:
    """Integration tests"""
    
    def test_full_workflow(self):
        engine = RemixEngine()
        
        # Create multiple remixes
        original = RemixRequest(
            source_content_id="source_1",
            remix_type=RemixType.CUT,
            parameters={"start": 0, "end": 60},
            creator="creator1",
            title="Original"
        )
        
        r1 = engine.create_remix(original)
        
        remix1 = RemixRequest(
            source_content_id=r1.content_id,
            remix_type=RemixType.OVERLAY,
            parameters={"overlay": "text"},
            creator="creator2",
            title="Remix 1"
        )
        
        r2 = engine.create_remix(remix1)
        
        remix2 = RemixRequest(
            source_content_id=r2.content_id,
            remix_type=RemixType.MIX,
            parameters={"sources": [r1.content_id, r2.content_id]},
            creator="creator3",
            title="Remix 2"
        )
        
        r3 = engine.create_remix(remix2)
        
        # Verify full lineage
        verified = engine.verify_provenance(r3.content_id)
        assert verified["verified"] is True
        
        # Check ancestors
        provenance = engine.get_provenance(r3.content_id)
        assert provenance["total_ancestors"] >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
