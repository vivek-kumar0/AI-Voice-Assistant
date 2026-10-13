import React, { useEffect, useState } from "react";
import {
  Navigate,
  NavLink,
  Outlet,
  Route,
  Routes,
  useNavigate,
  useSearchParams,
} from "react-router-dom";

import {
  Bot,
  LayoutDashboard,
  MessageSquare,
  FileText,
  StickyNote,
  Bell,
  Settings,
  LogOut,
  Menu,
  X,
  Mic2,
  Sparkles,
} from "lucide-react";

import { api } from "./api";

/* =========================================================
   PROTECTED LAYOUT
========================================================= */

function ProtectedLayout() {
  if (!localStorage.getItem("voice_token")) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Layout>
      <Outlet />
    </Layout>
  );
}

/* =========================================================
   ERROR BOUNDARY
========================================================= */

class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);

    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      error,
    };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-page">
          <div className="panel">
            <h1>Something went wrong</h1>

            <p className="muted">
              This page hit an unexpected error. Your data is safe. Reload the
              application or return to the dashboard.
            </p>

            <div className="actions">
              <button
                className="primary"
                onClick={() => window.location.reload()}
              >
                Reload application
              </button>

              <a className="secondary" href="/dashboard">
                Dashboard
              </a>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/* =========================================================
   FOOTER
========================================================= */

function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-glow" />

      <div className="footer-grid">
        {/* Brand */}
        <div className="footer-brand">
          <div className="brand-icon">
            <Bot size={22} />
          </div>

          <div>
            <strong>Nova AI</strong>
            <span>Your intelligent voice workspace</span>
          </div>

          <p>
            Talk, type, organize, search and ask questions from your documents
            — all from one responsive workspace.
          </p>
        </div>

        {/* Workspace */}
        <div>
          <h4>Workspace</h4>

          <NavLink to="/dashboard">Dashboard</NavLink>
          <NavLink to="/chat">AI Chat</NavLink>
          <NavLink to="/documents">Documents</NavLink>
        </div>

        {/* Productivity */}
        <div>
          <h4>Productivity</h4>

          <NavLink to="/notes">Notes</NavLink>
          <NavLink to="/reminders">Reminders</NavLink>
          <NavLink to="/settings">Settings</NavLink>
        </div>

        {/* Built With */}
        <div>
          <h4>Built with</h4>

          <span>React + Vite +</span>
          <span> FastAPI + Python </span>
          <span>SQLAlchemy + </span>
          <span>Docker - ready</span>
        </div>
      </div>

      <div className="footer-bottom">
        <span>© 2026 Nova AI Voice Assistant Vivek Kumar</span>

        <span>
          Secure server-side AI · Responsive · Deployment ready
        </span>
      </div>
    </footer>
  );
}

/* =========================================================
   MAIN LAYOUT
========================================================= */

function Layout({ children }) {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("voice_token");
    localStorage.removeItem("voice_user");

    navigate("/login");
  };

  const links = [
    ["/dashboard", "Dashboard", LayoutDashboard],
    ["/chat", "AI Chat", MessageSquare],
    ["/documents", "Documents", FileText],
    ["/notes", "Notes", StickyNote],
    ["/reminders", "Reminders", Bell],
    ["/settings", "Settings", Settings],
  ];

  return (
    <div className="app-shell">
      {/* Sidebar */}
      <aside className={open ? "sidebar open" : "sidebar"}>
        <div className="brand">
          <div className="brand-icon">
            <Bot size={24} />
          </div>

          <div>
            <b>Nova</b>
            <small>AI Assistant</small>
          </div>
        </div>

        <nav>
          {links.map(([to, label, Icon]) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                isActive ? "active" : ""
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <button className="logout" onClick={logout}>
          <LogOut size={18} />
          Logout
        </button>
      </aside>

      {/* Main */}
      <div className="main">
        <header className="topbar">
          <button
            className="icon-btn mobile-menu"
            onClick={() => setOpen(!open)}
          >
            {open ? <X /> : <Menu />}
          </button>

          <div>
            <strong>AI Voice Assistant</strong>

            <span className="online">
              <i />
              Online
            </span>
          </div>

          <button
            className="profile-chip"
            onClick={() => navigate("/settings")}
          >
            <Sparkles size={16} />
            Profile
          </button>
        </header>

        <main>{children}</main>

        <Footer />
      </div>
    </div>
  );
}

/* =========================================================
   AUTH CARD
========================================================= */

function AuthCard({ title, subtitle, children }) {
  return (
    <div className="auth-page">
      <div>
        <div className="auth-brand">
          <div className="brand-icon large">
            <Bot />
          </div>

          <h1>Nova</h1>

          <p>Your intelligent voice workspace</p>
        </div>

        <section className="auth-card">
          <h2>{title}</h2>

          <p>{subtitle}</p>

          {children}
        </section>
      </div>
    </div>
  );
}

/* =========================================================
   LOGIN
========================================================= */

function Login() {
  const [form, setForm] = useState({
    username: "",
    password: "",
  });

  const [error, setError] = useState("");

  const nav = useNavigate();

  useEffect(() => {
    if (
      new URLSearchParams(window.location.search).get("session") ===
      "expired"
    ) {
      setError("Your login session expired. Please sign in again.");
    }
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const d = await api("/api/auth/login", {
        method: "POST",
        body: JSON.stringify(form),
      });

      localStorage.setItem("voice_token", d.access_token);
      localStorage.setItem("voice_user", JSON.stringify(d.user));

      nav("/dashboard");
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <AuthCard
      title="Welcome back"
      subtitle="Sign in to your personal AI assistant"
    >
      <form onSubmit={submit}>
        {error && <div className="error">{error}</div>}

        <input
          required
          placeholder="Username"
          value={form.username}
          onChange={(e) =>
            setForm({
              ...form,
              username: e.target.value,
            })
          }
        />

        <input
          required
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={(e) =>
            setForm({
              ...form,
              password: e.target.value,
            })
          }
        />

        <button className="primary full">
          Sign in
        </button>
      </form>

      <div className="auth-links">
        <NavLink to="/forgot-password">
          Forgot password?
        </NavLink>

        <NavLink to="/register">
          Create account
        </NavLink>
      </div>
    </AuthCard>
  );
}

/* =========================================================
   REGISTER
========================================================= */

function Register() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    full_name: "",
  });

  const [error, setError] = useState("");

  const nav = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const d = await api("/api/auth/register", {
        method: "POST",
        body: JSON.stringify(form),
      });

      localStorage.setItem("voice_token", d.access_token);
      localStorage.setItem("voice_user", JSON.stringify(d.user));

      nav("/dashboard");
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <AuthCard
      title="Create your account"
      subtitle="Save chats, notes, documents and reminders"
    >
      <form onSubmit={submit}>
        {error && <div className="error">{error}</div>}

        <input
          required
          placeholder="Full name"
          value={form.full_name}
          onChange={(e) =>
            setForm({
              ...form,
              full_name: e.target.value,
            })
          }
        />

        <input
          required
          minLength="3"
          placeholder="Username"
          value={form.username}
          onChange={(e) =>
            setForm({
              ...form,
              username: e.target.value,
            })
          }
        />

        <input
          required
          type="email"
          placeholder="Email"
          value={form.email}
          onChange={(e) =>
            setForm({
              ...form,
              email: e.target.value,
            })
          }
        />

        <input
          required
          minLength="8"
          type="password"
          placeholder="Password (8+ characters)"
          value={form.password}
          onChange={(e) =>
            setForm({
              ...form,
              password: e.target.value,
            })
          }
        />

        <button className="primary full">
          Create account
        </button>
      </form>

      <div className="auth-links">
        <NavLink to="/login">
          Already have an account?
        </NavLink>
      </div>
    </AuthCard>
  );
}

/* =========================================================
   FORGOT PASSWORD
========================================================= */

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const send = async (e) => {
    e.preventDefault();

    setError("");
    setMsg("");

    try {
      const d = await api("/api/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });

      setMsg(d.message);
      setSent(true);
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <AuthCard
      title="Forgot password"
      subtitle="Enter your registered email and we will send you a secure reset link"
    >
      {error && <div className="error">{error}</div>}

      {msg && <div className="success">{msg}</div>}

      {!sent && (
        <form onSubmit={send}>
          <input
            required
            type="email"
            placeholder="Registration email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <button className="primary full">
            Send reset link
          </button>
        </form>
      )}

      {sent && (
        <p className="muted">
          Check your inbox (and Spam/Junk folder). The link expires in 30
          minutes.
        </p>
      )}

      <div className="auth-links">
        <NavLink to="/login">
          Back to login
        </NavLink>
      </div>
    </AuthCard>
  );
}

/* =========================================================
   RESET PASSWORD
========================================================= */

function ResetPassword() {
  const [params] = useSearchParams();

  const token = params.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const nav = useNavigate();

  const submit = async (e) => {
    e.preventDefault();

    setError("");
    setMsg("");

    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const d = await api("/api/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({
          token,
          new_password: password,
        }),
      });

      setMsg(d.message);

      setTimeout(() => {
        nav("/login");
      }, 1200);
    } catch (e) {
      setError(e.message);
    }
  };

  if (!token) {
    return (
      <AuthCard
        title="Invalid reset link"
        subtitle="This password reset link is missing or invalid."
      >
        <div className="error">
          Please request a new reset link.
        </div>

        <div className="auth-links">
          <NavLink to="/forgot-password">
            Request reset link
          </NavLink>
        </div>
      </AuthCard>
    );
  }

  return (
    <AuthCard
      title="Set new password"
      subtitle="Choose a new password for your Nova AI Assistant account"
    >
      {error && <div className="error">{error}</div>}

      {msg && <div className="success">{msg}</div>}

      <form onSubmit={submit}>
        <input
          required
          minLength="8"
          type="password"
          placeholder="New password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <input
          required
          minLength="8"
          type="password"
          placeholder="Confirm new password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
        />

        <button className="primary full">
          Reset password
        </button>
      </form>

      <div className="auth-links">
        <NavLink to="/login">
          Back to login
        </NavLink>
      </div>
    </AuthCard>
  );
}

/* =========================================================
   DASHBOARD
========================================================= */

function Dashboard() {
  const [stats, setStats] = useState({
    conversations: 0,
    notes: 0,
    reminders: 0,
    documents: 0,
  });

  const user = JSON.parse(
    localStorage.getItem("voice_user") || "{}"
  );

  useEffect(() => {
    api("/api/dashboard/stats")
      .then(setStats)
      .catch(() => {});
  }, []);

  return (
    <>
      <div className="hero hero-animated">
        <div className="hero-copy">
          <span className="eyebrow">
            PERSONAL AI WORKSPACE
          </span>

          <h1>
            Hello,{" "}
            {user.full_name || user.username || "there"} 👋
          </h1>

          <p>
            Talk, type, upload documents and let Nova handle your everyday
            tasks.
          </p>
        </div>

        <NavLink to="/chat" className="primary">
          <Mic2 size={18} />
          Start assistant
        </NavLink>
      </div>

      <div className="stat-grid">
        {[
          ["Conversations", stats.conversations, MessageSquare],
          ["Saved notes", stats.notes, StickyNote],
          ["Pending reminders", stats.reminders, Bell],
          ["PDF documents", stats.documents, FileText],
        ].map(([label, value, Icon]) => (
          <div className="stat-card" key={label}>
            <div className="stat-icon">
              <Icon size={20} />
            </div>

            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>

      <div className="dashboard-banner">
        <div className="banner-orb orb-a" />
        <div className="banner-orb orb-b" />

        <Sparkles size={20} />

        <div>
          <strong>Nova is ready</strong>

          <span>
            Voice input, AI chat, PDF knowledge and productivity tools in one
            place.
          </span>
        </div>

        <NavLink to="/chat" className="banner-link">
          Open AI Chat →
        </NavLink>
      </div>

      <div className="grid-2">
        <div className="panel">
          <h3>What you can say</h3>

          <ul className="capabilities">
            <li>“What’s the weather in Delhi?”</li>
            <li>“Search Python tutorials on Google”</li>
            <li>“Take a note: prepare my resume”</li>
            <li>“Remind me to call at 6 PM”</li>
            <li>“Wikipedia Alan Turing”</li>
            <li>“Define artificial intelligence”</li>
          </ul>
        </div>

        <div className="panel">
          <h3>PDF questions</h3>

          <p className="muted">
            Upload a PDF from Documents, then select that PDF in AI Chat.
            Nova will use the extracted PDF text to answer document questions.
          </p>

          <NavLink className="secondary" to="/documents">
            Upload a PDF
          </NavLink>
        </div>
      </div>
    </>
  );
}

/* =========================================================
   CHAT
========================================================= */

function Chat() {
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [listening, setListening] = useState(false);
  const [docs, setDocs] = useState([]);
  const [doc, setDoc] = useState("");
  const [aiConnected, setAiConnected] = useState(false);
  const [status, setStatus] = useState("");

  useEffect(() => {
    api("/api/chat/history")
      .then(setMessages)
      .catch(() => {});

    api("/api/documents")
      .then(setDocs)
      .catch(() => {});

    api("/api/chat/status")
      .then((d) => setAiConnected(Boolean(d.connected)))
      .catch(() => setAiConnected(false));
  }, []);

  const speak = (t) => {
    if ("speechSynthesis" in window) {
      speechSynthesis.cancel();

      const u = new SpeechSynthesisUtterance(t);
      u.rate = 1;

      speechSynthesis.speak(u);
    }
  };

  const send = async (value) => {
    const m = (value ?? text).trim();

    if (!m) return;

    setText("");
    setStatus("");

    setMessages((x) => [
      ...x,
      {
        role: "user",
        message: m,
      },
    ]);

    try {
      const d = await api("/api/chat/message", {
        method: "POST",
        body: JSON.stringify({
          message: m,
          document_id: doc ? Number(doc) : null,
        }),
      });

      setMessages((x) => [
        ...x,
        {
          role: "assistant",
          message: d.response,
        },
      ]);

      speak(d.response);

      if (d.action?.type === "open_url") {
        window.open(
          d.action.url,
          "_blank",
          "noopener,noreferrer"
        );
      }
    } catch (e) {
      setStatus(e.message);

      setMessages((x) => [
        ...x,
        {
          role: "assistant",
          message: e.message,
        },
      ]);
    }
  };

  const startVoice = () => {
    const SR =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SR) {
      alert(
        "Speech recognition is not supported in this browser. Try Chrome or Edge."
      );
      return;
    }

    const r = new SR();

    r.lang = "en-IN";
    r.interimResults = false;
    r.maxAlternatives = 1;

    r.onstart = () => setListening(true);

    r.onend = () => setListening(false);

    r.onerror = () => setListening(false);

    r.onresult = (e) =>
      send(e.results[0][0].transcript);

    r.start();
  };

  const clear = async () => {
    try {
      await api("/api/chat/history", {
        method: "DELETE",
      });

      setMessages([]);
    } catch (e) {
      setStatus(e.message);
    }
  };

  return (
    <div className="chat-page">
      <div className="panel chat-panel">
        {/* Chat Header */}
        <div className="chat-head">
          <div>
            <h2>Nova AI</h2>

            <p>
              Voice + text assistant ·{" "}
              <span
                className={
                  aiConnected
                    ? "ai-status connected"
                    : "ai-status"
                }
              >
                {aiConnected
                  ? "OpenAI connected"
                  : "OpenAI not configured"}
              </span>
            </p>
          </div>

          <div className="chat-tools">
            <select
              value={doc}
              onChange={(e) => setDoc(e.target.value)}
            >
              <option value="">
                General assistant
              </option>

              {docs.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.filename}
                </option>
              ))}
            </select>

            <button className="secondary" onClick={clear}>
              Clear
            </button>
          </div>
        </div>

        {/* Status */}
        {status && (
          <div className="chat-notice error">
            {status}
          </div>
        )}

        {/* Messages */}
        <div className="messages">
          {messages.length === 0 && (
            <div className="empty-chat">
              <Bot size={40} />

              <h3>How can I help?</h3>

              <p>
                Ask anything, or select a PDF first for document questions.
              </p>
            </div>
          )}

          {messages.map((m, i) => (
            <div
              key={i}
              className={
                m.role === "user"
                  ? "message user"
                  : "message assistant"
              }
            >
              <div className="avatar">
                {m.role === "user" ? "You" : "N"}
              </div>

              <div>
                <span>
                  {m.role === "user" ? "You" : "Nova"}
                </span>

                <p>{m.message}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Composer */}
        <div className="composer">
          <button
            className={
              listening ? "mic listening" : "mic"
            }
            onClick={startVoice}
          >
            <Mic2 />
          </button>

          <input
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) =>
              e.key === "Enter" && send()
            }
            placeholder="Type a command or question..."
          />

          <button
            className="primary"
            onClick={() => send()}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

/* =========================================================
   DOCUMENTS
========================================================= */

function Documents() {
  const [docs, setDocs] = useState([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const load = () =>
    api("/api/documents")
      .then(setDocs)
      .catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const upload = async (e) => {
    const file = e.target.files?.[0];

    e.target.value = "";

    if (!file) return;

    setError("");

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please select a PDF file.");
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setError("PDF must be 15 MB or smaller.");
      return;
    }

    setBusy(true);

    const fd = new FormData();
    fd.append("file", file);

    try {
      await api("/api/documents/upload", {
        method: "POST",
        body: fd,
      });

      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  };

  const del = async (id) => {
    if (!confirm("Delete this document?")) return;

    try {
      await api(`/api/documents/${id}`, {
        method: "DELETE",
      });

      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="panel">
      <div className="section-head">
        <div>
          <h2>PDF Knowledge Base</h2>

          <p className="muted">
            Upload a PDF here. Then open AI Chat, select the PDF, and ask
            questions about its content.
          </p>
        </div>

        <label className="primary upload-btn">
          {busy ? "Uploading..." : "Upload PDF"}

          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={upload}
            disabled={busy}
          />
        </label>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="doc-grid">
        {docs.map((d) => (
          <div className="doc-card" key={d.id}>
            <FileText />

            <div>
              <b>{d.filename}</b>

              <small>
                {new Date(d.created_at).toLocaleString()}
              </small>
            </div>

            <button
              className="danger-icon"
              onClick={() => del(d.id)}
            >
              ×
            </button>
          </div>
        ))}

        {docs.length === 0 && (
          <div className="empty">
            No PDFs uploaded yet. Click Upload PDF to add one.
          </div>
        )}
      </div>
    </div>
  );
}

/* =========================================================
   NOTES
========================================================= */

function Notes() {
  const [notes, setNotes] = useState([]);
  const [content, setContent] = useState("");
  const [error, setError] = useState("");

  const load = () =>
    api("/api/notes")
      .then(setNotes)
      .catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const add = async () => {
    if (!content.trim()) return;

    setError("");

    try {
      await api("/api/notes", {
        method: "POST",
        body: JSON.stringify({
          content,
        }),
      });

      setContent("");

      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const del = async (id) => {
    try {
      await api(`/api/notes/${id}`, {
        method: "DELETE",
      });

      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="panel">
      <div className="section-head">
        <div>
          <h2>Notes</h2>

          <p className="muted">
            Save ideas by typing or saying “take a note”.
          </p>
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="inline-form">
        <input
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={(e) =>
            e.key === "Enter" && add()
          }
          placeholder="Write a new note..."
        />

        <button className="primary" onClick={add}>
          Add note
        </button>
      </div>

      <div className="list">
        {notes.map((n) => (
          <div className="list-item" key={n.id}>
            <div>
              <b>{n.content}</b>

              <small>
                {new Date(n.created_at).toLocaleString()}
              </small>
            </div>

            <button
              className="danger-icon"
              onClick={() => del(n.id)}
            >
              ×
            </button>
          </div>
        ))}

        {notes.length === 0 && (
          <div className="empty">
            No notes yet.
          </div>
        )}
      </div>
    </div>
  );
}

/* =========================================================
   REMINDERS
========================================================= */

function Reminders() {
  const [items, setItems] = useState([]);

  const [form, setForm] = useState({
    title: "",
    remind_at: "",
  });

  const [error, setError] = useState("");

  const load = () =>
    api("/api/reminders")
      .then(setItems)
      .catch((e) => setError(e.message));

  useEffect(() => {
    load();
  }, []);

  const add = async () => {
    if (
      !form.title.trim() ||
      !form.remind_at.trim()
    ) {
      return;
    }

    setError("");

    try {
      await api("/api/reminders", {
        method: "POST",
        body: JSON.stringify(form),
      });

      setForm({
        title: "",
        remind_at: "",
      });

      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const done = async (id) => {
    try {
      await api(
        `/api/reminders/${id}/complete`,
        {
          method: "PATCH",
        }
      );

      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  const del = async (id) => {
    try {
      await api(`/api/reminders/${id}`, {
        method: "DELETE",
      });

      await load();
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div className="panel">
      <h2>Reminders</h2>

      <p className="muted">
        Create and manage assistant reminders.
      </p>

      {error && <div className="error">{error}</div>}

      <div className="inline-form">
        <input
          value={form.title}
          onChange={(e) =>
            setForm({
              ...form,
              title: e.target.value,
            })
          }
          placeholder="Reminder title"
        />

        <input
          value={form.remind_at}
          onChange={(e) =>
            setForm({
              ...form,
              remind_at: e.target.value,
            })
          }
          onKeyDown={(e) =>
            e.key === "Enter" && add()
          }
          placeholder="e.g. tomorrow 6 PM"
        />

        <button className="primary" onClick={add}>
          Add
        </button>
      </div>

      <div className="list">
        {items.map((r) => (
          <div
            className={
              r.is_done
                ? "list-item done"
                : "list-item"
            }
            key={r.id}
          >
            <div>
              <b>{r.title}</b>

              <small>{r.remind_at}</small>
            </div>

            <div className="actions">
              {!r.is_done && (
                <button
                  className="secondary"
                  onClick={() => done(r.id)}
                >
                  Complete
                </button>
              )}

              <button
                className="danger-icon"
                onClick={() => del(r.id)}
              >
                ×
              </button>
            </div>
          </div>
        ))}

        {items.length === 0 && (
          <div className="empty">
            No reminders yet.
          </div>
        )}
      </div>
    </div>
  );
}

/* =========================================================
   SETTINGS
========================================================= */

function SettingsPage() {
  const [s, setS] = useState({
    theme: "dark",
    voice_rate: 175,
    voice_enabled: true,
  });

  const [saved, setSaved] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/api/settings")
      .then((d) => {
        setS(d);

        if (d.theme === "light") {
          document.body.classList.add("light");
        } else {
          document.body.classList.remove("light");
        }
      })
      .catch((e) => setError(e.message));
  }, []);

  const save = async () => {
    try {
      const d = await api("/api/settings", {
        method: "PUT",
        body: JSON.stringify(s),
      });

      setS(d);
      setSaved(true);

      setTimeout(() => {
        setSaved(false);
      }, 1500);

      if (d.theme === "light") {
        document.body.classList.add("light");
      } else {
        document.body.classList.remove("light");
      }
    } catch (e) {
      setError(e.message);
    }
  };

  const user = JSON.parse(
    localStorage.getItem("voice_user") || "{}"
  );

  return (
    <div className="settings-grid">
      {/* Profile */}
      <div className="panel">
        <h2>Profile</h2>

        <div className="profile-card">
          <div className="profile-avatar">
            {(user.full_name ||
              user.username ||
              "N")[0].toUpperCase()}
          </div>

          <div>
            <b>
              {user.full_name || user.username}
            </b>

            <small>
              @{user.username}
            </small>

            <small>{user.email}</small>
          </div>
        </div>
      </div>

      {/* Assistant Settings */}
      <div className="panel">
        <h2>Assistant settings</h2>

        {error && (
          <div className="error">
            {error}
          </div>
        )}

        <label>
          Theme

          <select
            value={s.theme}
            onChange={(e) =>
              setS({
                ...s,
                theme: e.target.value,
              })
            }
          >
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
        </label>

        <label>
          Voice rate

          <input
            type="range"
            min="80"
            max="260"
            value={s.voice_rate}
            onChange={(e) =>
              setS({
                ...s,
                voice_rate: Number(e.target.value),
              })
            }
          />
        </label>

        <label className="check">
          <input
            type="checkbox"
            checked={s.voice_enabled}
            onChange={(e) =>
              setS({
                ...s,
                voice_enabled: e.target.checked,
              })
            }
          />

          Enable browser voice responses
        </label>

        <button
          className="primary"
          onClick={save}
        >
          {saved ? "Saved ✓" : "Save settings"}
        </button>
      </div>
    </div>
  );
}

/* =========================================================
   APP ROUTES
========================================================= */

export default function App() {
  return (
    <AppErrorBoundary>
      <Routes>
        {/* Authentication */}
        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route
          path="/forgot-password"
          element={<ForgotPassword />}
        />

        <Route
          path="/reset-password"
          element={<ResetPassword />}
        />

        {/* Protected Routes */}
        <Route element={<ProtectedLayout />}>
          <Route
            path="/"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/chat"
            element={<Chat />}
          />

          <Route
            path="/documents"
            element={<Documents />}
          />

          <Route
            path="/notes"
            element={<Notes />}
          />

          <Route
            path="/reminders"
            element={<Reminders />}
          />

          <Route
            path="/settings"
            element={<SettingsPage />}
          />

          <Route
            path="*"
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />
        </Route>
      </Routes>
    </AppErrorBoundary>
  );
}