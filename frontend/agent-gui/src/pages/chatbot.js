// import React, { useState, useEffect, useRef } from "react";
// import { marked } from "marked";
// import DOMPurify from "dompurify";
// import { AIChatInput } from "../components/ui/ai-chat-input";

// export default function Chatbot() {
//   const [messages, setMessages] = useState([]);
//   const chatboxRef = useRef(null);

//   const scrollToBottom = () => {
//     chatboxRef.current?.scrollTo(0, chatboxRef.current.scrollHeight);
//   };

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   const sendMessage = async (userMsg) => {
//   if (!userMsg.trim()) return;

//   // Add user's message
//   setMessages((msgs) => [...msgs, { text: userMsg, type: "outgoing" }]);

//   try {
//     const res = await fetch("http://127.0.0.1:5000/chat", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ message: userMsg }),
//     });

//     const data = await res.json();
//     const fullReply = data.response || "No response from server.";

//     // Typing animation
//     let index = 0;
//     let currentText = "";
//     const typingId = Symbol(); // Unique ID to track typing

//     setMessages((msgs) => [...msgs, { text: "", type: "incoming", id: typingId }]);

//     const typeInterval = setInterval(() => {
//       index++;
//       currentText = fullReply.slice(0, index);
//       setMessages((msgs) =>
//         msgs.map((msg) =>
//           msg.id === typingId ? { ...msg, text: currentText } : msg
//         )
//       );
//       if (index >= fullReply.length) clearInterval(typeInterval);
//     }, 20); // Speed of typing

//   } catch {
//     setMessages((msgs) => [
//       ...msgs,
//       { text: "Error communicating with server.", type: "incoming" },
//     ]);
//   }
// };


//   return (
//     <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
//       <div
//         className="w-full max-w-3xl flex flex-col bg-white rounded-3xl shadow-xl overflow-hidden"
//         style={{ height: "90vh" }}
//       >
//         {/* Scrollable Chat Messages */}
//         <ul
//           ref={chatboxRef}
//           className="flex-1 overflow-y-auto px-6 py-4 space-y-4"
//           style={{ listStyle: "none", margin: 0 }}
//         >
//           {messages.map((msg, i) => (
//             <li
//               key={i}
//               className={`chat ${msg.type} w-full flex ${msg.type === "incoming" ? "justify-start" : "justify-end"}`}
//             >
//               <p
//                 className={`rounded-xl px-4 py-2 max-w-[75%] text-sm ${
//                   msg.type === "incoming"
//                     ? "bg-gray-200 text-gray-800"
//                     : "bg-blue-600 text-white"
//                 }`}
//                 dangerouslySetInnerHTML={{
//                   __html: DOMPurify.sanitize(marked.parse(msg.text)),
//                 }}
//               />
//             </li>
//           ))}
//         </ul>

//         {/* Chat Input at the bottom */}
//         <div className="border-t border-gray-200 bg-white p-4">
//           <AIChatInput onSend={sendMessage} />
//         </div>
//       </div>
//     </div>
//   );
// }
import React, { useState, useEffect, useRef } from "react";
import { marked } from "marked";
import DOMPurify from "dompurify";
import { AIChatInput } from "../components/ui/ai-chat-input";
import {TextShimmer} from '../components/ui/text-shimmer'

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { text: "Hi there!👋 This portion of our site is under construction but check back later!", type: "incoming" },
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [displayedText, setDisplayedText] = useState("");
  const chatboxRef = useRef(null);

  const scrollToBottom = () => {
    chatboxRef.current?.scrollTo({
      top: chatboxRef.current.scrollHeight,
      behavior: "smooth",
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, displayedText, isTyping]);

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

    try {
      const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });
      const data = await res.json();
      const reply = data.response || "No response from server.";

      // Animate the response with typewriter effect
      typeWriterEffect(reply, () => {
        setMessages((msgs) => [...msgs, { text: reply, type: "incoming" }]);
        setDisplayedText("");
        setIsTyping(false);
      });
    } catch {
      const errorMsg = "Error communicating with server.";
      setMessages((msgs) => [...msgs, { text: errorMsg, type: "incoming" }]);
      setIsTyping(false);
    }
  };

  const loadingTexts = [
  "Thinking...",
  "Crafting a reply...",
  "Generating response...",
  "Please hold on...",
  "Summoning AI magic...",
];

const renderTypingIndicator = () => {
  const randomText = loadingTexts[Math.floor(Math.random() * loadingTexts.length)];
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
        }}
      >
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
    <div
      className="chatbot-container"
      style={{
        width: "100%",
        maxWidth: "600px",
        margin: "auto",
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        padding: "16px",
        boxSizing: "border-box",
      }}
    >
      <ul
        className="chatbox"
        ref={chatboxRef}
        style={{
          flexGrow: 1,
          overflowY: "auto",
          padding: 0,
          listStyle: "none",
          display: "flex",
          flexDirection: "column",
          gap: "6px", // tight spacing
        }}
      >
        {renderMessages()}

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

      <div style={{ paddingTop: "8px" }}>
        <AIChatInput onSend={sendMessage} />
      </div>
    </div>
  );
}
