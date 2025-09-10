import React, { useEffect, useState } from 'react';

const platforms = ['reddit', 'telegram', 'threads', 'instagram'];

function App() {
  const [queues, setQueues] = useState({});
  const [log, setLog] = useState('');

  useEffect(() => {
    // Fetch queue JSON files (assumes API or static files served)
    platforms.forEach(platform => {
      fetch(`/content_queue/${platform}_queue.json`)
        .then(response => response.json())
        .then(data => {
          setQueues(prev => ({ ...prev, [platform]: data }));
        }).catch(() => {
          setQueues(prev => ({ ...prev, [platform]: {} }));
        });
    });

    // Fetch log file
    fetch('/EXECUTION_LOG.md')
      .then(res => res.text())
      .then(text => setLog(text))
      .catch(() => setLog('Failed to load logs'));
  }, []);

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: 20 }}>
      <h1>SocialFlow AI Dashboard</h1>
      <section>
        <h2>Content Queues</h2>
        {platforms.map(p => (
          <div key={p} style={{ marginBottom: 20 }}>
            <h3>{p.charAt(0).toUpperCase() + p.slice(1)}</h3>
            <pre style={{ backgroundColor: '#f7f7f7', padding: 10, maxHeight: 200, overflowY: 'scroll' }}>
              {JSON.stringify(queues[p], null, 2)}
            </pre>
          </div>
        ))}
      </section>

      <section style={{ marginTop: 40 }}>
        <h2>Execution Log</h2>
        <pre style={{ whiteSpace: 'pre-wrap', backgroundColor: '#222', color: '#0f0', padding: 10, maxHeight: 400, overflowY: 'scroll' }}>
          {log}
        </pre>
      </section>
    </div>
  );
}

export default App;
