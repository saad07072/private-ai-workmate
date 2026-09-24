import { useEffect, useState, type FormEvent, type ReactNode } from 'react'
import {
  Activity, BrainCircuit, Check, ChevronDown, ChevronRight, CircleAlert, Copy,
  FileText, FolderGit2, Menu, MessageSquare, Plus, RefreshCw, Search, ShieldCheck,
  Sparkles, Trash2, Upload, X, Zap,
} from 'lucide-react'

type Page = 'chat' | 'memory' | 'documents' | 'github' | 'security'
type Message = { role: 'user' | 'assistant'; content: string }
type Memory = { id: number; content: string; category: string; created_at?: string }
type Document = { id: number; filename: string; file_type: string; chunk_count?: number; created_at?: string }

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options)
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail || 'The Workmate service returned an error.')
  }
  return response.json()
}

function App() {
  const [page, setPage] = useState<Page>('chat')
  const [mobileNav, setMobileNav] = useState(false)
  const [conversationId, setConversationId] = useState<string>()
  const [messages, setMessages] = useState<Message[]>([])
  const [backendOnline, setBackendOnline] = useState(false)
  const [chatBusy, setChatBusy] = useState(false)
  const [chatError, setChatError] = useState('')
  const [memories, setMemories] = useState<Memory[]>([])
  const [documents, setDocuments] = useState<Document[]>([])

  useEffect(() => {
    request<{ status: string }>('/health').then(() => setBackendOnline(true)).catch(() => setBackendOnline(false))
  }, [])

  useEffect(() => {
    if (page === 'memory') request<{ memories: Memory[] }>('/api/memory').then((data) => setMemories(data.memories)).catch(() => undefined)
    if (page === 'documents') request<{ documents: Document[] }>('/api/documents').then((data) => setDocuments(data.documents)).catch(() => undefined)
  }, [page])

  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault()
        newChat()
      }
    }

    window.addEventListener('keydown', handleShortcut)
    return () => window.removeEventListener('keydown', handleShortcut)
  }, [])

  function navigate(next: Page) {
    setPage(next)
    setMobileNav(false)
  }

  function newChat() {
    setConversationId(undefined)
    setMessages([])
    setChatError('')
    navigate('chat')
  }

  async function sendMessage(message: string) {
    const clean = message.trim()
    if (!clean || chatBusy) return
    setChatError('')
    setMessages((current) => [...current, { role: 'user', content: clean }])
    setChatBusy(true)
    try {
      const data = await request<{ conversation_id: string; response: string }>('/api/chat', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: clean, conversation_id: conversationId }),
      })
      setConversationId(data.conversation_id)
      setMessages((current) => [...current, { role: 'assistant', content: data.response }])
    } catch (error) {
      setChatError(error instanceof Error ? error.message : 'Connection to Workmate was interrupted.')
    } finally {
      setChatBusy(false)
    }
  }

  return <div className="app-shell">
    <div className="ambient ambient-one" /><div className="ambient ambient-two" />
    <Sidebar page={page} backendOnline={backendOnline} onNavigate={navigate} onNewChat={newChat} />
    <main className="main-column">
      <header className="topbar">
        <button className="icon-button mobile-menu" aria-label="Open navigation" onClick={() => setMobileNav(true)}><Menu size={19} /></button>
        <div className="topbar-heading"><span className="eyebrow">PRIVATE AI WORKMATE <b>/</b> {pageTitle(page).toUpperCase()}</span><h1>{pageTitle(page)}</h1></div>
        <div className="topbar-actions"><div className="topbar-model"><Zap size={13} /><span>Nemotron</span><small>Nebius</small></div><StatusPill online={backendOnline} /><button className="avatar" aria-label="Account">S</button></div>
      </header>
      {mobileNav && <MobileNav page={page} onNavigate={navigate} onClose={() => setMobileNav(false)} />}
      <div className="content-area">
        {page === 'chat' && <ChatView messages={messages} busy={chatBusy} error={chatError} onSend={sendMessage} onRetry={() => setChatError('')} />}
        {page === 'memory' && <MemoryView memories={memories} onRefresh={() => request<{ memories: Memory[] }>('/api/memory').then((data) => setMemories(data.memories))} />}
        {page === 'documents' && <DocumentsView documents={documents} onRefresh={() => request<{ documents: Document[] }>('/api/documents').then((data) => setDocuments(data.documents))} />}
        {page === 'github' && <GithubView onAnalyze={sendMessage} busy={chatBusy} result={messages.filter((item) => item.role === 'assistant').at(-1)?.content} />}
        {page === 'security' && <SecurityView />}
      </div>
    </main>
    <aside className="context-panel"><ContextPanel page={page} messages={messages} online={backendOnline} busy={chatBusy} /></aside>
  </div>
}

function pageTitle(page: Page) {
  return ({ chat: 'Workspace', memory: 'Memory', documents: 'Documents', github: 'GitHub Agent', security: 'Security Center' })[page]
}

function Sidebar({ page, backendOnline, onNavigate, onNewChat }: { page: Page; backendOnline: boolean; onNavigate: (page: Page) => void; onNewChat: () => void }) {
  const items: { id: Page; label: string; icon: ReactNode }[] = [
    { id: 'chat', label: 'Chat', icon: <MessageSquare size={17} /> },
    { id: 'memory', label: 'Memory', icon: <BrainCircuit size={17} /> },
    { id: 'documents', label: 'Documents', icon: <FileText size={17} /> },
    { id: 'github', label: 'GitHub Agent', icon: <FolderGit2 size={17} /> },
    { id: 'security', label: 'Security', icon: <ShieldCheck size={17} /> },
  ]
  return <aside className="sidebar">
    <div className="brand"><span className="brand-mark"><Sparkles size={16} /></span><span>PRIVATE AI<br /><strong>WORKMATE</strong></span></div>
    <button className="new-chat" onClick={onNewChat}><Plus size={17} /> New chat <span>⌘ K</span></button>
    <div className="nav-label">Workspace</div>
    <nav>{items.map((item) => <button key={item.id} className={`nav-item ${page === item.id ? 'active' : ''}`} onClick={() => onNavigate(item.id)}>{item.icon}<span>{item.label}</span>{item.id === 'chat' && <i />}</button>)}</nav>
    <div className="recent-label">Recent conversations</div>
    <button className="recent-item" onClick={() => onNavigate('chat')}><span className="recent-dot" />New workspace session</button>
    <div className="sidebar-footer"><div className="model-card"><div className="model-icon"><Zap size={16} /></div><div><b>Nemotron</b><small>Nebius Token Factory</small></div><span className={`online-dot ${backendOnline ? '' : 'offline'}`} /></div><button className="settings-button"><Activity size={16} />System status</button></div>
  </aside>
}

function MobileNav({ page, onNavigate, onClose }: { page: Page; onNavigate: (page: Page) => void; onClose: () => void }) {
  return <div className="mobile-nav"><div className="mobile-nav-head"><b>Navigate</b><button className="icon-button" onClick={onClose} aria-label="Close navigation"><X size={18} /></button></div>{(['chat', 'memory', 'documents', 'github', 'security'] as Page[]).map((item) => <button key={item} className={page === item ? 'active' : ''} onClick={() => onNavigate(item)}>{pageTitle(item)}</button>)}</div>
}

function StatusPill({ online }: { online: boolean }) { return <span className={`status-pill ${online ? '' : 'offline'}`}><span />{online ? 'CONNECTED' : 'OFFLINE'}</span> }

function ChatView({ messages, busy, error, onSend, onRetry }: { messages: Message[]; busy: boolean; error: string; onSend: (text: string) => void; onRetry: () => void }) {
  const [draft, setDraft] = useState('')
  function submit(event: FormEvent) { event.preventDefault(); onSend(draft); setDraft('') }
  return <section className="chat-view">
    {messages.length === 0 ? <div className="welcome"><div className="orb"><div className="orb-core" /><div className="orb-ring ring-one" /><div className="orb-ring ring-two" /></div><span className="eyebrow accent">PRIVATE AI WORKSPACE</span><h2>Good evening.</h2><p>Your private AI workspace is ready.</p><div className="suggestions"><Prompt label="Analyze my GitHub repository" onClick={onSend} /><Prompt label="Search my documents" onClick={onSend} /><Prompt label="What do you remember about my projects?" onClick={onSend} /><Prompt label="Explain my backend architecture" onClick={onSend} /></div></div> : <div className="message-list">{messages.map((message, index) => <MessageBubble key={`${message.role}-${index}`} message={message} />)}{busy && <div className="thinking"><span className="pulse" /><span>Preparing a response</span><span className="thinking-dots">...</span></div>}{error && <ErrorBox message={error} onRetry={onRetry} />}</div>}
    <form className="composer-wrap" onSubmit={submit}><div className="composer"><textarea value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Ask Workmate anything..." rows={1} aria-label="Message Workmate" onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); submit(event) } }} /><button className="send-button" disabled={busy || !draft.trim()} aria-label="Send message"><Sparkles size={17} /></button></div><div className="composer-note"><span><ShieldCheck size={13} /> Private workspace</span><span>Enter to send · Shift + Enter for new line</span></div></form>
  </section>
}

function Prompt({ label, onClick }: { label: string; onClick: (text: string) => void }) { return <button className="prompt" onClick={() => onClick(label)}><span>{label}</span><ChevronRight size={15} /></button> }

function MessageBubble({ message }: { message: Message }) { return <article className={`message ${message.role}`}><div className="message-meta">{message.role === 'assistant' ? <><span className="mini-mark"><Sparkles size={12} /></span> WORKMATE</> : 'YOU'}</div><div className="message-content"><MarkdownText text={message.content} /></div>{message.role === 'assistant' && <button className="copy-button" aria-label="Copy response" onClick={() => navigator.clipboard?.writeText(message.content)}><Copy size={14} /></button>}</article> }

function MarkdownText({ text }: { text: string }) { return <div className="markdown">{text.split('\n').map((line, index) => <p key={index} className={line.startsWith('```') ? 'code-line' : ''}>{line || '\u00a0'}</p>)}</div> }

function ErrorBox({ message, onRetry }: { message: string; onRetry: () => void }) { return <div className="error-box"><CircleAlert size={17} /><div><b>Workmate is temporarily unavailable.</b><span>{message}</span></div><button onClick={onRetry}>Retry</button></div> }

function MemoryView({ memories, onRefresh }: { memories: Memory[]; onRefresh: () => void }) { return <section className="page-view"><PageIntro icon={<BrainCircuit />} title="Memory, with context" text="Long-term memories are retrieved by the backend when they are relevant to a conversation." action={<button className="outline-button" onClick={onRefresh}><RefreshCw size={15} /> Refresh</button>} /><div className="stat-row"><Stat label="Stored memories" value={String(memories.length).padStart(2, '0')} /><Stat label="Storage" value="SQLite + Qdrant" /><Stat label="Retrieval" value="Semantic" /></div><div className="section-heading"><div><span className="eyebrow">LONG-TERM MEMORY</span><h3>Recent memories</h3></div><button className="search-button" aria-label="Search memory"><Search size={17} /></button></div>{memories.length === 0 ? <EmptyState icon={<BrainCircuit />} title="No memories stored yet" text="Save memories through the chat or the API to see them here." /> : <div className="memory-grid">{memories.map((memory) => <div className="memory-card" key={memory.id}><div className="memory-card-top"><span className="category-badge">{memory.category}</span><span>#{memory.id}</span></div><p>{memory.content}</p><small>{memory.created_at || 'Stored in long-term memory'}</small></div>)}</div>}</section> }

function DocumentsView({ documents, onRefresh }: { documents: Document[]; onRefresh: () => void }) { const [uploading, setUploading] = useState(false); const [error, setError] = useState(''); async function upload(file?: File) { if (!file) return; setUploading(true); setError(''); const form = new FormData(); form.append('file', file); try { await request('/api/documents/upload', { method: 'POST', body: form }); onRefresh() } catch (problem) { setError(problem instanceof Error ? problem.message : 'Document processing failed.') } finally { setUploading(false) } } return <section className="page-view"><PageIntro icon={<FileText />} title="Your private library" text="Upload documents to index them for grounded answers inside your workspace." action={<label className="primary-button"><Upload size={15} /> {uploading ? 'Indexing...' : 'Upload document'}<input type="file" accept=".pdf,.docx,.txt" hidden disabled={uploading} onChange={(event) => upload(event.target.files?.[0])} /></label>} />{error && <ErrorBox message={error} onRetry={() => setError('')} />}<div className="upload-strip"><div className="upload-symbol"><Upload size={19} /></div><div><b>Drop a PDF, DOCX, or TXT file here</b><span>Maximum file size: 10 MB · Content is chunked and embedded by the backend.</span></div><span className="upload-count">{documents.length} indexed</span></div><div className="section-heading"><div><span className="eyebrow">INDEXED DOCUMENTS</span><h3>Knowledge base</h3></div><button className="search-button" onClick={onRefresh} aria-label="Refresh documents"><RefreshCw size={17} /></button></div>{documents.length === 0 ? <EmptyState icon={<FileText />} title="Your library is empty" text="Upload a document to make it available to private semantic search." /> : <div className="document-grid">{documents.map((document) => <div className="document-card" key={document.id}><div className="file-icon"><FileText size={19} /></div><div className="document-details"><b>{document.filename}</b><span>{document.file_type.toUpperCase()} · ID {document.id}</span><small>{document.chunk_count ?? 0} chunks · {document.created_at || 'Indexed'}</small></div><Check className="success-icon" size={17} /></div>)}</div>}</section> }

function GithubView({ onAnalyze, busy, result }: { onAnalyze: (text: string) => void; busy: boolean; result?: string }) { const [repository, setRepository] = useState('saad07072/private-ai-workmate'); return <section className="page-view github-view"><PageIntro icon={<FolderGit2 />} title="Read-only repository intelligence" text="Ask Workmate to inspect repository metadata, structure, and source files through its approved GitHub tools." /><div className="repo-form"><label>Repository</label><div className="repo-input"><FolderGit2 size={17} /><input value={repository} onChange={(event) => setRepository(event.target.value)} placeholder="owner/name" /><button disabled={busy || !repository.includes('/')} onClick={() => onAnalyze(`Analyze the GitHub repository ${repository}. Start with metadata and structure, then explain its architecture.`)}>{busy ? 'Inspecting...' : 'Analyze repository'}<ChevronRight size={16} /></button></div><small>GitHub operations are read-only and executed by the backend permission layer.</small></div>{result ? <div className="analysis-result"><div className="result-header"><div className="result-icon"><Sparkles size={17} /></div><div><span className="eyebrow accent">LATEST ANALYSIS</span><h3>Workmate's repository brief</h3></div></div><MarkdownText text={result} /></div> : <div className="repo-empty"><div className="repo-tree"><div><ChevronDown size={15} /> {repository}</div><span><ChevronRight size={15} /> backend/</span><span><ChevronRight size={15} /> frontend/</span><span><ChevronRight size={15} /> tests/</span><span><FileText size={14} /> README.md</span></div><div><span className="eyebrow">READY TO INSPECT</span><h3>Turn a repository into a conversation.</h3><p>Use the analysis action above to let the actual agent gather repository context.</p></div></div>}</section> }

function SecurityView() { const checks = [['Tool mode', 'READ ONLY', true], ['GitHub access', 'Approved read operations', true], ['Arbitrary shell', 'Blocked', false], ['Arbitrary code execution', 'Blocked', false], ['Prompt injection protection', 'Active', true], ['Permission validation', 'Active', true], ['Audit logging', 'Active', true], ['Untrusted tool boundary', 'Active', true]] as const; return <section className="page-view"><PageIntro icon={<ShieldCheck />} title="Security is a product feature" text="The interface reflects the controls implemented in the backend tool execution path." /><div className="security-hero"><div className="security-seal"><ShieldCheck size={32} /></div><div><span className="eyebrow accent">WORKMATE SECURITY MODEL</span><h2>Controlled by design.</h2><p>Every model-requested tool passes through validation, permission checks, security scanning, and audit logging.</p></div></div><div className="security-list">{checks.map(([label, value, active]) => <div className="security-row" key={label}><div className={`check-icon ${active ? 'active' : 'blocked'}`}>{active ? <Check size={15} /> : <X size={15} />}</div><span>{label}</span><b>{value}</b></div>)}</div><div className="security-note"><Activity size={17} /><span>Audit events are recorded by the backend. Live tool events are not exposed by the current API.</span></div></section> }

function ContextPanel({ page, messages, online, busy }: { page: Page; messages: Message[]; online: boolean; busy: boolean }) { const activityState = busy ? 'PROCESSING' : messages.length ? 'READY' : 'IDLE'; return <div className="context-inner"><div className="context-title"><span>WORKSPACE SIGNALS</span><Activity size={15} /></div>{page === 'chat' && <><div className={`signal-card ${busy ? 'is-processing' : ''}`}><div className="signal-head"><span className="signal-icon"><Sparkles size={14} /></span><b>Agent activity</b><span className="signal-live">{activityState}</span></div><div className="activity-line"><span className="activity-check"><Check size={11} /></span><span>Conversation context</span><small>{messages.length ? `${messages.length} messages` : 'Waiting for input'}</small></div><div className="activity-line"><span className={`activity-check ${busy ? 'activity-pending' : ''}`}>{busy ? <span /> : <Check size={11} />}</span><span>{busy ? 'Preparing response' : 'Tool boundary'}</span><small>{busy ? 'Backend processing' : 'Read-only'}</small></div></div><div className="context-card"><span className="eyebrow">MODEL CONFIGURATION</span><h3>Nemotron</h3><p>Nebius Token Factory</p><div className="routing-bar"><span /><span /><span /></div><small>Fast / reasoning models configured</small></div></>}{page !== 'chat' && <div className="context-card page-context"><span className="eyebrow">CURRENT VIEW</span><h3>{pageTitle(page)}</h3><p>{online ? 'Connected to the local Workmate API.' : 'API connection unavailable.'}</p><StatusPill online={online} /></div>}<div className="context-footer"><span className={`online-dot ${online ? '' : 'offline'}`} />Backend {online ? 'reachable' : 'unavailable'}<small>127.0.0.1:8000</small></div></div> }

function PageIntro({ icon, title, text, action }: { icon: ReactNode; title: string; text: string; action?: ReactNode }) { return <div className="page-intro"><div className="intro-icon">{icon}</div><div><span className="eyebrow">PRIVATE AI WORKSPACE</span><h2>{title}</h2><p>{text}</p></div>{action && <div className="intro-action">{action}</div>}</div> }
function Stat({ label, value }: { label: string; value: string }) { return <div className="stat"><span>{label}</span><b>{value}</b></div> }
function EmptyState({ icon, title, text }: { icon: ReactNode; title: string; text: string }) { return <div className="empty-state"><div>{icon}</div><h3>{title}</h3><p>{text}</p></div> }

export default App
