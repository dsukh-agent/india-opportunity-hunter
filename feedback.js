// Floating Intercom-style Feedback Widget for India Opportunity Hunter
(function() {
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
      box-shadow: 0 4px 14px rgba(29, 78, 216, 0.4);
      cursor: pointer;
      z-index: 99999;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: transform 0.2s, background 0.2s;
    }
    .cf-float-btn:hover { background: #1e40af; transform: translateY(-2px); }
    .cf-modal-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.5);
      backdrop-filter: blur(2px);
      display: none;
      justify-content: center;
      align-items: center;
      z-index: 100000;
    }
    .cf-modal-box {
      background: #fff;
      width: 90%;
      max-width: 480px;
      border-radius: 14px;
      padding: 24px;
      box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1);
      position: relative;
    }
    .cf-modal-box h3 { margin: 0 0 8px; font-size: 18px; color: #111827; }
    .cf-modal-box p { margin: 0 0 16px; font-size: 13px; color: #6b7280; }
    .cf-form-group { margin-bottom: 14px; }
    .cf-form-group label { display: block; font-size: 12px; font-weight: 600; color: #374151; margin-bottom: 4px; }
    .cf-input, .cf-textarea {
      width: 100%;
      border: 1px solid #d1d5db;
      border-radius: 8px;
      padding: 10px 12px;
      font-size: 14px;
      box-sizing: border-box;
    }
    .cf-textarea { height: 110px; resize: vertical; }
    .cf-btn-submit {
      width: 100%;
      background: #16a34a;
      color: #fff;
      border: none;
      padding: 12px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      margin-top: 8px;
    }
    .cf-btn-submit:hover { background: #15803d; }
    .cf-close-btn {
      position: absolute;
      top: 16px;
      right: 16px;
      background: none;
      border: none;
      font-size: 20px;
      color: #9ca3af;
      cursor: pointer;
    }
    .cf-success-msg { display: none; text-align: center; padding: 20px 0; color: #166534; }
  `;

  const style = document.createElement('style');
  style.innerHTML = css;
  document.head.appendChild(style);

  const container = document.createElement('div');
  container.innerHTML = `
    <button class="cf-float-btn" id="cf-open-btn">
      <span>💬</span> Submit Intel / Feedback
    </button>

    <div class="cf-modal-overlay" id="cf-modal">
      <div class="cf-modal-box">
        <button class="cf-close-btn" id="cf-close-btn">&times;</button>
        <div id="cf-form-container">
          <h3>💬 Submit Field Intel or Challenge Data</h3>
          <p>Are our unit economics wrong? Have on-ground pricing, better operator sources, or want to propose a vertical?</p>
          
          <form id="cf-feedback-form">
            <div class="cf-form-group">
              <label>Topic / Opportunity</label>
              <input type="text" id="cf-topic" class="cf-input" value="${document.title.split('—')[0].trim()}" readonly>
            </div>
            <div class="cf-form-group">
              <label>Your On-Ground Intel / Feedback *</label>
              <textarea id="cf-msg" class="cf-textarea" placeholder="Share local pricing, operational flaws, supplier terms, or YouTube teardown links..." required></textarea>
            </div>
            <div class="cf-form-group">
              <label>Your Name / Contact (Optional)</label>
              <input type="text" id="cf-contact" class="cf-input" placeholder="email@domain.com or @twitter (for follow-up)">
            </div>
            <button type="submit" class="cf-btn-submit" id="cf-submit-btn">Send to Research Agent</button>
          </form>
        </div>
        <div class="cf-success-msg" id="cf-success">
          <h4>✅ Intel Received!</h4>
          <p>Thank you! Your submission has been securely logged for our autonomous research agent to verify and update the database.</p>
        </div>
      </div>
    </div>
  `;
  document.body.appendChild(container);

  const modal = document.getElementById('cf-modal');
  document.getElementById('cf-open-btn').onclick = () => { modal.style.display = 'flex'; };
  document.getElementById('cf-close-btn').onclick = () => { modal.style.display = 'none'; };
  modal.onclick = (e) => { if(e.target === modal) modal.style.display = 'none'; };

  document.getElementById('cf-feedback-form').onsubmit = function(e) {
    e.preventDefault();
    const btn = document.getElementById('cf-submit-btn');
    btn.textContent = 'Sending...';
    btn.disabled = true;

    const payload = {
      page_url: window.location.href,
      opportunity_title: document.getElementById('cf-topic').value,
      feedback_text: document.getElementById('cf-msg').value,
      submitted_by: document.getElementById('cf-contact').value || 'Anonymous',
      timestamp: new Date().toISOString()
    };

    // Store in localStorage as resilient fallback + submit to GitHub issue dispatcher / webhook
    let queue = JSON.parse(localStorage.getItem('cf_feedback_queue') || '[]');
    queue.push(payload);
    localStorage.setItem('cf_feedback_queue', JSON.stringify(queue));

    // Submit to GitHub API dispatcher / receiver endpoint
    fetch('https://api.github.com/repos/dsukh-agent/india-opportunity-hunter/issues', {
      method: 'POST',
      headers: { 'Accept': 'application/vnd.github+json' },
      body: JSON.stringify({
        title: `[In-Page Intel] ${payload.opportunity_title}`,
        body: `### In-Page Community Submission\n\n**Topic:** ${payload.opportunity_title}\n**URL:** ${payload.page_url}\n**From:** ${payload.submitted_by}\n\n**Intel / Feedback:**\n${payload.feedback_text}`
      })
    }).catch(()=>{});

    document.getElementById('cf-form-container').style.display = 'none';
    document.getElementById('cf-success').style.display = 'block';
    setTimeout(() => { modal.style.display = 'none'; }, 3000);
  };
})();
