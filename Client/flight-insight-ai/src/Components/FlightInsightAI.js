import React, { useState, useEffect, useRef } from 'react';
import { Send, Plane, Loader, Trash2, Settings } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import TypewriterEffect from './TypeWriterEffect';

const FlightInsightAI = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState(null);
  const [airlines, setAirlines] = useState([]);
  const messagesEndRef = useRef(null);
  const ws = useRef(null);

  useEffect(() => {
    fetch('http://localhost:8000/supported-airlines')
      .then(response => response.json())
      .then(data => setAirlines(data.airlines))
      .catch(error => console.error('Error fetching airlines:', error));

    ws.current = new WebSocket('ws://localhost:8000/ws');
    ws.current.onopen = () => console.log('WebSocket Connected');
    ws.current.onclose = () => console.log('WebSocket Disconnected');
    return () => {
      ws.current.close();
    };
  }, [error]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = () => {
    if (inputMessage.trim() === '') return;

    const newMessage = { type: 'user', content: inputMessage };
    setMessages((prevMessages) => [...prevMessages, newMessage]);
    setInputMessage('');
    setIsLoading(true);
    setIsStreaming(false);
    setError(null);

    ws.current.send(inputMessage);

    ws.current.onmessage = (event) => {
      if (event.data === '[END_OF_RESPONSE]') {
        setIsLoading(false);
        setIsStreaming(false);
      }
      else if (event.data === '[END_OF_ERROR_RESPONSE]') {
        setError('An error occurred. Please try again.');
        setIsLoading(false);
        setError('An error occurred with the Assistant. Please try again. Page will reload in 5 seconds.');
        setTimeout(() => window.location.reload(), 5000);
        ws.current.close();
      } 
      else {
        setIsStreaming(true);
        setMessages((prevMessages) => {
          const updatedMessages = [...prevMessages];
          const lastMessage = updatedMessages[updatedMessages.length - 1];
          if (lastMessage && lastMessage.type === 'ai') {
            return [
              ...updatedMessages.slice(0, -1),
              { ...lastMessage, content: lastMessage.content + event.data },
            ];
          } else {
            return [...updatedMessages, { type: 'ai', content: event.data }];
          }
        });
      }
    };

    ws.current.onerror = (error) => {
      console.error('WebSocket Error:', error);
    };
  };

  const clearChat = () => {
    setMessages([]);
  };

   return (
    <div className="flex flex-col h-screen bg-gray-800 text-gray-100">
      <header className="bg-blue-800 text-white p-3 shadow-md">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-semibold flex items-center">
            <Plane className="w-5 h-5 mr-2" /> Flight Insight AI
          </h1>
          <div className="flex space-x-2">
            <button onClick={clearChat} className="p-2 hover:bg-blue-700 rounded-full">
              <Trash2 className="w-5 h-5" />
            </button>
            <button className="p-2 hover:bg-blue-700 rounded-full">
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>
      <div className="flex-grow overflow-auto p-4 mx-auto max-w-3xl w-full">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-4xl text-gray-400 font-sans">
              ✈️ Ask me about <TypewriterEffect airlines={airlines} />
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                {message.type === 'ai' && (
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 mr-2 flex-shrink-0">
                    <span role="img" aria-label="robot">🤖</span>
                  </div>
                )}
                <div className={`max-w-sm p-3 rounded-lg ${
                  message.type === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700 text-white'
                }`}>
                  {message.type === 'user' ? (
                    message.content
                  ) : (
                    <ReactMarkdown
                      components={{
                        code({node, inline, className, children, ...props}) {
                          const match = /language-(\w+)/.exec(className || '')
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={oneDark}
                              language={match[1]}
                              PreTag="div"
                              {...props}
                            >{String(children).replace(/\n$/, '')}</SyntaxHighlighter>
                          ) : (
                            <code className={className} {...props}>
                              {children}
                            </code>
                          )
                        }
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  )}
                  {message.type === 'ai' && isStreaming && index === messages.length - 1 && (
                    <span className="inline-block animate-pulse ml-1">▋</span>
                  )}
                </div>
              </div>
            ))}
            {isLoading && !isStreaming && (
              <div className="flex justify-start items-center">
                <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600 mr-2 flex-shrink-0">
                  <span role="img" aria-label="robot">🤖</span>
                </div>
                <div className="bg-gray-700 p-3 rounded-lg flex items-center space-x-2">
                  <Loader className="animate-spin w-4 h-4" />
                  <span>AI is thinking...</span>
                </div>
              </div>
            )}
          </div>
        )}
        {error && (
          <div className="bg-red-500 text-white p-3 rounded-lg mt-4">
            {error}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-4 bg-gray-700">
        <div className="max-w-3xl mx-auto flex items-center space-x-2">
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask about flights, airlines, reviews..."
            className="flex-grow p-3 rounded-lg bg-gray-600 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSendMessage}
            disabled={isLoading || isStreaming}
            className="bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors duration-200 disabled:opacity-50"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default FlightInsightAI;