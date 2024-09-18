import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [summary, setSummary] = useState('');  // State to store the result

  // Function to handle the form submission
  const handleSubmit = (e) => {
    e.preventDefault();

    // Sample JSON payload
    const payload = {
      creditLimit: 1000,
      events: [
        { eventType: 'TXN_AUTHED', eventTime: 1, txnId: 't1', amount: 123 },
        { eventType: 'TXN_SETTLED', eventTime: 2, txnId: 't1', amount: 123 }
      ]
    };

    // Post the JSON to the Flask backend
    axios
      .post('http://127.0.0.1:5000/summarize', payload)
      .then((response) => {
        // Set the response data as the summary
        setSummary(response.data);
      })
      .catch((error) => {
        console.error('There was an error!', error);
      });
  };

  return (
    <div className="App">
      <h1>Transaction Summary</h1>
      <form onSubmit={handleSubmit}>
        <button type="submit">Get Summary</button>
      </form>
      <div>
        <h2>Summary Result</h2>
        <pre>{summary}</pre>
      </div>
    </div>
  );
}

export default App;
