import React from 'react';
import { X, CheckCircle2, Database, Code2, Layers, RefreshCw } from 'lucide-react';

interface RecruiterInfoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onResetDemo: () => void;
}

const RecruiterInfoModal: React.FC<RecruiterInfoModalProps> = ({ isOpen, onClose, onResetDemo }) => {
  if (!isOpen) return null;

  const features = [
    {
      icon: <Database className="h-5 w-5 text-blue-500" />,
      title: "Table Design & Constraints",
      desc: "Supports declaring tables with typed columns (INT, VARCHAR, DECIMAL, etc.), Primary Keys, and Foreign Keys."
    },
    {
      icon: <Code2 className="h-5 w-5 text-purple-500" />,
      title: "Interactive REPL & CRUD",
      desc: "Executes SQL commands (SELECT, INSERT, UPDATE, DELETE) with syntax highlighting and a results console."
    },
    {
      icon: <Layers className="h-5 w-5 text-green-500" />,
      title: "Schema Visualization & Joins",
      desc: "Visualizes relationships (Foreign Keys) and executes basic INNER JOIN operations via a custom mock engine."
    },
    {
        icon: <CheckCircle2 className="h-5 w-5 text-amber-500" />,
        title: "Mocking & State Persistence",
        desc: "Maintains state in memory to simulate a real persistent database connection during the session."
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-slate-900 w-full max-w-2xl rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex justify-between items-start bg-slate-50 dark:bg-slate-950">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs font-bold uppercase tracking-wider mb-3">
              Candidate Submission
            </div>
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Pesapal Junior Dev Challenge '26</h2>
            <p className="text-slate-500 dark:text-slate-400 mt-1 text-sm">
              Custom RDBMS Implementation & Web Interface
            </p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-full transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="p-6 overflow-y-auto">
          <div className="prose dark:prose-invert max-w-none mb-8">
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
              This application is designed to demonstrate the "ingenuity to develop unorthodox solutions" as requested by the challenge. 
              Instead of simply connecting to an existing SQL database, this project implements a <strong>frontend-based Relational Database Management System simulator</strong>. 
              It parses a subset of SQL, manages schema metadata, enforces constraints, and visualizes execution plans entirely in the browser.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {features.map((f, i) => (
              <div key={i} className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700/50 flex gap-3">
                <div className="shrink-0 mt-1">{f.icon}</div>
                <div>
                  <h3 className="font-bold text-slate-800 dark:text-slate-200 text-sm">{f.title}</h3>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-relaxed">{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer / Actions */}
        <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 flex justify-between items-center">
          <div className="text-xs text-slate-400">
            Click "Close" to interact with the RDBMS.
          </div>
          <div className="flex gap-3">
            <button 
                onClick={() => { onResetDemo(); onClose(); }}
                className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors text-sm font-medium"
            >
                <RefreshCw className="h-4 w-4" /> Reset Demo Data
            </button>
            <button 
                onClick={onClose}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm font-medium shadow-lg shadow-blue-500/20"
            >
                Explore Solution
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecruiterInfoModal;
