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
import type { KeyboardEvent } from 'react';
import './ChatScreen.css';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

const ChatScreen: React.FC = () => {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);
  const [input, setInput] = useState('');
  const [cooldown, setCooldown] = useState(false);
  const [cooldownTime, setCooldownTime] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const cooldownRef = useRef<NodeJS.Timeout | null>(null);

  const startCooldown = (seconds: number) => {
    setCooldown(true);
    setCooldownTime(seconds);

    cooldownRef.current = setInterval(() => {
      setCooldownTime((time) => {
        if (time <= 1) {
          clearInterval(cooldownRef.current!);
          setCooldown(false);
          return 0;
        }
        return time - 1;
      });
    }, 1000);
  };

  const sendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || cooldown) return;

    // Bloquear YA para evitar enviar multiples mensajes
    setCooldown(true);
    setCooldownTime(10);  // ponemos 10 de inicio, countdown empezará luego

    const userMsg = { sender: 'Tú', text: input.trim() };
    setMessages(prev => [...prev, userMsg]);
    const prompt = input.trim();
    setInput('');

    const botReply = await getLLMResponse(prompt);
    setMessages(prev => [...prev, { sender: 'LLM', text: botReply }]);

    // Ahora empieza el countdown dinámico
    cooldownRef.current = setInterval(() => {
      setCooldownTime(time => {
        if (time <= 1) {
          clearInterval(cooldownRef.current!);
          setCooldown(false);
          return 0;
        }
        return time - 1;
      });
    }, 1000);
  };


  const getLLMResponse = async (msg: string): Promise<string> => {
    try {
      const response = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: msg }),
      });
      const data = await response.json();
      return data.response || '[Respuesta vacía del modelo]';
    } catch (error) {
      console.error('Error conectando con el backend:', error);
      return '[Error al conectar con el modelo]';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLIonTextareaElement>) => {
    const allowed = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Tab'];
    if (input.length >= 500 && !allowed.includes(e.key)) {
      e.preventDefault();
    }
    if (e.key === 'Enter' && !e.shiftKey && !cooldown) {
      e.preventDefault();
      sendMessage();
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    return () => {
      if (cooldownRef.current) clearInterval(cooldownRef.current);
    };
  }, []);

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
              setInput(val.slice(0, 500));  // Limite 500 chars
            }}
            onKeyDown={handleKeyDown}
            placeholder="Haz tu pregunta..."
            className="chat-textarea"
          />
          <div className={`char-counter ${input.length > 490 ? 'red' : ''}`}>
            {input.length} / 500
          </div>
          <IonButton type="submit" disabled={input.trim().length === 0 || cooldown}>
            {cooldown ? `Envia en ${cooldownTime}s...` : 'Enviar'}
          </IonButton>
        </form>
      </IonFooter>
    </IonPage>
  );
};

export default ChatScreen;
