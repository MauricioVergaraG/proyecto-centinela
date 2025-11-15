/* Autor: Mauricio Vergara */
import React from "react";
import { createRoot } from "react-dom/client";


function App(){
  return (
    <div style={{fontFamily:'Arial, sans-serif', padding:20}}>
      <h1>Centinela — MVP</h1>
      <p>Frontend mínimo. API health: <a href="http://localhost:8000/health">/health</a></p>
    </div>
  );
}


createRoot(document.getElementById("root")).render(<App />);
