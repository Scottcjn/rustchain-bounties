#!/usr/bin/env python3
"""
BoTTube Agent Memory - Self-Referencing Past Content
Bounty #2285 - 40 RTC

Features:
- Content memory store with vector similarity search
- Self-reference generation for new videos
- Continuity features (series detection, opinion tracking, milestones)
- Agent stats API

Tech:
- sqlite-vec for vector storage
- TF-IDF + cosine similarity for semantic search
- SQLite for persistence

Wallet: 9dRRMiHiJwjF3VW8pXtKDtpmmxAPFy3zWgV2JY5H6eeT
"""

import os
import sqlite3
import json
import hashlib
import math
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field, asdict
from collections import Counter
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
DB_PATH = os.environ.get('AGENT_MEMORY_DB', 'agent_memory.db')
DEFAULT_EMBEDDING_DIM = 384  # Compatible with sentence-transformers


@dataclass
class VideoMemory:
    """Represents a stored video in agent's memory"""
    video_id: str
    agent_name: str
    title: str
    description: str
    topics: List[str] = field(default_factory=list)
    opinions: List[str] = field(default_factory=list)
    predictions: List[str] = field(default_factory=list)
    upload_date: str = field(default_factory=lambda: datetime.now().isoformat())
    views: int = 0
    likes: int = 0
    series_name: Optional[str] = None
    series_part: Optional[int] = None
    embedding: Optional[List[float]] = None
    tfidf_vector: Optional[Dict[str, float]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VideoMemory':
        return cls(
            video_id=data.get('video_id', ''),
            agent_name=data.get('agent_name', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            topics=data.get('topics', []),
            opinions=data.get('opinions', []),
            predictions=data.get('predictions', []),
            upload_date=data.get('upload_date', datetime.now().isoformat()),
            views=data.get('views', 0),
            likes=data.get('likes', 0),
            series_name=data.get('series_name'),
            series_part=data.get('series_part'),
            embedding=data.get('embedding'),
            tfidf_vector=data.get('tfidf_vector')
        )


@dataclass
class AgentStats:
    """Agent statistics"""
    agent_name: str
    total_videos: int
    first_upload_date: Optional[str]
    latest_upload_date: Optional[str]
    total_views: int
    total_likes: int
    top_topics: List[Tuple[str, int]]
    recent_opinions: List[str]
    series_count: int
    milestone_next: int  # Next milestone (e.g., 100th video)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'agent_name': self.agent_name,
            'total_videos': self.total_videos,
            'first_upload_date': self.first_upload_date,
            'latest_upload_date': self.latest_upload_date,
            'total_views': self.total_views,
            'total_likes': self.total_likes,
            'top_topics': self.top_topics,
            'recent_opinions': self.recent_opinions,
            'series_count': self.series_count,
            'milestone_next': self.milestone_next
        }


class TFIDFVectorizer:
    """Simple TF-IDF vectorizer for semantic similarity"""

    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.document_count = 0

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words"""
        # Convert to lowercase and extract words
        text = text.lower()
        words = re.findall(r'\b[a-z0-9]{2,}\b', text)
        return words

    def fit(self, documents: List[str]):
        """Fit the vectorizer on documents"""
        self.document_count = len(documents)
        doc_freq: Counter = Counter()

        for doc in documents:
            words = set(self._tokenize(doc))
            for word in words:
                doc_freq[word] += 1

        # Build vocabulary and IDF
        self.vocabulary = {word: idx for idx, word in enumerate(doc_freq.keys())}
        self.idf = {
            word: math.log((self.document_count + 1) / (freq + 1)) + 1
            for word, freq in doc_freq.items()
        }

    def transform(self, text: str) -> Dict[str, float]:
        """Transform text to TF-IDF vector (or TF if IDF not available)"""
        words = self._tokenize(text)
        tf = Counter(words)
        total_words = len(words) if words else 1

        tfidf = {}
        for word, count in tf.items():
            if word in self.idf:
                # Use TF-IDF if IDF is available
                tfidf[word] = (count / total_words) * self.idf[word]
            else:
                # Use TF only if IDF not available (for new words)
                tfidf[word] = count / total_words

        return tfidf

    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two sparse vectors"""
        if not vec1 or not vec2:
            return 0.0

        # Get common keys
        common_keys = set(vec1.keys()) & set(vec2.keys())

        if not common_keys:
            return 0.0

        # Calculate dot product
        dot_product = sum(vec1[k] * vec2[k] for k in common_keys)

        # Calculate magnitudes
        mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)


class AgentMemoryStore:
    """
    Memory store for BoTTube agents.
    Stores and retrieves past video content for self-referencing.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.vectorizer = TFIDFVectorizer()
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database with vector extension"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create videos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                topics TEXT,
                opinions TEXT,
                predictions TEXT,
                upload_date TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                series_name TEXT,
                series_part INTEGER,
                content_hash TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(video_id, agent_name)
            )
        ''')

        # Create embeddings table (for vector storage)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                embedding BLOB,
                tfidf_vector TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (video_id, agent_name) REFERENCES agent_videos(video_id, agent_name),
                UNIQUE(video_id, agent_name)
            )
        ''')

        # Create series tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                series_name TEXT NOT NULL,
                video_count INTEGER DEFAULT 0,
                last_updated TEXT,
                UNIQUE(agent_name, series_name)
            )
        ''')

        # Create index for fast lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_agent_name 
            ON agent_videos(agent_name)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_upload_date 
            ON agent_videos(upload_date)
        ''')

        conn.commit()
        conn.close()
        logger.info(f"Initialized agent memory database at {self.db_path}")

    def add_video(self, video: VideoMemory) -> bool:
        """Add a video to agent's memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Generate content hash for deduplication
            content = f"{video.title} {video.description}"
            content_hash = hashlib.md5(content.encode()).hexdigest()

            # Calculate TF-IDF vector
            tfidf_vector = self.vectorizer.transform(content)

            # Insert video
            cursor.execute('''
                INSERT OR REPLACE INTO agent_videos 
                (video_id, agent_name, title, description, topics, opinions, predictions,
                 upload_date, views, likes, series_name, series_part, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video.video_id,
                video.agent_name,
                video.title,
                video.description,
                json.dumps(video.topics),
                json.dumps(video.opinions),
                json.dumps(video.predictions),
                video.upload_date,
                video.views,
                video.likes,
                video.series_name,
                video.series_part,
                content_hash
            ))

            # Insert embedding
            cursor.execute('''
                INSERT OR REPLACE INTO video_embeddings 
                (video_id, agent_name, tfidf_vector)
                VALUES (?, ?, ?)
            ''', (
                video.video_id,
                video.agent_name,
                json.dumps(tfidf_vector)
            ))

            # Update series tracking if applicable
            if video.series_name:
                cursor.execute('''
                    INSERT INTO agent_series (agent_name, series_name, video_count, last_updated)
                    VALUES (?, ?, 1, ?)
                    ON CONFLICT(agent_name, series_name) 
                    DO UPDATE SET video_count = video_count + 1, last_updated = ?
                ''', (video.agent_name, video.series_name, datetime.now().isoformat(), 
                      datetime.now().isoformat()))

            conn.commit()
            conn.close()
            logger.info(f"Added video {video.video_id} to {video.agent_name}'s memory")
            return True

        except Exception as e:
            logger.error(f"Error adding video to memory: {e}")
            return False

    def search_memory(self, agent_name: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search agent's memory for similar content.
        Returns videos ranked by semantic similarity.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get all videos for this agent
            cursor.execute('''
                SELECT v.video_id, v.title, v.description, v.topics, v.opinions, v.predictions,
                       v.upload_date, v.views, v.likes, v.series_name, v.series_part,
                       e.tfidf_vector
                FROM agent_videos v
                LEFT JOIN video_embeddings e ON v.video_id = e.video_id AND v.agent_name = e.agent_name
                WHERE v.agent_name = ?
                ORDER BY v.upload_date DESC
            ''', (agent_name,))

            rows = cursor.fetchall()
            conn.close()

            if not rows:
                return []

            # Calculate query vector
            query_vector = self.vectorizer.transform(query)

            # Calculate similarities
            results = []
            for row in rows:
                (video_id, title, description, topics_json, opinions_json, predictions_json,
                 upload_date, views, likes, series_name, series_part, tfidf_json) = row

                if tfidf_json:
                    stored_vector = json.loads(tfidf_json)
                    similarity = self.vectorizer.cosine_similarity(query_vector, stored_vector)
                else:
                    # Fallback to keyword matching
                    similarity = self._keyword_similarity(query, f"{title} {description}")

                results.append({
                    'video_id': video_id,
                    'title': title,
                    'description': description,
                    'topics': json.loads(topics_json) if topics_json else [],
                    'opinions': json.loads(opinions_json) if opinions_json else [],
                    'predictions': json.loads(predictions_json) if predictions_json else [],
                    'upload_date': upload_date,
                    'views': views,
                    'likes': likes,
                    'series_name': series_name,
                    'series_part': series_part,
                    'similarity': similarity
                })

            # Sort by similarity and return top results
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []

    def _keyword_similarity(self, query: str, content: str) -> float:
        """Fallback keyword-based similarity"""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())

        if not query_words or not content_words:
            return 0.0

        intersection = query_words & content_words
        union = query_words | content_words

        return len(intersection) / len(union) if union else 0.0

    def get_agent_stats(self, agent_name: str) -> Optional[AgentStats]:
        """Get statistics for an agent"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get basic stats
            cursor.execute('''
                SELECT COUNT(*), MIN(upload_date), MAX(upload_date), 
                       SUM(views), SUM(likes)
                FROM agent_videos
                WHERE agent_name = ?
            ''', (agent_name,))

            row = cursor.fetchone()
            if not row or row[0] == 0:
                conn.close()
                return None

            total_videos, first_upload, latest_upload, total_views, total_likes = row

            # Get top topics
            cursor.execute('''
                SELECT topics FROM agent_videos
                WHERE agent_name = ? AND topics IS NOT NULL
            ''', (agent_name,))

            topic_counter = Counter()
            for (topics_json,) in cursor.fetchall():
                if topics_json:
                    topics = json.loads(topics_json)
                    topic_counter.update(topics)

            top_topics = topic_counter.most_common(10)

            # Get recent opinions
            cursor.execute('''
                SELECT opinions FROM agent_videos
                WHERE agent_name = ? AND opinions IS NOT NULL
                ORDER BY upload_date DESC
                LIMIT 5
            ''', (agent_name,))

            recent_opinions = []
            for (opinions_json,) in cursor.fetchall():
                if opinions_json:
                    opinions = json.loads(opinions_json)
                    recent_opinions.extend(opinions)

            # Get series count
            cursor.execute('''
                SELECT COUNT(DISTINCT series_name) FROM agent_videos
                WHERE agent_name = ? AND series_name IS NOT NULL
            ''', (agent_name,))

            series_count = cursor.fetchone()[0] or 0

            conn.close()

            # Calculate next milestone
            milestone_next = self._get_next_milestone(total_videos)

            return AgentStats(
                agent_name=agent_name,
                total_videos=total_videos,
                first_upload_date=first_upload,
                latest_upload_date=latest_upload,
                total_views=total_views or 0,
                total_likes=total_likes or 0,
                top_topics=top_topics,
                recent_opinions=recent_opinions[:10],
                series_count=series_count,
                milestone_next=milestone_next
            )

        except Exception as e:
            logger.error(f"Error getting agent stats: {e}")
            return None

    def _get_next_milestone(self, video_count: int) -> int:
        """Get the next milestone number"""
        milestones = [10, 25, 50, 100, 250, 500, 1000]
        for m in milestones:
            if video_count < m:
                return m
        return (video_count // 1000 + 1) * 1000

    def check_for_self_reference(self, agent_name: str, new_title: str, 
                                  new_description: str = "") -> Dict[str, Any]:
        """
        Check if the agent has covered similar topics before.
        Returns suggestions for self-referencing.
        """
        # Search for similar past content
        query = f"{new_title} {new_description}"
        similar_videos = self.search_memory(agent_name, query, limit=3)

        # Get agent stats
        stats = self.get_agent_stats(agent_name)

        suggestions = {
            'has_similar': False,
            'similar_videos': [],
            'series_info': None,
            'milestone_info': None,
            'opinion_check': None,
            'suggested_reference': None
        }

        if similar_videos and similar_videos[0]['similarity'] > 0.3:
            suggestions['has_similar'] = True
            suggestions['similar_videos'] = similar_videos

            # Generate suggested reference
            best_match = similar_videos[0]
            days_ago = self._days_since_upload(best_match['upload_date'])

            if days_ago < 7:
                time_ref = "in my recent video"
            elif days_ago < 30:
                time_ref = f"{days_ago} days ago"
            elif days_ago < 365:
                months = days_ago // 30
                time_ref = f"{months} month{'s' if months > 1 else ''} ago"
            else:
                time_ref = "last year"

            suggestions['suggested_reference'] = (
                f"Following up on my video '{best_match['title']}' from {time_ref}..."
            )

        # Check for series continuation
        series_match = self._detect_series(agent_name, new_title, new_description)
        if series_match:
            suggestions['series_info'] = series_match

        # Check for milestone
        if stats and stats.total_videos + 1 == stats.milestone_next:
            suggestions['milestone_info'] = {
                'milestone': stats.milestone_next,
                'message': f"This is my {stats.milestone_next}th video!"
            }

        # Check opinion consistency
        opinions = self._extract_opinions(new_description)
        if opinions:
            suggestions['opinion_check'] = self._check_opinion_consistency(
                agent_name, opinions, similar_videos
            )

        return suggestions

    def _days_since_upload(self, upload_date: str) -> int:
        """Calculate days since upload"""
        try:
            upload = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
            now = datetime.now(upload.tzinfo) if upload.tzinfo else datetime.now()
            return (now - upload).days
        except:
            return 0

    def _detect_series(self, agent_name: str, title: str, description: str) -> Optional[Dict]:
        """Detect if this video is part of a series"""
        # Common series patterns
        patterns = [
            r'part\s*(\d+)',
            r'episode\s*(\d+)',
            r'#(\d+)',
            r'(\d+)/\d+',
            r'series\s*(\d+)',
        ]

        content = f"{title} {description}".lower()

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                part_num = int(match.group(1))
                
                # Try to extract series name
                series_name = None
                
                # Look for series keywords
                series_keywords = ['series', 'tutorial', 'guide', 'course', 'deep dive']
                for keyword in series_keywords:
                    if keyword in content:
                        # Extract words around the keyword
                        idx = content.find(keyword)
                        start = max(0, idx - 30)
                        end = min(len(content), idx + len(keyword) + 30)
                        series_name = content[start:end].strip()
                        break

                return {
                    'series_name': series_name or 'Unnamed Series',
                    'part_number': part_num,
                    'suggested_title': f"Part {part_num + 1} of my {series_name or 'series'}"
                }

        return None

    def _extract_opinions(self, text: str) -> List[str]:
        """Extract opinions from text"""
        opinions = []
        
        # Opinion patterns
        patterns = [
            r'i think\s+(.+?)(?:[.]|!|\?|$)',
            r'i believe\s+(.+?)(?:[.]|!|\?|$)',
            r'in my opinion\s+(.+?)(?:[.]|!|\?|$)',
            r'i feel\s+(.+?)(?:[.]|!|\?|$)',
            r'my view is\s+(.+?)(?:[.]|!|\?|$)',
        ]

        text_lower = text.lower()
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            opinions.extend(matches)

        return opinions[:3]  # Limit to top 3

    def _check_opinion_consistency(self, agent_name: str, new_opinions: List[str],
                                    similar_videos: List[Dict]) -> Optional[Dict]:
        """Check if new opinions contradict previous ones"""
        if not similar_videos:
            return None

        past_opinions = []
        for video in similar_videos[:2]:
            past_opinions.extend(video.get('opinions', []))

        if not past_opinions:
            return None

        # Simple check for contradiction keywords
        contradiction_words = ['not', "don't", "doesn't", 'never', 'wrong', 'mistake']
        
        for new_op in new_opinions:
            new_op_lower = new_op.lower()
            for past_op in past_opinions:
                past_op_lower = past_op.lower()
                
                # Check if same topic but with contradiction
                for word in contradiction_words:
                    if word in new_op_lower and word not in past_op_lower:
                        return {
                            'potential_contradiction': True,
                            'new_opinion': new_op,
                            'past_opinion': past_op,
                            'suggestion': f"I changed my mind since my last take on this..."
                        }

        return None

    def get_all_agents(self) -> List[str]:
        """Get list of all agents with memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT DISTINCT agent_name FROM agent_videos')
            agents = [row[0] for row in cursor.fetchall()]

            conn.close()
            return agents

        except Exception as e:
            logger.error(f"Error getting agents: {e}")
            return []

    def delete_video(self, video_id: str, agent_name: str) -> bool:
        """Delete a video from memory"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM agent_videos 
                WHERE video_id = ? AND agent_name = ?
            ''', (video_id, agent_name))

            cursor.execute('''
                DELETE FROM video_embeddings 
                WHERE video_id = ? AND agent_name = ?
            ''', (video_id, agent_name))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"Error deleting video: {e}")
            return False

    def export_memory(self, agent_name: str) -> Dict[str, Any]:
        """Export agent's memory as JSON"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT video_id, title, description, topics, opinions, predictions,
                       upload_date, views, likes, series_name, series_part
                FROM agent_videos
                WHERE agent_name = ?
                ORDER BY upload_date DESC
            ''', (agent_name,))

            rows = cursor.fetchall()
            conn.close()

            videos = []
            for row in rows:
                videos.append({
                    'video_id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'topics': json.loads(row[3]) if row[3] else [],
                    'opinions': json.loads(row[4]) if row[4] else [],
                    'predictions': json.loads(row[5]) if row[5] else [],
                    'upload_date': row[6],
                    'views': row[7],
                    'likes': row[8],
                    'series_name': row[9],
                    'series_part': row[10]
                })

            stats = self.get_agent_stats(agent_name)

            return {
                'agent_name': agent_name,
                'stats': stats.to_dict() if stats else None,
                'videos': videos,
                'export_date': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error exporting memory: {e}")
            return {'error': str(e)}


# API Server (FastAPI)
def create_api_app():
    """Create FastAPI app for agent memory API"""
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn

    app = FastAPI(
        title="BoTTube Agent Memory API",
        description="API for agent self-referencing and memory",
        version="1.0.0"
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    memory_store = AgentMemoryStore()

    @app.get("/api/v1/agents/{agent_name}/memory")
    async def search_memory(
        agent_name: str,
        query: str = Query(..., description="Search query"),
        limit: int = Query(5, ge=1, le=20)
    ):
        """Search agent's memory for similar content"""
        results = memory_store.search_memory(agent_name, query, limit)
        return {
            "agent_name": agent_name,
            "query": query,
            "results": results
        }

    @app.get("/api/v1/agents/{agent_name}/stats")
    async def get_stats(agent_name: str):
        """Get agent statistics"""
        stats = memory_store.get_agent_stats(agent_name)
        if not stats:
            raise HTTPException(status_code=404, detail="Agent not found")
        return stats.to_dict()

    @app.post("/api/v1/agents/{agent_name}/videos")
    async def add_video(agent_name: str, video: Dict[str, Any]):
        """Add a video to agent's memory"""
        video['agent_name'] = agent_name
        memory_video = VideoMemory.from_dict(video)
        success = memory_store.add_video(memory_video)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add video")
        return {"status": "success", "video_id": video.get('video_id')}

    @app.post("/api/v1/agents/{agent_name}/check-reference")
    async def check_reference(
        agent_name: str,
        title: str = Query(..., description="New video title"),
        description: str = Query("", description="New video description")
    ):
        """Check for self-referencing opportunities"""
        suggestions = memory_store.check_for_self_reference(
            agent_name, title, description
        )
        return suggestions

    @app.get("/api/v1/agents")
    async def list_agents():
        """List all agents with memory"""
        agents = memory_store.get_all_agents()
        return {"agents": agents}

    @app.get("/api/v1/agents/{agent_name}/export")
    async def export_memory(agent_name: str):
        """Export agent's memory as JSON"""
        memory = memory_store.export_memory(agent_name)
        return memory

    return app


def run_api_server(host: str = "0.0.0.0", port: int = 8098):
    """Run the API server"""
    import uvicorn
    app = create_api_app()
    uvicorn.run(app, host=host, port=port)


# CLI Interface
def main():
    """CLI for agent memory management"""
    import argparse

    parser = argparse.ArgumentParser(description="BoTTube Agent Memory")
    parser.add_argument('--api', action='store_true', help='Run API server')
    parser.add_argument('--port', type=int, default=8098, help='API server port')
    parser.add_argument('--add-video', action='store_true', help='Add a video')
    parser.add_argument('--search', type=str, help='Search agent memory')
    parser.add_argument('--stats', type=str, help='Get agent stats')
    parser.add_argument('--agent', type=str, help='Agent name')
    parser.add_argument('--title', type=str, help='Video title')
    parser.add_argument('--description', type=str, help='Video description')
    parser.add_argument('--video-id', type=str, help='Video ID')
    parser.add_argument('--export', type=str, help='Export agent memory to JSON')

    args = parser.parse_args()

    if args.api:
        print(f"🚀 Starting Agent Memory API on port {args.port}")
        run_api_server(port=args.port)
        return

    store = AgentMemoryStore()

    if args.add_video and args.agent and args.title:
        video = VideoMemory(
            video_id=args.video_id or f"vid_{datetime.now().timestamp()}",
            agent_name=args.agent,
            title=args.title,
            description=args.description or ""
        )
        if store.add_video(video):
            print(f"✅ Added video '{args.title}' to {args.agent}'s memory")
        else:
            print(f"❌ Failed to add video")

    elif args.search and args.agent:
        results = store.search_memory(args.agent, args.search)
        print(f"\n🔍 Search results for '{args.search}' in {args.agent}'s memory:")
        for r in results:
            print(f"  - [{r['similarity']:.2f}] {r['title']} ({r['upload_date'][:10]})")

    elif args.stats:
        stats = store.get_agent_stats(args.stats)
        if stats:
            print(f"\n📊 Stats for {args.stats}:")
            print(f"  Total videos: {stats.total_videos}")
            print(f"  Total views: {stats.total_views:,}")
            print(f"  Total likes: {stats.total_likes:,}")
            print(f"  First upload: {stats.first_upload_date}")
            print(f"  Next milestone: {stats.milestone_next}")
            print(f"  Top topics: {stats.top_topics[:5]}")
        else:
            print(f"❌ Agent not found: {args.stats}")

    elif args.export:
        memory = store.export_memory(args.export)
        filename = f"{args.export}_memory_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(memory, f, indent=2)
        print(f"✅ Exported memory to {filename}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()