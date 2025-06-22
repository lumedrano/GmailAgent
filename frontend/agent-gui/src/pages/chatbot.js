import React, { useState, useEffect, useRef } from "react";
import { marked } from "marked";
import DOMPurify from "dompurify";
import { AIChatInput } from "../components/ui/ai-chat-input";
import { TextShimmer } from "../components/ui/text-shimmer";
import logo from "../components/images/logo.png";
import { LoaderIcon, CheckCircle2Icon } from "lucide-react";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      text: "Hi there! 👋 Welcome to Echo Beta. Give me any task like sending an email, checking unread emails, or replying to one.",
      type: "incoming",
    },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [displayedText, setDisplayedText] = useState("");
  const [toolStatus, setToolStatus] = useState([]);
  const chatboxRef = useRef(null);

  const scrollToBottom = () => {
    chatboxRef.current?.scrollTo({
      top: chatboxRef.current.scrollHeight,
      behavior: "smooth",
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, displayedText, toolStatus, isTyping]);

  const typeWriterEffect = (text, onFinish) => {
    let index = 0;
    setDisplayedText("");

    const interval = setInterval(() => {
      setDisplayedText((prev) => prev + text[index]);
      index++;
      if (index === text.length) {
        clearInterval(interval);
        onFinish();
      }
    }, 20);
  };

  const sendMessage = async (userMsg) => {
    if (!userMsg.trim()) return;

    setMessages((msgs) => [...msgs, { text: userMsg, type: "outgoing" }]);
    setIsTyping(true);
    setToolStatus([]);

    try {
      const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });
      const data = await res.json();
      let reply = data.response || "No response from server.";

      const toolCallRegex = /Running:\s*(.*?)\n/g;
      let match;
      let newToolStatus = [];
      while ((match = toolCallRegex.exec(reply)) !== null) {
        newToolStatus.push({ tool: match[1], done: false });
      }
      setToolStatus(newToolStatus);

      const cleanedReply = reply.replace(/Running: .*?\n/g, "");

      typeWriterEffect(cleanedReply, () => {
        setMessages((msgs) => [...msgs, { text: cleanedReply, type: "incoming" }]);
        setDisplayedText("");
        setIsTyping(false);

        setToolStatus((prev) =>
          prev.map((item) => ({ ...item, done: true }))
        );
      });
    } catch {
      const errorMsg = "Error communicating with server.";
      setMessages((msgs) => [...msgs, { text: errorMsg, type: "incoming" }]);
      setIsTyping(false);
    }
  };

  const renderToolStatus = () =>
    toolStatus.map((item, idx) => (
      <li
        key={`tool-${idx}`}
        className="chat incoming"
        style={{
          display: "flex",
          justifyContent: "flex-start",
          fontSize: "14px",
          color: "#555",
        }}
      >
        <div
          className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-sm"
          style={{
            backgroundColor: "#f1f1f1",
            color: "#333",
            whiteSpace: "nowrap",
          }}
        >
          {item.done ? (
            <CheckCircle2Icon className="w-4 h-4 text-green-600" />
          ) : (
            <LoaderIcon className="w-4 h-4 animate-spin text-blue-500" />
          )}
          {item.tool}
        </div>
      </li>
    ));

  const loadingTexts = [
    "Thinking...",
    "Crafting a reply...",
    "Generating response...",
    "Please hold on...",
    "Summoning AI magic...",
  ];

  const renderTypingIndicator = () => {
    const randomText =
      loadingTexts[Math.floor(Math.random() * loadingTexts.length)];
    return (
      <li
        className="chat incoming"
        style={{
          display: "flex",
          justifyContent: "flex-start",
          paddingLeft: "4px",
        }}
      >
        <TextShimmer
          duration={1.2}
          className="font-mono text-base [--base-color:#444] [--base-gradient-color:#999]"
        >
          {randomText}
        </TextShimmer>
      </li>
    );
  };

  const renderMessages = () => {
  return messages.map((msg, i) => (
    <li
      key={i}
      className={`chat ${msg.type}`}
      style={{
        display: "flex",
        justifyContent: msg.type === "outgoing" ? "flex-end" : "flex-start",
        alignItems: "flex-start", // Aligns logo + text at top
        gap: msg.type === "incoming" ? "8px" : "0", // Space between logo & text
      }}
    >
      {msg.type === "incoming" && (
        <img
          src={logo}
          alt="Bot"
          style={{
            width: "32px",
            height: "32px",
            borderRadius: "50%", // makes it circular like a profile pic
            objectFit: "cover",
            marginTop: "2px",
          }}
        />
      )}

      <div
        style={{
          backgroundColor: msg.type === "outgoing" ? "#007bff" : "#e5e5ea",
          color: msg.type === "outgoing" ? "#fff" : "#000",
          padding: "8px 12px",
          borderRadius: "16px",
          maxWidth: "80%",
          whiteSpace: "pre-wrap",
          wordWrap: "break-word",
          fontSize: "16px",
        }}
        dangerouslySetInnerHTML={{
          __html: DOMPurify.sanitize(
            marked.parse(msg.text, { breaks: true }).replace(/<\/?p>/g, "")
          ),
        }}
      />
    </li>
  ));
};


  return (
    <>
      {/* Title + Animated Logo */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "12px",
          marginTop: "24px",
          marginBottom: "12px",
          userSelect: "none",
        }}
      >
        <TextShimmer
          duration={1.5}
          className="font-poppins font-semibold text-4xl"
          style={{
            fontFamily: "'Poppins', sans-serif",
            fontWeight: 600,
            userSelect: "none",
          }}
        >
          Echo
        </TextShimmer>

       <img
  src={logo}
  alt="Logo"
  style={{
    width: "60px",
    height: "60px",
    objectFit: "contain",
    animationName: "rotateShakePause",
    animationDuration: "3s",     // 0.5s shaking + ~2.5s pause
    animationTimingFunction: "ease-in-out",
    animationIterationCount: "infinite",
    transformOrigin: "bottom center",
  }}
/>


        
      </div>

      {/* Username and Logout Button */}
      <div
        style={{
          position: "fixed",
          top: "16px",
          right: "16px",
          display: "flex",
          alignItems: "center",
          gap: "12px",
          zIndex: 9999,
          userSelect: "none",
        }}
      >
        <span style={{ fontSize: "18px", fontWeight: "bold" }}>Luigi</span>
        <button
          style={{
            backgroundColor: "transparent",
            color: "#000",
            border: "1px solid #000",
            padding: "6px 12px",
            borderRadius: "4px",
            cursor: "pointer",
            fontSize: "14px",
          }}
          onClick={async () => {
            try {
              const res = await fetch("http://127.0.0.1:5000/logout", {
                method: "POST",
              });
              const data = await res.json();

              if (res.ok) {
                alert(data.message);
              } else {
                alert(`Logout failed: ${data.error}`);
              }
            } catch (error) {
              alert("Logout error: " + error.message);
            }
          }}
        >
          Logout
        </button>

      </div>

      {/* Chatbot Container */}
      <div
        className="chatbot-container"
        style={{
          width: "100%",
          maxWidth: "600px",
          margin: "auto",
          display: "flex",
          flexDirection: "column",
          height: "calc(100vh - 120px)",
          padding: "0",
          boxSizing: "border-box",
          position: "relative",
        }}
      >
        <ul
          className="chatbox"
          ref={chatboxRef}
          style={{
            flexGrow: 1,
            overflowY: "auto",
            padding: "16px",
            listStyle: "none",
            display: "flex",
            flexDirection: "column",
            gap: "6px",
            marginTop: "0",
          }}
        >
          {renderMessages()}
          {renderToolStatus()}
          {displayedText && (
            <li
              className="chat incoming"
              style={{ display: "flex", justifyContent: "flex-start" }}
            >
              <div
                style={{
                  backgroundColor: "#e5e5ea",
                  color: "#000",
                  padding: "8px 12px",
                  borderRadius: "16px",
                  maxWidth: "80%",
                  whiteSpace: "pre-wrap",
                  wordWrap: "break-word",
                  fontSize: "16px",
                }}
                dangerouslySetInnerHTML={{
                  __html: DOMPurify.sanitize(
                    marked.parse(displayedText, { breaks: true }).replace(/<\/?p>/g, "")
                  ),
                }}
              />
            </li>
          )}
          {isTyping && !displayedText && renderTypingIndicator()}
        </ul>

        <div style={{ padding: "8px 16px" }}>
          <AIChatInput onSend={sendMessage} />
        </div>
      </div>

      {/* Animation CSS */}
      <style>
        {`
          @keyframes peekWave {
            0% {
              transform: translateY(60px) scale(0.8);
              opacity: 0;
            }
            30% {
              transform: translateY(0) scale(1);
              opacity: 1;
            }
            40%, 80% {
              opacity: 1;
            }
            40% {
              transform: translateX(-10px) translateY(0) scale(1);
            }
            50% {
              transform: translateX(10px) translateY(0) scale(1);
            }
            60% {
              transform: translateX(-8px) translateY(0) scale(1);
            }
            70% {
              transform: translateX(8px) translateY(0) scale(1);
            }
            80% {
              transform: translateX(0) translateY(0) scale(1);
            }
            100% {
              transform: translateY(60px) scale(0.8);
              opacity: 0;
            }
          }

          @keyframes rotateShakePause {
  0% { transform: rotate(0deg); }
  10% { transform: rotate(-10deg); }
  20% { transform: rotate(10deg); }
  30% { transform: rotate(-10deg); }
  40% { transform: rotate(10deg); }
  50% { transform: rotate(0deg); }
  100% { transform: rotate(0deg); } /* Pause until restart */
}


        `}
      </style>
    </>
  );
}
