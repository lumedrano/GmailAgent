
// import React, { useState, useEffect, useRef } from "react";
// import { marked } from "marked";
// import DOMPurify from "dompurify";
// import { AIChatInput } from "../components/ui/ai-chat-input";
// import { TextShimmer } from "../components/ui/text-shimmer";
// import logo from "../components/images/logo.png";

// // You can add this in your main HTML <head> or use a CSS import:
// // import '@fontsource/poppins'; // if you install it via npm
// // Or add this in your index.html head:
// // <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap" rel="stylesheet" />

// export default function Chatbot() {
//   const [messages, setMessages] = useState([
//     {
//       text: "Hi there!👋 This portion of our site is under construction but check back later!",
//       type: "incoming",
//     },
//   ]);
//   const [isTyping, setIsTyping] = useState(false);
//   const [displayedText, setDisplayedText] = useState("");
//   const chatboxRef = useRef(null);

//   const scrollToBottom = () => {
//     chatboxRef.current?.scrollTo({
//       top: chatboxRef.current.scrollHeight,
//       behavior: "smooth",
//     });
//   };

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages, displayedText, isTyping]);

//   const typeWriterEffect = (text, onFinish) => {
//     let index = 0;
//     setDisplayedText("");

//     const interval = setInterval(() => {
//       setDisplayedText((prev) => prev + text[index]);
//       index++;

//       if (index === text.length) {
//         clearInterval(interval);
//         onFinish();
//       }
//     }, 20);
//   };

//   const sendMessage = async (userMsg) => {
//     if (!userMsg.trim()) return;

//     setMessages((msgs) => [...msgs, { text: userMsg, type: "outgoing" }]);
//     setIsTyping(true);

//     try {
//       const res = await fetch("http://127.0.0.1:5000/chat", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ message: userMsg }),
//       });
//       const data = await res.json();
//       const reply = data.response || "No response from server.";

//       typeWriterEffect(reply, () => {
//         setMessages((msgs) => [...msgs, { text: reply, type: "incoming" }]);
//         setDisplayedText("");
//         setIsTyping(false);
//       });
//     } catch {
//       const errorMsg = "Error communicating with server.";
//       setMessages((msgs) => [...msgs, { text: errorMsg, type: "incoming" }]);
//       setIsTyping(false);
//     }
//   };

//   const loadingTexts = [
//     "Thinking...",
//     "Crafting a reply...",
//     "Generating response...",
//     "Please hold on...",
//     "Summoning AI magic...",
//   ];

//   const renderTypingIndicator = () => {
//     const randomText =
//       loadingTexts[Math.floor(Math.random() * loadingTexts.length)];
//     return (
//       <li
//         className="chat incoming"
//         style={{
//           display: "flex",
//           justifyContent: "flex-start",
//           paddingLeft: "4px",
//         }}
//       >
//         <TextShimmer
//           duration={1.2}
//           className="font-mono text-base [--base-color:#444] [--base-gradient-color:#999]"
//         >
//           {randomText}
//         </TextShimmer>
//       </li>
//     );
//   };

//   const renderMessages = () => {
//     return messages.map((msg, i) => (
//       <li
//         key={i}
//         className={`chat ${msg.type}`}
//         style={{
//           display: "flex",
//           justifyContent: msg.type === "outgoing" ? "flex-end" : "flex-start",
//         }}
//       >
//         <div
//           style={{
//             backgroundColor: msg.type === "outgoing" ? "#007bff" : "#e5e5ea",
//             color: msg.type === "outgoing" ? "#fff" : "#000",
//             padding: "8px 12px",
//             borderRadius: "16px",
//             maxWidth: "80%",
//             whiteSpace: "pre-wrap",
//             wordWrap: "break-word",
//             fontSize: "16px",
//           }}
//           dangerouslySetInnerHTML={{
//             __html: DOMPurify.sanitize(
//               marked.parse(msg.text, { breaks: true }).replace(/<\/?p>/g, "")
//             ),
//           }}
//         />
//       </li>
//     ));
//   };

//   return (
//     <>
//       {/* Title + Logo container */}
// <div
//   style={{
//     display: "flex",
//     alignItems: "center",
//     justifyContent: "center",
//     gap: "12px", // space between logo and title
//     marginTop: "24px",
//     marginBottom: "12px",
//     userSelect: "none",
//   }}
// >
//   <img
//     src={logo}
//     alt="Logo"
//     style={{
//       width: "60px",
//       height: "60px",
//       objectFit: "contain",
//     }}
//   />
  
//   <TextShimmer
//     duration={1.5}
//     className="font-poppins font-semibold text-4xl" // adjust classes if using Tailwind or your CSS
//     style={{
//       fontFamily: "'Poppins', sans-serif",
//       fontWeight: 600,
//       userSelect: "none",
//     }}
//   >
//     Echo
//   </TextShimmer>
// </div>

//       <div
//         className="chatbot-container"
//         style={{
//           width: "100%",
//           maxWidth: "600px",
//           margin: "auto",
//           display: "flex",
//           flexDirection: "column",
//           height: "calc(100vh - 100px)", // account for title height + margins
//           padding: "0",
//           boxSizing: "border-box",
//           position: "relative",
//         }}
//       >
//         {/* Logo on top-left corner, bigger size
//         <div
//           style={{
//             position: "fixed",
//             top: "16px",
//             left: "16px",
//             zIndex: 9999,
//           }}
//         >
//           <img
//             src={logo}
//             alt="Logo"
//             style={{ width: "85px", height: "85px", objectFit: "contain" }}
//           />
//         </div> */}

//         {/* Name and Logout button on top-right corner */}
//         <div
//           style={{
//             position: "fixed",
//             top: "16px",
//             right: "16px",
//             display: "flex",
//             alignItems: "center",
//             gap: "12px",
//             zIndex: 9999,
//           }}
//         >
//           <span style={{ fontSize: "18px", fontWeight: "bold" }}>Luigi</span>

//           <button
//             style={{
//               backgroundColor: "transparent",
//               color: "#000",
//               border: "1px solid #000",
//               padding: "6px 12px",
//               borderRadius: "4px",
//               cursor: "pointer",
//               fontSize: "14px",
//             }}
//             onClick={() => console.log("Logout clicked (does nothing)")}
//           >
//             Logout
//           </button>
//         </div>

//         <ul
//           className="chatbox"
//           ref={chatboxRef}
//           style={{
//             flexGrow: 1,
//             overflowY: "auto",
//             padding: "16px",
//             listStyle: "none",
//             display: "flex",
//             flexDirection: "column",
//             gap: "6px",
//             marginTop: "96px", // push content below fixed header area
//           }}
//         >
//           {renderMessages()}

//           {displayedText && (
//             <li
//               className="chat incoming"
//               style={{ display: "flex", justifyContent: "flex-start" }}
//             >
//               <div
//                 style={{
//                   backgroundColor: "#e5e5ea",
//                   color: "#000",
//                   padding: "8px 12px",
//                   borderRadius: "16px",
//                   maxWidth: "80%",
//                   whiteSpace: "pre-wrap",
//                   wordWrap: "break-word",
//                   fontSize: "16px",
//                 }}
//                 dangerouslySetInnerHTML={{
//                   __html: DOMPurify.sanitize(
//                     marked.parse(displayedText, { breaks: true }).replace(
//                       /<\/?p>/g,
//                       ""
//                     )
//                   ),
//                 }}
//               />
//             </li>
//           )}

//           {isTyping && !displayedText && renderTypingIndicator()}
//         </ul>

//         <div style={{ padding: "8px 16px" }}>
//           <AIChatInput onSend={sendMessage} />
//         </div>
//       </div>
//     </>
//   );
// }


import React, { useState, useEffect, useRef } from "react";
import { marked } from "marked";
import DOMPurify from "dompurify";
import { AIChatInput } from "../components/ui/ai-chat-input";
import { TextShimmer } from "../components/ui/text-shimmer";
import logo from "../components/images/logo.png";

// Make sure to include Poppins font in your project (index.html or npm package)
// Example in index.html:
// <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600&display=swap" rel="stylesheet" />

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      text: "Hi there!👋 Welcome to Echo's Beta, feel free to give me any task like sending an email, scheduling meetings, etc. I'm here to help you with any task you need to complete. I'm still learning, so please be patient and give me a few seconds to think about your request.",
      type: "incoming",
    },
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
    <>
      {/* Title + Logo container */}
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
    animationName: "peekWave",
    animationDuration: "4s",
    animationTimingFunction: "ease-in-out",
    animationIterationCount: "infinite",
    transformOrigin: "bottom center",
  }}
/>


      </div>

      {/* Name and Logout button on top-right corner */}
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
          onClick={() => console.log("Logout clicked (does nothing)")}
        >
          Logout
        </button>
      </div>

      <div
        className="chatbot-container"
        style={{
          width: "100%",
          maxWidth: "600px",
          margin: "auto",
          display: "flex",
          flexDirection: "column",
          height: "calc(100vh - 120px)", // space for title + margins
          padding: "0",
          boxSizing: "border-box",
          position: "relative",
          marginTop: "12px",
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
            marginTop: "0", // no extra margin needed here
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
                    marked.parse(displayedText, { breaks: true }).replace(
                      /<\/?p>/g,
                      ""
                    )
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

      {/* Add animation CSS */}
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
    opacity: 1; /* Stay fully visible while shaking */
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


        `}
      </style>
    </>
  );
}
