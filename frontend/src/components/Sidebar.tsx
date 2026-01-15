import React, { useState, useEffect, useRef } from 'react';
import { Database, Table as TableIcon, ChevronRight, ChevronDown, MoreVertical, Plus, Key, Hash, Search, GitGraph, FileCode, Trash2, Eye, Pencil, Edit } from 'lucide-react';
import { DatabaseState, TableSchema } from '../types';

interface SidebarProps {
  dbState: DatabaseState;
  databases: string[];
  onSelectTable: (tableName: string) => void;
  onDropTable: (tableName: string) => void;
  onCreateTable: () => void;
  onCreateDatabase: () => void;
  onSwitchDatabase: (dbName: string) => void;
  onOpenSchema: () => void;
  onScriptTable: (tableName: string) => void;
  onEditTable: (tableName: string) => void;
  onRenameTable: (tableName: string) => void;
  onDropDatabase: (dbName: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  dbState,
  databases,
  onSelectTable,
  onDropTable,
  onCreateTable,
  onCreateDatabase,
  onSwitchDatabase,
  onOpenSchema,
  onScriptTable,
  onEditTable,
  onRenameTable,
  onDropDatabase
}) => {
  const [expandedDb, setExpandedDb] = useState(true);
  const [expandedTables, setExpandedTables] = useState<Record<string, boolean>>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const toggleTable = (tableName: string) => {
    setExpandedTables(prev => ({ ...prev, [tableName]: !prev[tableName] }));
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setActiveMenu(null);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const filteredTables = dbState.tables.filter(t => t.name.toLowerCase().includes(searchTerm.toLowerCase()));

  return (
    <div className="w-64 bg-slate-50 dark:bg-slate-900 text-slate-700 dark:text-slate-300 flex flex-col h-full border-r border-slate-200 dark:border-slate-700 select-none relative transition-colors duration-200">
      <div className="p-4 border-b border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-950 flex flex-col gap-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500">DB Explorer</h2>
        
        <button 
           onClick={onCreateDatabase}
           className="w-full flex items-center justify-center gap-2 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-blue-600 dark:text-blue-400 py-1.5 px-3 rounded text-xs transition-colors border border-slate-300 dark:border-slate-700 shadow-sm"
         >
           <Plus className="h-3 w-3" /> New Database
         </button>

        <div className="relative">
          <Search className="absolute left-2 top-2 h-4 w-4 text-slate-400" />
          <input 
            type="text" 
            placeholder="Search tables..." 
            className="w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded pl-8 pr-2 py-1 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-slate-800 dark:text-slate-200"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2 pb-24">
      {/* pb-24 to allow space for dropdown at bottom */}
        {/* Database Selector */}
        {databases.length > 1 && (
          <div className="mb-4">
            <label className="block text-xs font-medium text-slate-500 dark:text-slate-400 mb-1">Switch Database</label>
            <select
              value={dbState.name}
              onChange={(e) => onSwitchDatabase(e.target.value)}
              className="w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded px-2 py-1 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-slate-800 dark:text-slate-200"
            >
              {databases.map(db => (
                <option key={db} value={db}>{db}</option>
              ))}
            </select>
          </div>
        )}

        <div className="mb-2">
          <div className="flex items-center justify-between p-2 hover:bg-slate-200 dark:hover:bg-slate-800 rounded group transition-colors">
             <div
                className="flex items-center cursor-pointer text-blue-600 dark:text-blue-400 font-semibold flex-1 overflow-hidden"
                onClick={() => setExpandedDb(!expandedDb)}
             >
                {expandedDb ? <ChevronDown className="h-4 w-4 mr-1 shrink-0" /> : <ChevronRight className="h-4 w-4 mr-1 shrink-0" />}
                <Database className="h-4 w-4 mr-2 shrink-0" />
                <span className="truncate">{dbState.name}</span>
             </div>
             <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
               <button
                  onClick={(e) => { e.stopPropagation(); onOpenSchema(); }}
                  className="p-1 hover:bg-slate-300 dark:hover:bg-slate-700 rounded text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white"
                  title="View Schema Diagram"
               >
                  <GitGraph className="h-3.5 w-3.5" />
               </button>
               <button
                  onClick={(e) => { e.stopPropagation(); onDropDatabase(dbState.name); }}
                  className="p-1 hover:bg-red-100 dark:hover:bg-red-900/20 rounded text-red-500 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                  title="Drop Database"
               >
                  <Trash2 className="h-3.5 w-3.5" />
               </button>
             </div>
          </div>

          {expandedDb && (
            <div className="pl-4 space-y-1 mt-1 relative">
              {filteredTables.map(table => (
                <div key={table.id} className="relative">
                  <div 
                    className="group flex items-center justify-between p-1.5 hover:bg-slate-200 dark:hover:bg-slate-800 rounded cursor-pointer text-sm transition-colors"
                    onClick={() => onSelectTable(table.name)} // Click to view table data
                  >
                    <div className="flex items-center overflow-hidden">
                      {/* Separate chevron click to avoid triggering selection when expanding col details */}
                      <span onClick={(e) => { e.stopPropagation(); toggleTable(table.name); }} className="flex items-center p-0.5 hover:bg-slate-300 dark:hover:bg-slate-700 rounded mr-1">
                        {expandedTables[table.name] ? <ChevronDown className="h-3 w-3 text-slate-500" /> : <ChevronRight className="h-3 w-3 text-slate-500" />}
                      </span>
                      <TableIcon className="h-3.5 w-3.5 mr-2 text-green-600 dark:text-green-500 shrink-0" />
                      <span className="truncate text-slate-700 dark:text-slate-300" title={table.name}>{table.name}</span>
                    </div>
                    <div className="flex shrink-0">
                        <button 
                            onClick={(e) => { 
                                e.stopPropagation(); 
                                setActiveMenu(activeMenu === table.name ? null : table.name); 
                            }} 
                            className={`p-1 rounded transition-colors ${activeMenu === table.name ? 'text-white bg-slate-700' : 'text-transparent group-hover:text-slate-500 dark:group-hover:text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-300 dark:hover:bg-slate-700'}`}
                        >
                           <MoreVertical className="h-3 w-3" />
                        </button>
                    </div>
                  </div>
                  
                  {/* Dropdown Menu */}
                  {activeMenu === table.name && (
                    <div 
                        ref={menuRef}
                        className="absolute right-0 top-8 w-40 bg-white dark:bg-slate-800 rounded-md shadow-xl border border-slate-200 dark:border-slate-700 z-50 overflow-hidden"
                        style={{ boxShadow: '0 4px 20px rgba(0,0,0,0.5)' }}
                    >
                        <div className="py-1">
                            <button 
                                onClick={() => { onSelectTable(table.name); setActiveMenu(null); }}
                                className="flex items-center gap-2 w-full text-left px-4 py-2 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                            >
                                <Eye className="h-3 w-3" /> View Data
                            </button>
                            <button 
                                onClick={() => { onScriptTable(table.name); setActiveMenu(null); }}
                                className="flex items-center gap-2 w-full text-left px-4 py-2 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                            >
                                <FileCode className="h-3 w-3" /> Script SELECT
                            </button>
                            <button
                                onClick={() => { onEditTable(table.name); setActiveMenu(null); }}
                                className="flex items-center gap-2 w-full text-left px-4 py-2 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                            >
                                <Pencil className="h-3 w-3" /> Edit Structure
                            </button>
                            <button
                                onClick={() => { onRenameTable(table.name); setActiveMenu(null); }}
                                className="flex items-center gap-2 w-full text-left px-4 py-2 text-xs text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700"
                            >
                                <Edit className="h-3 w-3" /> Rename Table
                            </button>
                            <div className="h-px bg-slate-200 dark:bg-slate-700 my-1" />
                            <button 
                                onClick={() => { onDropTable(table.name); setActiveMenu(null); }}
                                className="flex items-center gap-2 w-full text-left px-4 py-2 text-xs text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
                            >
                                <Trash2 className="h-3 w-3" /> Drop Table
                            </button>
                        </div>
                    </div>
                  )}

                  {expandedTables[table.name] && (
                    <div className="pl-6 border-l border-slate-300 dark:border-slate-800 ml-2.5 mt-1 space-y-1">
                      {table.columns.map(col => (
                        <div key={col.id} className="flex items-center text-xs text-slate-500 dark:text-slate-400 p-1 hover:bg-slate-200 dark:hover:bg-slate-800 rounded transition-colors">
                            {col.isPrimaryKey ? <Key className="h-3 w-3 mr-1.5 text-yellow-500 shrink-0" /> : <span className="w-3 mr-1.5 shrink-0" />}
                            <span className="mr-2 truncate">{col.name}</span>
                            <span className="text-slate-400 dark:text-slate-600 ml-auto text-[10px]">{col.type}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {filteredTables.length === 0 && <div className="text-xs text-slate-500 pl-6 italic">No tables found</div>}
            </div>
          )}
        </div>
      </div>
      
      <div className="p-4 border-t border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-950 mt-auto">
         <button 
           onClick={onCreateTable}
           className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded text-sm transition-colors shadow-md"
         >
           <Plus className="h-4 w-4" /> New Table
         </button>
      </div>
    </div>
  );
};

export default Sidebar;
