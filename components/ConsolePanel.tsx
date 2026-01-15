import React, { useRef, useEffect, useState } from 'react';
import { Terminal } from 'lucide-react';
import { LogEntry } from '../types';

interface ConsolePanelProps {
  logs: LogEntry[];
  onClear: () => void;
  height: number;
  onHeightChange: (h: number) => void;
}

const ConsolePanel: React.FC<ConsolePanelProps> = ({ logs, onClear, height, onHeightChange }) => {
  const logsEndRef = useRef<HTMLDivElement>(null);
  const [isDragging, setIsDragging] = useState(false);

  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDragging) {
        const newHeight = window.innerHeight - e.clientY;
        // Limit constraints
        if (newHeight > 50 && newHeight < window.innerHeight - 100) {
            onHeightChange(newHeight);
        }
      }
    };
    
    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, onHeightChange]);

  return (
    <div className="flex flex-col border-t border-slate-200 dark:border-slate-700 bg-slate-950 text-slate-300 font-mono text-xs shrink-0" style={{ height: height }}>
      {/* Resizer Handle */}
      <div 
        className="h-1 bg-slate-700 hover:bg-blue-500 cursor-ns-resize flex items-center justify-center transition-colors"
        onMouseDown={() => setIsDragging(true)}
      >
        <div className="w-8 h-0.5 bg-slate-500 rounded-full" />
      </div>

      {/* Header */}
      <div className="flex items-center justify-between p-2 sticky top-0 bg-slate-950/90 border-b border-slate-800">
        <div className="flex items-center gap-2 text-slate-500 uppercase font-bold tracking-wider text-[10px]">
          <Terminal className="h-3 w-3" /> Console Output
        </div>
        <button onClick={onClear} className="text-[10px] text-slate-500 hover:text-slate-300">Clear</button>
      </div>

      {/* Content */}
      <div className="overflow-y-auto p-2 flex-1">
        {logs.length === 0 && <span className="text-slate-600 italic block p-2">Ready...</span>}
        {logs.map((log, i) => (
          <div key={i} className="mb-1.5 border-b border-slate-800/50 pb-1 last:border-0">
            <div className="flex items-center gap-2">
              <span className="text-slate-600">[{log.timestamp}]</span>
              <span className={log.type === 'error' ? 'text-red-500 font-bold' : 'text-green-500 font-bold'}>
                {log.type === 'error' ? 'ERROR' : 'SUCCESS'}
              </span>
              <span className="text-slate-300">{log.message}</span>
            </div>
            {log.details && <div className="text-slate-500 ml-[8.5rem] mt-0.5">{log.details}</div>}
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>
    </div>
  );
};

export default ConsolePanel;
