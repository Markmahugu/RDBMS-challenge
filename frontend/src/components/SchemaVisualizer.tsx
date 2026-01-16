import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import { DatabaseState } from '../types';
import { RefreshCw, ZoomIn, ZoomOut, Maximize2, Minimize2, Move, Pencil } from 'lucide-react';

interface SchemaVisualizerProps {
  dbState: DatabaseState;
  onTogglePK?: (tableName: string, columnName: string) => void;
  onEditTable?: (tableName: string) => void;
  onCreateRelationship?: (sourceTable: string, sourceColumn: string, targetTable: string, targetColumn: string) => void;
  isDarkMode: boolean;
}

const SchemaVisualizer: React.FC<SchemaVisualizerProps> = ({ dbState, onTogglePK, onEditTable, onCreateRelationship, isDarkMode }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Persist positions across re-renders
  const positions = useRef<Record<string, {x: number, y: number, fx?: number | null, fy?: number | null}>>({});

  // UI State
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const [transform, setTransform] = useState({ k: 1, x: 0, y: 0 });
  const d3Zoom = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);

  // Drag state for relationship creation
  const [dragState, setDragState] = useState<{
    isDragging: boolean;
    sourceTable: string;
    sourceColumn: string;
    sourceType: string;
    startX: number;
    startY: number;
  } | null>(null);

  // Helper to calculate intersection point between line and rectangle
  const getIntersection = (source: {x: number, y: number}, target: {x: number, y: number, width: number, height: number}) => {
     const dx = target.x - source.x;
     const dy = target.y - source.y;
     const angle = Math.atan2(dy, dx);
     
     // Target box dimensions relative to center
     const w = target.width / 2;
     const h = target.height / 2;
     
     // Calculate intersection with box
     // x = w or -w,  y = x * tan(angle)
     // y = h or -h,  x = y / tan(angle)
     
     const tan = Math.tan(angle);
     let ix, iy;
     
     if (Math.abs(w * tan) <= h) {
         // Intersects left or right side
         ix = dx > 0 ? w : -w;
         iy = ix * tan;
     } else {
         // Intersects top or bottom
         iy = dy > 0 ? h : -h;
         ix = iy / tan;
     }
     
     return { x: target.x + ix, y: target.y + iy };
  };

  const getLinkPath = (d: any) => {
     if (!d.source || !d.target) return "";
     
     // Note: In D3 force simulation, d.source/target are objects after initialization, 
     // but might be strings before. However, we call this inside runSimulation after creating simulation.
     // We rely on the simulation modifying the objects in place or the warmup logic.
     
     const sourceCenter = { x: d.source.x, y: d.source.y };
     const targetCenter = { x: d.target.x, y: d.target.y };
     
     const sourcePoint = getIntersection(targetCenter, { 
         x: d.source.x, 
         y: d.source.y, 
         width: d.source.width, 
         height: d.source.height 
     });
     
     const targetPoint = getIntersection(sourceCenter, { 
         x: d.target.x, 
         y: d.target.y, 
         width: d.target.width, 
         height: d.target.height 
     });
     
     return `M${sourcePoint.x},${sourcePoint.y} L${targetPoint.x},${targetPoint.y}`;
  };

  const runSimulation = useCallback((forceReset = false) => {
    if (!svgRef.current || !dbState.tables.length) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); 

    const width = containerRef.current?.clientWidth || 800;
    const height = containerRef.current?.clientHeight || 600;

    // --- Theme ---
    const colors = {
      bg: isDarkMode ? '#0f172a' : '#f8fafc', // slate-900 : slate-50
      grid: isDarkMode ? '#1e293b' : '#e2e8f0', // slate-800 : slate-200
      nodeBg: isDarkMode ? '#1e293b' : '#ffffff', // slate-800 : white
      nodeBorder: isDarkMode ? '#334155' : '#cbd5e1', // slate-600 : slate-300
      headerBg: isDarkMode ? '#0f172a' : '#f1f5f9', // slate-900 : slate-100
      headerText: isDarkMode ? '#f1f5f9' : '#1e293b', // slate-100 : slate-800
      text: isDarkMode ? '#94a3b8' : '#64748b', // slate-400 : slate-500
      link: isDarkMode ? '#64748b' : '#94a3b8', // slate-500 : slate-400
      linkHover: isDarkMode ? '#3b82f6' : '#2563eb', // blue-500 : blue-600
      pk: '#eab308', // yellow-500
      fk: '#8b5cf6'  // violet-500
    };

    // --- Data Setup ---
    const tableWidth = 200;
    const headerHeight = 40;
    const rowHeight = 24;

    const nodes = dbState.tables.map(t => {
      const isCollapsed = collapsed[t.name];
      const contentHeight = isCollapsed ? 0 : (t.columns.length * rowHeight) + 10; // +10 padding
      const boxHeight = headerHeight + contentHeight;
      
      const pos = positions.current[t.name];
      return { 
        id: t.name, 
        ...t, 
        height: boxHeight,
        width: tableWidth,
        collapsed: isCollapsed,
        x: pos?.x || (forceReset ? 0 : 0), 
        y: pos?.y || (forceReset ? 0 : 0),
        fx: forceReset ? null : pos?.fx,
        fy: forceReset ? null : pos?.fy
      };
    });

    const links: any[] = [];
    dbState.tables.forEach(table => {
      table.columns.forEach(col => {
        if (col.isForeignKey && col.references) {
           const targetTable = dbState.tables.find(t => t.id === col.references!.tableId)?.name;
           if (targetTable) {
             links.push({
               source: table.name,
               target: targetTable,
               sourceCol: col.name,
               targetCol: dbState.tables.find(t => t.name === targetTable)?.columns.find(c => c.id === col.references?.columnId)?.name,
               id: `${table.name}-${targetTable}`
             });
           }
        }
      });
    });

    // --- Grid ---
    const defs = svg.append("defs");
    const pattern = defs.append("pattern")
        .attr("id", "grid")
        .attr("width", 20)
        .attr("height", 20)
        .attr("patternUnits", "userSpaceOnUse");
    pattern.append("circle")
        .attr("cx", 1)
        .attr("cy", 1)
        .attr("r", 1)
        .style("fill", colors.grid);

    // Arrow Marker
    defs.append("marker")
        .attr("id", "arrow-end")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 8) // Tip at end of line
        .attr("refY", 0)
        .attr("markerWidth", 8)
        .attr("markerHeight", 8)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", colors.link);
    
    // Highlighted Arrow
    defs.append("marker")
        .attr("id", "arrow-end-active")
        .attr("viewBox", "0 -5 10 10")
        .attr("refX", 8) 
        .attr("refY", 0)
        .attr("markerWidth", 8)
        .attr("markerHeight", 8)
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M0,-5L10,0L0,5")
        .attr("fill", colors.linkHover);

    // Background
    svg.append("rect")
        .attr("width", "100%")
        .attr("height", "100%")
        .attr("fill", "url(#grid)");

    const g = svg.append("g");

    // --- Zoom ---
    const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.2, 4])
        .on("zoom", (event) => {
            g.attr("transform", event.transform);
            setTransform(event.transform);
        });
    d3Zoom.current = zoom;
    svg.call(zoom).on("dblclick.zoom", null); 
    
    // RESTORE ZOOM STATE
    if (!forceReset) {
        const currentTransform = d3.zoomTransform(svg.node()!);
        if (currentTransform.k !== 1 || currentTransform.x !== 0 || currentTransform.y !== 0) {
             g.attr("transform", currentTransform.toString());
        }
    }

    // --- Simulation ---
    const simulation = d3.forceSimulation(nodes as any)
      .force("link", d3.forceLink(links).id((d: any) => d.id).distance(250))
      .force("charge", d3.forceManyBody().strength(-1000))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius((d: any) => Math.max(d.width, d.height)/1.5));

    // Warmup if no positions saved
    if (Object.keys(positions.current).length === 0 || forceReset) {
        simulation.stop();
        simulation.tick(300);
        nodes.forEach((n: any) => {
             positions.current[n.name] = { x: n.x, y: n.y, fx: n.fx, fy: n.fy };
        });
        
        // Auto fit initial
        let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
        nodes.forEach((n: any) => {
            minX = Math.min(minX, n.x - tableWidth/2);
            maxX = Math.max(maxX, n.x + tableWidth/2);
            minY = Math.min(minY, n.y - n.height/2);
            maxY = Math.max(maxY, n.y + n.height/2);
        });
        
        const bW = maxX - minX;
        const bH = maxY - minY;
        const scale = Math.min(1.2, 0.8 / Math.max(bW/width, bH/height));
        const center = d3.zoomIdentity.translate(width/2, height/2).scale(scale).translate(-(minX+maxX)/2, -(minY+maxY)/2);
        svg.call(zoom.transform, center);
    }

    // --- Drawing ---

    // Links (Back)
    const linkGroup = g.append("g").attr("class", "links");
    const linkPath = linkGroup.selectAll("path")
        .data(links)
        .join("path")
        .attr("stroke", colors.link)
        .attr("stroke-width", 1.5)
        .attr("fill", "none")
        .attr("marker-end", "url(#arrow-end)")
        .attr("d", (d: any) => getLinkPath(d)) // Apply path initially
        .style("cursor", "pointer")
        .on("mouseenter", function(e, d: any) {
            d3.select(this)
                .attr("stroke", colors.linkHover)
                .attr("stroke-width", 2.5)
                .attr("marker-end", "url(#arrow-end-active)");
                
            // Highlight nodes
            d3.select(`#node-${d.source.id}`).select("rect").attr("stroke", colors.linkHover).attr("stroke-width", 2);
            d3.select(`#node-${d.target.id}`).select("rect").attr("stroke", colors.linkHover).attr("stroke-width", 2);
        })
        .on("mouseleave", function(e, d: any) {
             d3.select(this)
                .attr("stroke", colors.link)
                .attr("stroke-width", 1.5)
                .attr("marker-end", "url(#arrow-end)");
             
             d3.select(`#node-${d.source.id}`).select("rect").attr("stroke", colors.nodeBorder).attr("stroke-width", 1);
             d3.select(`#node-${d.target.id}`).select("rect").attr("stroke", colors.nodeBorder).attr("stroke-width", 1);
        });

    // Nodes
    const node = g.append("g")
        .selectAll(".node")
        .data(nodes)
        .join("g")
        .attr("class", "node")
        .attr("id", d => `node-${d.id}`)
        .attr("transform", d => `translate(${d.x},${d.y})`) // Apply pos initially
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended) as any);

    // Drop Shadow Filter
    const filter = defs.append("filter")
        .attr("id", "card-shadow")
        .attr("height", "150%");
    filter.append("feGaussianBlur").attr("in", "SourceAlpha").attr("stdDeviation", 3);
    filter.append("feOffset").attr("dx", 2).attr("dy", 3).attr("result", "offsetblur");
    filter.append("feComponentTransfer").append("feFuncA").attr("type", "linear").attr("slope", 0.3);
    const feMerge = filter.append("feMerge");
    feMerge.append("feMergeNode").attr("in", "offsetblur");
    feMerge.append("feMergeNode").attr("in", "SourceGraphic");

    // Card Body
    node.append("rect")
        .attr("width", d => d.width)
        .attr("height", d => d.height)
        .attr("x", d => -d.width / 2)
        .attr("y", d => -d.height / 2)
        .attr("rx", 6)
        .attr("ry", 6)
        .attr("fill", colors.nodeBg)
        .attr("stroke", colors.nodeBorder)
        .attr("stroke-width", 1)
        .style("filter", "url(#card-shadow)")
        .on("mouseenter", function() {
             d3.select(this).attr("stroke", colors.linkHover).attr("stroke-width", 1.5);
        })
        .on("mouseleave", function() {
             d3.select(this).attr("stroke", colors.nodeBorder).attr("stroke-width", 1);
        });

    // Header Background
    node.append("path")
        .attr("d", d => {
            const w = d.width;
            const h = headerHeight;
            const r = 6;
            // Top rounded rect only
            return `M${-w/2},${-d.height/2} a${r},${r} 0 0 1 ${r},-${r} h${w-2*r} a${r},${r} 0 0 1 ${r},${r} v${h} h-${w} z`;
        })
        .attr("fill", colors.headerBg)
        .style("cursor", "move");

    // Header Title
    node.append("text")
        .attr("x", d => -d.width/2 + 10)
        .attr("y", d => -d.height/2 + 25)
        .attr("font-weight", "bold")
        .attr("font-size", "13px")
        .attr("fill", colors.headerText)
        .style("pointer-events", "none")
        .text(d => d.name);

    // ACTION GROUP (Edit + Collapse)
    const actionGroup = node.append("g")
        .attr("transform", d => `translate(${d.width/2 - 45}, ${-d.height/2 + 12})`);

    // Edit Button
    const editBtn = actionGroup.append("g")
        .style("cursor", "pointer")
        .on("click", (e, d: any) => {
            e.stopPropagation();
            if (onEditTable) onEditTable(d.name);
        });
        
    editBtn.append("rect")
         .attr("width", 16).attr("height", 16).attr("fill", "transparent");
         
    editBtn.append("path")
        .attr("d", "M11.25 1.75a1.768 1.768 0 0 1 2.5 2.5l-9 9l-4.5 1l1 -4.5l9 -9z") // Pencil path
        .attr("transform", "scale(0.8) translate(2,2)")
        .attr("fill", "none")
        .attr("stroke", colors.text)
        .attr("stroke-width", 1.5);

    // Collapse Button
    const collapseBtn = actionGroup.append("g")
        .attr("transform", "translate(20, 0)")
        .style("cursor", "pointer")
        .on("click", (e, d: any) => {
             e.stopPropagation();
             // Just use toggleCollapse from component scope.
             toggleCollapse(d.id);
        });
        
    collapseBtn.append("rect")
        .attr("width", 16).attr("height", 16).attr("fill", "transparent");
        
    collapseBtn.append("path")
        .attr("d", (d: any) => d.collapsed 
             ? "M4,8 L12,8 M8,4 L8,12" // Plus
             : "M4,8 L12,8")           // Minus
        .attr("stroke", colors.text)
        .attr("stroke-width", 2);

    // Columns
    node.each(function(d: any) {
        if (d.collapsed) return;

        const el = d3.select(this);
        const startY = -d.height/2 + headerHeight + 5;

        d.columns.forEach((col: any, i: number) => {
            const y = startY + (i * rowHeight);
            const row = el.append("g")
                .attr("transform", `translate(${-d.width/2}, ${y})`)
                .style("cursor", col.isPrimaryKey && onCreateRelationship ? "grab" : "default");

            // Row Highlight on hover
            row.append("rect")
               .attr("width", d.width)
               .attr("height", rowHeight)
               .attr("fill", "transparent")
               .on("mouseenter", function() {
                   d3.select(this).attr("fill", isDarkMode ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.03)");
                   if (dragState && !col.isPrimaryKey && col.type === dragState.sourceType) {
                       d3.select(this).attr("fill", isDarkMode ? "rgba(34,197,94,0.2)" : "rgba(34,197,94,0.1)");
                   }
               })
               .on("mouseleave", function() {
                   d3.select(this).attr("fill", "transparent");
               });

            // Drag handlers for PK columns
            if (col.isPrimaryKey && onCreateRelationship) {
                row.call(d3.drag()
                    .on("start", function(event) {
                        setDragState({
                            isDragging: true,
                            sourceTable: d.name,
                            sourceColumn: col.name,
                            sourceType: col.type,
                            startX: event.x,
                            startY: event.y
                        });
                        d3.select(event.sourceEvent.target).style("cursor", "grabbing");
                    })
                    .on("drag", function(event) {
                        // Visual feedback could be added here
                    })
                    .on("end", function(event) {
                        if (dragState) {
                            setDragState(null);
                        }
                        d3.select(event.sourceEvent.target).style("cursor", "grab");
                    }) as any
                );
            }

            // Drop handlers for non-PK columns
            if (!col.isPrimaryKey && onCreateRelationship) {
                row.on("mouseup", function(event) {
                    if (dragState && dragState.isDragging && col.type === dragState.sourceType) {
                        // Check if relationship already exists
                        const existingRelationship = d.columns.some((c: any) =>
                            c.isForeignKey && c.references &&
                            c.references.tableId === dragState.sourceTable &&
                            dbState.tables.find(t => t.name === dragState.sourceTable)?.columns.find(c => c.name === dragState.sourceColumn)?.id === c.references.columnId
                        );

                        if (!existingRelationship) {
                            onCreateRelationship(
                                dragState.sourceTable,
                                dragState.sourceColumn,
                                d.name,
                                col.name
                            );
                        }
                    }
                    if (dragState) {
                        setDragState(null);
                    }
                });
            }

            // Icons
            if (col.isPrimaryKey) {
                row.append("path")
                   .attr("d", "M4.5,4h-2V3h2V1.5C4.5,0.7,5.2,0,6,0s1.5,0.7,1.5,1.5V3h2v1h-2v1.5c0,0.8-0.7,1.5-1.5,1.5S4.5,6.3,4.5,5.5V4z M6,5c0.3,0,0.5-0.2,0.5-0.5S6.3,4,6,4S5.5,4.2,5.5,4.5S5.7,5,6,5z")
                   .attr("transform", "translate(10, 8) scale(1.2)")
                   .attr("fill", colors.pk);
            } else if (col.isForeignKey) {
                row.append("circle").attr("cx", 14).attr("cy", 12).attr("r", 3).attr("fill", colors.fk);
            } else {
                 row.append("circle").attr("cx", 14).attr("cy", 12).attr("r", 2).attr("fill", colors.nodeBorder);
            }

            // Name
            row.append("text")
                .attr("x", 28)
                .attr("y", 16)
                .attr("font-size", "11px")
                .attr("fill", col.isPrimaryKey ? colors.headerText : colors.text)
                .attr("font-weight", col.isPrimaryKey ? "600" : "400")
                .text(col.name);

            // Type
            row.append("text")
                .attr("x", d.width - 10)
                .attr("y", 16)
                .attr("text-anchor", "end")
                .attr("font-size", "10px")
                .attr("fill", colors.text)
                .style("opacity", 0.7)
                .text(col.type.toLowerCase());
        });
    });

    // --- Tick Function ---
    simulation.on("tick", () => {
        linkPath.attr("d", (d: any) => getLinkPath(d));

        node.attr("transform", (d: any) => {
            positions.current[d.name] = { x: d.x, y: d.y, fx: d.fx, fy: d.fy };
            return `translate(${d.x},${d.y})`;
        });
    });

    // --- Drag Handlers ---
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
      d3.select(`#node-${d.id}`).raise();
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = event.x;
      d.fy = event.y;
      positions.current[d.name] = { x: d.x, y: d.y, fx: d.x, fy: d.y };
    }

  }, [dbState, collapsed, isDarkMode, dragState]);

  const toggleCollapse = (tableName: string) => {
    setCollapsed(prev => ({ ...prev, [tableName]: !prev[tableName] }));
  };

  const resetLayout = () => {
    positions.current = {};
    if (svgRef.current && d3Zoom.current) {
        // Reset zoom
        const svg = d3.select(svgRef.current);
        const width = containerRef.current?.clientWidth || 800;
        const height = containerRef.current?.clientHeight || 600;
        
        svg.transition().duration(750).call(
            d3Zoom.current.transform as any, 
            d3.zoomIdentity.translate(width/2, height/2).scale(1)
        );
        
        // Re-run simulation
        runSimulation(true);
    }
  };

  const handleZoomBtn = (factor: number) => {
     if (svgRef.current && d3Zoom.current) {
         d3.select(svgRef.current).transition().duration(300).call(d3Zoom.current.scaleBy as any, factor);
     }
  };

  // Run initial simulation
  useEffect(() => {
    runSimulation(false);
  }, [runSimulation]);


  return (
    <div className={`w-full h-full relative overflow-hidden ${isDarkMode ? 'bg-slate-900' : 'bg-slate-50'}`} ref={containerRef}>
      {/* Toolbar */}
      <div className="absolute top-4 left-4 flex flex-col gap-2 z-20">
        <div className={`flex flex-col rounded-lg shadow-lg border overflow-hidden ${isDarkMode ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
             <button onClick={() => handleZoomBtn(1.2)} className={`p-2 hover:bg-slate-100 dark:hover:bg-slate-700 border-b border-slate-200 dark:border-slate-700 ${isDarkMode ? 'text-slate-200' : 'text-slate-600'}`} title="Zoom In">
                <ZoomIn className="h-4 w-4" />
             </button>
             <button onClick={() => handleZoomBtn(0.8)} className={`p-2 hover:bg-slate-100 dark:hover:bg-slate-700 border-b border-slate-200 dark:border-slate-700 ${isDarkMode ? 'text-slate-200' : 'text-slate-600'}`} title="Zoom Out">
                <ZoomOut className="h-4 w-4" />
             </button>
             <button onClick={resetLayout} className={`p-2 hover:bg-slate-100 dark:hover:bg-slate-700 ${isDarkMode ? 'text-slate-200' : 'text-slate-600'}`} title="Reset Layout">
                <RefreshCw className="h-4 w-4" />
             </button>
        </div>
      </div>

      {/* Legend / Info */}
      <div className={`absolute bottom-4 right-4 p-4 rounded-lg shadow-lg border z-10 text-xs pointer-events-none ${isDarkMode ? 'bg-slate-800/90 border-slate-700 text-slate-300' : 'bg-white/90 border-slate-200 text-slate-600'}`}>
        <div className="flex items-center gap-2 mb-2 font-bold">
            <Move className="h-3 w-3" /> Interactive Schema
        </div>
        <div className="space-y-1.5">
            <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-yellow-500"></span> Primary Key</div>
            <div className="flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-violet-500"></span> Foreign Key</div>
            <div className="mt-2 text-[10px] opacity-70">
                • Scroll to Zoom<br/>
                • Drag to Rearrange<br/>
                • Drag PK to FK to create relationships<br/>
                • Hover relations to highlight
            </div>
        </div>
      </div>

      <svg ref={svgRef} className="w-full h-full cursor-move touch-none" />
    </div>
  );
};

export default SchemaVisualizer;
