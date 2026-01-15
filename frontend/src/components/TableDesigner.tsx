import React, { useState, useEffect } from 'react';
import { ColumnSchema, DataType, TableSchema } from '../types';
import { Trash2, Plus, ArrowUp, ArrowDown } from 'lucide-react';

interface TableDesignerProps {
  onSave: (table: any, oldName?: string) => void;
  initialData?: TableSchema;
}

const TableDesigner: React.FC<TableDesignerProps> = ({ onSave, initialData }) => {
  const [tableName, setTableName] = useState('new_table');
  const [columns, setColumns] = useState<ColumnSchema[]>([
    { id: '1', name: 'id', type: 'INT', nullable: false, isPrimaryKey: true, isUnique: true }
  ]);

  useEffect(() => {
    if (initialData) {
        setTableName(initialData.name);
        setColumns(initialData.columns.map(c => ({...c}))); // Deep copy cols
    } else {
        // Reset defaults
        setTableName('new_table');
        setColumns([
          { id: '1', name: 'id', type: 'INT', nullable: false, isPrimaryKey: true, isUnique: true }
        ]);
    }
  }, [initialData]);

  const addColumn = () => {
    setColumns([
      ...columns,
      { id: Math.random().toString(), name: 'new_column', type: 'VARCHAR', length: 255, nullable: true, isPrimaryKey: false }
    ]);
  };

  const removeColumn = (id: string) => {
    if (columns.length > 1) {
        setColumns(columns.filter(c => c.id !== id));
    }
  };

  const updateColumn = (id: string, field: keyof ColumnSchema, value: any) => {
    setColumns(columns.map(c => c.id === id ? { ...c, [field]: value } : c));
  };

  const handleSave = () => {
      // Basic validation
      if(!tableName) return alert("Table name required");
      if(columns.some(c => !c.name)) return alert("All columns must have names");
      
      const newSchema = {
          id: tableName.toLowerCase(), // In a real app id might be UUID, here we sync with name usually
          name: tableName,
          columns,
          rows: [], // Will be ignored/merged by backend update logic if editing
          indexes: []
      };

      onSave(newSchema, initialData?.name);
  };

  return (
    <div className="p-8 h-full overflow-y-auto bg-slate-50 dark:bg-slate-900 transition-colors duration-200">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6 flex justify-between items-end">
            <div>
                <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-2">
                    {initialData ? `Edit Table: ${initialData.name}` : 'Create New Table'}
                </h2>
                <div className="flex gap-4">
                    <div>
                        <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Table Name</label>
                        <input 
                            type="text" 
                            value={tableName} 
                            onChange={(e) => setTableName(e.target.value)}
                            className="bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded p-2 text-sm w-64 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>
            </div>
            <button 
                onClick={handleSave}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded shadow-sm font-medium transition-colors"
            >
                {initialData ? 'Save Changes' : 'Create Table'}
            </button>
        </div>

        <div className="bg-white dark:bg-slate-800 shadow rounded-lg overflow-hidden border border-slate-200 dark:border-slate-700 transition-colors duration-200">
          <table className="w-full text-left">
            <thead className="bg-slate-100 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-700">
              <tr>
                <th className="p-3 text-xs font-bold text-slate-500 uppercase w-8"></th>
                <th className="p-3 text-xs font-bold text-slate-500 uppercase">Column Name</th>
                <th className="p-3 text-xs font-bold text-slate-500 uppercase">Type</th>
                <th className="p-3 text-xs font-bold text-slate-500 uppercase w-24">Length</th>
                <th className="p-3 text-xs font-bold text-slate-500 uppercase text-center w-20">Null</th>
                <th className="p-3 text-xs font-bold text-slate-500 uppercase text-center w-20">PK</th>
                <th className="p-3 text-xs font-bold text-slate-500 uppercase text-center w-20">Auto</th>
                <th className="p-3 text-xs font-bold text-slate-500 uppercase w-16"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {columns.map((col, idx) => (
                <tr key={col.id} className="group hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                  <td className="p-3 text-slate-400 text-xs text-center">{idx + 1}</td>
                  <td className="p-2">
                    <input 
                      type="text" 
                      value={col.name} 
                      onChange={(e) => updateColumn(col.id, 'name', e.target.value)}
                      className="w-full bg-transparent border-b border-transparent hover:border-slate-300 focus:border-blue-500 focus:outline-none py-1 px-2 text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400"
                      placeholder="col_name"
                    />
                  </td>
                  <td className="p-2">
                    <select 
                      value={col.type} 
                      onChange={(e) => updateColumn(col.id, 'type', e.target.value as DataType)}
                      className="w-full bg-transparent border-b border-transparent hover:border-slate-300 focus:border-blue-500 focus:outline-none py-1 px-2 text-sm text-slate-900 dark:text-slate-100 [&>option]:bg-white [&>option]:text-slate-900 dark:[&>option]:bg-slate-800 dark:[&>option]:text-slate-100"
                    >
                      {['INT', 'VARCHAR', 'TEXT', 'DATE', 'DATETIME', 'DECIMAL', 'BOOLEAN'].map(t => (
                        <option key={t} value={t}>{t}</option>
                      ))}
                    </select>
                  </td>
                  <td className="p-2">
                    <input 
                      type="number" 
                      value={col.length || ''} 
                      onChange={(e) => updateColumn(col.id, 'length', parseInt(e.target.value))}
                      disabled={!['VARCHAR', 'DECIMAL'].includes(col.type)}
                      className="w-full bg-transparent border-b border-transparent hover:border-slate-300 focus:border-blue-500 focus:outline-none py-1 px-2 text-sm disabled:opacity-30 text-slate-900 dark:text-slate-100 placeholder-slate-400"
                      placeholder={['VARCHAR', 'DECIMAL'].includes(col.type) ? "Size" : ""}
                    />
                  </td>
                  <td className="p-2 text-center">
                    <input 
                      type="checkbox" 
                      checked={col.nullable} 
                      onChange={(e) => updateColumn(col.id, 'nullable', e.target.checked)}
                      className="rounded text-blue-600 focus:ring-blue-500 bg-slate-100 dark:bg-slate-700 border-slate-300 dark:border-slate-600"
                    />
                  </td>
                  <td className="p-2 text-center">
                    <input
                      type="checkbox"
                      checked={col.isPrimaryKey}
                      onChange={(e) => updateColumn(col.id, 'isPrimaryKey', e.target.checked)}
                      className="rounded text-yellow-500 focus:ring-yellow-500 bg-slate-100 dark:bg-slate-700 border-slate-300 dark:border-slate-600"
                    />
                  </td>
                  <td className="p-2 text-center">
                    <input
                      type="checkbox"
                      checked={col.autoIncrement || false}
                      onChange={(e) => updateColumn(col.id, 'autoIncrement', e.target.checked)}
                      disabled={col.type !== 'INT'}
                      className="rounded text-green-500 focus:ring-green-500 bg-slate-100 dark:bg-slate-700 border-slate-300 dark:border-slate-600 disabled:opacity-30"
                    />
                  </td>
                  <td className="p-2 text-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={() => removeColumn(col.id)} className="text-red-400 hover:text-red-600 p-1">
                        <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="p-3 bg-slate-50 dark:bg-slate-950 border-t border-slate-200 dark:border-slate-700">
            <button 
                onClick={addColumn}
                className="flex items-center gap-2 text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
                <Plus className="h-4 w-4" /> Add Column
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TableDesigner;
