#!/usr/bin/env python3
"""
Beacon Dashboard v1.1 - Transport monitoring TUI

A real-time dashboard for monitoring Beacon transport traffic,
agent health, and network status.

Usage:
    python -m beacon_dashboard.dashboard
    python -m beacon_dashboard.dashboard --export json snapshot.json
    python -m beacon_dashboard.dashboard --export csv snapshot.csv
"""

import argparse
import csv
import json
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from functools import lru_cache


# Try to import rich for TUI, fallback to CLI mode
try:
    from rich.console import Console
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None


# ===== Data Models =====

@dataclass
class TransportStats:
    """Statistics for a single transport."""
    name: str
    status: str  # healthy, degraded, down
    messages_sent: int = 0
    messages_received: int = 0
    errors: int = 0
    last_activity: Optional[str] = None
    top_agents: List[Dict] = field(default_factory=list)


@dataclass
class AgentStats:
    """Statistics for a single agent."""
    agent_id: str
    role: str
    status: str  # active, idle, down
    last_heartbeat: Optional[str] = None
    messages_sent: int = 0
    tips_earned: float = 0.0


@dataclass
class DashboardState:
    """Current state of the dashboard."""
    transports: Dict[str, TransportStats] = field(default_factory=dict)
    agents: Dict[str, AgentStats] = field(default_factory=dict)
    mayday_alerts: List[Dict] = field(default_factory=list)
    high_value_tips: List[Dict] = field(default_factory=list)
    filters: List[str] = field(default_factory=list)
    search_query: str = ""
    last_update: str = ""


# ===== Core Functions =====

def get_dashboard_state() -> DashboardState:
    """Fetch current dashboard state from Beacon API.
    
    In production, this would call the Beacon API.
    For now, returns mock data for demonstration.
    """
    state = DashboardState()
    state.last_update = datetime.now().isoformat()
    
    # Mock transport data
    state.transports = {
        "discord": TransportStats(
            name="discord",
            status="healthy",
            messages_sent=1250,
            messages_received=1180,
            errors=2,
            last_activity=datetime.now().isoformat(),
            top_agents=[
                {"agent_id": "agent-001", "messages": 450},
                {"agent_id": "agent-002", "messages": 380},
                {"agent_id": "agent-003", "messages": 290},
            ]
        ),
        "telegram": TransportStats(
            name="telegram",
            status="healthy",
            messages_sent=890,
            messages_received=865,
            errors=1,
            last_activity=datetime.now().isoformat(),
            top_agents=[
                {"agent_id": "agent-004", "messages": 320},
                {"agent_id": "agent-005", "messages": 280},
            ]
        ),
        "webhook": TransportStats(
            name="webhook",
            status="degraded",
            messages_sent=450,
            messages_received=420,
            errors=15,
            last_activity=datetime.now().isoformat(),
            top_agents=[
                {"agent_id": "agent-006", "messages": 180},
            ]
        ),
    }
    
    # Mock agent data
    state.agents = {
        "agent-001": AgentStats(
            agent_id="agent-001",
            role="coordinator",
            status="active",
            last_heartbeat=datetime.now().isoformat(),
            messages_sent=450,
            tips_earned=25.5
        ),
        "agent-002": AgentStats(
            agent_id="agent-002",
            role="worker",
            status="active",
            last_heartbeat=datetime.now().isoformat(),
            messages_sent=380,
            tips_earned=18.2
        ),
    }
    
    # Mock alerts
    state.mayday_alerts = [
        {"timestamp": datetime.now().isoformat(), "message": "Agent agent-006 connection lost"}
    ]
    
    state.high_value_tips = [
        {"timestamp": datetime.now().isoformat(), "amount": 50.0, "source": "bounty #315"},
    ]
    
    return state


def filter_transports(state: DashboardState) -> Dict[str, TransportStats]:
    """Filter transports based on current filters and search query."""
    filtered = state.transports.copy()
    
    # Apply status filter
    if state.filters:
        filtered = {
            k: v for k, v in filtered.items() 
            if v.status in state.filters
        }
    
    # Apply search query
    if state.search_query:
        query = state.search_query.lower()
        filtered = {
            k: v for k, v in filtered.items()
            if query in k.lower() or query in v.name.lower()
        }
    
    return filtered


def export_to_json(state: DashboardState, filepath: str) -> bool:
    """Export dashboard state to JSON file."""
    try:
        data = {
            "timestamp": state.last_update,
            "transports": {
                name: {
                    "status": stats.status,
                    "messages_sent": stats.messages_sent,
                    "messages_received": stats.messages_received,
                    "errors": stats.errors,
                    "last_activity": stats.last_activity,
                    "top_agents": stats.top_agents,
                }
                for name, stats in state.transports.items()
            },
            "agents": {
                aid: {
                    "role": agent.role,
                    "status": agent.status,
                    "last_heartbeat": agent.last_heartbeat,
                    "messages_sent": agent.messages_sent,
                    "tips_earned": agent.tips_earned,
                }
                for aid, agent in state.agents.items()
            },
            "mayday_alerts": state.mayday_alerts,
            "high_value_tips": state.high_value_tips,
        }
        
        Path(filepath).write_text(json.dumps(data, indent=2))
        return True
    except Exception as e:
        print(f"Export error: {e}", file=sys.stderr)
        return False


def export_to_csv(state: DashboardState, filepath: str) -> bool:
    """Export dashboard state to CSV file."""
    try:
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Transport stats
            writer.writerow(["=== Transport Stats ==="])
            writer.writerow(["Name", "Status", "Sent", "Received", "Errors", "Last Activity"])
            for name, stats in state.transports.items():
                writer.writerow([
                    name, stats.status, stats.messages_sent,
                    stats.messages_received, stats.errors, stats.last_activity
                ])
            
            # Agent stats
            writer.writerow([])
            writer.writerow(["=== Agent Stats ==="])
            writer.writerow(["Agent ID", "Role", "Status", "Messages", "Tips"])
            for aid, agent in state.agents.items():
                writer.writerow([
                    aid, agent.role, agent.status,
                    agent.messages_sent, agent.tips_earned
                ])
        
        return True
    except Exception as e:
        print(f"Export error: {e}", file=sys.stderr)
        return False


# ===== TUI Functions =====

def render_dashboard_tui(state: DashboardState, console: Console) -> None:
    """Render the dashboard using Rich TUI."""
    # Title
    console.print(Panel(
        f"[bold cyan]Beacon Dashboard v1.1[/bold cyan] | Last Update: {state.last_update}",
        style="blue"
    ))
    
    # Transport Health Panel
    transport_table = Table(title="Transport Health")
    transport_table.add_column("Transport", style="cyan")
    transport_table.add_column("Status", style="white")
    transport_table.add_column("Sent", justify="right")
    transport_table.add_column("Received", justify="right")
    transport_table.add_column("Errors", justify="right")
    
    for name, stats in state.transports.items():
        status_color = {
            "healthy": "green",
            "degraded": "yellow",
            "down": "red",
        }.get(stats.status, "white")
        
        transport_table.add_row(
            name,
            f"[{status_color}]{stats.status}[/{status_color}]",
            str(stats.messages_sent),
            str(stats.messages_received),
            str(stats.errors),
        )
    
    console.print(transport_table)
    
    # Mayday Alerts
    if state.mayday_alerts:
        console.print("\n[bold red]⚠️ Mayday Alerts[/bold red]")
        for alert in state.mayday_alerts:
            console.print(f"  • {alert['message']} ({alert['timestamp']})")
    
    # High Value Tips
    if state.high_value_tips:
        console.print("\n[bold yellow]💰 High Value Tips[/bold yellow]")
        for tip in state.high_value_tips:
            console.print(f"  • {tip['amount']} RTC from {tip.get('source', 'unknown')}")


def render_dashboard_cli(state: DashboardState) -> None:
    """Render dashboard in CLI mode (no Rich)."""
    print("=" * 60)
    print(f"Beacon Dashboard v1.1 | Last Update: {state.last_update}")
    print("=" * 60)
    
    print("\n--- Transport Health ---")
    print(f"{'Name':<15} {'Status':<10} {'Sent':>8} {'Received':>10} {'Errors':>8}")
    for name, stats in state.transports.items():
        print(f"{name:<15} {stats.status:<10} {stats.messages_sent:>8} {stats.messages_received:>10} {stats.errors:>8}")
    
    if state.mayday_alerts:
        print("\n--- Mayday Alerts ---")
        for alert in state.mayday_alerts:
            print(f"  ⚠️  {alert['message']}")
    
    if state.high_value_tips:
        print("\n--- High Value Tips ---")
        for tip in state.high_value_tips:
            print(f"  💰 {tip['amount']} RTC from {tip.get('source', 'unknown')}")


# ===== Sound Alerts =====

def play_alert_sound(alert_type: str) -> bool:
    """Play sound alert for mayday or high-value tips.
    
    Requires pygame or similar audio library.
    """
    try:
        # Try pygame first
        import pygame
        pygame.mixer.init()
        
        if alert_type == "mayday":
            # Play alert sound (would need actual file)
            print("🔊 Playing mayday alert sound")
        elif alert_type == "high_value":
            print("🔊 Playing high-value tip notification")
        
        return True
    except ImportError:
        # Fallback: just print
        if alert_type == "mayday":
            print("🔔 MAYDAY ALERT!")
        elif alert_type == "high_value":
            print("🔔 High-value tip received!")
        return True
    except Exception as e:
        print(f"Sound error: {e}", file=sys.stderr)
        return False


# ===== Main Entry Point =====

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Beacon Dashboard v1.1 - Transport monitoring"
    )
    parser.add_argument(
        "--export",
        choices=["json", "csv"],
        help="Export current view to file"
    )
    parser.add_argument(
        "--output",
        help="Output file path for export"
    )
    parser.add_argument(
        "--filter",
        action="append",
        dest="filters",
        help="Filter by status (healthy, degraded, down)"
    )
    parser.add_argument(
        "--search",
        help="Search transports by name"
    )
    parser.add_argument(
        "--sound",
        action="store_true",
        help="Enable sound alerts"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Refresh interval in seconds (default: 5)"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    # Get dashboard state
    state = get_dashboard_state()
    
    # Apply filters
    if args.filters:
        state.filters = args.filters
    if args.search:
        state.search_query = args.search
    
    # Export mode
    if args.export and args.output:
        if args.export == "json":
            success = export_to_json(state, args.output)
        else:
            success = export_to_csv(state, args.output)
        
        if success:
            print(f"Exported to {args.output}")
            return 0
        else:
            return 1
    
    # Interactive mode
    if RICH_AVAILABLE:
        console = Console()
        render_dashboard_tui(state, console)
    else:
        render_dashboard_cli(state)
    
    # Play sound if enabled and there are alerts
    if args.sound:
        if state.mayday_alerts:
            play_alert_sound("mayday")
        if state.high_value_tips:
            play_alert_sound("high_value")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
