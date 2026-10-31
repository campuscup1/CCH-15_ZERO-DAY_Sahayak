/* SAHAYAK — API layer (single place for all network calls).
   Uses mock/local data until the Python FastAPI backend (Yash) is ready.
   To go live: set USE_MOCK=false and align the ENDPOINTS + normalisers below. */
(function(){
  const CONFIG={
    BASE_URL:'http://localhost:8000',   // FastAPI dev server (assumed)
    USE_MOCK:true,                       // flip to false when the backend is ready
    TIMEOUT_MS:8000,
    MOCK_DELAY_MS:120
  };
  // Assumed endpoints — to be confirmed with the backend contract.
  const ENDPOINTS={health:'/health',schemes:'/api/schemes',match:'/api/match',profile:'/api/profile'};

  const wait=ms=>new Promise(r=>setTimeout(r,ms));

  async function request(path,{method='GET',body}={}){
    const ctl=new AbortController();
    const t=setTimeout(()=>ctl.abort(),CONFIG.TIMEOUT_MS);
    try{
      const res=await fetch(CONFIG.BASE_URL+path,{
        method,signal:ctl.signal,
        headers:{'Content-Type':'application/json','Accept':'application/json'},
        body:body?JSON.stringify(body):undefined
      });
      if(!res.ok) throw new Error('HTTP '+res.status);
      return await res.json();
    } finally { clearTimeout(t); }
  }

  /* Try the backend; on failure fall back to the local mock so the demo never breaks. */
  async function call(real,mock){
    if(CONFIG.USE_MOCK){ await wait(CONFIG.MOCK_DELAY_MS); return {data:await mock(),source:'mock'}; }
    try{ return {data:await real(),source:'api'}; }
    catch(err){ console.warn('[SAHAYAK] API unavailable, using mock data:',err.message); return {data:await mock(),source:'mock-fallback'}; }
  }

  // Normalise backend payloads into the shapes the UI expects.
  const normaliseSchemes=raw=>Array.isArray(raw)&&raw.length&&raw[0].rules?raw:SAH.SCHEMES;
  const normaliseMatches=(raw,profile)=>SAH.engine.evalAll(profile); // replace once the match response shape is agreed

  SAH.api={
    config:CONFIG,
    mode:()=>CONFIG.USE_MOCK?'Mock data':'Live API',
    async health(){
      return call(()=>request(ENDPOINTS.health),()=>({status:'ok',mode:'mock'}));
    },
    async getSchemes(){
      const r=await call(async()=>normaliseSchemes(await request(ENDPOINTS.schemes)),async()=>SAH.SCHEMES);
      return r.data;
    },
    async matchSchemes(profile){
      const r=await call(async()=>normaliseMatches(await request(ENDPOINTS.match,{method:'POST',body:profile}),profile),async()=>SAH.engine.evalAll(profile));
      return r.data;
    },
    /* Simulation never touches the saved profile — it only evaluates the copy it is given. */
    async simulate(hypotheticalProfile){
      const r=await call(async()=>normaliseMatches(await request(ENDPOINTS.match,{method:'POST',body:{...hypotheticalProfile,simulate:true}}),hypotheticalProfile),async()=>SAH.engine.evalAll(hypotheticalProfile));
      return r.data;
    },
    async saveProfile(profile){
      const r=await call(()=>request(ENDPOINTS.profile,{method:'POST',body:profile}),async()=>({ok:true}));
      SAH.store.saveProfile(profile); // demo profile always persists in localStorage
      return r.data;
    },
    getProfile(){return SAH.store.getProfile();}
  };
})();
