import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Send, 
  Copy, 
  Check, 
  RefreshCcw, 
  ChevronRight, 
  Layout, 
  Settings, 
  Target, 
  FileText,
  History,
  X,
  Clock
} from 'lucide-react';

// Backend API URLs
const API_URL = "http://localhost:5000/api/generate-email";
const HISTORY_URL = "http://localhost:5000/api/history";

function App() {
  // 1. State management for form inputs
  const [formData, setFormData] = useState({
    purpose: '',
    tone: 'professional',
    audience: '',
    points: ''
  });

  // 2. State for handling AI response, loading and errors
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  // 3. State for History feature
  const [showHistory, setShowHistory] = useState(false);
  const [historyData, setHistoryData] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  // Handle Input Changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // API Communication logic for generation
  const handleGenerate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    // Simple validation
    if (!formData.purpose || !formData.audience || !formData.points) {
      setError("Please fill in all the core fields first.");
      setLoading(false);
      return;
    }

    try {
      const response = await axios.post(API_URL, formData);
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || err.response?.data?.error || "Whoops! The AI is stuck. Check your backend connection or API keys.");
    } finally {
      setLoading(false);
    }
  };

  // Fetch History Logic
  const fetchHistory = async () => {
    setLoadingHistory(true);
    try {
      const resp = await axios.get(HISTORY_URL);
      setHistoryData(resp.data);
    } catch (err) {
      console.error("Failed to load history", err);
    } finally {
      setLoadingHistory(false);
    }
  };

  const openHistory = () => {
    setShowHistory(true);
    fetchHistory();
  };

  const loadFromHistory = (item) => {
    setFormData({
      purpose: item.purpose || '',
      tone: item.tone || 'professional',
      audience: item.audience || '',
      points: item.points || ''
    });
    setResult({
      subject: item.subject,
      email: item.email_body
    });
    setShowHistory(false);
  };

  // Copy to Clipboard Feature
  const handleCopy = () => {
    if(!result) return;
    const textToCopy = `Subject: ${result.subject}\n\n${result.email || result.email_body}`;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8 relative">
      
      {/* Absolute floating button for History */}
      <div className="absolute top-6 right-6 lg:top-12 lg:right-12">
        <button 
          onClick={openHistory}
          className="flex items-center space-x-2 bg-white border border-slate-200 shadow-sm text-slate-600 px-4 py-2 rounded-full hover:bg-slate-50 hover:shadow-md hover:text-primary-600 transition-all font-semibold active:scale-95"
        >
          <History className="w-4 h-4" />
          <span>History</span>
        </button>
      </div>

      {/* Header Section */}
      <header className="max-w-4xl w-full text-center mb-12">
        <div className="inline-flex items-center space-x-2 bg-primary-100 text-primary-600 px-4 py-1.5 rounded-full mb-4 text-sm font-semibold tracking-wide uppercase">
          <Send className="w-4 h-4" />
          <span>Next-Gen AI Writing</span>
        </div>
        <h1 className="text-5xl font-extrabold text-slate-900 tracking-tight leading-tight mb-4">
          AI Email <span className="text-primary-600">Generator</span>
        </h1>
        <p className="text-lg text-slate-500 max-w-2xl mx-auto font-medium">
          Draft high-converting, professional emails in seconds with the power of Google Gemini & Hugging Face.
        </p>
      </header>

      <main className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-8 lg:items-start">
        
        {/* Step 1: Input Form (Left Side) - Modern, Card-based */}
        <section className="bg-white rounded-3xl p-8 shadow-premium border border-slate-100 relative z-10">
          <div className="mb-6">
            <h2 className="text-2xl font-bold flex items-center mb-2">
              <Settings className="w-5 h-5 mr-2 text-primary-500" />
              Email Configuration
            </h2>
            <p className="text-slate-400 text-sm">Fine-tune the purpose, tone, and audience.</p>
          </div>

          <form onSubmit={handleGenerate} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Email Purpose</label>
              <select 
                name="purpose"
                value={formData.purpose}
                onChange={handleChange}
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all text-slate-700"
              >
                <option value="">Select a purpose...</option>
                <option value="sales">Sales Outreach</option>
                <option value="follow-up">Follow-up Meeting</option>
                <option value="job-application">Job Application</option>
                <option value="meeting-request">Meeting Request</option>
                <option value="thank-you">Thank You Note</option>
                <option value="announcement">New Feature / Launch</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Tone</label>
                <select 
                  name="tone"
                  value={formData.tone}
                  onChange={handleChange}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all text-slate-700 font-medium"
                >
                  <option value="professional">Professional</option>
                  <option value="friendly">Friendly</option>
                  <option value="persuasive">Persuasive</option>
                  <option value="formal">Formal</option>
                  <option value="urgent">Urgent</option>
                  <option value="bold">Bold & Energetic</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-2">Target Audience</label>
                <input 
                  name="audience"
                  value={formData.audience}
                  onChange={handleChange}
                  placeholder="e.g. CMO, Hiring Manager"
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3.5 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all text-slate-700"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Key Highlights / Points</label>
              <textarea 
                name="points"
                value={formData.points}
                onChange={handleChange}
                placeholder="Mention the key context or value proposition..."
                rows="4"
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-4 focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all text-slate-700 resize-none"
              />
            </div>

            {error && <div className="p-3 bg-red-50 text-red-600 rounded-xl text-sm font-medium animate-pulse">{error}</div>}

            <button
              type="submit"
              disabled={loading}
              className="w-full group bg-slate-900 border-2 border-slate-900 text-white p-4 rounded-xl flex items-center justify-center font-bold text-lg hover:bg-slate-800 transition-all shadow-lg active:scale-95 disabled:opacity-70"
            >
              {loading ? (
                <div className="spinner"></div>
              ) : (
                <>
                  <ChevronRight className="w-5 h-5 mr-1 transition-transform group-hover:translate-x-1" />
                  Generate Blueprint
                </>
              )}
            </button>
          </form>
        </section>

        {/* Step 2: Output Section (Right Side) */}
        <section className="h-full flex flex-col">
          {!result && !loading ? (
            /* Placeholder state */
            <div className="flex-1 min-h-[500px] flex flex-col items-center justify-center bg-slate-100/50 border-2 border-dashed border-slate-200 rounded-3xl p-10 text-center space-y-4">
              <div className="p-5 bg-white rounded-2xl shadow-sm text-slate-300">
                <FileText className="w-12 h-12" />
              </div>
              <p className="text-slate-400 font-medium tracking-wide">Ready for generation</p>
              <p className="text-slate-400 text-sm">Configure your email and click the button to see the magic.</p>
            </div>
          ) : loading ? (
            /* Loading State */
            <div className="flex-1 min-h-[500px] bg-white rounded-3xl p-8 shadow-premium border border-slate-100 flex flex-col items-center justify-center">
              <div className="spinner mb-6 scale-150"></div>
              <h3 className="text-xl font-semibold text-slate-800 mb-2 animate-pulse">AI is crafting your message...</h3>
              <p className="text-slate-400 text-sm">Working with Gemini & Hugging Face infrastructure.</p>
            </div>
          ) : (
            /* Display Generated Email */
            <div className="flex-1 min-h-[500px] bg-white rounded-3xl flex flex-col shadow-premium border border-slate-100 overflow-hidden transform transition-all duration-500 animate-in fade-in zoom-in slide-in-from-right-10">
              <div className="p-6 border-b border-slate-50 flex justify-between items-center bg-slate-50/50 backdrop-blur-sm">
                <span className="text-emerald-600 font-bold text-sm flex items-center">
                  <Check className="w-4 h-4 text-emerald-500 mr-2" /> Blueprint Generated
                </span>
                <button 
                  onClick={handleCopy}
                  className="flex items-center space-x-1 px-4 py-2 bg-white border border-slate-200 rounded-xl text-sm font-semibold text-slate-600 hover:bg-slate-50 transition-all active:scale-95 shadow-sm"
                >
                  {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                  <span>{copied ? "Copied!" : "Copy Email"}</span>
                </button>
              </div>

              <div className="p-8 flex-1 overflow-y-auto max-h-[600px] space-y-8">
                <div>
                  <h4 className="text-[11px] font-extrabold text-slate-400 uppercase tracking-widest mb-3">Subject Line</h4>
                  <div className="pl-4 border-l-4 border-primary-500 text-slate-900 font-extrabold text-lg leading-relaxed">
                    {result.subject}
                  </div>
                </div>

                <div>
                  <h4 className="text-[11px] font-extrabold text-slate-400 uppercase tracking-widest mb-3">Email Body</h4>
                  <div className="whitespace-pre-wrap text-slate-600 leading-relaxed font-medium">
                    {result.email || result.email_body}
                  </div>
                </div>
              </div>

              <div className="p-6 bg-slate-50 mt-auto border-t border-slate-100">
                <p className="text-center text-xs text-slate-400 font-medium">
                  Automatically saved to your local database history.
                </p>
              </div>
            </div>
          )}
        </section>
      </main>

      {/* History Modal / Overlay */}
      {showHistory && (
        <div className="fixed inset-0 z-50 flex justify-end">
          {/* Backdrop */}
          <div 
            className="absolute inset-0 bg-slate-900/20 backdrop-blur-sm transition-opacity"
            onClick={() => setShowHistory(false)}
          />
          
          {/* Sidebar */}
          <div className="relative w-full max-w-md bg-white h-full shadow-2xl flex flex-col animate-in slide-in-from-right duration-300">
            <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
              <h2 className="text-xl font-bold text-slate-800 flex items-center">
                <Clock className="w-5 h-5 mr-2 text-primary-500" /> Generation History
              </h2>
              <button 
                onClick={() => setShowHistory(false)}
                className="p-2 bg-white border border-slate-200 rounded-full hover:bg-slate-100 transition-colors text-slate-500"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50">
              {loadingHistory ? (
                <div className="flex justify-center py-10">
                  <div className="spinner scale-125"></div>
                </div>
              ) : historyData.length === 0 ? (
                <div className="text-center py-12 text-slate-400 font-medium">
                  No emails generated yet.<br/>Generate your first one!
                </div>
              ) : (
                historyData.map((item) => (
                  <div 
                    key={item.id} 
                    className="bg-white p-5 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md hover:border-primary-100 transition-all cursor-pointer group"
                    onClick={() => loadFromHistory(item)}
                  >
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-bold text-slate-800 line-clamp-1 pr-4">{item.subject}</h4>
                      <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 bg-slate-100 px-2 py-1 rounded w-fit flex-shrink-0">
                        {item.tone}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mb-3 truncate">To: {item.audience}</p>
                    <div className="text-sm text-slate-600 line-clamp-2 bg-slate-50 p-2 rounded-lg font-medium">
                      {item.email_body}
                    </div>
                    <div className="mt-3 text-[10px] text-slate-400 font-medium text-right opacity-0 group-hover:opacity-100 transition-opacity">
                      Click to reload
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      <footer className="mt-16 text-slate-400 text-sm font-medium flex items-center bg-white px-6 py-3 rounded-full shadow-sm border border-slate-100 relative z-10">
        Built with Google Gemini & Vite React
      </footer>
    </div>
  );
}

export default App;
