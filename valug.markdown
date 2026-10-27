---
layout: page
title: VALUG Trend Monitor
permalink: /valug/
---

<style>
.valug-wrap{max-width:1100px;margin:0 auto}.valug-cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:22px 0}.valug-card{border:1px solid #ddd;border-radius:12px;padding:16px;background:#fff}.valug-label{font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;color:#666}.valug-value{font-size:1.65rem;font-weight:700;margin-top:5px}.valug-signal{display:inline-block;padding:5px 12px;border-radius:20px;font-weight:700;background:#e8f4ec;color:#176b36}.valug-signal.sell{background:#faeaea;color:#9d2525}.valug-chart{height:420px;border:1px solid #ddd;border-radius:12px;padding:16px;margin:20px 0}.valug-table{width:100%;border-collapse:collapse}.valug-table th,.valug-table td{padding:9px;border-bottom:1px solid #eee;text-align:left}.valug-table th{font-size:.8rem;color:#666}.valug-note{color:#666;font-size:.9rem}@media(max-width:600px){.valug-chart{height:300px;padding:8px}.valug-value{font-size:1.35rem}}
</style>
<div class="valug-wrap">
<p>Weekly-close trend model using a 4% reversal from the running extreme. A BUY signal remains active until a 4% decline from the highest close since BUY; a SELL signal remains active until a 4% rise from the lowest close since SELL.</p>
<div class="valug-cards">
 <div class="valug-card"><div class="valug-label">Latest weekly close</div><div class="valug-value" id="v-close">—</div><div class="valug-note" id="v-date"></div></div>
 <div class="valug-card"><div class="valug-label">Current signal</div><div class="valug-value" id="v-signal">—</div></div>
 <div class="valug-card"><div class="valug-label">Next reversal trigger</div><div class="valug-value" id="v-trigger">—</div><div class="valug-note" id="v-distance"></div></div>
 <div class="valug-card"><div class="valug-label">Reference extreme</div><div class="valug-value" id="v-extreme">—</div><div class="valug-note" id="v-extreme-date"></div></div>
</div>
<div class="valug-chart"><canvas id="valug-chart" aria-label="VALUG weekly closes and signal changes"></canvas></div>
<h2>Signal changes</h2>
<table class="valug-table"><thead><tr><th>Date</th><th>Signal</th><th>Close</th></tr></thead><tbody id="v-events"></tbody></table>
<p class="valug-note">Initialization assumption: BUY on October 31, 2025, with the reference high set to that observation's close. Historical signals are calculated from the supplied weekly closes. Dates reflect the dates supplied, including shortened holiday weeks.</p>
</div>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
fetch('{{ "/assets/valug_signals.json" | relative_url }}').then(r=>r.json()).then(data=>{\n{
 const a=data.observations, last=a[a.length-1], fmt=n=>Number(n).toFixed(2), dist=Math.abs(last.trigger-last.close), pct=dist/last.close*100;
 document.getElementById('v-close').textContent=fmt(last.close);
 document.getElementById('v-date').textContent=last.date;
 document.getElementById('v-signal').innerHTML='<span class="valug-signal '+(last.signal==='SELL'?'sell':'')+'">'+last.signal+'</span>';
 document.getElementById('v-trigger').textContent=fmt(last.trigger);
 document.getElementById('v-distance').textContent=fmt(dist)+' points ('+pct.toFixed(2)+'%) to '+(last.signal==='BUY'?'SELL':'BUY');
 document.getElementById('v-extreme').textContent=fmt(last.extreme);
 document.getElementById('v-extreme-date').textContent='Extreme since current signal';
 document.getElementById('v-events').innerHTML=data.events.slice().reverse().map(e=>'<tr><td>'+e.date+'</td><td><span class="valug-signal '+(e.signal==='SELL'?'sell':'')+'">'+e.signal+'</span></td><td>'+fmt(e.close)+'</td></tr>').join('');
 new Chart(document.getElementById('valug-chart'),{type:'line',data:{labels:a.map(x=>x.date),datasets:[
 {label:'VALUG weekly close',data:a.map(x=>x.close),borderColor:'#315f91',backgroundColor:'rgba(49,95,145,.08)',borderWidth:2,pointRadius:0,tension:.15},
 {type:'scatter',label:'BUY signals',data:data.events.filter(x=>x.signal==='BUY').map(x=>({x:x.date,y:x.close})),backgroundColor:'#23864b',pointRadius:6},
 {type:'scatter',label:'SELL signals',data:data.events.filter(x=>x.signal==='SELL').map(x=>({x:x.date,y:x.close})),backgroundColor:'#bd3535',pointRadius:6}
 ]},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},plugins:{legend:{position:'bottom'}},scales:{x:{ticks:{maxTicksLimit:10}},y:{title:{display:true,text:'VALUG'}}}}});
}).catch(e=>{document.querySelector(".valug-wrap").insertAdjacentHTML("beforeend","<p role=\"alert\">Dashboard data could not be loaded: "+e.message+"</p>")});
</script>
