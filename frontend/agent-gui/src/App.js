import React from "react";
import Chatbot from "./pages/chatbot";

function App() {
  return (
    <div className="App">
      <Chatbot />
    </div>
  );
}

export default App;

// import React, { useState, useEffect } from "react";
// import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
// import Login from "./pages/login";
// import Chatbot from "./pages/chatbot";

// function ProtectedRoute({ children }) {
//   const [isAuthenticated, setIsAuthenticated] = useState(null);

//   useEffect(() => {
//     // Call your backend to verify if user is authenticated (token/session)
//     fetch("/api/auth/verify", { credentials: "include" })
//       .then(res => res.json())
//       .then(data => setIsAuthenticated(data.authenticated))
//       .catch(() => setIsAuthenticated(false));
//   }, []);

//   if (isAuthenticated === null) {
//     return <div>Loading...</div>; // or spinner while checking auth
//   }

//   if (!isAuthenticated) {
//     return <Navigate to="/login" replace />;
//   }

//   return children;
// }

// function App() {
//   return (
//     <Router>
//       <Routes>
//         <Route path="/login" element={<Login />} />
//         <Route
//           path="/chatbot"
//           element={
//             <ProtectedRoute>
//               <Chatbot />
//             </ProtectedRoute>
//           }
//         />
//         <Route path="*" element={<Navigate to="/login" replace />} />
//       </Routes>
//     </Router>
//   );
// }

// export default App;
