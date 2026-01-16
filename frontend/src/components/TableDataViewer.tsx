import React, { useState, useEffect } from 'react';
import { LogEntry, QueryResult, TableSchema } from '../types';
import ConsolePanel from './ConsolePanel';
import { Save, RefreshCw, AlertCircle, X, Check, Trash2 } from 'lucide-react';

interface TableDataViewerProps {
  tableName: string;
  dbEngine: any; // Using any to avoid strict type coupling with MockDatabase for props
}

const TableDataViewer: React.FC<TableDataViewerProps> = ({ tableName, dbEngine }) => {
  const [data, setData] = useState<any[]>([]);
  const [columns, setColumns] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [consoleHeight, setConsoleHeight] = useState(200);
  const [editingCell, setEditingCell] = useState<{rowIndex: number, colName: string} | null>(null);
  const [editValue, setEditValue] = useState("");

  // Staging state
  const [pendingChanges, setPendingChanges] = useState<Record<string, any>>({}); // Key: "rowIndex-colName"
  const [originalDataLength, setOriginalDataLength] = useState(0);

  const loadData = async () => {
    setLoading(true);
    try {
      // Direct query execution to get fresh data
      const result = await dbEngine.executeSQL(`SELECT * FROM ${tableName}`);
      if (result.success && result.data) {
        setData(result.data);
        setColumns(result.columns || []);
        setOriginalDataLength(result.data.length);
        setPendingChanges({}); // Clear pending on reload
        addLog('success', `Loaded ${result.data.length} rows from ${tableName}`);
      } else {
        addLog('error', result.message || "Failed to load data");
      }
    } catch (e: any) {
      addLog('error', e.message);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, [tableName]);

  const addLog = (type: 'info' | 'success' | 'error', message: string, details?: string) => {
    setLogs(prev => [...prev, {
      timestamp: new Date().toLocaleTimeString(),
      type,
      message,
      details
    }]);
  };

  const getCellKey = (rowIndex: number, colName: string) => `${rowIndex}-${colName}`;

  const handleCellClick = (rowIndex: number, colName: string, currentValue: any) => {
    // If already pending, use that value for edit input
    const key = getCellKey(rowIndex, colName);
    const displayValue = pendingChanges[key] !== undefined ? pendingChanges[key] : currentValue;
    
    setEditingCell({ rowIndex, colName });
    setEditValue(String(displayValue));
  };

  const handleStageChange = () => {
    if (!editingCell) return;
    
    const { rowIndex, colName } = editingCell;
    const key = getCellKey(rowIndex, colName);
    const originalValue = data[rowIndex][colName];

    // If matches original, remove from pending
    // Note: This string comparison is basic. In a real app, handle types strictly.
    if (String(originalValue) === editValue) {
        const newPending = { ...pendingChanges };
        delete newPending[key];
        setPendingChanges(newPending);
    } else {
        setPendingChanges(prev => ({
            ...prev,
            [key]: editValue
        }));
    }
    setEditingCell(null);
  };

  const handleSaveChanges = async () => {
      setLoading(true);
      let successCount = 0;
      let errorCount = 0;

      // Group changes by row index
      const changesByRow: Record<number, Record<string, any>> = {};
      Object.entries(pendingChanges).forEach(([key, value]) => {
          const [rIndexStr, colName] = key.split('-');
          const rowIndex = parseInt(rIndexStr);
          if (!changesByRow[rowIndex]) changesByRow[rowIndex] = {};
          changesByRow[rowIndex][colName] = value;
      });

      // Process each row
      for (const [rowIndexStr, rowChanges] of Object.entries(changesByRow)) {
          const rowIndex = parseInt(rowIndexStr);

          try {
              if (rowIndex >= originalDataLength) {
                  // New row - INSERT
                  const cols = Object.keys(rowChanges);
                  const vals = Object.values(rowChanges);
                  const query = `INSERT INTO ${tableName} (${cols.join(', ')}) VALUES (${vals.map(v => `'${v}'`).join(', ')})`;
                  const result = await dbEngine.executeSQL(query);
                  if (result.success) successCount++;
                  else errorCount++;
              } else {
                  // Existing row - UPDATE each changed cell
                  for (const [colName, value] of Object.entries(rowChanges)) {
                      const result = dbEngine.updateCell(tableName, rowIndex, colName, value);
                      if (result.success) successCount++;
                      else errorCount++;
                  }
              }
          } catch(e) {
              errorCount++;
          }
      }

      // Reload data to reflect committed changes
      await loadData();
      setLoading(false);

      if (errorCount > 0) {
          addLog('error', `Saved with errors`, `${successCount} success, ${errorCount} failed`);
      } else if (successCount > 0) {
          addLog('success', `Successfully saved ${successCount} changes`);
      }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
        handleStageChange();
    } else if (e.key === 'Escape') {
        setEditingCell(null);
    }
  };

  const handleAddNewRow = () => {
    const newRow: any = {};
    columns.forEach(col => {
      newRow[col] = null; // Start with null values
    });
    setData(prev => [...prev, newRow]);
    // Auto-edit the first column of the new row
    setTimeout(() => {
      handleCellClick(data.length, columns[0], null);
    }, 100);
  };

  const handleDeleteRow = async (rowIndex: number) => {
    if (rowIndex >= originalDataLength) {
      // New unsaved row - just remove from local data
      setData(prev => prev.filter((_, i) => i !== rowIndex));
      // Remove any pending changes for this row
      const newPendingChanges = { ...pendingChanges };
      Object.keys(newPendingChanges).forEach(key => {
        if (key.startsWith(`${rowIndex}-`)) {
          delete newPendingChanges[key];
        }
      });
      setPendingChanges(newPendingChanges);
      addLog('success', 'Row removed from pending changes');
      return;
    }

    // Existing row - delete from database
    try {
      // Find a unique identifier for this row (prefer primary key)
      const row = data[rowIndex];
      // For simplicity, we'll use the first column as identifier
      // In a real app, you'd want to use the primary key
      const firstCol = columns[0];
      const identifierValue = row[firstCol];

      const query = `DELETE FROM ${tableName} WHERE ${firstCol} = '${identifierValue}'`;
      const result = await dbEngine.executeSQL(query);

      if (result.success) {
        addLog('success', `Row deleted successfully`);
        await loadData(); // Refresh data
      } else {
        addLog('error', result.message || 'Failed to delete row');
      }
    } catch (e: any) {
      addLog('error', e.message || 'Failed to delete row');
    }
  };

  const hasChanges = Object.keys(pendingChanges).length > 0;

  return (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900">
        {/* Toolbar */}
        <div className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 p-2 flex items-center justify-between min-h-[50px]">
            <h2 className="text-sm font-bold text-slate-700 dark:text-slate-200 px-2 flex items-center gap-2">
                Table: {tableName}
                {loading && <RefreshCw className="h-3 w-3 animate-spin text-slate-400" />}
            </h2>
            <div className="flex gap-3 items-center">
                {hasChanges && (
                    <div className="flex items-center gap-2 animate-in fade-in duration-200">
                        <span className="text-xs text-amber-600 dark:text-amber-400 font-medium">
                            {Object.keys(pendingChanges).length} pending change(s)
                        </span>
                        <button 
                            onClick={handleSaveChanges}
                            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded shadow-sm text-xs font-medium transition-all"
                        >
                            <Save className="h-3 w-3" /> Save Changes
                        </button>
                        <button 
                            onClick={() => setPendingChanges({})}
                            className="flex items-center gap-1 text-slate-500 hover:text-red-500 hover:bg-slate-100 dark:hover:bg-slate-700 px-2 py-1.5 rounded transition-colors text-xs"
                            title="Discard Changes"
                        >
                           <X className="h-3 w-3" /> Discard
                        </button>
                        <div className="w-px h-4 bg-slate-300 dark:bg-slate-600 mx-1" />
                    </div>
                )}
                <button 
                  onClick={loadData}
                  className="p-1.5 text-slate-500 hover:text-blue-500 hover:bg-slate-100 dark:hover:bg-slate-700 rounded transition-colors"
                  title="Refresh Data"
                >
                    <RefreshCw className="h-4 w-4" />
                </button>
            </div>
        </div>

        {/* Data Grid */}
        <div className="flex-1 overflow-auto bg-white dark:bg-slate-900 min-h-0 relative">
            <table className="w-full text-left border-collapse text-sm">
                <thead className="bg-slate-100 dark:bg-slate-800 sticky top-0 z-10 shadow-sm">
                    <tr>
                        <th className="p-2 border-b border-r border-slate-200 dark:border-slate-700 w-10 text-center text-slate-400 font-normal">#</th>
                        {columns.map(col => (
                            <th key={col} className="p-2 border-b border-r border-slate-200 dark:border-slate-700 font-semibold text-slate-600 dark:text-slate-300 min-w-[120px]">
                                {col}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, rIndex) => (
                        <tr key={rIndex} className="hover:bg-blue-50 dark:hover:bg-slate-800/50 group relative">
                            <td className="p-2 border-r border-b border-slate-100 dark:border-slate-800 text-slate-400 text-xs text-center select-none bg-slate-50 dark:bg-slate-900 relative">
                                {rIndex + 1}
                                {/* Delete button - visible on row hover */}
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleDeleteRow(rIndex);
                                    }}
                                    className="absolute right-1 top-1/2 transform -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity p-1 text-red-500 hover:text-red-700 hover:bg-red-50 dark:hover:bg-red-900/20 rounded"
                                    title="Delete row"
                                >
                                    <Trash2 className="h-3 w-3" />
                                </button>
                            </td>
                            {columns.map(col => {
                                const isEditing = editingCell?.rowIndex === rIndex && editingCell?.colName === col;
                                const changeKey = getCellKey(rIndex, col);
                                const isPending = pendingChanges[changeKey] !== undefined;
                                const displayValue = isPending ? pendingChanges[changeKey] : row[col];

                                return (
                                    <td 
                                        key={col} 
                                        className={`
                                            border-r border-b border-slate-100 dark:border-slate-800 font-mono text-xs cursor-text relative p-0
                                            ${isPending ? 'bg-amber-50 dark:bg-amber-900/20 text-amber-700 dark:text-amber-300' : 'text-slate-700 dark:text-slate-400'}
                                        `}
                                        onClick={() => !isEditing && handleCellClick(rIndex, col, row[col])}
                                    >
                                        {isEditing ? (
                                            <input
                                                autoFocus
                                                aria-label={`Edit ${col} for row ${rIndex + 1}`}
                                                className="w-full h-full p-2 bg-white dark:bg-slate-800 outline-none text-blue-600 dark:text-blue-400 absolute inset-0 z-20 shadow-inner border border-blue-500"
                                                value={editValue}
                                                onChange={(e) => setEditValue(e.target.value)}
                                                onBlur={handleStageChange}
                                                onKeyDown={handleKeyDown}
                                            />
                                        ) : (
                                            <div className="p-2 w-full h-full min-h-[32px] whitespace-nowrap overflow-hidden text-ellipsis flex items-center justify-between">
                                                 <span>
                                                   {displayValue !== null && displayValue !== undefined ?
                                                     (typeof displayValue === 'boolean' ? (displayValue ? 'TRUE' : 'FALSE') : String(displayValue)) :
                                                    displayValue === null ? <span className="text-slate-300 italic">NULL</span> :
                                                    <span className="text-slate-400 italic">undefined</span>}
                                                 </span>
                                                 {isPending && <div className="w-1.5 h-1.5 rounded-full bg-amber-500 mr-1" />}
                                            </div>
                                        )}
                                    </td>
                                );
                            })}
                        </tr>
                    ))}
                    {data.length === 0 && !loading && (
                        <tr>
                            <td colSpan={columns.length + 1} className="p-8 text-center text-slate-400">
                                <div className="space-y-3">
                                    <div>No data found in table.</div>
                                    <button
                                        onClick={handleAddNewRow}
                                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm transition-colors shadow-sm"
                                    >
                                        Add First Row
                                    </button>
                                </div>
                            </td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>

        {/* Resizable Console */}
        <ConsolePanel 
            logs={logs} 
            onClear={() => setLogs([])}
            height={consoleHeight}
            onHeightChange={setConsoleHeight}
        />
    </div>
  );
};

export default TableDataViewer;
