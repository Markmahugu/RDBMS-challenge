import React, { useState, useEffect, useRef } from 'react';
import { Play, RotateCw, Save, Eraser, Download, Clock } from 'lucide-react';
import { QueryResult, LogEntry } from '../types';
import ConsolePanel from './ConsolePanel';

interface SQLEditorProps {
  initialQuery?: string;
  onExecute: (query: string) => Promise<QueryResult>;
  history: string[];
}

const SQLEditor: React.FC<SQLEditorProps> = ({ initialQuery, onExecute, history }) => {
  const [query, setQuery] = useState(initialQuery || `CREATE DATABASE IF NOT EXISTS my_company;

-- 1. Create the Department table
CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(50)
);

-- 2. Create the Employees table
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    dept_id INT -- This is the 'Foreign Key' that links to the table above
);

-- 3. Insert data
INSERT INTO departments (dept_id, dept_name)
VALUES (101, 'Engineering'), (102, 'Marketing'), (103, 'HR');

INSERT INTO employees (emp_id, first_name, dept_id)
VALUES
    (1, 'Alice', 101),   -- Alice is in Engineering
    (2, 'Bob', 102),     -- Bob is in Marketing
    (3, 'Charlie', 101), -- Charlie is in Engineering
    (4, 'David', NULL);  -- David has no department assigned yet`);
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  
  // Layout state
  const [editorHeight, setEditorHeight] = useState(300);
  const [consoleHeight, setConsoleHeight] = useState(200);
  const [isDraggingEditor, setIsDraggingEditor] = useState(false);

  useEffect(() => {
    if (initialQuery) setQuery(initialQuery);
  }, [initialQuery]);

  // Handle Editor Resize
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isDraggingEditor) {
        // Calculate new height based on mouse Y relative to toolbar (approx 48px offset)
        const newHeight = e.clientY - 90; // Adjust for header + tabs + toolbar offset
        if (newHeight > 50 && newHeight < window.innerHeight - 200) {
            setEditorHeight(newHeight);
        }
      }
    };
    
    const handleMouseUp = () => {
      setIsDraggingEditor(false);
    };

    if (isDraggingEditor) {
      document.body.style.cursor = 'row-resize';
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.body.style.cursor = 'default';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'default';
    };
  }, [isDraggingEditor]);

  const handleExecute = async () => {
    if (!query.trim()) return;
    
    // Auto-layout: Optimize space for results on execution
    // If editor is very tall, shrink it.
    if (editorHeight > 250) setEditorHeight(250);
    // If console is very tall, shrink it to show results.
    if (consoleHeight > 150) setConsoleHeight(150);

    setIsExecuting(true);
    const res = await onExecute(query);
    setResult(res);
    setIsExecuting(false);

    const log: LogEntry = {
      timestamp: new Date().toLocaleTimeString(),
      type: res.success ? 'success' : 'error',
      message: res.success ? 'Query Executed' : 'Execution Failed',
      details: res.message || (res.success && res.data ? `${res.data.length} rows returned in ${res.executionTime?.toFixed(2)}ms` : undefined)
    };
    setLogs(prev => [...prev, log]);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.ctrlKey && e.key === 'Enter') {
      handleExecute();
    }
  };

  const handleDownloadCSV = () => {
    if (!result || !result.success || !result.data || !result.columns) return;

    const csvContent = [
      result.columns.join(','), // Header row
      ...result.data.map(row =>
        result.columns!.map(col => {
          const value = row[col];
          // Escape commas and quotes in values
          const stringValue = value !== null ? String(value) : '';
          return stringValue.includes(',') || stringValue.includes('"')
            ? `"${stringValue.replace(/"/g, '""')}"`
            : stringValue;
        }).join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', 'query_results.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900 overflow-hidden">
      {/* Toolbar */}
      <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 p-2 flex items-center gap-2 shrink-0">
        <button 
          onClick={handleExecute}
          disabled={isExecuting}
          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded shadow-sm text-sm font-medium transition-colors disabled:opacity-50"
        >
          {isExecuting ? <RotateCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
          Run (Ctrl+Enter)
        </button>
        <div className="h-6 w-px bg-slate-300 dark:bg-slate-600 mx-2" />
        <button className="p-1.5 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded" title="Clear Editor">
          <Eraser className="h-4 w-4" onClick={() => setQuery('')} />
        </button>
        <button className="p-1.5 text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 rounded" title="Save Query">
          <Save className="h-4 w-4" />
        </button>
        <div className="flex-1" />
        <span className="text-xs text-slate-400">Mock DB Connection: Active</span>
      </div>

      {/* Editor Area */}
      <div style={{ height: editorHeight }} className="relative border-b border-slate-200 dark:border-slate-700 shrink-0">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          className="w-full h-full p-4 font-mono text-sm bg-slate-50 dark:bg-[#1e1e1e] text-slate-800 dark:text-slate-200 focus:outline-none resize-none"
          placeholder="Write your SQL query here..."
          spellCheck={false}
        />
      </div>

      {/* Resize Handle for Editor */}
      <div 
        className="h-1 bg-slate-200 dark:bg-slate-700 hover:bg-blue-500 cursor-row-resize flex items-center justify-center transition-colors shrink-0 z-10 hover:h-1.5"
        onMouseDown={() => setIsDraggingEditor(true)}
      >
      </div>

      {/* Results Area */}
      <div className="flex-1 overflow-hidden flex flex-col bg-white dark:bg-slate-900 min-h-0">
        <div className="flex-1 overflow-auto flex flex-col min-h-0">
          {result ? (
            <>
              <div className="p-2 bg-slate-100 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center text-xs shrink-0">
                <div className="flex items-center gap-4">
                  <span className={result.success ? "text-green-600 font-bold" : "text-red-500 font-bold"}>
                    {result.success ? "Success" : "Error"}
                  </span>
                  <span className="text-slate-500 flex items-center gap-1">
                    <Clock className="h-3 w-3" /> {result.executionTime?.toFixed(2)}ms
                  </span>
                  {result.data && (
                    <span className="text-slate-500">
                      {result.data.length} rows
                    </span>
                  )}
                </div>
                {result.success && <button onClick={handleDownloadCSV} className="flex items-center gap-1 text-blue-500 hover:text-blue-600"><Download className="h-3 w-3" /> CSV</button>}
              </div>

              {result.success ? (
                result.data && result.data.length > 0 ? (
                  <div className="overflow-auto flex-1">
                    <table className="w-full text-left border-collapse text-sm">
                      <thead className="bg-slate-50 dark:bg-slate-800 sticky top-0 shadow-sm z-10">
                        <tr>
                          {result.columns?.map(col => (
                            <th key={col} className="p-2 border-b border-r border-slate-200 dark:border-slate-700 font-semibold text-slate-600 dark:text-slate-300 min-w-[100px] bg-slate-50 dark:bg-slate-800">
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {result.data.map((row, i) => (
                          <tr key={i} className="hover:bg-blue-50 dark:hover:bg-slate-800/50 border-b border-slate-100 dark:border-slate-800">
                            {result.columns?.map(col => (
                              <td key={`${i}-${col}`} className="p-2 border-r border-slate-100 dark:border-slate-800 text-slate-700 dark:text-slate-400 font-mono text-xs whitespace-nowrap">
                                {row[col] !== null ? String(row[col]) : <span className="text-slate-400 italic">NULL</span>}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="p-8 text-center text-slate-400 flex-1 flex items-center justify-center">
                    {result.message || "No results returned."}
                  </div>
                )
              ) : (
                <div className="p-4 bg-red-50 dark:bg-red-900/10 text-red-600 dark:text-red-400 font-mono text-sm">
                  Error: {result.message}
                </div>
              )}
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-slate-400">
              <div className="bg-slate-100 dark:bg-slate-800 p-4 rounded-full mb-4">
                <Play className="h-8 w-8 text-slate-300 dark:text-slate-600" />
              </div>
              <p>Execute a query to see results</p>
            </div>
          )}
        </div>

        {/* Resizable Console */}
        <ConsolePanel 
            logs={logs} 
            onClear={() => setLogs([])} 
            height={consoleHeight}
            onHeightChange={setConsoleHeight}
        />
      </div>
    </div>
  );
};

export default SQLEditor;
