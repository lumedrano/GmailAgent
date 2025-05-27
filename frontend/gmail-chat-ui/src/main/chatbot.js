//main code
import React, { useState, useEffect, useRef } from "react";
import { marked } from "marked";
import DOMPurify from "dompurify";
import "../App.css";
import logo from "../SHPE_logo.png";

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { text: "Hi there!👋\nThis portion of our site is under construction but check back later!", type: "incoming" },
  ]);
  const [input, setInput] = useState("");
  const chatboxRef = useRef(null);

  const scrollToBottom = () => {
    chatboxRef.current?.scrollTo(0, chatboxRef.current.scrollHeight);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setMessages([...messages, { text: input, type: "outgoing" }]);
    const userMsg = input;
    setInput("");

    try {
      const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg }),
      });
      const data = await res.json();
      const reply = data.response || "No response from server.";
      setMessages((msgs) => [...msgs, { text: reply, type: "incoming" }]);
    } catch {
      setMessages((msgs) => [...msgs, { text: "Error communicating with server.", type: "incoming" }]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <button className="chatbot-toggler" onClick={() => document.body.classList.toggle("show-chatbot")}>
        <span className="material-symbols-rounded">
          <img src={logo} alt="Chatbot Logo" className="chatbot-logo" />
        </span>
        <span className="material-symbols-outlined">close</span>
      </button>
      <div className="chatbot">
        <header>
          <h2>Gmail Agent</h2>
          <span className="close-btn material-symbols-outlined" onClick={() => document.body.classList.remove("show-chatbot")}>close</span>
        </header>
        <ul className="chatbox" ref={chatboxRef}>
          {messages.map((msg, i) => (
            <li key={i} className={`chat ${msg.type}`}>
              {msg.type === "incoming" && (
                <span className="material-symbols-rounded">
                  <img src={logo} alt="Chatbot Logo" className="chatbot-logo" />
                </span>
              )}
              <p dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(msg.text)) }} />
            </li>
          ))}
        </ul>
        <div className="chat-input">
          <textarea
            placeholder="Enter a message..."
            spellCheck="false"
            required
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
          ></textarea>
          <span id="send-btn" className="material-symbols-rounded" onClick={sendMessage}>
            send
          </span>
        </div>
      </div>
    </>
  );
}


// import React, { useState, useEffect, useRef } from "react";
// import { marked } from "marked";
// import DOMPurify from "dompurify";
// import "../styles/globals.css";  // Tailwind + your theme CSS
// import { PromptInputBox } from "../components/ui/ai-prompt-box"; // Adjust path if needed
// import logo from "../SHPE_logo.png";

// export default function Chatbot() {
//   const [messages, setMessages] = useState([
//     {
//       text: "Hi there!👋\nThis portion of our site is under construction but check back later!",
//       type: "incoming",
//     },
//   ]);
//   const chatboxRef = useRef<HTMLUListElement>(null);

//   // Scroll to bottom when messages update
//   useEffect(() => {
//     chatboxRef.current?.scrollTo(0, chatboxRef.current.scrollHeight);
//   }, [messages]);

//   // Handle sending message from PromptInputBox
//   const handleSend = (message, files) => {
//     if (!message.trim()) return;

//     // Add user's outgoing message
//     setMessages((msgs) => [...msgs, { text: message, type: "outgoing" }]);

//     // Send message to backend
//     fetch("http://127.0.0.1:5000/chat", {
//       method: "POST",
//       headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({ message }),
//     })
//       .then((res) => res.json())
//       .then((data) => {
//         const reply = data.response || "No response from server.";
//         setMessages((msgs) => [...msgs, { text: reply, type: "incoming" }]);
//       })
//       .catch(() => {
//         setMessages((msgs) => [
//           ...msgs,
//           { text: "Error communicating with server.", type: "incoming" },
//         ]);
//       });
//   };

//   return (
//     <>
//       <button
//         className="chatbot-toggler"
//         onClick={() => document.body.classList.toggle("show-chatbot")}
//         aria-label="Toggle Chatbot"
//       >
//         <img src={logo} alt="Chatbot Logo" className="chatbot-logo" />
//       </button>

//       <div className="chatbot">
//         <header className="flex justify-between items-center p-4 border-b border-gray-300">
//           <h2 className="text-xl font-semibold">Gmail Agent</h2>
//           <button
//             className="close-btn material-symbols-outlined"
//             onClick={() => document.body.classList.remove("show-chatbot")}
//             aria-label="Close Chatbot"
//           >
//             close
//           </button>
//         </header>

//         <ul
//           className="chatbox overflow-y-auto p-4 space-y-3 max-h-[400px]"
//           ref={chatboxRef}
//         >
//           {messages.map((msg, i) => (
//             <li
//               key={i}
//               className={`chat flex items-start space-x-2 ${
//                 msg.type === "incoming" ? "justify-start" : "justify-end"
//               }`}
//             >
//               {msg.type === "incoming" && (
//                 <img src={logo} alt="Chatbot Logo" className="chatbot-logo w-8 h-8" />
//               )}
//               <div
//                 className={`rounded-lg p-3 max-w-xs whitespace-pre-wrap ${
//                   msg.type === "incoming"
//                     ? "bg-gray-200 text-gray-900"
//                     : "bg-blue-600 text-white"
//                 }`}
//                 dangerouslySetInnerHTML={{
//                   __html: DOMPurify.sanitize(marked.parse(msg.text)),
//                 }}
//               />
//             </li>
//           ))}
//         </ul>

//         <div className="chat-input border-t border-gray-300 p-4">
//           <PromptInputBox onSend={handleSend} />
//         </div>
//       </div>
//     </>
//   );
// }
