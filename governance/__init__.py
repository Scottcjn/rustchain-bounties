"""
RustChain Governance Package
============================

On-chain governance system for RustChain blockchain.

Usage:
    from governance import create_governance_blueprint, init_governance_db
    
    # Initialize database
    init_governance_db("rustchain.db")
    
    # Create Flask blueprint
    bp = create_governance_blueprint("rustchain.db")
    app.register_blueprint(bp)
"""

from governance import (
    create_governance_blueprint,
    create_governance_ui,
    init_governance_db,
    GOVERNANCE_SCHEMA,
    GOVERNANCE_UI_TEMPLATE,
    GOVERNANCE_SCHEMA as SCHEMA,
)

__all__ = [
    "create_governance_blueprint",
    "create_governance_ui", 
    "init_governance_db",
    "GOVERNANCE_SCHEMA",
    "GOVERNANCE_UI_TEMPLATE",
    "SCHEMA",
]

__version__ = "1.0.0"
__author__ = "Bounty #50 Implementation"
