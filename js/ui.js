/* SAHAYAK — shared UI: icons, layout shell, toasts, modal, transitions, reusable components */
(function(){
  const P={
    grid:'<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/>',
    user:'<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
    users:'<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    search:'<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    check:'<polyline points="20 6 9 17 4 12"/>',
    'check-circle':'<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
    alert:'<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    x:'<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
    'x-circle':'<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>',
    help:'<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    sliders:'<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/>',
    file:'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>',
    columns:'<path d="M12 3h7a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-7m0-18H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h7m0-18v18"/>',
    menu:'<line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/>',
    arrow:'<line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>',
    back:'<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
    shield:'<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    heart:'<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>',
    book:'<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    briefcase:'<rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    leaf:'<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    wallet:'<rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/>',
    home:'<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
    flame:'<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.07-2.14-.22-4.05 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.15.43-2.29 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    zap:'<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    target:'<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    plus:'<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    trash:'<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    printer:'<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/>',
    info:'<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    down:'<polyline points="6 9 12 15 18 9"/>',
    refresh:'<polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>',
    clip:'<path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/>',
    wifi:'<path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><line x1="12" y1="20" x2="12.01" y2="20"/>',
    lock:'<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
    eye:'<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>'
  };
  const icon=(n,s=18)=>`<svg class="ic" width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${P[n]||P.info}</svg>`;
  const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const $=(s,r=document)=>r.querySelector(s);
  const $$=(s,r=document)=>[...r.querySelectorAll(s)];
  const initials=n=>(n||'').trim().split(/\s+/).slice(0,2).map(w=>w[0]).join('').toUpperCase()||'G';

  /* ---------- toast ---------- */
  function toast(msg,type='ok'){
    let box=$('.toasts');
    if(!box){box=document.createElement('div');box.className='toasts';box.setAttribute('role','status');document.body.appendChild(box)}
    const t=document.createElement('div');t.className='toast '+type;
    t.innerHTML=icon(type==='ok'?'check-circle':'info',18)+'<span>'+esc(msg)+'</span>';
    box.appendChild(t);
    setTimeout(()=>{t.classList.add('out');setTimeout(()=>t.remove(),300)},3200);
  }

  /* ---------- modal ---------- */
  function modal(html){
    closeModal();
    const bg=document.createElement('div');bg.className='modal-bg';bg.id='modal';
    bg.innerHTML=`<div class="modal" role="dialog" aria-modal="true">${html}</div>`;
    document.body.appendChild(bg);document.body.style.overflow='hidden';
    bg.addEventListener('click',e=>{if(e.target===bg||e.target.closest('[data-close]'))closeModal()});
    const f=$('[data-close]',bg);f&&f.focus();
    return bg;
  }
  function closeModal(){const m=$('#modal');if(m){m.remove();document.body.style.overflow=''}}
  document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});

  /* ---------- shell ---------- */
  const NAV=[
    ['dashboard','dashboard.html','Dashboard','grid'],
    ['profile','profile.html','My Profile','user'],
    ['schemes','schemes.html','Discover Schemes','search'],
    ['matches','matches.html','My Matches','check-circle'],
    ['gap','gap-analyzer.html','Gap Analyzer','target'],
    ['simulator','simulator.html','What-if Simulator','sliders'],
    ['documents','documents.html','Documents','file'],
    ['compare','compare.html','Compare Schemes','columns']
  ];
  function updateCompareBadge(){
    const n=SAH.store.getCompare().length;
    $$('.cmp-badge').forEach(b=>{b.textContent=n;b.style.display=n?'grid':'none'});
  }
  function buildShell(){
    const page=document.body.dataset.page;
    const prof=SAH.store.getProfile();
    const sb=$('#sidebar'),tb=$('#topbar');
    if(!sb||!tb) return;
    sb.className='sidebar';sb.id='sidebar';
    sb.innerHTML=`
      <a class="brand" href="index.html"><img src="assets/logo.svg" alt="" width="40" height="40"><span><b>SAHAYAK</b><small class="hi">सहायक · Team ZERRODAY</small></span></a>
      <div class="nav-l">Menu</div>
      <nav class="nav" aria-label="Main navigation">${NAV.map(n=>`<a href="${n[1]}" class="${n[0]===page?'on':''}" ${n[0]===page?'aria-current="page"':''}>${icon(n[3],19)}<span>${n[2]}</span>${n[0]==='compare'?'<em class="count cmp-badge" style="display:none;font-style:normal">0</em>':''}</a>`).join('')}</nav>
      <div class="side-foot">
        <div class="side-note"><b>Illustrative data</b>Scheme details and limits here are simplified for a hackathon demo. Always confirm with official sources.</div>
        <a class="side-back" href="index.html">${icon('back',16)} Back to home</a>
      </div>`;
    const title=document.body.dataset.title||'SAHAYAK';
    tb.className='topbar';
    tb.innerHTML=`
      <button class="burger" id="burger" aria-label="Open menu">${icon('menu',20)}</button>
      <div><h1>${esc(title)}</h1><div class="sub">Your Benefits. Your Opportunities.</div></div>
      <form class="search tb-search" action="schemes.html" method="get" role="search"><span class="sr"><label for="gq">Search schemes</label></span>${icon('search',17)}<input id="gq" class="input" type="search" name="q" placeholder="Search schemes…"></form>
      <a class="tb-user" href="profile.html" title="My profile"><span class="avatar">${esc(initials(prof&&prof.name))}</span><span class="nm">${esc(prof&&prof.name?prof.name:'Guest')}</span></a>`;
    const scrim=document.createElement('div');scrim.className='scrim';document.body.appendChild(scrim);
    $('#burger').addEventListener('click',()=>document.body.classList.toggle('nav-open'));
    scrim.addEventListener('click',()=>document.body.classList.remove('nav-open'));
    updateCompareBadge();
  }

  /* ---------- page transitions ---------- */
  function transitions(){
    document.addEventListener('click',e=>{
      const a=e.target.closest('a[href]');
      if(!a||e.defaultPrevented||e.metaKey||e.ctrlKey||e.shiftKey||a.target==='_blank'||a.hasAttribute('download')) return;
      const h=a.getAttribute('href');
      if(!h||h.startsWith('#')||/^(https?:|mailto:|tel:)/.test(h)) return;
      e.preventDefault();
      document.body.classList.add('page-out');
      setTimeout(()=>{location.href=h},170);
    });
    window.addEventListener('pageshow',e=>{if(e.persisted)document.body.classList.remove('page-out')});
  }
  function reveal(){
    const els=$$('.reveal');
    if(!('IntersectionObserver' in window)){els.forEach(e=>e.classList.add('in'));return}
    const io=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('in');io.unobserve(x.target)}}),{threshold:.12});
    els.forEach(e=>io.observe(e));
  }

  /* ---------- reusable components ---------- */
  const badge=(st,txt)=>`<span class="badge ${st}">${icon(st==='eligible'?'check-circle':st==='potential'?'help':'x-circle',14)}${txt||SAH.STATUS[st]}</span>`;

  function ruleList(results,withLinks=true){
    return `<ul class="rules">${results.map(r=>{
      const ic=r.status==='pass'?'check':r.status==='fail'?'x':'help';
      let sub;
      if(r.status==='pass') sub='Met — your value: '+esc(r.yours);
      else if(r.status==='fail') sub='Not met — your value: '+esc(r.yours)+'. Needs: '+esc(r.need);
      else sub='Information missing — not counted against you. '+(withLinks?'<a href="profile.html">Add it in your profile</a>':'');
      return `<li class="rule ${r.status}"><span class="rule-ic">${icon(ic,14)}</span><div><div class="rule-t">${esc(r.rule.label)}</div><div class="rule-s">${sub}</div></div></li>`;
    }).join('')}</ul>`;
  }
  const plainRules=s=>`<ul class="rules">${s.rules.map(r=>`<li class="rule plain"><span class="rule-ic">${icon('info',14)}</span><div><div class="rule-t">${esc(r.label)}</div></div></li>`).join('')}</ul>`;

  function toggleCompare(id){
    let c=SAH.store.getCompare();
    if(c.includes(id)){c=c.filter(x=>x!==id);toast('Removed from comparison','warn')}
    else{
      if(c.length>=3){toast('You can compare up to 3 schemes. Remove one first.','warn');return false}
      c.push(id);toast('Added to comparison ('+c.length+'/3)');
    }
    SAH.store.setCompare(c);updateCompareBadge();return true;
  }

  function schemeModal(id){
    const s=SAH.SCHEME_MAP[id];if(!s)return;
    const p=SAH.store.getProfile();
    const ev=p?SAH.engine.evalScheme(s,p):null;
    const inCmp=SAH.store.getCompare().includes(id);
    const html=`
      <div class="modal-h"><div class="s-ic">${icon(s.icon,22)}</div>
        <div><h3 style="font-size:19px">${esc(s.name)}</h3><div class="hi muted" style="font-size:13.5px">${esc(s.hi)}</div>
        <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap"><span class="pill">${esc(s.category)}</span><span class="tag-illus">${icon('info',12)} Illustrative</span>${ev?badge(ev.status):''}</div></div>
        <button class="x-btn" data-close aria-label="Close">${icon('x',16)}</button></div>
      <div class="modal-b">
        <div><h4>About</h4><p>${esc(s.summary)}</p></div>
        <div><h4>Benefit (illustrative)</h4><p>${esc(s.benefit)}</p><p class="muted" style="font-size:13px;margin-top:6px">${esc(s.type)} · ${esc(s.ministry)}</p></div>
        <div><h4>${ev?'Your eligibility check':'Eligibility criteria'}</h4>${ev?ruleList(ev.results):plainRules(s)}${ev?'':'<p class="muted" style="font-size:13px;margin-top:10px">Create a profile to see how you match each criterion.</p>'}</div>
        <div><h4>Documents usually needed</h4><div class="chips">${s.docs.map(d=>`<span class="pill">${esc(docName(d))}</span>`).join('')}</div></div>
        <div><h4>How to apply (general guidance)</h4><ol style="padding-left:20px;display:flex;flex-direction:column;gap:6px">${s.apply.map(a=>`<li>${esc(a)}</li>`).join('')}</ol></div>
        <div class="disclaim" style="background:#FFF2E0;border:1px solid #f6d9ab;border-radius:12px;padding:12px 14px;font-size:13px;color:#6a3a00">Illustrative information for a hackathon prototype — not official. Verify the latest criteria and the official application process with the concerned ministry or department before applying.</div>
        <div class="acts" style="margin-top:0"><button class="btn btn-primary" id="mCmp">${icon('columns',16)} <span>${inCmp?'Remove from comparison':'Add to comparison'}</span></button><a class="btn btn-ghost" href="${p?'matches.html':'profile.html'}">${p?'View my matches':'Create profile'}</a></div>
      </div>`;
    const m=modal(html);
    $('#mCmp',m).addEventListener('click',e=>{toggleCompare(id);const on=SAH.store.getCompare().includes(id);e.currentTarget.querySelector('span').textContent=on?'Remove from comparison':'Add to comparison';$$('[data-cmp="'+id+'"]').forEach(b=>b.classList.toggle('on',on))});
  }

  function emptyProfile(msg){
    return `<div class="card empty"><div class="e-ic">${icon('user',26)}</div><h3>No profile yet</h3><p>${msg||'Create your profile (or load the demo profile) to see personalised results.'}</p>
      <div class="row"><a class="btn btn-primary" href="profile.html">${icon('plus',16)} Create profile</a><button class="btn btn-ghost" data-demo>${icon('zap',16)} Load demo profile</button></div></div>`;
  }
  function bindDemo(root,after){
    $$('[data-demo]',root||document).forEach(b=>b.addEventListener('click',async()=>{
      await SAH.api.saveProfile({...SAH.DEMO_PROFILE});
      toast('Demo profile loaded (illustrative)');
      after?after():location.reload();
    }));
  }
  function ring(pct,cls=''){return `<div class="ring ${cls}" style="--p:${pct}"><span>${pct}%</span></div>`}

  function hydrateIcons(root){
    $$('i[data-ic]',root||document).forEach(el=>{
      const t=document.createElement('span');t.style.display='inline-flex';
      t.innerHTML=icon(el.dataset.ic,Number(el.dataset.s)||18);
      el.replaceWith(t.firstChild);
    });
  }

  function docName(d){
    if(!d) return '';
    const e=SAH.DOCS[d];
    if(e) return e.name;
    // Backend returns full document names (e.g. "Aadhaar Card"); display them directly
    return String(d);
  }
  function docDesc(d){
    if(!d) return '';
    const e=SAH.DOCS[d];
    return e?e.desc:'';
  }

  SAH.ui={hydrateIcons,icon,esc,$,$$,initials,toast,modal,closeModal,badge,ruleList,plainRules,toggleCompare,schemeModal,emptyProfile,bindDemo,ring,updateCompareBadge,buildShell,transitions,reveal,docName,docDesc};
})();
