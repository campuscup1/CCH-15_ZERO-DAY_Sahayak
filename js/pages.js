/* SAHAYAK — page controllers */
(function(){
  const {icon,esc,$,$$,toast,badge,ruleList,ring,schemeModal,toggleCompare,emptyProfile,bindDemo}=SAH.ui;
  const E=SAH.engine, S=SAH.store;
  const rank={eligible:2,potential:1,not:0};
  const fl=k=>SAH.FIELD_MAP[k].label;

  function animateBars(root){
    requestAnimationFrame(()=>requestAnimationFrame(()=>$$('[data-w]',root||document).forEach(b=>{b.style.width=b.dataset.w+'%'})));
  }
  function setRing(el,pct){el.style.setProperty('--p',pct)}

  /* ---------- shared scheme card ---------- */
  function schemeCard(s,ev){
    const inC=S.getCompare().includes(s.id);
    return `<article class="card hover sc">
      <div class="sc-top"><div class="s-ic">${icon(s.icon,21)}</div><div><h3>${esc(s.name)}</h3><div class="hi">${esc(s.hi)}</div></div></div>
      <div style="display:flex;gap:8px;flex-wrap:wrap"><span class="pill">${esc(s.category)}</span>${ev?badge(ev.status):''}</div>
      <p class="b">${esc(s.summary)}</p>
      <div class="sc-foot"><button class="btn btn-primary btn-sm" data-open="${s.id}">View details</button>
      <button class="btn btn-ghost btn-sm cmp-btn ${inC?'on':''}" data-cmp="${s.id}" title="Add to comparison">${icon('columns',15)} Compare</button></div>
    </article>`;
  }
  function bindCards(root){
    root.addEventListener('click',e=>{
      const o=e.target.closest('[data-open]');
      if(o){schemeModal(o.dataset.open);return}
      const c=e.target.closest('[data-cmp]');
      if(c){toggleCompare(c.dataset.cmp);c.classList.toggle('on',S.getCompare().includes(c.dataset.cmp))}
    });
  }

  const pages={};

  /* ================= LANDING ================= */
  pages.index=function(){
    const feat=['pm-kisan','pmjay','pmay-g','post-matric-sc','mudra','apy'].map(id=>SAH.SCHEME_MAP[id]);
    const box=$('#featured');
    box.innerHTML=feat.map(s=>schemeCard(s)).join('');
    bindCards(box);
    const mt=$('#mt'),nl=$('#nl');
    mt.addEventListener('click',()=>{const o=nl.classList.toggle('open');mt.setAttribute('aria-expanded',o)});
    $$('#nl a').forEach(a=>a.addEventListener('click',()=>nl.classList.remove('open')));
    $$('[data-demo-go]').forEach(b=>b.addEventListener('click',async()=>{
      await SAH.api.saveProfile({...SAH.DEMO_PROFILE});
      document.body.classList.add('page-out');setTimeout(()=>location.href='dashboard.html',170);
    }));
    const prof=S.getProfile();
    if(prof){const c=$('#ctaCheck');if(c){c.querySelector('span').textContent='Continue to dashboard';c.href='dashboard.html'}}
  };

  /* ================= DASHBOARD ================= */
  pages.dashboard=async function(){
    const root=$('#dash');
    const p=S.getProfile();
    if(!p){root.innerHTML=`<div class="hero-card"><div><h2>Namaste! <span class="hi">नमस्ते</span></h2><p>Tell us a little about yourself and SAHAYAK will show which schemes you may qualify for — and exactly why.</p><div class="btns"><a class="btn btn-saffron" href="profile.html">${icon('plus',16)} Create your profile</a><button class="btn btn-light" data-demo>${icon('zap',16)} Load demo profile</button></div></div></div>`;
      bindDemo(root);return}
    const ev=await SAH.api.matchSchemes(p);
    const sm=E.summarize(ev), cp=E.completeness(p);
    const top=ev.filter(e=>e.status==='eligible').sort((a,b)=>b.passed.length-a.passed.length).slice(0,4);
    const gaps=E.missingImpact(ev).slice(0,3);
    root.innerHTML=`
      <div class="hero-card reveal-in">
        <div><div class="hi" style="opacity:.8;font-size:14px;margin-bottom:6px">नमस्ते</div><h2>Welcome, ${esc(p.name||'Citizen')}</h2>
        <p>${sm.eligible} scheme${sm.eligible===1?'':'s'} match your profile today and ${sm.potential} more could match once a few details are added.</p>
        <div class="btns"><a class="btn btn-saffron" href="matches.html">${icon('check-circle',16)} View my matches</a><a class="btn btn-light" href="profile.html">${icon('user',16)} Update profile</a></div></div>
        <div style="display:flex;gap:14px;align-items:center">${ring(cp.pct)}<div><b style="font-size:15px">Profile completeness</b><div style="opacity:.8;font-size:13px">${cp.done} of ${cp.total} details provided</div></div></div>
      </div>
      <div class="grid g4" style="margin-top:20px">
        <a class="card hover stat ok" href="matches.html?tab=eligible"><div class="si">${icon('check-circle',24)}</div><div><b>${sm.eligible}</b><small>Eligible</small></div></a>
        <a class="card hover stat warn" href="matches.html?tab=potential"><div class="si">${icon('help',24)}</div><div><b>${sm.potential}</b><small>Potentially eligible</small></div></a>
        <a class="card hover stat bad" href="matches.html?tab=not"><div class="si">${icon('x-circle',24)}</div><div><b>${sm.not}</b><small>Not eligible</small></div></a>
        <a class="card hover stat nv" href="schemes.html"><div class="si">${icon('search',24)}</div><div><b>${sm.total}</b><small>Schemes in this demo</small></div></a>
      </div>
      <div class="grid g2" style="margin-top:20px;align-items:start">
        <div class="card"><div class="card-h"><h3>Your top matches</h3><a class="btn btn-ghost btn-sm" href="matches.html">See all ${icon('arrow',14)}</a></div>
          ${top.length?`<div class="list">${top.map(e=>`<div class="li"><div class="s-ic">${icon(e.scheme.icon,20)}</div><div><div class="t">${esc(e.scheme.name)}</div><div class="d">${esc(e.scheme.type)}</div></div><button class="btn btn-ghost btn-sm go" data-open="${e.scheme.id}">Details</button></div>`).join('')}</div>`:`<p class="muted">No fully confirmed matches yet. Check “Potentially eligible” for schemes waiting on a few details.</p>`}
        </div>
        <div class="card"><div class="card-h"><h3>Details that could unlock more</h3><a class="btn btn-ghost btn-sm" href="gap-analyzer.html">Gap analyzer ${icon('arrow',14)}</a></div>
          ${gaps.length?`<div class="list">${gaps.map(g=>`<div class="li"><div class="s-ic" style="background:var(--warn-bg);color:var(--warn)">${icon('help',20)}</div><div><div class="t">${esc(fl(g.field))}</div><div class="d">Needed to confirm ${g.schemes.length} scheme${g.schemes.length>1?'s':''}</div></div></div>`).join('')}</div><p class="muted" style="font-size:12.5px;margin-top:14px">Missing details are never counted as a failed criterion.</p>`:`<p class="muted">Great — nothing important is missing from your profile.</p>`}
        </div>
      </div>
      <h3 style="margin:28px 0 14px">Quick actions</h3>
      <div class="grid g4">
        <a class="qa" href="simulator.html"><div class="s-ic">${icon('sliders',20)}</div><b>What-if simulator</b><span>Test changes without touching your profile.</span></a>
        <a class="qa" href="documents.html"><div class="s-ic">${icon('file',20)}</div><b>Document checklist</b><span>See what to keep ready.</span></a>
        <a class="qa" href="compare.html"><div class="s-ic">${icon('columns',20)}</div><b>Compare schemes</b><span>Side-by-side, up to three.</span></a>
        <a class="qa" href="schemes.html"><div class="s-ic">${icon('search',20)}</div><b>Discover schemes</b><span>Search and filter everything.</span></a>
      </div>
      <div class="card" style="margin-top:22px;display:flex;gap:14px;align-items:center;flex-wrap:wrap">
        <div class="s-ic">${icon('wifi',20)}</div>
        <div style="flex:1;min-width:220px"><b>Data source: ${esc(SAH.api.mode())}</b><div class="muted" style="font-size:13px">Illustrative data is used until the FastAPI backend is connected.</div></div>
        <button class="btn btn-ghost btn-sm" id="ping">${icon('refresh',15)} Test backend connection</button>
      </div>`;
    bindCards(root);
    $('#ping').addEventListener('click',async()=>{
      const r=await SAH.api.health();
      toast(r.source==='mock'?'Mock mode active — no backend call made':'Backend responded: '+r.source,'ok');
    });
  };

  /* ================= PROFILE ================= */
  pages.profile=function(){
    const form=$('#pform');
    const saved=S.getProfile()||{};
    let html=`<div class="card" id="g-name"><div class="card-h"><h3>Basic details</h3></div><div class="grid g2"><div class="field"><label for="f-name">Name (optional)</label><input class="input" id="f-name" name="name" maxlength="60" placeholder="e.g. Your first name" autocomplete="off"><span class="hint">Stored only in this browser.</span></div></div></div>`;
    SAH.GROUPS.forEach(g=>{
      const fs=SAH.FIELDS.filter(f=>f.group===g);
      html+=`<div class="card"><div class="card-h"><h3>${g}</h3></div><div class="grid g2">${fs.map(f=>{
        if(f.type==='number') return `<div class="field"><label for="f-${f.key}">${f.label}${f.unit?` <span class="muted" style="font-weight:500">(${f.unit})</span>`:''}</label><input class="input" type="number" inputmode="numeric" id="f-${f.key}" name="${f.key}" min="${f.min}" max="${f.max}" step="1" placeholder="Leave blank if unsure">${f.hint?`<span class="hint">${f.hint}</span>`:''}<span class="err-msg" id="e-${f.key}"></span></div>`;
        return `<div class="field"><label for="f-${f.key}">${f.label}</label><select class="input" id="f-${f.key}" name="${f.key}"><option value="">Not sure / prefer not to say</option>${f.options.map(o=>`<option value="${esc(o[0])}">${esc(o[1])}</option>`).join('')}</select>${f.hint?`<span class="hint">${f.hint}</span>`:''}</div>`;
      }).join('')}</div></div>`;
    });
    $('#pfields').innerHTML=html;
    const fill=p=>{
      $('#f-name').value=p.name||'';
      SAH.FIELDS.forEach(f=>{const el=$('#f-'+f.key);el.value=E.isMissing(p[f.key])?'':p[f.key]});
      live();
    };
    const collect=()=>{
      const p={name:$('#f-name').value.trim()};
      SAH.FIELDS.forEach(f=>{
        const v=$('#f-'+f.key).value;
        p[f.key]=f.type==='number'?(v===''?'':Number(v)):v;
      });
      return p;
    };
    function live(){
      const p=collect(),cp=E.completeness(p),sm=E.summarize(E.evalAll(p));
      setRing($('#pring'),cp.pct);$('#pring span').textContent=cp.pct+'%';
      $('#pdone').textContent=cp.done+' of '+cp.total+' details provided';
      $('#lv-e').textContent=sm.eligible;$('#lv-p').textContent=sm.potential;$('#lv-n').textContent=sm.not;
    }
    function validate(){
      let ok=true;
      SAH.FIELDS.filter(f=>f.type==='number').forEach(f=>{
        const el=$('#f-'+f.key),er=$('#e-'+f.key),v=el.value;
        let m='';
        if(v!==''){const n=Number(v);if(isNaN(n)||n<f.min||n>f.max)m=`Enter a value between ${f.min} and ${f.max}.`;else if(!Number.isInteger(n))m='Enter a whole number.'}
        er.textContent=m;el.classList.toggle('err',!!m);if(m)ok=false;
      });
      return ok;
    }
    fill(saved);
    form.addEventListener('input',live);
    form.addEventListener('submit',async e=>{
      e.preventDefault();
      if(!validate()){toast('Please fix the highlighted fields.','warn');const b=$('.err');b&&b.focus();return}
      await SAH.api.saveProfile(collect());
      toast('Profile saved in this browser');
      $('#afterSave').hidden=false;
      $('#afterSave').scrollIntoView({behavior:'smooth',block:'nearest'});
      const n=$('.tb-user .nm');if(n)n.textContent=collect().name||'Guest';
    });
    $('#demoBtn').addEventListener('click',()=>{fill(SAH.DEMO_PROFILE);toast('Demo values filled in — press Save to keep them')});
    $('#clearBtn').addEventListener('click',()=>{
      if(!confirm('Clear your saved profile from this browser?'))return;
      S.clearProfile();fill({});$('#afterSave').hidden=true;toast('Profile cleared','warn');
    });
    $('#resetBtn').addEventListener('click',()=>{fill(S.getProfile()||{})});
  };

  /* ================= SCHEMES ================= */
  pages.schemes=function(){
    const prm=new URLSearchParams(location.search);
    const prof=S.getProfile();
    const evs=prof?Object.fromEntries(E.evalAll(prof).map(e=>[e.scheme.id,e])):{};
    const st={q:prm.get('q')||'',cat:prm.get('cat')||'All',status:'all',sort:'name'};
    $('#q').value=st.q;
    $('#cats').innerHTML=['All',...SAH.CATEGORIES].map(c=>`<button class="chip ${c===st.cat?'on':''}" data-c="${c}">${c}</button>`).join('');
    if(!prof){$('#status').disabled=true;$('#status').title='Create a profile to filter by eligibility';$('#noprof').hidden=false}
    const grid=$('#grid');
    function render(){
      const q=st.q.trim().toLowerCase();
      let list=SAH.SCHEMES.filter(s=>{
        if(st.cat!=='All'&&s.category!==st.cat)return false;
        if(st.status!=='all'&&(!evs[s.id]||evs[s.id].status!==st.status))return false;
        if(q&&!(s.name+' '+s.hi+' '+s.summary+' '+s.category+' '+s.ministry+' '+s.type).toLowerCase().includes(q))return false;
        return true;
      });
      if(st.sort==='name')list.sort((a,b)=>a.name.localeCompare(b.name));
      if(st.sort==='category')list.sort((a,b)=>a.category.localeCompare(b.category)||a.name.localeCompare(b.name));
      if(st.sort==='match'&&prof)list.sort((a,b)=>rank[evs[b.id].status]-rank[evs[a.id].status]||evs[b.id].score-evs[a.id].score);
      $('#count').textContent=list.length+' of '+SAH.SCHEMES.length+' schemes';
      grid.innerHTML=list.length?list.map(s=>schemeCard(s,evs[s.id])).join(''):`<div class="card empty" style="grid-column:1/-1"><div class="e-ic">${icon('search',26)}</div><h3>No schemes found</h3><p>Try a different keyword or clear the filters.</p><div class="row"><button class="btn btn-ghost" id="clr">Clear filters</button></div></div>`;
      const c=$('#clr');c&&c.addEventListener('click',()=>{st.q='';st.cat='All';st.status='all';$('#q').value='';$('#status').value='all';syncChips();render()});
    }
    function syncChips(){$$('#cats .chip').forEach(c=>c.classList.toggle('on',c.dataset.c===st.cat))}
    $('#cats').addEventListener('click',e=>{const c=e.target.closest('.chip');if(!c)return;st.cat=c.dataset.c;syncChips();render()});
    let t;$('#q').addEventListener('input',e=>{clearTimeout(t);t=setTimeout(()=>{st.q=e.target.value;render()},150)});
    $('#status').addEventListener('change',e=>{st.status=e.target.value;render()});
    $('#sort').addEventListener('change',e=>{st.sort=e.target.value;render()});
    if(!prof){const mo=[...$('#sort').options].find(o=>o.value==='match');if(mo)mo.remove()}
    bindCards(grid);render();
  };

  /* ================= MATCHES ================= */
  pages.matches=async function(){
    const root=$('#mroot');
    const p=S.getProfile();
    if(!p){root.innerHTML=emptyProfile();bindDemo(root);return}
    const ev=await SAH.api.matchSchemes(p);
    const sm=E.summarize(ev);
    let tab=new URLSearchParams(location.search).get('tab');
    if(!['eligible','potential','not'].includes(tab))tab=sm.eligible?'eligible':(sm.potential?'potential':'not');
    let q='';
    const reasonOf=e=>{
      if(e.status==='eligible')return 'You meet every listed criterion for this scheme.';
      if(e.status==='potential')return `None of your answers rule you out. Still to confirm: ${e.missingFields.map(fl).join(', ')}. Missing information is not counted against you.`;
      return 'Not met: '+e.failed.map(f=>f.rule.label).join('; ')+'.';
    };
    root.innerHTML=`
      <div class="toolbar"><div class="tabs" role="tablist" id="tabs">
        <button class="tab" data-t="eligible" role="tab">${icon('check-circle',16)} Eligible <span class="n">${sm.eligible}</span></button>
        <button class="tab" data-t="potential" role="tab">${icon('help',16)} Potentially eligible <span class="n">${sm.potential}</span></button>
        <button class="tab" data-t="not" role="tab">${icon('x-circle',16)} Not eligible <span class="n">${sm.not}</span></button></div>
        <div class="search" style="margin-left:auto;min-width:220px;max-width:300px;flex:1">${icon('search',17)}<input class="input" id="mq" type="search" placeholder="Search within results" aria-label="Search within results"></div></div>
      <div class="card" id="tabnote" style="margin-bottom:18px;padding:14px 18px;font-size:14px"></div>
      <div class="grid" id="mlist"></div>`;
    const notes={
      eligible:'You meet all listed criteria for these schemes. Always confirm with the official source before applying.',
      potential:'You are not ruled out. These schemes need a few more details from you — missing information is never treated as a failed criterion.',
      not:'At least one criterion is clearly not met. Open a scheme to see the exact reason — and try the simulator to explore what-if changes.'
    };
    function render(){
      $$('#tabs .tab').forEach(t=>{const on=t.dataset.t===tab;t.classList.toggle('on',on);t.setAttribute('aria-selected',on)});
      $('#tabnote').textContent=notes[tab];
      const list=ev.filter(e=>e.status===tab&&(!q||(e.scheme.name+' '+e.scheme.category).toLowerCase().includes(q))).sort((a,b)=>b.score-a.score);
      $('#mlist').innerHTML=list.length?list.map(e=>{
        const s=e.scheme,col=e.status==='eligible'?'':e.status==='potential'?'saf':'';
        return `<article class="card match" data-id="${s.id}">
          <div class="match-h"><div class="s-ic">${icon(s.icon,21)}</div>
            <div class="info"><h3>${esc(s.name)}</h3><div class="muted" style="font-size:13px">${esc(s.category)} · ${esc(s.type)}</div></div>
            <div class="match-meter"><small>${e.passed.length} of ${e.results.length} criteria met${e.unknown.length?`, ${e.unknown.length} unknown`:''}</small><div class="bar ${col}"><i data-w="${e.score}" ${e.status==='not'?'style="background:var(--bad)"':''}></i></div></div>
            ${badge(e.status)}
            <button class="btn btn-ghost btn-sm tg" aria-expanded="false">Why? ${icon('down',15)}</button></div>
          <div class="reason">${esc(reasonOf(e))}</div>
          <div class="match-body">${ruleList(e.results)}
            <div class="acts"><button class="btn btn-primary btn-sm" data-open="${s.id}">Scheme details</button><button class="btn btn-ghost btn-sm cmp-btn ${S.getCompare().includes(s.id)?'on':''}" data-cmp="${s.id}">${icon('columns',15)} Compare</button><a class="btn btn-ghost btn-sm" href="documents.html">${icon('file',15)} Documents</a>${e.status==='not'?`<a class="btn btn-ghost btn-sm" href="simulator.html">${icon('sliders',15)} Try simulator</a>`:''}${e.status==='potential'?`<a class="btn btn-ghost btn-sm" href="gap-analyzer.html">${icon('target',15)} Fill the gaps</a>`:''}</div></div>
        </article>`}).join(''):`<div class="card empty"><div class="e-ic">${icon('info',26)}</div><h3>Nothing here</h3><p>${tab==='eligible'?'No fully confirmed matches yet. Check “Potentially eligible”.':'No schemes in this group.'}</p></div>`;
      animateBars($('#mlist'));
    }
    $('#tabs').addEventListener('click',e=>{const t=e.target.closest('.tab');if(!t)return;tab=t.dataset.t;history.replaceState(null,'','?tab='+tab);render()});
    $('#mq').addEventListener('input',e=>{q=e.target.value.trim().toLowerCase();render()});
    $('#mlist').addEventListener('click',e=>{
      const tg=e.target.closest('.tg');
      if(tg){const m=tg.closest('.match');const o=m.classList.toggle('open');tg.setAttribute('aria-expanded',o);return}
      const o=e.target.closest('[data-open]');if(o){schemeModal(o.dataset.open);return}
      const c=e.target.closest('[data-cmp]');if(c){toggleCompare(c.dataset.cmp);c.classList.toggle('on',S.getCompare().includes(c.dataset.cmp))}
    });
    render();
  };

  /* ================= GAP ANALYZER ================= */
  pages.gap=async function(){
    const root=$('#groot');
    const p=S.getProfile();
    if(!p){root.innerHTML=emptyProfile('The gap analyzer needs a profile to find what is missing.');bindDemo(root);return}
    async function draw(){
      const prof=S.getProfile();
      const ev=await SAH.api.matchSchemes(prof);
      const cp=E.completeness(prof),imp=E.missingImpact(ev),near=E.nearMisses(ev,2);
      root.innerHTML=`
        <div class="grid g3" style="margin-bottom:20px">
          <div class="card" style="display:flex;gap:16px;align-items:center">${ring(cp.pct)}<div><b>Profile completeness</b><div class="muted" style="font-size:13px">${cp.missing.length} detail${cp.missing.length===1?'':'s'} not provided</div></div></div>
          <div class="card stat warn"><div class="si">${icon('help',24)}</div><div><b>${ev.filter(e=>e.status==='potential').length}</b><small>Schemes waiting on information</small></div></div>
          <div class="card stat bad"><div class="si">${icon('target',24)}</div><div><b>${near.length}</b><small>Near-miss schemes (1–2 criteria)</small></div></div>
        </div>
        <div class="card" style="margin-bottom:20px">
          <div class="card-h"><h3>1 · Missing information</h3><span class="muted" style="font-size:13px">Answer here — it updates your saved profile</span></div>
          ${imp.length?`<div class="list">${imp.map(g=>{
            const f=SAH.FIELD_MAP[g.field];
            const inp=f.type==='number'?`<input class="input" type="number" min="${f.min}" max="${f.max}" placeholder="${f.unit||'Value'}" data-f="${f.key}" aria-label="${esc(f.label)}">`:`<select class="input" data-f="${f.key}" aria-label="${esc(f.label)}"><option value="">Select…</option>${f.options.map(o=>`<option value="${esc(o[0])}">${esc(o[1])}</option>`).join('')}</select>`;
            return `<div class="li gap"><div class="s-ic" style="background:var(--warn-bg);color:var(--warn)">${icon('help',20)}</div><div class="gi"><div class="t">${esc(f.label)}</div><div class="unlock">Needed to confirm <b>${g.schemes.length}</b> scheme${g.schemes.length>1?'s':''}: ${g.schemes.slice(0,3).map(s=>esc(s.name)).join(', ')}${g.schemes.length>3?' +'+(g.schemes.length-3)+' more':''}</div></div><div class="qf">${inp}<button class="btn btn-primary btn-sm" data-save="${f.key}">Save</button></div></div>`}).join('')}</div>`
          :`<div class="empty" style="padding:24px"><div class="e-ic" style="background:var(--ok-bg);color:var(--ok)">${icon('check-circle',26)}</div><h3>No missing information</h3><p>Every scheme can be fully evaluated with what you have provided.</p></div>`}
          ${cp.missing.length&&!imp.length?`<p class="muted" style="font-size:13px">Other optional details are blank, but no current scheme depends on them.</p>`:''}
        </div>
        <div class="card">
          <div class="card-h"><h3>2 · Eligibility gaps</h3><span class="muted" style="font-size:13px">Schemes you narrowly miss</span></div>
          ${near.length?`<div class="list">${near.map(e=>`<div class="li gap"><div class="s-ic">${icon(e.scheme.icon,20)}</div><div class="gi"><div class="t">${esc(e.scheme.name)}</div>
            ${e.failed.map(f=>{const sg=E.suggest(f.rule);return `<div class="rule fail" style="margin-top:8px"><span class="rule-ic">${icon('x',14)}</span><div><div class="rule-t">${esc(f.rule.label)}</div><div class="rule-s">Yours: ${esc(f.yours)} · Needs: ${esc(f.need)}${sg?` · <a href="simulator.html?f=${sg.f}&v=${encodeURIComponent(sg.v)}">Try this in the simulator</a>`:''}</div></div></div>`}).join('')}</div>
            <div style="display:flex;flex-direction:column;gap:8px;align-items:flex-end"><span class="badge not">${e.failed.length} gap${e.failed.length>1?'s':''}</span><button class="btn btn-ghost btn-sm" data-open="${e.scheme.id}">Details</button></div></div>`).join('')}</div>
          <p class="muted" style="font-size:12.5px;margin-top:14px">Some criteria (such as age or category) cannot be changed. Use the simulator only to understand what-if scenarios — it never edits your profile.</p>`
          :`<p class="muted">No near-miss schemes right now.</p>`}
        </div>`;
    }
    bindCards(root);
    root.addEventListener('click',async e=>{
      const b=e.target.closest('[data-save]');if(!b)return;
      const k=b.dataset.save,f=SAH.FIELD_MAP[k],el=$('[data-f="'+k+'"]',root);
      if(el.value===''){toast('Choose or enter a value first.','warn');return}
      let v=f.type==='number'?Number(el.value):el.value;
      if(f.type==='number'&&(isNaN(v)||v<f.min||v>f.max)){toast(`Enter a value between ${f.min} and ${f.max}.`,'warn');return}
      const prof={...S.getProfile(),[k]:v};
      await SAH.api.saveProfile(prof);toast(f.label+' saved');draw();
    });
    draw();
  };

  /* ================= SIMULATOR ================= */
  pages.simulator=async function(){
    const root=$('#sroot');
    const base=S.getProfile();
    const baseP=base?{...base}:{};
    let sim={...baseP};
    const prm=new URLSearchParams(location.search);
    if(prm.get('f')&&SAH.FIELD_MAP[prm.get('f')]){
      const f=SAH.FIELD_MAP[prm.get('f')],v=prm.get('v');
      sim[f.key]=f.type==='number'?Number(v):v;
    }
    const fields=SAH.FIELDS.filter(f=>!f.noRule);
    const baseEv=E.evalAll(baseP);
    root.innerHTML=`
      <div class="sim-banner">${icon('lock',20)}<div><b>Simulation mode.</b> Changes here are only a what-if. They are <b>never saved</b> and your profile stays untouched.${base?'':' You have no saved profile, so the simulation starts with every detail unknown.'}</div></div>
      <div class="sim"><div class="card"><div class="card-h"><h3>Change details</h3><button class="btn btn-ghost btn-sm" id="sreset">${icon('refresh',15)} Reset to saved</button></div><div class="sim-ctl" id="sctl"></div></div>
      <div class="card sticky" id="sres"></div></div>`;
    const ctl=$('#sctl');
    function ctlHtml(){
      ctl.innerHTML=fields.map(f=>{
        const v=sim[f.key];
        if(f.key==='age')return `<div class="field full"><label for="s-age">Age: <span id="v-age">${E.isMissing(v)?'not provided':v}</span></label><input type="range" id="s-age-r" min="0" max="100" value="${E.isMissing(v)?30:v}"><input class="input" type="number" id="s-age" data-k="age" min="0" max="120" value="${E.isMissing(v)?'':v}" placeholder="Not provided"></div>`;
        if(f.key==='income')return `<div class="field full"><label for="s-income">Annual household income: <span id="v-income">${E.isMissing(v)?'not provided':E.inr(v)}</span></label><input type="range" id="s-income-r" min="0" max="1500000" step="10000" value="${E.isMissing(v)?200000:Math.min(v,1500000)}"><input class="input" type="number" id="s-income" data-k="income" min="0" step="1000" value="${E.isMissing(v)?'':v}" placeholder="Not provided"></div>`;
        return `<div class="field"><label for="s-${f.key}">${f.label}</label><select class="input" id="s-${f.key}" data-k="${f.key}"><option value="">Not provided</option>${f.options.map(o=>`<option value="${esc(o[0])}" ${v===o[0]?'selected':''}>${esc(o[1])}</option>`).join('')}</select></div>`;
      }).join('');
      markChanged();
    }
    function markChanged(){
      $$('[data-k]',ctl).forEach(el=>{
        const k=el.dataset.k,a=E.isMissing(sim[k])?'':sim[k],b=E.isMissing(baseP[k])?'':baseP[k];
        el.classList.toggle('changed',a!==b);
      });
    }
    let timer;
    async function run(){
      const ev=await SAH.api.simulate({...sim});          // evaluates a copy only
      const a=E.summarize(baseEv),b=E.summarize(ev);
      const d=(x,y)=>{const n=y-x;return n?`<i class="${n>0?'up':'dn'}">${n>0?'+':''}${n}</i>`:''};
      const changes=ev.map((e,i)=>({e,from:baseEv[i].status,to:e.status})).filter(c=>c.from!==c.to);
      const up=changes.filter(c=>rank[c.to]>rank[c.from]),down=changes.filter(c=>rank[c.to]<rank[c.from]);
      const row=c=>`<div class="chg"><span class="s-ic" style="width:32px;height:32px">${icon(c.e.scheme.icon,16)}</span><b style="flex:1">${esc(c.e.scheme.name)}</b>${badge(c.from)}<span class="arrow">${icon('arrow',14)}</span>${badge(c.to)}</div>`;
      $('#sres').innerHTML=`
        <div class="card-h"><h3>Simulated result</h3><span class="tag-illus">${icon('eye',12)} Not saved</span></div>
        <div class="delta"><div><b>${b.eligible}${d(a.eligible,b.eligible)}</b><small>Eligible</small></div><div><b>${b.potential}${d(a.potential,b.potential)}</b><small>Potential</small></div><div><b>${b.not}${d(a.not,b.not)}</b><small>Not eligible</small></div></div>
        ${up.length?`<div class="chg-h" style="color:var(--ok)">${icon('check-circle',16)} Improved (${up.length})</div>${up.map(row).join('')}`:''}
        ${down.length?`<div class="chg-h" style="color:var(--bad)">${icon('alert',16)} Worsened (${down.length})</div>${down.map(row).join('')}`:''}
        ${!changes.length?`<div class="empty" style="padding:22px"><div class="e-ic">${icon('sliders',24)}</div><p>No difference yet. Adjust a detail on the left to see how your matches would change.</p></div>`:''}
        <div class="chg-h">${icon('check-circle',16)} Eligible in this simulation</div>
        ${ev.filter(e=>e.status==='eligible').map(e=>`<div class="chg"><span class="s-ic" style="width:32px;height:32px">${icon(e.scheme.icon,16)}</span><b style="flex:1">${esc(e.scheme.name)}</b><button class="btn btn-ghost btn-sm" data-open="${e.scheme.id}">Details</button></div>`).join('')||'<p class="muted" style="font-size:13.5px">None yet.</p>'}`;
    }
    const sched=()=>{clearTimeout(timer);timer=setTimeout(run,100)};
    ctl.addEventListener('input',e=>{
      const el=e.target,id=el.id;
      if(id==='s-age-r'){sim.age=Number(el.value);$('#s-age').value=el.value;$('#v-age').textContent=el.value}
      else if(id==='s-income-r'){sim.income=Number(el.value);$('#s-income').value=el.value;$('#v-income').textContent=E.inr(el.value)}
      else if(id==='s-age'||id==='s-income'){
        const k=el.dataset.k,v=el.value===''?'':Number(el.value);
        sim[k]=(v!==''&&(isNaN(v)||v<0))?'':v;
        $('#v-'+k).textContent=sim[k]===''?'not provided':(k==='income'?E.inr(sim[k]):sim[k]);
        const r=$('#'+id+'-r');if(r&&sim[k]!=='')r.value=Math.min(sim[k],Number(r.max));
      } else if(el.dataset.k){sim[el.dataset.k]=el.value}
      markChanged();sched();
    });
    $('#sreset').addEventListener('click',()=>{sim={...baseP};ctlHtml();run();toast('Reset to your saved profile','warn')});
    root.addEventListener('click',e=>{const o=e.target.closest('[data-open]');if(o)schemeModal(o.dataset.open)});
    ctlHtml();run();
  };

  /* ================= DOCUMENTS ================= */
  pages.documents=async function(){
    const root=$('#droot');
    const p=S.getProfile();
    const ev=p?await SAH.api.matchSchemes(p):null;
    const st={scope:p?'matched':'all',scheme:'all'};
    root.innerHTML=`
      ${p?'':`<div class="sim-banner">${icon('info',20)}<div>No profile found, so every scheme’s documents are listed. <a href="profile.html"><b>Create a profile</b></a> for a personalised checklist.</div></div>`}
      <div class="toolbar no-print"><div class="chips" id="scope">
        ${p?`<button class="chip" data-s="matched">Eligible + potential</button><button class="chip" data-s="eligible">Eligible only</button>`:''}<button class="chip" data-s="all">All schemes</button></div>
        <select class="input" id="sch" aria-label="Filter by scheme" style="margin-left:auto"></select>
        <button class="btn btn-ghost btn-sm" id="dprint">${icon('printer',15)} Print</button><button class="btn btn-danger btn-sm" id="dreset">${icon('trash',15)} Reset ticks</button></div>
      <div class="card" style="margin-bottom:18px"><div style="display:flex;justify-content:space-between;gap:10px;margin-bottom:10px;flex-wrap:wrap"><b id="dprog">0 of 0 ready</b><span class="muted" style="font-size:13px">Ticks are saved in this browser</span></div><div class="bar"><i id="dbar"></i></div></div>
      <div class="doc-list" id="dlist"></div>`;
    function inScope(){
      return SAH.SCHEMES.filter(s=>{
        if(st.scope==='all'||!ev)return true;
        const e=ev.find(x=>x.scheme.id===s.id);
        return st.scope==='eligible'?e.status==='eligible':e.status!=='not';
      });
    }
    function draw(){
      $$('#scope .chip').forEach(c=>c.classList.toggle('on',c.dataset.s===st.scope));
      const sc=inScope();
      const sel=$('#sch');
      if(st.scheme!=='all'&&!sc.find(s=>s.id===st.scheme))st.scheme='all';
      sel.innerHTML='<option value="all">All schemes in view</option>'+sc.map(s=>`<option value="${s.id}" ${s.id===st.scheme?'selected':''}>${esc(s.name)}</option>`).join('');
      const use=st.scheme==='all'?sc:sc.filter(s=>s.id===st.scheme);
      const map={};use.forEach(s=>s.docs.forEach(d=>(map[d]=map[d]||[]).push(s)));
      const ids=Object.keys(map).sort((a,b)=>map[b].length-map[a].length||SAH.DOCS[a].name.localeCompare(SAH.DOCS[b].name));
      const done=S.getDocs();
      $('#dlist').innerHTML=ids.length?ids.map(d=>`<label class="doc ${done[d]?'done':''}"><input type="checkbox" data-d="${d}" ${done[d]?'checked':''}><span class="cb">${icon('check',14)}</span><div style="flex:1"><div class="dn">${esc(SAH.DOCS[d].name)}</div><div class="dd">${esc(SAH.DOCS[d].desc)}</div><div class="used">${map[d].map(s=>`<span class="pill">${esc(s.name)}</span>`).join('')}</div></div></label>`).join(''):`<div class="card empty"><div class="e-ic">${icon('file',26)}</div><h3>No documents to list</h3><p>No schemes in this view yet. Try “All schemes”.</p></div>`;
      progress(ids);
    }
    function progress(ids){
      const done=S.getDocs(),n=ids.filter(d=>done[d]).length;
      $('#dprog').textContent=n+' of '+ids.length+' documents ready';
      $('#dbar').style.width=(ids.length?Math.round(n/ids.length*100):0)+'%';
    }
    $('#scope').addEventListener('click',e=>{const c=e.target.closest('.chip');if(!c)return;st.scope=c.dataset.s;draw()});
    $('#sch').addEventListener('change',e=>{st.scheme=e.target.value;draw()});
    $('#dlist').addEventListener('change',e=>{
      const cb=e.target.closest('[data-d]');if(!cb)return;
      const d=S.getDocs();d[cb.dataset.d]=cb.checked;S.setDocs(d);
      cb.closest('.doc').classList.toggle('done',cb.checked);
      progress($$('[data-d]').map(x=>x.dataset.d));
    });
    $('#dprint').addEventListener('click',()=>window.print());
    $('#dreset').addEventListener('click',()=>{S.setDocs({});draw();toast('Checklist reset','warn')});
    draw();
  };

  /* ================= COMPARE ================= */
  pages.compare=async function(){
    const root=$('#croot');
    const p=S.getProfile();
    const ev=p?Object.fromEntries((await SAH.api.matchSchemes(p)).map(e=>[e.scheme.id,e])):{};
    let diff=false;
    function draw(){
      const ids=S.getCompare(),list=ids.map(i=>SAH.SCHEME_MAP[i]);
      const rest=SAH.SCHEMES.filter(s=>!ids.includes(s.id));
      const bar=`<div class="toolbar no-print"><select class="input" id="cadd" aria-label="Add a scheme" ${ids.length>=3?'disabled':''} style="min-width:240px"><option value="">${ids.length>=3?'Maximum of 3 schemes reached':'Add a scheme to compare…'}</option>${rest.map(s=>`<option value="${s.id}">${esc(s.name)}</option>`).join('')}</select>
        <label style="display:flex;gap:8px;align-items:center;font-size:14px"><input type="checkbox" id="cdiff" ${diff?'checked':''} style="accent-color:var(--navy)"> Show only differences</label>
        <button class="btn btn-danger btn-sm" id="cclr" style="margin-left:auto" ${ids.length?'':'disabled'}>${icon('trash',15)} Clear all</button></div>`;
      if(list.length<2){
        root.innerHTML=bar+`<div class="card empty"><div class="e-ic">${icon('columns',26)}</div><h3>${list.length?'Add one more scheme':'Nothing to compare yet'}</h3><p>Pick at least two schemes (up to three) from the menu above, or use the “Compare” buttons on the scheme cards.</p><div class="row"><a class="btn btn-primary" href="schemes.html">${icon('search',16)} Browse schemes</a></div></div>`+(list.length?`<div class="grid auto" style="margin-top:18px">${list.map(s=>schemeCard(s,ev[s.id])).join('')}</div>`:'');
        wire();return;
      }
      const rows=[
        ['Category',s=>esc(s.category),s=>s.category],
        ['Ministry / department',s=>esc(s.ministry),s=>s.ministry],
        ['Type of benefit',s=>esc(s.type),s=>s.type],
        ['What you get (illustrative)',s=>esc(s.benefit),s=>s.benefit],
        ['Key eligibility',s=>`<ul>${s.rules.map(r=>`<li>${esc(r.label)}</li>`).join('')}</ul>`,s=>s.rules.map(r=>r.label).join('|')],
        ['Documents',s=>`<ul>${s.docs.map(d=>`<li>${esc(SAH.DOCS[d].name)}</li>`).join('')}</ul>`,s=>s.docs.join('|')],
        ['How to apply',s=>`<ul>${s.apply.map(a=>`<li>${esc(a)}</li>`).join('')}</ul>`,s=>s.apply.join('|')]
      ];
      if(p)rows.unshift(['Your status',s=>badge(ev[s.id].status)+`<div class="muted" style="font-size:12.5px;margin-top:8px">${ev[s.id].passed.length} of ${ev[s.id].results.length} criteria met</div>`,s=>ev[s.id].status]);
      root.innerHTML=bar+`<div class="cmp-wrap"><table class="cmp ${diff?'diff':''}"><thead><tr><th class="rl"></th>${list.map(s=>`<th><div style="display:flex;gap:10px;align-items:flex-start"><div class="s-ic">${icon(s.icon,20)}</div><div><div style="font-size:16px;color:var(--blue)">${esc(s.name)}</div><div class="hi muted" style="font-size:12.5px;font-weight:500">${esc(s.hi)}</div></div></div><button class="btn btn-ghost btn-sm no-print" data-rm="${s.id}" style="margin-top:12px">${icon('x',14)} Remove</button></th>`).join('')}</tr></thead>
        <tbody>${rows.map(r=>{const same=new Set(list.map(r[2])).size===1;return `<tr class="${same?'same':''}"><th class="rl">${r[0]}</th>${list.map(s=>`<td>${r[1](s)}</td>`).join('')}</tr>`}).join('')}</tbody></table></div>
        <p class="muted" style="font-size:12.5px;margin-top:12px">Illustrative information for a hackathon prototype — not official.</p>`;
      wire();
    }
    function wire(){
      const add=$('#cadd');add&&add.addEventListener('change',e=>{if(e.target.value){toggleCompare(e.target.value);draw()}});
      const df=$('#cdiff');df&&df.addEventListener('change',e=>{diff=e.target.checked;draw()});
      const cl=$('#cclr');cl&&cl.addEventListener('click',()=>{S.setCompare([]);SAH.ui.updateCompareBadge();draw();toast('Comparison cleared','warn')});
      $$('[data-rm]',root).forEach(b=>b.addEventListener('click',()=>{toggleCompare(b.dataset.rm);draw()}));
      bindOnce();
    }
    let bound=false;
    function bindOnce(){if(bound)return;bound=true;root.addEventListener('click',e=>{const o=e.target.closest('[data-open]');if(o){schemeModal(o.dataset.open);return}const c=e.target.closest('[data-cmp]');if(c){toggleCompare(c.dataset.cmp);draw()}})}
    draw();
  };

  /* ---------- boot ---------- */
  document.addEventListener('DOMContentLoaded',()=>{
    SAH.ui.buildShell();
    SAH.ui.hydrateIcons();
    SAH.ui.transitions();
    SAH.ui.reveal();
    const fn=pages[document.body.dataset.page];
    if(fn)Promise.resolve(fn()).catch(err=>{console.error(err);toast('Something went wrong loading this page.','warn')});
  });
})();
