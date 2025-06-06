import React, { useState, useRef, useEffect } from 'react';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonFooter,
  IonTextarea,
  IonButton
} from '@ionic/react';
import './ChatScreen.css';

const ChatScreen: React.FC = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const sendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { sender: 'Tú', text: input.trim() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');

    const botReply = await getLLMResponse(input);
    setMessages(prev => [...prev, { sender: 'LLM', text: botReply }]);
  };

  const getLLMResponse = async (msg: string): Promise<string> => {
    try {
      const response = await fetch('https://2943-201-223-112-22.ngrok-free.app', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: msg }),
      });

      const data = await response.json();
      return data.response || '[Respuesta vacía del modelo]';
    } catch (error) {
      console.error('Error conectando con el backend:', error);
      return '[Error al conectar con el modelo]';
    }
  };


  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar>
          <IonTitle>Chat Herencia Java</IonTitle>
        </IonToolbar>
      </IonHeader>

      <IonContent className="chat-content">
        {messages.length === 0 ? (
          <div className="welcome-container">
            <div className="welcome-message">
              <h2>👋 ¡Hola!</h2>
              <p>Pregúntame cualquier cosa sobre <strong>herencia en Java</strong> y te ayudaré encantado.</p>
            </div>
          </div>
        ) : (
          <div className="messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.sender === 'Tú' ? 'user' : 'bot'}`}>
                <strong>{msg.sender}:</strong> {msg.text}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </IonContent>

      <IonFooter>
        <form onSubmit={sendMessage} className="input-form">
          <IonTextarea
            value={input}
            onIonInput={e => {
              const val = e.detail.value ?? '';
              setInput(val.slice(0, 3000));
            }}
            onKeyDown={e => {
              const allowed = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Tab'];
              if (input.length >= 3000 && !allowed.includes(e.key)) {
                e.preventDefault();
              }
            }}
            placeholder="Haz tu pregunta..."
            className="chat-textarea"
          />
          <div className={`char-counter ${input.length > 2900 ? 'red' : ''}`}>
            {input.length} / 3000
          </div>
          <IonButton type="submit" disabled={input.trim().length === 0}>
            Enviar
          </IonButton>
        </form>
      </IonFooter>
    </IonPage>
  );
};

export default ChatScreen;
