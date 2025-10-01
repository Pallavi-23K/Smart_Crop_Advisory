document.addEventListener('DOMContentLoaded', function() {
  const chatAsk = document.getElementById('chatAsk');
  const chatUseLocation = document.getElementById('chatUseLocation');
  const chatResp = document.getElementById('chatResponse');

  function showMessage(msg, kind='info'){
    chatResp.innerHTML = `<div style="white-space:pre-wrap">${msg}</div>`;
  }

  chatUseLocation && chatUseLocation.addEventListener('click', () => {
    if (!navigator.geolocation) return showMessage('Geolocation not supported by browser');
    navigator.geolocation.getCurrentPosition(pos => {
      document.getElementById('chat_lat').value = pos.coords.latitude.toFixed(6);
      document.getElementById('chat_lon').value = pos.coords.longitude.toFixed(6);
    }, err => {
      showMessage('Unable to get location: ' + err.message);
    })
  });

  chatAsk && chatAsk.addEventListener('click', async () => {
    const payload = {
      language: document.getElementById('lang_select').value,
      soil: document.getElementById('soil_select').value,
      latitude: document.getElementById('chat_lat').value,
      longitude: document.getElementById('chat_lon').value,
      month: null,
      farmer_name: document.getElementById('farmer_name').value,
      farmer_phone: document.getElementById('farmer_phone').value,
      field_size: document.getElementById('field_size').value,
      prev_crop: document.getElementById('prev_crop').value
    };

    showMessage('Thinking...');
    try{
      const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if(!data.ok) return showMessage(data.message || 'Error');
  // New response format: top_suggestions (list), market, combined, final
      let html = `<strong>${data.message}</strong><br/>`;
      html += `<div style="margin-top:8px"><b>Temperature:</b> ${data.data.temperature_c} \u00b0C<br/>`;
      html += `<b>Rainfall (monthly):</b> ${data.data.rainfall_mm} mm<br/></div>`;
  html += `<div style="margin-top:8px"><b>Top crop suggestions for your field:</b> ${data.data.top_suggestions.map(a=>a.crop).join(', ')}<br/></div>`;
      html += `<div style="margin-top:8px"><b>Market Prices:</b><br/>`;
      for(const [k,v] of Object.entries(data.data.market.prices)){
        html += `${k}: INR ${v} / qtl<br/>`;
      }
      html += `</div>`;
      html += `<div style="margin-top:8px"><b>Final pick:</b> ${data.data.final.crop} (score: ${data.data.final.combined_score})</div>`;
      showMessage(html);
    }catch(err){
      showMessage('Error contacting server: ' + err.message);
    }
  });

  // Market modal handler
  const openMarketBtn = document.getElementById('openMarketBtn');
  if(openMarketBtn){
    openMarketBtn.addEventListener('click', async () => {
      const marketBody = document.getElementById('marketBody');
      marketBody.innerHTML = 'Loading...';
      try{
        const res = await fetch('/market');
        const data = await res.json();
        let html = `<div><small>As of: ${data.as_of}</small></div><table class="table table-sm mt-2"><thead><tr><th>Crop</th><th>Price (INR/qtl)</th></tr></thead><tbody>`;
        for(const [k,v] of Object.entries(data.prices)){
          html += `<tr><td>${k}</td><td>${v}</td></tr>`;
        }
        html += '</tbody></table>';
        marketBody.innerHTML = html;
        // show modal
        var marketModal = new bootstrap.Modal(document.getElementById('marketModal'));
        marketModal.show();
      }catch(err){
        marketBody.innerHTML = 'Error fetching market data: ' + err.message;
      }
    });
  }
});