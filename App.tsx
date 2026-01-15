import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import SQLEditor from './components/SQLEditor';
import TableDesigner from './components/TableDesigner';
import SchemaVisualizer from './components/SchemaVisualizer';
import TableDataViewer from './components/TableDataViewer';
import RecruiterInfoModal from './components/RecruiterInfoModal';
import { MockDatabase } from './services/DatabaseEngine';
import { DatabaseState, TabItem } from './types';
import { X, Code2, PenTool, GitGraph, Database as DbIcon, Sun, Moon, Table as TableIcon } from 'lucide-react';

const dbEngine = new MockDatabase();

function App() {
  const [dbState, setDbState] = useState<DatabaseState>(dbEngine.getDatabaseState());
  const [tabs, setTabs] = useState<TabItem[]>([
    { id: '1', type: 'sql', title: 'SQL Query 1', active: true },
    { id: '2', type: 'schema', title: 'Schema Diagram', active: false }
  ]);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [queryHistory, setQueryHistory] = useState<string[]>([]);
  const [showRecruiterInfo, setShowRecruiterInfo] = useState(false);

  // Apply dark mode class to html
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const refreshState = () => {
      const state = dbEngine.getDatabaseState();
      // Ensure we trigger a re-render by creating a new reference for the tables array
      setDbState({ 
          name: state.name,
          tables: [...state.tables] 
      });
  };

  const activeTab = tabs.find(t => t.active);

  const activateTab = (id: string) => {
    setTabs(tabs.map(t => ({ ...t, active: t.id === id })));
  };

  const closeTab = (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    const remaining = tabs.filter(t => t.id !== id);
    if (remaining.length === 0) {
        // Always keep one
        setTabs([{ id: 'new', type: 'sql', title: 'New Query', active: true }]);
    } else {
        if (id === activeTab?.id) {
            remaining[remaining.length - 1].active = true;
        }
        setTabs(remaining);
    }
  };

  const addTab = (type: TabItem['type'], title: string, data?: any) => {
    const newId = Math.random().toString(36).substr(2, 9);
    setTabs([...tabs.map(t => ({...t, active: false})), { id: newId, type, title, active: true, data }]);
  };

  const handleExecuteQuery = async (query: string) => {
      setQueryHistory(prev => [query, ...prev].slice(0, 20));
      const result = await dbEngine.executeSQL(query);
      if(result.success && !result.data) {
          // It was a command like INSERT/UPDATE/DROP, refresh state
          refreshState();
      }
      return result;
  };

  const handleSaveTable = (tableSchema: any, oldName?: string) => {
      try {
          if (oldName) {
            dbEngine.updateTable(oldName, tableSchema);
          } else {
            dbEngine.createTable(tableSchema);
          }
          refreshState();
          // Switch to query to verify
          addTab('sql', 'Query', `SELECT * FROM ${tableSchema.name}`);
      } catch (e: any) {
          alert(e.message);
      }
  };

  const handleDropTable = async (tableName: string) => {
      if(confirm(`Are you sure you want to drop table '${tableName}'?`)) {
          await dbEngine.executeSQL(`DROP TABLE ${tableName}`);
          refreshState();
      }
  };

  const handleTogglePK = (tableName: string, columnName: string) => {
      dbEngine.togglePrimaryKey(tableName, columnName);
      refreshState();
  };

  const handleCreateDatabase = () => {
    const name = prompt("Enter new database name:");
    if (name) {
      try {
        dbEngine.createDatabase(name);
        refreshState();
        setTabs([{ id: 'new', type: 'sql', title: 'New Query', active: true }]); // Reset tabs for new DB
      } catch (e: any) {
        alert(e.message);
      }
    }
  };

  const handleOpenSchema = () => {
      const existing = tabs.find(t => t.type === 'schema');
      if (existing) {
          activateTab(existing.id);
      } else {
          addTab('schema', 'Schema Diagram');
      }
  };
  
  const handleEditTable = (tableName: string) => {
      const table = dbState.tables.find(t => t.name === tableName);
      if (!table) return;
      addTab('designer', `Edit: ${tableName}`, table);
  };

  const handleScriptTable = (tableName: string) => {
      addTab('sql', `Select ${tableName}`, `SELECT * FROM ${tableName} LIMIT 1000;`);
  };

  const handleResetDemo = () => {
      dbEngine.resetDatabase();
      refreshState();
      // Reset tabs to default state
      setTabs([
        { id: '1', type: 'sql', title: 'SQL Query 1', active: true },
        { id: '2', type: 'schema', title: 'Schema Diagram', active: false }
      ]);
  };

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans transition-colors duration-200">
      <RecruiterInfoModal 
        isOpen={showRecruiterInfo} 
        onClose={() => setShowRecruiterInfo(false)} 
        onResetDemo={handleResetDemo}
      />

      {/* Sidebar */}
      <Sidebar 
        dbState={dbState} 
        onSelectTable={(name) => addTab('table-data', name, name)}
        onDropTable={handleDropTable}
        onCreateTable={() => addTab('designer', 'New Table')}
        onCreateDatabase={handleCreateDatabase}
        onOpenSchema={handleOpenSchema}
        onScriptTable={handleScriptTable}
        onEditTable={handleEditTable}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 bg-white dark:bg-slate-900 transition-colors duration-200">
        
        {/* Top Header */}
        <header className="h-12 bg-white dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 flex items-center px-4 justify-between shrink-0 transition-colors duration-200">
            <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400 text-sm">
                <DbIcon className="h-4 w-4 text-blue-500" />
                <span className="font-semibold text-slate-700 dark:text-slate-200">{dbState.name}</span>
                <span className="bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 text-xs px-2 py-0.5 rounded-full border border-green-200 dark:border-green-800">Connected</span>
            </div>
            
            <div className="flex items-center gap-4">
                <button 
                  onClick={() => setIsDarkMode(!isDarkMode)}
                  className="p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition-colors"
                >
                    {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </button>
                <div 
                    onClick={() => setShowRecruiterInfo(true)}
                    className="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-xs font-bold text-white cursor-pointer shadow-lg hover:shadow-blue-500/30 transition-shadow ring-2 ring-transparent hover:ring-blue-400"
                    title="View Submission Info & Demo Data"
                >
                    PS
                </div>
            </div>
        </header>

        {/* Tab Bar */}
        <div className="flex items-center bg-slate-100 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800 overflow-x-auto transition-colors duration-200">
            {tabs.map(tab => (
                <div 
                    key={tab.id}
                    onClick={() => activateTab(tab.id)}
                    className={`
                        group flex items-center gap-2 px-4 py-2 text-sm border-r border-slate-200 dark:border-slate-800 cursor-pointer select-none min-w-[150px] max-w-[200px] transition-colors duration-200
                        ${tab.active 
                            ? 'bg-white dark:bg-slate-900 text-blue-600 dark:text-blue-400 border-t-2 border-t-blue-500' 
                            : 'bg-slate-50 dark:bg-slate-950 text-slate-500 dark:text-slate-500 hover:bg-slate-200 dark:hover:bg-slate-900/50 hover:text-slate-700 dark:hover:text-slate-300'
                        }
                    `}
                >
                    {tab.type === 'sql' && <Code2 className="h-3 w-3 shrink-0" />}
                    {tab.type === 'designer' && <PenTool className="h-3 w-3 shrink-0" />}
                    {tab.type === 'schema' && <GitGraph className="h-3 w-3 shrink-0" />}
                    {tab.type === 'table-data' && <TableIcon className="h-3 w-3 shrink-0" />}
                    <span className="truncate flex-1">{tab.title}</span>
                    <button 
                        onClick={(e) => closeTab(e, tab.id)}
                        className="opacity-0 group-hover:opacity-100 p-0.5 hover:bg-slate-200 dark:hover:bg-slate-800 rounded text-slate-500 hover:text-red-500 transition-all"
                    >
                        <X className="h-3 w-3" />
                    </button>
                </div>
            ))}
             <button 
                onClick={() => addTab('sql', 'New Query')} 
                className="px-3 text-slate-500 hover:text-blue-500 hover:bg-slate-200 dark:hover:bg-slate-800 h-full transition-colors duration-200"
                title="New Tab"
            >
                +
            </button>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-hidden relative">
            {activeTab && (
                <>
                    {activeTab.type === 'sql' && (
                        <SQLEditor 
                            key={activeTab.id} 
                            initialQuery={typeof activeTab.data === 'string' && activeTab.data.startsWith('SELECT') ? activeTab.data : undefined}
                            onExecute={handleExecuteQuery}
                            history={queryHistory}
                        />
                    )}
                    {activeTab.type === 'designer' && (
                        <TableDesigner 
                            onSave={handleSaveTable} 
                            initialData={typeof activeTab.data === 'object' ? activeTab.data : undefined}
                        />
                    )}
                    {activeTab.type === 'schema' && (
                        <SchemaVisualizer 
                          dbState={dbState} 
                          onTogglePK={handleTogglePK}
                          onEditTable={handleEditTable}
                          isDarkMode={isDarkMode}
                        />
                    )}
                    {activeTab.type === 'table-data' && (
                        <TableDataViewer 
                            key={activeTab.id + activeTab.data} // force re-mount if data changes
                            tableName={activeTab.data}
                            dbEngine={dbEngine}
                        />
                    )}
                </>
            )}
        </div>
      </div>
    </div>
  );
}

export default App;