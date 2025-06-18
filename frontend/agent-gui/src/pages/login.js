import React, { useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

const CLIENT_ID = '323234489282-7l4qenrlanl4q81e9kapgpu5j0l317uj.apps.googleusercontent.com';

function Login() {
  const navigate = useNavigate();

  // Wrap the callback in useCallback to make it stable and avoid recreating on every render
  const handleCredentialResponse = useCallback(async (response) => {
  const idToken = response.credential;

  try {
    const res = await fetch('http://127.0.0.1:5000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: idToken })
    });

    const data = await res.json();
    console.log(data);

    if (res.ok) {
      // Success! Redirect to chatbot
      navigate('/chatbot');
    } else {
      alert(data.error || "Login failed");
    }
  } catch (error) {
    console.error("Error logging in:", error);
  }
}, [navigate]);


  useEffect(() => {
    /* global google */
    if (window.google) {
      google.accounts.id.initialize({
        client_id: CLIENT_ID,
        callback: handleCredentialResponse,
      });

      google.accounts.id.renderButton(
        document.getElementById("google-signin-btn"),
        { theme: "outline", size: "large" }
      );

      // Optional: prompt the user to sign in automatically if possible
      // google.accounts.id.prompt();
    }
  }, [handleCredentialResponse]); // <-- add dependency here

  return (
    <div style={{ display: 'flex', justifyContent: 'center', marginTop: '100px' }}>
      <div id="google-signin-btn"></div>
    </div>
  );
}

export default Login;
