(function(){
  const D = window.PROCURE_ATLAS_DATA || {manufacturers:[],products:[],capabilities:[]};
  const bySlug=(arr,slug)=>arr.find(x=>x.slug===slug);
  const norm=s=>(s||'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();

  // Home sourcing search: deterministic MVP, deliberately not presented as AI.
  const sourcingInput=document.querySelector('[data-sourcing-input]');
  const sourcingResults=document.querySelector('[data-sourcing-results]');
  if(sourcingInput && sourcingResults){
    const render=()=>{
      const q=norm(sourcingInput.value);
      if(q.length<2){sourcingResults.classList.remove('show');sourcingResults.innerHTML='';return;}
      const terms=q.split(/\s+/).filter(Boolean);
      const scored=D.manufacturers.map(m=>{
        const products=m.products.map(s=>bySlug(D.products,s)?.name||s).join(' ');
        const caps=m.capabilities.map(s=>bySlug(D.capabilities,s)?.name||s).join(' ');
        const hay=norm([m.name,m.shortName,m.city,m.province,products,caps,m.summary].join(' '));
        const score=terms.reduce((n,t)=>n+(hay.includes(t)?1:0),0);
        return {m,score};
      }).filter(x=>x.score>0).sort((a,b)=>b.score-a.score).slice(0,4);
      if(!scored.length){sourcingResults.innerHTML='<div class="search-result"><div><b>No direct preview match</b><br><span>Try a machine type such as filling, pouch, palletizer, labeling or strapping.</span></div></div>';}
      else sourcingResults.innerHTML=scored.map(({m,score})=>`<a class="search-result" href="./manufacturers/${m.slug}/"><div><b>${m.shortName}</b><br><span>${m.city} · ${m.summary}</span></div><span>${score} matched terms →</span></a>`).join('');
      sourcingResults.classList.add('show');
    };
    sourcingInput.addEventListener('input',render);
    const form=sourcingInput.closest('form');
    if(form)form.addEventListener('submit',e=>{e.preventDefault();location.href=`./manufacturers/?q=${encodeURIComponent(sourcingInput.value)}`;});
  }

  // Manufacturer finder.
  const finder=document.querySelector('[data-manufacturer-finder]');
  if(finder){
    const qInput=finder.querySelector('[data-filter-q]');
    const productSelect=finder.querySelector('[data-filter-product]');
    const regionSelect=finder.querySelector('[data-filter-region]');
    const cards=[...finder.querySelectorAll('[data-manufacturer-card]')];
    const count=finder.querySelector('[data-result-count]');
    const params=new URLSearchParams(location.search);
    if(qInput && params.get('q'))qInput.value=params.get('q');
    const apply=()=>{
      const q=norm(qInput?.value||''); const p=productSelect?.value||''; const r=regionSelect?.value||'';
      let shown=0;
      cards.forEach(card=>{
        const hay=norm(card.dataset.search||'');
        const okQ=!q||q.split(/\s+/).every(t=>hay.includes(t));
        const okP=!p||(card.dataset.products||'').split(',').includes(p);
        const okR=!r||card.dataset.region===r;
        const ok=okQ&&okP&&okR; card.style.display=ok?'':'none'; if(ok)shown++;
      });
      if(count)count.textContent=`${shown} manufacturer${shown===1?'':'s'} shown`;
    };
    [qInput,productSelect,regionSelect].forEach(el=>el&&el.addEventListener(el.tagName==='INPUT'?'input':'change',apply)); apply();
  }

  // Compare selection persisted per browser.
  const key='procureatlas_compare';
  const getCompare=()=>{try{return JSON.parse(localStorage.getItem(key)||'[]')}catch(e){return[]}};
  const setCompare=a=>localStorage.setItem(key,JSON.stringify(a.slice(0,4)));
  const box=document.querySelector('[data-compare-box]');
  const syncCompare=()=>{
    const selected=getCompare();
    document.querySelectorAll('[data-compare-toggle]').forEach(btn=>{
      const on=selected.includes(btn.dataset.compareToggle);btn.textContent=on?'✓ Added':'Compare';btn.classList.toggle('btn-primary',on);
    });
    if(box){
      box.classList.toggle('active',selected.length>0);
      const names=selected.map(s=>D.manufacturers.find(m=>m.slug===s)?.shortName||s);
      const items=box.querySelector('[data-compare-items]'); if(items)items.textContent=names.length?`${names.length}/4 selected: ${names.join(', ')}`:'No manufacturers selected';
      const go=box.querySelector('[data-compare-go]'); if(go)go.href=`${box.dataset.base||'../'}compare/?m=${selected.join(',')}`;
    }
  };
  document.querySelectorAll('[data-compare-toggle]').forEach(btn=>btn.addEventListener('click',()=>{
    let a=getCompare(); const s=btn.dataset.compareToggle;
    if(a.includes(s))a=a.filter(x=>x!==s); else if(a.length<4)a.push(s); else alert('Compare up to 4 manufacturers at a time.');
    setCompare(a);syncCompare();
  }));
  document.querySelectorAll('[data-compare-clear]').forEach(btn=>btn.addEventListener('click',()=>{setCompare([]);syncCompare()}));
  syncCompare();

  // Compare page renderer.
  const compareRender=document.querySelector('[data-compare-render]');
  if(compareRender){
    const params=new URLSearchParams(location.search);
    let selected=(params.get('m')||'').split(',').filter(Boolean);
    if(!selected.length) selected=getCompare();
    selected=selected.filter(s=>D.manufacturers.some(m=>m.slug===s)).slice(0,4);
    const empty=document.querySelector('[data-compare-empty]');
    if(selected.length<2){ if(empty) empty.style.display='block'; }
    else{
      if(empty) empty.style.display='none';
      const ms=selected.map(s=>D.manufacturers.find(m=>m.slug===s));
      const allProducts=[...new Set(ms.flatMap(m=>m.products))];
      const allCaps=[...new Set(ms.flatMap(m=>m.capabilities))];
      const row=(label,fn)=>`<tr><td><b>${label}</b></td>${ms.map(fn).join('')}</tr>`;
      const head=`<tr><th>Comparison</th>${ms.map(m=>`<th><div class="manufacturer-header">${m.shortName}</div><div class="meta">${m.city}</div></th>`).join('')}</tr>`;
      let rows=row('Profile status',m=>`<td>${m.status}<br><span class="meta">${m.auditStatus}</span></td>`);
      rows+=allProducts.map(slug=>row((bySlug(D.products,slug)||{name:slug}).name,m=>`<td class="${m.products.includes(slug)?'yes':'no'}">${m.products.includes(slug)?'✓ Evidenced':'—'}</td>`)).join('');
      rows+=`<tr><th>Capabilities</th>${ms.map(()=>'<th></th>').join('')}</tr>`;
      rows+=allCaps.map(slug=>row((bySlug(D.capabilities,slug)||{name:slug}).name,m=>`<td class="${m.capabilities.includes(slug)?'yes':'no'}">${m.capabilities.includes(slug)?'✓ Recorded':'—'}</td>`)).join('');
      rows+=row('Evidence records',m=>`<td><b>${m.evidence.length}</b><br><span class="meta">current snapshot</span></td>`);
      compareRender.innerHTML=`<div class="compare-table-wrap"><table class="compare-table"><thead>${head}</thead><tbody>${rows}</tbody></table></div><p class="search-hint">A dash means “not recorded in this data snapshot”, not “manufacturer cannot do it”. Missing data is never converted into a negative capability claim.</p>`;
    }
  }

  // RFQ demo: local-only until Supabase is connected.
  const rfq=document.querySelector('[data-rfq-form]');
  if(rfq){
    rfq.addEventListener('submit',e=>{
      e.preventDefault();
      const data=Object.fromEntries(new FormData(rfq).entries());
      data.createdAt=new Date().toISOString();
      const existing=JSON.parse(localStorage.getItem('procureatlas_rfqs')||'[]'); existing.push(data); localStorage.setItem('procureatlas_rfqs',JSON.stringify(existing));
      const s=rfq.querySelector('[data-form-status]'); if(s){s.textContent='MVP saved this RFQ locally in your browser. Production submission remains disabled until the Supabase backend and spam protection are connected.';s.classList.add('show');}
      rfq.reset();
    });
  }
})();
