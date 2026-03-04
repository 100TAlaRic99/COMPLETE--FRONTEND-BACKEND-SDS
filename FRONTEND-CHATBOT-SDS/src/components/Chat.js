import React, { useState, useEffect, useRef } from 'react';
import api from '../api/axios';
import { Send, LogOut, History, Trash2, User, AlertCircle } from 'lucide-react';
import './Chat.css';

function Chat({ user, onLogout }) {
  const [inputText, setInputText] = useState('');
  const [analyzer, setAnalyzer] = useState('hybrid'); // vader, hybrid, llm
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    setLoading(true);
    setError('');

    // Add user message
    const userMessage = {
      type: 'user',
      text: inputText,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const payload = { text: inputText };
      if (analyzer && analyzer !== 'default') payload.analyzer = analyzer;
      const response = await api.post(
        '/api/analyze',
        payload
      );

      // Add bot response
      const botMessage = {
        type: 'bot',
        text: response.data.text,
        sentiment: response.data.sentiment,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
      setInputText('');
    } catch (err) {
      // for debugging, log the entire error object
      console.error('analysis error', err);
      // If unauthorized, force logout and show a clear message
      if (err.response?.status === 401) {
        setError('Session expired or unauthorized. Redirecting to login...');
        try { onLogout(); } catch (e) { /* ignore */ }
      } else {
        setError(
          err.response?.data?.error ||
          err.message ||
          'Failed to analyze sentiment'
        );
      }
      // Remove the user message if analysis failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await api.get('/api/history');
      setHistory(response.data.chats);
      setShowHistory(true);
    } catch (err) {
      setError('Failed to load history');
    }
  };

  const deleteHistoryItem = async (chatId) => {
    try {
      await api.delete(`/api/history/${chatId}`);
      setHistory(prev => prev.filter(item => item._id !== chatId));
    } catch (err) {
      setError('Failed to delete chat');
    }
  };

  const getSentimentColor = (label) => {
    switch (label) {
      case 'Positive':
        return '#10b981';
      case 'Negative':
        return '#ef4444';
      case 'Neutral':
        return '#6b7280';
      default:
        return '#6b7280';
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="header-left">
          <h1>Sentiment Analysis Chatbot</h1>
          <p>Analyze the sentiment of your text</p>
        </div>
        <div className="header-right">
          <button className="icon-button" onClick={loadHistory} title="View History">
            <History size={20} />
          </button>
          <div className="user-info">
            <User size={20} />
            <span>{user?.username}</span>
          </div>
          <button className="logout-button" onClick={onLogout}>
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={20} />
          <span>{error}</span>
          <button onClick={() => setError('')}>×</button>
        </div>
      )}

      <div className="chat-content">
        <div className="messages-container">
          {messages.length === 0 ? (
            <div className="empty-state">
              <p>Start a conversation by typing a message below!</p>
              <p className="empty-state-subtitle">
                I'll analyze the sentiment of your text and tell you if it's positive, negative, or neutral.
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} className={`message ${message.type}`}>
                {message.type === 'user' ? (
                  <div className="message-content user-message">
                    <p>{message.text}</p>
                  </div>
                ) : (
                  <div className="message-content bot-message">
                    <p className="analyzed-text">{message.text}</p>
                    <div 
                      className="sentiment-result"
                      style={{ borderLeftColor: getSentimentColor(message.sentiment.label) }}
                    >
                      <div className="sentiment-header">
                        <span className="sentiment-emoji">{message.sentiment.emoji}</span>
                        <span className="sentiment-label">{message.sentiment.label}</span>
                      </div>
                      <div className="sentiment-scores">
                        {message.sentiment.scores && (
                          <>
                            <div className="score-item">
                              <span className="score-label">Positive:</span>
                              <span className="score-value">
                                {(message.sentiment.scores.pos * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="score-item">
                              <span className="score-label">Neutral:</span>
                              <span className="score-value">
                                {(message.sentiment.scores.neu * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="score-item">
                              <span className="score-label">Negative:</span>
                              <span className="score-value">
                                {(message.sentiment.scores.neg * 100).toFixed(1)}%
                              </span>
                            </div>
                          </>
                        )}
                        <div className="score-item compound">
                          <span className="score-label">
                            {message.sentiment.combined_score !== undefined ? 'Combined:' : 'Compound:'}
                          </span>
                          <span className="score-value">
                            {(message.sentiment.combined_score || message.sentiment.compound || 0).toFixed(3)}
                          </span>
                        </div>
                        {message.sentiment.analyzer && (
                          <div className="score-item analyzer">
                            <span className="score-label">Analyzer:</span>
                            <span className="score-value analyzer-name">
                              {message.sentiment.provider 
                                ? `${message.sentiment.provider} (${message.sentiment.model || 'unknown'})`
                                : message.sentiment.analyzer}
                            </span>
                          </div>
                        )}
                        {message.sentiment.confidence !== undefined && (
                          <div className="score-item confidence">
                            <span className="score-label">Confidence:</span>
                            <span className="score-value">
                              {(message.sentiment.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                        )}
                        {message.sentiment.models_agree !== undefined && (
                          <div className="score-item agreement">
                            <span className="score-label">Models Agree:</span>
                            <span className="score-value">
                              {message.sentiment.models_agree ? '✓ Yes' : '✗ No'}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="input-form">
          <div className="input-group">
          <select
            value={analyzer}
            onChange={e => setAnalyzer(e.target.value)}
            disabled={loading}
            className="analyzer-select"
          >
            <option value="hybrid">Hybrid (default)</option>
            <option value="vader">VADER only</option>
            <option value="llm">LLM</option>
          </select>
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type your message here..."
            disabled={loading}
            className="message-input"
          />
        </div>
          <button type="submit" disabled={loading || !inputText.trim()} className="send-button">
            {loading ? (
              <span className="loading-spinner"></span>
            ) : (
              <Send size={20} />
            )}
          </button>
        </form>
      </div>

      {showHistory && (
        <div className="modal-overlay" onClick={() => setShowHistory(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Chat History</h2>
              <button className="close-button" onClick={() => setShowHistory(false)}>
                ×
              </button>
            </div>
            <div className="history-list">
              {history.length === 0 ? (
                <p className="empty-history">No chat history yet</p>
              ) : (
                history.map((item) => (
                  <div key={item._id} className="history-item">
                    <div className="history-text">
                      <p>{item.text}</p>
                      <div className="history-sentiment">
                        <span>{item.sentiment.emoji}</span>
                        <span>{item.sentiment.label}</span>
                      </div>
                    </div>
                    <div className="history-actions">
                      <span className="history-date">
                        {new Date(item.timestamp).toLocaleDateString()}
                      </span>
                      <button
                        className="delete-button"
                        onClick={() => deleteHistoryItem(item._id)}
                        title="Delete"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chat;
