import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [user, setUser] = useState(null);
  const [userId, setUserId] = useState('');
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // Initialize with a sample user ID for testing
  useEffect(() => {
    setUserId('user-' + Math.random().toString(36).substr(2, 9));
  }, []);

  const handleSendMessage = async () => {
    if (!message.trim()) return;
    
    // Add user message to UI immediately
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setIsLoading(true);
    
    try {
      // Send message to backend API
      const response = await axios.post(
        `http://localhost:8000/api/${userId}/chat`,
        {
          message: message,
          conversation_id: currentConversationId
        }
      );
      
      // Add AI response to messages
      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      setCurrentConversationId(response.data.conversation_id);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="App">
      <header className="app-header">
        <h1>Todo AI Chatbot</h1>
        <div className="user-info">
          <input
            type="text"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            placeholder="Enter user ID"
            disabled={isLoading}
          />
        </div>
      </header>
      
      <div className="chat-container">
        <div className="messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`message ${msg.role}`}>
              <div className="message-content">{msg.content}</div>
              <div className="message-timestamp">
                {new Date(msg.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">Thinking...</div>
            </div>
          )}
        </div>
        
        <div className="input-area">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            rows="3"
            disabled={isLoading}
          />
          <button 
            onClick={handleSendMessage} 
            disabled={isLoading || !message.trim()}
            className="send-button"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;