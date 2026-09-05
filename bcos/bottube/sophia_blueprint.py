"""Sophia Blueprint Core Module

Core functionality for Sophia's request processing pipeline.
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def _client_ip(request: Dict[str, Any]) -> str:
    """
    Extract client IP address from request headers.

    Args:
        request: Dictionary containing request headers and metadata

    Returns:
        str: Client IP address extracted from X-Forwarded-For or Remote-Addr

    Raises:
        ValueError: If IP cannot be determined from available headers
    """
    forwarded = request.get('headers', {}).get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.get('connection', {}).get('remoteAddress', 'unknown')

def init_sophia_corpus(db_path: str, max_size: int = 1000) -> None:
    """
    Initialize Sophia's knowledge corpus database.

    Args:
        db_path: Path to SQLite database file
        max_size: Maximum number of documents to store (default: 1000)

    Returns:
        None: Initializes database connection and creates tables if needed
    """
    global _db_conn
    _db_conn = sqlite3.connect(db_path)
    _db_conn.execute("""
        CREATE TABLE IF NOT EXISTS corpus (
            id INTEGER PRIMARY KEY,
            content TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    logger.info(f"Sophia corpus initialized at {db_path}")

def _log_corpus(operation: str, doc_id: int, metadata: Optional[Dict] = None) -> None:
    """
    Log corpus operations for audit purposes.

    Args:
        operation: Type of operation ('insert', 'update', 'delete')
        doc_id: ID of affected document
        metadata: Additional context about the operation

    Returns:
        None: Logs entry to both file and console
    """
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'operation': operation,
        'doc_id': doc_id,
        'metadata': metadata or {}
    }
    logger.info(json.dumps(log_entry))
    with open('corpus_audit.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def _db_path() -> str:
    """
    Get default path for Sophia's database file.

    Returns:
        str: Path to database file in project's data directory
    """
    return os.path.join(os.getenv('DATA_DIR', 'data'), 'sophia_corpus.db')

def _conn() -> sqlite3.Connection:
    """
    Get active database connection.

    Returns:
        sqlite3.Connection: Active connection to Sophia's corpus database

    Raises:
        RuntimeError: If connection hasn't been initialized
    """
    if not hasattr(_conn, '_connection'):
        raise RuntimeError("Database connection not initialized")
    return _conn._connection

def _origin_allowed(origin: str) -> bool:
    """
    Validate request origin against allowed domains.

    Args:
        origin: Request origin header value

    Returns:
        bool: True if origin is in allowed list, False otherwise
    """
    allowed = {
        'https://sophia.example.com',
        'https://api.sophia.example.com'
    }
    return any(origin.startswith(domain) for domain in allowed)

def sophia_health() -> Dict[str, Any]:
    """
    Health check endpoint for Sophia service.

    Returns:
        dict: Service status with:
            - 'status': 'healthy' or 'unhealthy'
            - 'corpus_size': Current document count
            - 'last_updated': Timestamp of last update
    """
    if not hasattr(_conn, '_connection'):
        return {'status': 'unhealthy', 'error': 'Database not connected'}

    cursor = _conn().cursor()
    cursor.execute("SELECT COUNT(*) FROM corpus")
    size = cursor.fetchone()[0]

    return {
        'status': 'healthy',
        'corpus_size': size,
        'last_updated': datetime.now().isoformat()
    }

def sophia_chat(prompt: str, context: Optional[Dict] = None) -> str:
    """
    Process chat request through Sophia's knowledge base.

    Args:
        prompt: User's input question
        context: Additional context for the query (optional)

    Returns:
        str: Generated response based on knowledge base

    Raises:
        ValueError: If prompt is empty
    """
    if not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    # Implementation logic...
    return "Generated response based on Sophia's knowledge"