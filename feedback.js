// Sleek In-Page Feedback Widget connected to live autonomous API (api.dipesh.one)
(function() {
  const API_ENDPOINT = "https://api.dipesh.one/api/feedback";

  const css = `
    .cf-float-btn {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #1d4ed8;
      color: #fff;
      border: none;
      border-radius: 50px;
      padding: 12px 20px;
      font-size: 14px;
      font-weight: 600;
      box-shadow: 0 4px 14px rgba(29, 78, 216, 0.35);
      cursor: pointer;
      z-index: 99999;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: transform 0.2s, background 0.2s;
    }
    .cf-float-btn:hover { background: #1e40af; transform: translateY(-2px); }
    
    /* Desktop: Non-blocking bottom-right flyout card */
    .cf-panel {
      position: fixed;
      bottom: 80px;
      right: 24px;
      width: 360px;
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 14px;
      box-shadow: 0 12px 28px rgba(0,0,0,0.15);
      padding: 20px;
      z-index: 100000;
      display: none;
      box-sizing: border-box;
    }
    
    /* Mobile: Centered modal / bottom-sheet */
    @media (max-width: 640px) {
      .cf-panel {
        bottom: 0;
        right: 0;
        left: 0;
        width: 100%;
        border-radius: 16px 16px 0 0;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.15);
      }
    }

    .cf-panel h3 { margin: 0 0 4px; font-size: 16px; color: #111827; }
    .cf-panel p { margin: 0 0 14px; font-size: 12px; color: #6b7280; line-height: 1.4; }
    .cf-form-group { margin-bottom: 10px; }
    .cf-form-group label { display: block; font-size: 11px; font-weight: 600; color: #374151; margin-bottom: 3px; text-transform: uppercase; }
    .cf-input, .cf-textarea {
      width: 100%;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      padding: 8px 10px;
      font-size: 13px;
      box-sizing: border-box;
      font-family: inherit;
    }
    .cf-input:focus, .cf-textarea:focus { outline: none; border-color: #1d4ed8; }
    .cf-textarea { height: 90px; resize: vertical; }
    .cf-btn-submit {
      width: 100%;
      background: #16a34a;
      color: #fff;
      border: none;
      padding: 10px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      margin-top: 4px;
      transition: background 0.2s;
    }
    .cf-btn-submit:hover:not(:disabled) { background: #15803d; }
    .cf-btn-submit:disabled { background: #9ca3af; cursor: not-allowed; }
    .cf-close-btn {
      position: absolute;
      top: 14px;
      right: 14px;
      background: none;
      border: none;
      font-size: 18px;
      color: #9ca3af;
      cursor: pointer;
    }
    .cf-success-msg { display: none; text-align: center; padding: 14px 0; color: #166534; font-size: 13px; }
    .cf-error-msg { display: none; text-align: center; padding: 10px 0; color: #dc2626; font-size: 12px; }
    .cf-privacy-note { font-size: 10px; color: #9ca3af; margin-top: 6px; text-align: center; }
  `;

  const style = document.createElement('style');
  style.innerHTML = css;
  document.head.appendChild(style);

  const container = document.createElement('div');
  container.innerHTML = `
    <button class="cf-float-btn" id="cf-open-btn">
      <span>💬</span> Submit Intel / Feedback
    </button>

    <div class="cf-panel" id="cf-panel">
      <button class="cf-close-btn" id="cf-close-btn">&times;</button>
      <div id="cf-form-container">
        <h3>💬 Submit Field Intel</h3>
        <p>Challenge numbers, report broken links, or share local supplier terms. Submissions are processed by our research agent.</p>
        
        <form id="cf-feedback-form">
          <div class="cf-form-group">
            <label>Topic / Page</label>
            <input type="text" id="cf-topic" class="cf-input" value="${document.title.split('—')[0].trim()}" readonly>
          </div>
          <div class="cf-form-group">
            <label>On-Ground Intel / Correction *</label>
            <textarea id="cf-msg" class="cf-textarea" placeholder="Share local pricing, operational flaws, supplier terms, or YouTube teardown links..." required></textarea>
          </div>
          <div class="cf-form-group">
            <label>Your Email / Handle (Kept 100% Private)</label>
            <input type="text" id="cf-contact" class="cf-input" placeholder="email@domain.com (optional)">
          </div>
          <button type="submit" class="cf-btn-submit" id="cf-submit-btn">Send to Research Agent</button>
          <div class="cf-error-msg" id="cf-error">⚠️ Transmission failed. Please try again.</div>
          <div class="cf-privacy-note">🔒 Contact info is kept strictly private in our review ledger.</div>
        </form>
      </div>
      <div class="cf-success-msg" id="cf-success">
        <h4 style="margin:0 0 4px">✅ Intel Dispatched to Agent</h4>
        <p>Your submission has reached the autonomous research pipeline and triggered an immediate triage alert.</p>
      </div>
    </div>
  `;
  document.body.appendChild(container);

  const panel = document.getElementById('cf-panel');
  document.getElementById('cf-open-btn').onclick = () => {
    panel.style.display = panel.style.display === 'block' ? 'none' : 'block';
  };
  document.getElementById('cf-close-btn').onclick = () => { panel.style.display = 'none'; };

  document.getElementById('cf-feedback-form').onsubmit = async function(e) {
    e.preventDefault();
    const btn = document.getElementById('cf-submit-btn');
    const errBox = document.getElementById('cf-error');
    errBox.style.display = 'none';
    btn.textContent = 'Transmitting to Agent...';
    btn.disabled = true;

    const payload = {
      page_url: window.location.href,
      opportunity_title: document.getElementById('cf-topic').value,
      feedback_text: document.getElementById('cf-msg').value,
      submitted_by: document.getElementById('cf-contact').value || 'Anonymous',
      timestamp: new Date().toISOString()
    };

    try {
      const response = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error("HTTP error " + response.status);
      }

      // Success
      document.getElementById('cf-form-container').style.display = 'none';
      document.getElementById('cf-success').style.display = 'block';
      setTimeout(() => { 
        panel.style.display = 'none'; 
        document.getElementById('cf-form-container').style.display = 'block';
        document.getElementById('cf-success').style.display = 'none';
        document.getElementById('cf-feedback-form').reset();
        btn.textContent = 'Send to Research Agent';
        btn.disabled = false;
      }, 3500);
    } catch (err) {
      console.error("Failed to send feedback:", err);
      // Save locally as fallback
      try {
        let queue = JSON.parse(localStorage.getItem('hunter_pending_feedback') || '[]');
        queue.push(payload);
        localStorage.setItem('hunter_pending_feedback', JSON.stringify(queue));
      } catch (storageErr) {}
      
      errBox.textContent = '⚠️ Network error communicating with agent. Saved offline.';
      errBox.style.display = 'block';
      btn.textContent = 'Retry Sending';
      btn.disabled = false;
    }
  };
})();
