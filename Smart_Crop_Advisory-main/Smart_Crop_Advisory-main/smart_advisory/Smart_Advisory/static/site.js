// site.js - general site JS (tooltips, logout confirmation)
document.addEventListener('DOMContentLoaded', function(){
  // enable Bootstrap tooltips where present
  try{
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (el) { return new bootstrap.Tooltip(el) })
  }catch(e){console.warn('tooltips init failed', e)}

  const confirmBtn = document.getElementById('confirmLogoutBtn');
  if(confirmBtn){
    confirmBtn.addEventListener('click', function(e){
      e.preventDefault();
      // POST to API logout then redirect to home
      fetch('/api/logout', {method: 'POST', headers: {'Content-Type':'application/json'}})
        .then(r => r.json())
        .then(j => { window.location.href = '/'; })
        .catch(err => { window.location.href = '/'; });
    });
  }

  // Live clock
  function updateClock() {
    var el = document.getElementById('liveClock')
    if (!el) return
    var now = new Date()
    // format like '28 Sep 2025 14:35:08'
    var opts = { year: 'numeric', month: 'short', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit' }
    el.textContent = now.toLocaleString(undefined, opts)
  }
  updateClock(); setInterval(updateClock, 1000)

  // Market ticker polling
  // market UI removed; no polling required
  // Re-add market card polling to update marketCardBody when present
  var marketCard = document.getElementById('marketCardBody')
  function updateMarketCard(){
    if(!marketCard) return
    fetch('/market').then(r=>r.json()).then(function(data){
      // data expected: { ticker: '...', prices: {crop:price, ...} }
      var out = ''
        if(data && data.prices){
          // intentionally do not render crop names on the card; keep it minimal
          out = ''
      } else if(data && data.ticker){
        out = data.ticker
      } else {
        out = 'No market data'
      }
      marketCard.innerHTML = out
    }).catch(function(){ marketCard.innerHTML = 'Market unavailable' })
  }
  updateMarketCard(); setInterval(updateMarketCard, 15000)

  var openMarketDetails = document.getElementById('openMarketDetails')
  if(openMarketDetails){
    openMarketDetails.addEventListener('click', function(){
      // populate and show market modal
      var modalEl = document.getElementById('marketModal')
      var modalBody = document.getElementById('marketBody')
      if(modalBody){
        modalBody.innerHTML = 'Loading...'
        fetch('/market').then(r=>r.json()).then(function(data){
            if(data && data.prices){
              var html = '<table class="table table-sm table-borderless mb-0"><thead><tr><th>Crop</th><th class="text-end">INR / qtl</th><th class="text-end">INR / kg</th></tr></thead><tbody>'
              Object.entries(data.prices).forEach(function(e){ 
                var crop = e[0]; var price = parseFloat(e[1])||0; var perKg = (price/100).toFixed(2);
                html += '<tr><td>' + crop + '</td><td class="text-end">' + price.toFixed(0) + '</td><td class="text-end">' + perKg + '</td></tr>'
              })
              html += '</tbody></table>'
            modalBody.innerHTML = html
              // add source link if present
              if(data.source || data.source_url){
                var sourceUrl = data.source_url || data.source
                modalBody.innerHTML += '<div class="small text-muted mt-2">Source: <a href="'+sourceUrl+'" target="_blank" rel="noopener">'+(data.source_name||sourceUrl)+'</a></div>'
              } else {
                modalBody.innerHTML += '<div class="small text-muted mt-2">Source: <a href="https://agmarknet.gov.in" target="_blank" rel="noopener">Agmarknet</a></div>'
              }
          } else if(data && data.ticker){
            modalBody.innerHTML = data.ticker
          } else {
            modalBody.innerHTML = 'No market data'
          }
        }).catch(function(){ modalBody.innerHTML = 'Market unavailable' })
      }
      if(modalEl) new bootstrap.Modal(modalEl).show()
    })
  }

  // Smooth scroll for in-page anchors (Get Started -> #dashboard)
  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener('click', function (e) {
      var target = this.getAttribute('href')
      if (!target || target === '#') return
      var el = document.querySelector(target)
      if (!el) return
      e.preventDefault()
      el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    })
  })
});
