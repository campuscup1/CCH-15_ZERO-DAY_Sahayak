/* SAHAYAK — eligibility engine + local storage helpers.
   Core rule: MISSING information is "unknown" and never counts as a failed rule. */
(function(){
  const KEYS={profile:'sahayak_profile_v1',compare:'sahayak_compare_v1',docs:'sahayak_docs_v1'};

  const store={
    _get(k,d){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}},
    _set(k,v){try{localStorage.setItem(k,JSON.stringify(v));return true}catch(e){return false}},
    getProfile(){return this._get(KEYS.profile,null)},
    saveProfile(p){return this._set(KEYS.profile,p)},
    clearProfile(){try{localStorage.removeItem(KEYS.profile)}catch(e){}},
    getCompare(){return this._get(KEYS.compare,[]).filter(id=>SAH.SCHEME_MAP[id])},
    setCompare(a){return this._set(KEYS.compare,a.slice(0,3))},
    getDocs(){return this._get(KEYS.docs,{})},
    setDocs(o){return this._set(KEYS.docs,o)}
  };

  const isMissing=v=>v===undefined||v===null||v===''||(typeof v==='number'&&isNaN(v));
  const inr=n=>'₹'+Number(n).toLocaleString('en-IN');

  function valueLabel(key,val){
    if(isMissing(val)) return 'Not provided';
    const f=SAH.FIELD_MAP[key];
    if(!f) return String(val);
    if(key==='income') return inr(val)+' / year';
    if(f.type==='number') return val+(f.unit?' '+f.unit:'');
    const o=(f.options||[]).find(x=>x[0]===val);
    return o?o[1]:String(val);
  }
  function ruleNeed(r){
    const f=SAH.FIELD_MAP[r.f];
    switch(r.op){
      case 'gte': return (r.f==='income'?inr(r.v):r.v)+' or more';
      case 'lte': return (r.f==='income'?inr(r.v):r.v)+' or less';
      case 'eq': return valueLabel(r.f,r.v);
      case 'in': return r.v.map(x=>valueLabel(r.f,x)).join(' / ');
    }
    return '';
  }

  function leaf(r,p){
    const v=p[r.f];
    if(isMissing(v)) return {status:'unknown',missing:[r.f]};
    let ok=false;
    if(r.op==='gte') ok=Number(v)>=r.v;
    else if(r.op==='lte') ok=Number(v)<=r.v;
    else if(r.op==='eq') ok=v===r.v;
    else if(r.op==='in') ok=r.v.includes(v);
    return {status:ok?'pass':'fail',missing:[]};
  }

  function evalRule(rule,p){
    if(rule.or){
      const subs=rule.or.map(s=>leaf(s,p));
      const yours=rule.or.map(s=>SAH.FIELD_MAP[s.f].label+': '+valueLabel(s.f,p[s.f])).join('; ');
      const need=rule.or.map(s=>SAH.FIELD_MAP[s.f].label+' → '+ruleNeed(s)).join('  OR  ');
      if(subs.some(s=>s.status==='pass')) return {rule,status:'pass',missing:[],yours,need};
      const missing=[...new Set(subs.flatMap(s=>s.missing))];
      if(missing.length) return {rule,status:'unknown',missing,yours,need};
      return {rule,status:'fail',missing:[],yours,need};
    }
    const r=leaf(rule,p);
    return {rule,status:r.status,missing:r.missing,yours:valueLabel(rule.f,p[rule.f]),need:ruleNeed(rule)};
  }

  function evalScheme(s,p){
    p=p||{};
    const results=s.rules.map(r=>evalRule(r,p));
    const failed=results.filter(r=>r.status==='fail');
    const unknown=results.filter(r=>r.status==='unknown');
    const passed=results.filter(r=>r.status==='pass');
    const status=failed.length?'not':(unknown.length?'potential':'eligible');
    return {scheme:s,status,results,failed,unknown,passed,
      score:Math.round(passed.length/results.length*100),
      missingFields:[...new Set(unknown.flatMap(r=>r.missing))]};
  }
  const evalAll=(p,list)=>(list||SAH.SCHEMES).map(s=>evalScheme(s,p));
  const summarize=ev=>({eligible:ev.filter(e=>e.status==='eligible').length,potential:ev.filter(e=>e.status==='potential').length,not:ev.filter(e=>e.status==='not').length,total:ev.length});

  function completeness(p){
    p=p||{};
    const ks=SAH.FIELDS.map(f=>f.key);
    const done=ks.filter(k=>!isMissing(p[k])).length;
    return {done,total:ks.length,pct:Math.round(done/ks.length*100),missing:ks.filter(k=>isMissing(p[k]))};
  }

  /* fields whose answer could move 'potential' schemes forward */
  function missingImpact(ev){
    const m={};
    ev.filter(e=>e.status==='potential').forEach(e=>e.missingFields.forEach(f=>{(m[f]=m[f]||[]).push(e.scheme)}));
    return Object.entries(m).map(([field,schemes])=>({field,schemes})).sort((a,b)=>b.schemes.length-a.schemes.length);
  }
  /* schemes missed by at most `max` criteria */
  const nearMisses=(ev,max=2)=>ev.filter(e=>e.status==='not'&&e.failed.length<=max).sort((a,b)=>a.failed.length-b.failed.length||b.score-a.score);

  /* suggest a value for the simulator that would satisfy a failed rule */
  function suggest(rule){
    const r=rule.or?rule.or[0]:rule;
    if(r.op==='eq') return {f:r.f,v:r.v};
    if(r.op==='in') return {f:r.f,v:r.v[0]};
    if(r.op==='gte') return {f:r.f,v:r.v};
    if(r.op==='lte') return {f:r.f,v:r.v};
  }

  SAH.store=store;
  SAH.engine={isMissing,inr,valueLabel,ruleNeed,evalRule,evalScheme,evalAll,summarize,completeness,missingImpact,nearMisses,suggest};
  SAH.STATUS={eligible:'Eligible',potential:'Potentially eligible',not:'Not eligible'};
})();
