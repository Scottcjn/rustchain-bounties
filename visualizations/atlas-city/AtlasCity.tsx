import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import './AtlasCity.css';

interface Agent {
  id: string;
  name: string;
  role: string;
  city: string;
  x: number;
  y: number;
  heartbeat: boolean;
  properties: number;
  valuation: number;
  connections: string[];
}

interface City {
  name: string;
  x: number;
  y: number;
  radius: number;
  color: string;
}

const mockAgents: Agent[] = [
  { id: '1', name: 'AlphaAgent', role: 'Explorer', city: 'TechHub', x: 200, y: 200, heartbeat: true, properties: 3, valuation: 1500, connections: ['2', '3'] },
  { id: '2', name: 'BetaBot', role: 'Trader', city: 'TechHub', x: 250, y: 180, heartbeat: true, properties: 5, valuation: 3200, connections: ['1', '4'] },
  { id: '3', name: 'GammaGuard', role: 'Sentinel', city: 'Defense', x: 400, y: 300, heartbeat: false, properties: 2, valuation: 800, connections: ['1'] },
  { id: '4', name: 'DeltaDev', role: 'Builder', city: 'Innovation', x: 300, y: 400, heartbeat: true, properties: 8, valuation: 5600, connections: ['2', '5'] },
  { id: '5', name: 'EpsilonEye', role: 'Observer', city: 'Innovation', x: 350, y: 420, heartbeat: true, properties: 1, valuation: 400, connections: ['4'] },
  { id: '6', name: 'ZetaZen', role: 'Mediator', city: 'Defense', x: 450, y: 280, heartbeat: true, properties: 4, valuation: 2100, connections: ['3'] },
];

const mockCities: City[] = [
  { name: 'TechHub', x: 225, y: 190, radius: 80, color: '#4facfe' },
  { name: 'Defense', x: 425, y: 290, radius: 70, color: '#f093fb' },
  { name: 'Innovation', x: 325, y: 410, radius: 75, color: '#43e97b' },
];

export const AtlasCity: React.FC = () => {
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [filter, setFilter] = useState<string>('all');
  const [maydayActive, setMaydayActive] = useState<boolean>(false);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = 800;
    const height = 600;

    // Create city boundaries
    const cityGroups = svg.selectAll('.city')
      .data(mockCities)
      .enter()
      .append('g')
      .attr('class', 'city');

    cityGroups.append('circle')
      .attr('cx', d => d.x)
      .attr('cy', d => d.y)
      .attr('r', d => d.radius)
      .attr('fill', d => d.color)
      .attr('opacity', 0.2)
      .attr('stroke', d => d.color)
      .attr('stroke-width', 2);

    cityGroups.append('text')
      .attr('x', d => d.x)
      .attr('y', d => d.y - d.radius - 10)
      .attr('text-anchor', 'middle')
      .attr('fill', d => d.color)
      .attr('font-size', '16px')
      .attr('font-weight', 'bold')
      .text(d => d.name);

    // Draw connections
    const links: { source: Agent; target: Agent }[] = [];
    mockAgents.forEach(agent => {
      agent.connections.forEach(connId => {
        const target = mockAgents.find(a => a.id === connId);
        if (target) {
          links.push({ source: agent, target });
        }
      });
    });

    svg.selectAll('.link')
      .data(links)
      .enter()
      .append('line')
      .attr('class', 'link')
      .attr('x1', d => d.source.x)
      .attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x)
      .attr('y2', d => d.target.y)
      .attr('stroke', '#667eea')
      .attr('stroke-width', 2)
      .attr('opacity', 0.6);

    // Create agent nodes
    const agentGroups = svg.selectAll('.agent')
      .data(mockAgents)
      .enter()
      .append('g')
      .attr('class', 'agent')
      .attr('transform', d => `translate(${d.x}, ${d.y})`)
      .on('click', (event, d) => setSelectedAgent(d))
      .on('mouseover', function() {
        d3.select(this).select('circle').attr('r', 25);
      })
      .on('mouseout', function() {
        d3.select(this).select('circle').attr('r', 20);
      });

    // Agent circles
    agentGroups.append('circle')
      .attr('r', 20)
      .attr('fill', d => {
        if (!d.heartbeat) return '#ff4757';
        if (d.role === 'Explorer') return '#4facfe';
        if (d.role === 'Trader') return '#f093fb';
        if (d.role === 'Sentinel') return '#ff6b6b';
        if (d.role === 'Builder') return '#43e97b';
        return '#ffa502';
      })
      .attr('stroke', '#fff')
      .attr('stroke-width', 3)
      .style('cursor', 'pointer');

    // Agent labels
    agentGroups.append('text')
      .attr('dy', 35)
      .attr('text-anchor', 'middle')
      .attr('fill', '#fff')
      .attr('font-size', '12px')
      .text(d => d.name);

    // Heartbeat indicator
    agentGroups.filter(d => d.heartbeat)
      .append('circle')
      .attr('r', 5)
      .attr('cx', 12)
      .attr('cy', -12)
      .attr('fill', '#2ed573')
      .append('animate')
      .attr('attributeName', 'r')
      .attr('values', '5;8;5')
      .attr('dur', '1.5s')
      .attr('repeatCount', 'indefinite');

    // Mayday animation
    if (maydayActive) {
      svg.append('circle')
        .attr('cx', 400)
        .attr('cy', 300)
        .attr('r', 10)
        .attr('fill', 'none')
        .attr('stroke', '#ff4757')
        .attr('stroke-width', 3)
        .append('animate')
        .attr('attributeName', 'r')
        .attr('values', '10;100;10')
        .attr('dur', '2s')
        .attr('repeatCount', 'indefinite');
    }

  }, [filter, maydayActive]);

  return (
    <div className="atlas-container">
      <header className="atlas-header">
        <h1>🌍 Beacon Atlas City</h1>
        <div className="controls">
          <select value={filter} onChange={(e) => setFilter(e.target.value)}>
            <option value="all">All Cities</option>
            <option value="TechHub">TechHub</option>
            <option value="Defense">Defense</option>
            <option value="Innovation">Innovation</option>
          </select>
          <button onClick={() => setMaydayActive(!maydayActive)}>
            {maydayActive ? '🆘 Mayday OFF' : '🆘 Mayday ON'}
          </button>
        </div>
      </header>

      <div className="visualization">
        <svg ref={svgRef} width={800} height={600} className="city-svg"></svg>
        
        {selectedAgent && (
          <div className="agent-panel">
            <h3>{selectedAgent.name}</h3>
            <p><strong>Role:</strong> {selectedAgent.role}</p>
            <p><strong>City:</strong> {selectedAgent.city}</p>
            <p><strong>Status:</strong> {selectedAgent.heartbeat ? '❤️ Active' : '💔 Offline'}</p>
            <p><strong>Properties:</strong> {selectedAgent.properties}</p>
            <p><strong>Valuation:</strong> {selectedAgent.valuation} RTC</p>
            <p><strong>Connections:</strong> {selectedAgent.connections.length}</p>
            <button onClick={() => setSelectedAgent(null)}>Close</button>
          </div>
        )}
      </div>

      <div className="stats">
        <div className="stat-card">
          <span className="stat-value">{mockAgents.length}</span>
          <span className="stat-label">Total Agents</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{mockAgents.filter(a => a.heartbeat).length}</span>
          <span className="stat-label">Active</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{mockAgents.reduce((acc, a) => acc + a.valuation, 0)} RTC</span>
          <span className="stat-label">Total Value</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">{mockCities.length}</span>
          <span className="stat-label">Cities</span>
        </div>
      </div>
    </div>
  );
};