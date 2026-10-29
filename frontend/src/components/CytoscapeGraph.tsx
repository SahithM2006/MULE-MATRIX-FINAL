import React, { useEffect, useRef } from 'react';
import cytoscape, { Core, EventObject } from 'cytoscape';
import { GraphNode, GraphEdge } from '../types';
import { ZoomIn, ZoomOut, Maximize2, RefreshCw } from 'lucide-react';

interface CytoscapeGraphProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  startAccountId?: string;
  onSelectNode?: (node: GraphNode) => void;
  onSelectEdge?: (edge: GraphEdge) => void;
  height?: string;
}

export const CytoscapeGraph: React.FC<CytoscapeGraphProps> = ({
  nodes,
  edges,
  startAccountId,
  onSelectNode,
  onSelectEdge,
  height = '600px'
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Build Cytoscape elements
    const elements: any[] = [];

    nodes.forEach((n) => {
      let bg = '#2A2E39'; // standard
      let borderColor = '#4A5060';
      let shape = 'ellipse';

      if (n.is_start || n.id === startAccountId) {
        bg = '#C6A45A'; // Muted Gold
        borderColor = '#FFFFFF';
        shape = 'diamond';
      } else if (n.is_offramp || n.account_type === 'CRYPTO_OFFRAMP') {
        bg = '#A63D40'; // Muted Burgundy
        borderColor = '#C83232';
        shape = 'hexagon';
      } else if (n.risk_score >= 50.0 || n.risk_tier === 'CRITICAL' || n.risk_tier === 'HIGH') {
        bg = '#C83232'; // Critical Red
        borderColor = '#FFA0A0';
      } else if (n.account_type === 'MERCHANT') {
        bg = '#3B6E8C'; // Steel Teal
        shape = 'round-rectangle';
      } else if (n.account_type === 'CORPORATE') {
        bg = '#5A6375';
        shape = 'rectangle';
      }

      elements.push({
        group: 'nodes',
        data: {
          id: n.id,
          label: `${n.account_number}\n${n.holder_name.split(' ')[0]}`,
          rawNode: n
        },
        style: {
          'background-color': bg,
          'border-color': borderColor,
          'border-width': n.is_start ? 3 : 1.5,
          'shape': shape,
          'width': n.is_start ? 50 : 38,
          'height': n.is_start ? 50 : 38,
          'label': `${n.account_number}\n${n.holder_name.split(' ')[0]}`,
          'color': '#EAEAEA',
          'font-size': '10px',
          'font-family': 'monospace',
          'text-valign': 'bottom',
          'text-margin-y': 6,
          'text-wrap': 'wrap',
          'text-max-width': '90px'
        }
      });
    });

    edges.forEach((e) => {
      const formattedAmount = e.amount >= 100000
        ? `₹${(e.amount / 100000).toFixed(1)}L`
        : `₹${(e.amount / 1000).toFixed(0)}k`;

      elements.push({
        group: 'edges',
        data: {
          id: e.id,
          source: e.source,
          target: e.target,
          label: formattedAmount,
          rawEdge: e
        },
        style: {
          'width': Math.min(6, Math.max(1.5, Math.log10(e.amount + 1) * 0.8)),
          'line-color': e.has_lineage ? '#C6A45A' : '#7596C8',
          'target-arrow-color': e.has_lineage ? '#C6A45A' : '#7596C8',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'line-style': e.has_lineage ? 'dashed' : 'solid',
          'label': formattedAmount,
          'font-size': '9px',
          'font-family': 'monospace',
          'color': '#A0AEC0',
          'text-rotation': 'autorotate',
          'text-margin-y': -8
        }
      });
    });

    // Initialize Cytoscape
    const cy = cytoscape({
      container: containerRef.current,
      elements: elements,
      style: [
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#FFFFFF'
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'width': 4,
            'line-color': '#FFFFFF',
            'target-arrow-color': '#FFFFFF'
          }
        }
      ],
      layout: {
        name: 'breadthfirst',
        directed: true,
        padding: 40,
        spacingFactor: 1.25,
        roots: startAccountId ? [`#${startAccountId}`] : undefined
      }
    });

    cy.on('tap', 'node', (evt: EventObject) => {
      const rawNode = evt.target.data('rawNode');
      if (rawNode && onSelectNode) {
        onSelectNode(rawNode);
      }
    });

    cy.on('tap', 'edge', (evt: EventObject) => {
      const rawEdge = evt.target.data('rawEdge');
      if (rawEdge && onSelectEdge) {
        onSelectEdge(rawEdge);
      }
    });

    cyRef.current = cy;

    return () => {
      cy.destroy();
    };
  }, [nodes, edges, startAccountId]);

  const handleZoomIn = () => cyRef.current?.zoom(cyRef.current.zoom() * 1.25);
  const handleZoomOut = () => cyRef.current?.zoom(cyRef.current.zoom() * 0.8);
  const handleFit = () => cyRef.current?.fit(undefined, 30);
  const handleResetLayout = () => {
    cyRef.current?.layout({
      name: 'breadthfirst',
      directed: true,
      padding: 40,
      spacingFactor: 1.25
    }).run();
  };

  return (
    <div className="relative w-full rounded-md border border-[#252A34] overflow-hidden bg-[#0F1117]">
      {/* Canvas */}
      <div ref={containerRef} style={{ height }} className="w-full graph-dark-grid cursor-grab active:cursor-grabbing" />

      {/* Floating Tactical Controls */}
      <div className="absolute top-4 right-4 flex items-center space-x-1.5 bg-[#171A23]/90 backdrop-blur border border-[#2E3440] p-1.5 rounded shadow-lg text-white">
        <button
          onClick={handleZoomIn}
          title="Zoom In"
          className="p-1.5 hover:bg-[#252A36] rounded text-[#E0E0E0] hover:text-white transition"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={handleZoomOut}
          title="Zoom Out"
          className="p-1.5 hover:bg-[#252A36] rounded text-[#E0E0E0] hover:text-white transition"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <div className="w-[1px] h-4 bg-[#2E3440] my-auto" />
        <button
          onClick={handleFit}
          title="Fit to View"
          className="p-1.5 hover:bg-[#252A36] rounded text-[#E0E0E0] hover:text-white transition"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
        <button
          onClick={handleResetLayout}
          title="Re-layout"
          className="p-1.5 hover:bg-[#252A36] rounded text-[#E0E0E0] hover:text-white transition"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Graph Legend Overlay */}
      <div className="absolute bottom-3 left-4 flex flex-wrap gap-4 text-[11px] font-mono bg-[#141720]/80 backdrop-blur px-3 py-1.5 rounded border border-[#252A34] text-[#A0AEC0]">
        <span className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 bg-[#C6A45A] rotate-45 inline-block" />
          <span>Root / Focus</span>
        </span>
        <span className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 bg-[#C83232] rounded-full inline-block" />
          <span>High Risk Mule</span>
        </span>
        <span className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 bg-[#A63D40] inline-block" />
          <span>Terminal Off-Ramp</span>
        </span>
        <span className="flex items-center space-x-1.5">
          <span className="w-2.5 h-2.5 bg-[#2A2E39] rounded-full inline-block border border-[#4A5060]" />
          <span>Intermediary Rail</span>
        </span>
        <span className="flex items-center space-x-1.5">
          <span className="w-4 h-0 border-t border-dashed border-[#C6A45A] inline-block" />
          <span>e₹ Token Lineage</span>
        </span>
      </div>
    </div>
  );
};
