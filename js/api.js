/* SAHAYAK — API layer (connects to Python FastAPI backend).
   Backend endpoints (no /api/ prefix):
   GET  /health
   GET  /schemes
   GET  /schemes/{scheme_id}
   POST /profile
   GET  /profile
   DELETE /profile
   POST /match
   POST /analyze
   POST /simulate
   GET  /documents/{scheme_id}
   POST /documents/check
   POST /compare
*/
(function(){
  const CONFIG = {
    BASE_URL: 'http://localhost:8000',
    USE_MOCK: false,
    TIMEOUT_MS: 8000,
    MOCK_DELAY_MS: 120
  };

  const ENDPOINTS = {
    health: '/health',
    schemes: '/schemes',
    schemeDetail: (id) => `/schemes/${encodeURIComponent(id)}`,
    profile: '/profile',
    match: '/match',
    analyze: '/analyze',
    simulate: '/simulate',
    documents: (id) => `/documents/${encodeURIComponent(id)}`,
    documentsCheck: '/documents/check',
    compare: '/compare'
  };

  const wait = ms => new Promise(r => setTimeout(r, ms));

  // Field mapping: Frontend (SAH.FIELDS) -> Backend (UserProfile)
  const FIELD_MAP_F2B = {
    age: 'age',
    gender: 'gender',
    maritalStatus: null,
    state: 'state',
    area: 'residential_status',
    income: 'annual_income',
    category: 'category',
    bpl: null,
    occupation: 'occupation',
    education: 'education_level',
    landOwner: 'landholding_required',
    ownsPuccaHouse: 'pucca_house_owned',
    hasLPG: null,
    bankAccount: null,
    disability: null,
    expectingMother: null
  };

  function transformValue(field, value) {
    if (value === '' || value === undefined || value === null) return null;

    switch (field) {
      case 'area':
        return value === 'rural' ? 'Rural' : value === 'urban' ? 'Urban' : value;

      case 'category':
        const catMap = { general: 'OPEN', obc: 'OBC', sc: 'SC', st: 'ST', ews: 'EWS' };
        return catMap[value] ?? value;

      case 'occupation':
        const occMap = {
          farmer: 'Farmer', student: 'Student', salaried: 'Salaried Employee',
          selfEmployed: 'Self-Employed', artisan: 'Artisan', streetVendor: 'Street Vendor',
          unemployed: 'Unemployed', homemaker: 'Homemaker', other: 'Other'
        };
        return occMap[value] ?? value;

      case 'education':
        const eduMap = {
          none: 'No formal schooling', primary: 'Primary', secondary: '10th',
          higherSecondary: '12th', undergraduate: 'Undergraduate', postgraduate: 'Postgraduate'
        };
        return eduMap[value] ?? value;

      case 'landOwner':
        return value === 'yes' ? true : value === 'no' ? false : value;

      case 'ownsPuccaHouse':
        return value === 'yes' ? true : value === 'no' ? false : value;

      case 'income':
      case 'age':
        return Number(value);

      default:
        return value;
    }
  }

  function profileF2B(frontendProfile) {
    const backend = {};
    for (const [fKey, bKey] of Object.entries(FIELD_MAP_F2B)) {
      if (!bKey) continue;
      const fVal = frontendProfile[fKey];
      if (fVal !== '' && fVal !== undefined && fVal !== null) {
        backend[bKey] = transformValue(fKey, fVal);
      }
    }
    if (frontendProfile.documents_held) {
      backend.documents_held = frontendProfile.documents_held;
    }
    return backend;
  }

  function profileB2F(backendProfile) {
    if (!backendProfile) return null;
    const frontend = { name: backendProfile.name || 'Citizen' };
    const reverseMap = {
      age: 'age', annual_income: 'income', state: 'state', category: 'category',
      occupation: 'occupation', education_level: 'education', residential_status: 'area',
      pucca_house_owned: 'ownsPuccaHouse', landholding_required: 'landOwner', gender: 'gender'
    };
    for (const [bKey, fKey] of Object.entries(reverseMap)) {
      if (backendProfile[bKey] !== undefined && backendProfile[bKey] !== null) {
        let val = backendProfile[bKey];
        if (fKey === 'category') {
          const revCat = { OPEN: 'general', OBC: 'obc', SC: 'sc', ST: 'st', EWS: 'ews' };
          val = revCat[val] ?? val.toLowerCase();
        } else if (fKey === 'area') {
          val = val === 'Rural' ? 'rural' : val === 'Urban' ? 'urban' : val;
        } else if (fKey === 'ownsPuccaHouse' || fKey === 'landOwner') {
          val = val === true ? 'yes' : val === false ? 'no' : val;
        }
        frontend[fKey] = val;
      }
    }
    return frontend;
  }

  function normalizeSchemes(raw) {
    if (!Array.isArray(raw)) return SAH.SCHEMES;
    return raw.map(s => ({
      id: s.scheme_id,
      name: s.scheme_name,
      hi: '',
      category: s.category,
      icon: categoryToIcon(s.category),
      ministry: '',
      type: '',
      summary: s.description,
      benefit: s.benefits,
      rules: convertRules(s.eligibility_rules),
      docs: s.required_documents,
      apply: typeof s.application_process === 'string' ? [s.application_process] : (s.application_process || [])
    }));
  }

  function categoryToIcon(cat) {
    const icons = {
      'Agriculture': 'leaf', 'Healthcare': 'heart', 'Health': 'heart',
      'Education': 'book', 'Housing and Financial Assistance': 'home',
      'Housing': 'home', 'Women and Child Welfare': 'users',
      'Employment': 'zap', 'Pension': 'shield', 'Finance': 'wallet',
      'Energy': 'flame', 'Disability': 'heart'
    };
    return icons[cat] ?? 'file';
  }

  function convertRules(rules) {
    if (!rules) return [];
    const out = [];
    if (rules.min_age) out.push({ f: 'age', op: 'gte', v: rules.min_age, label: `Age ${rules.min_age} or above` });
    if (rules.max_age) out.push({ f: 'age', op: 'lte', v: rules.max_age, label: `Age ${rules.max_age} or below` });
    if (rules.max_income !== null && rules.max_income !== undefined) out.push({ f: 'income', op: 'lte', v: rules.max_income, label: `Income ≤ ${rules.max_income}` });
    if (rules.domicile && rules.domicile !== 'All') out.push({ f: 'state', op: 'eq', v: rules.domicile, label: `Domicile: ${rules.domicile}` });
    if (rules.category) {
      const cats = Array.isArray(rules.category) ? rules.category : [rules.category];
      out.push({ f: 'category', op: 'in', v: cats.map(c => c.toLowerCase()), label: `Category: ${cats.join(', ')}` });
    }
    if (rules.education_level) {
      const edus = Array.isArray(rules.education_level) ? rules.education_level : [rules.education_level];
      out.push({ f: 'education', op: 'in', v: edus.map(e => e.toLowerCase()), label: `Education: ${edus.join(', ')}` });
    }
    if (rules.occupation) {
      const occs = Array.isArray(rules.occupation) ? rules.occupation : [rules.occupation];
      out.push({ f: 'occupation', op: 'in', v: occs.map(o => o.toLowerCase()), label: `Occupation: ${occs.join(', ')}` });
    }
    if (rules.gender) out.push({ f: 'gender', op: 'eq', v: rules.gender.toLowerCase(), label: `Gender: ${rules.gender}` });
    if (rules.residential_status) out.push({ f: 'area', op: 'eq', v: rules.residential_status.toLowerCase(), label: `Area: ${rules.residential_status}` });
    if (rules.pucca_house_owned !== undefined) out.push({ f: 'ownsPuccaHouse', op: 'eq', v: rules.pucca_house_owned ? 'yes' : 'no', label: `Pucca house: ${rules.pucca_house_owned ? 'Yes' : 'No'}` });
    if (rules.landholding_required === true) out.push({ f: 'landOwner', op: 'eq', v: 'yes', label: 'Owns cultivable land' });
    return out;
  }

  function normalizeMatches(raw, profile) {
    if (!raw || !raw.results) return SAH.engine.evalAll(profile);
    return raw.results.map(r => ({
      scheme: SAH.SCHEME_MAP[r.scheme_id] || { id: r.scheme_id, name: r.scheme_name, icon: 'file', category: r.category, type: '', summary: '', rules: [], docs: [] },
      status: r.status === 'match' ? 'eligible' : r.status === 'potential_match' ? 'potential' : 'not',
      results: (r.conditions || []).map(c => ({
        rule: { label: c.name },
        status: c.status === 'satisfied' ? 'pass' : c.status === 'not_satisfied' ? 'fail' : 'unknown',
        reason: c.reason,
        yours: '',
        need: ''
      })),
      passed: (r.conditions || []).filter(c => c.status === 'satisfied').length,
      unknown: (r.conditions || []).filter(c => c.status === 'missing_information').length,
      failed: (r.conditions || []).filter(c => c.status === 'not_satisfied').length,
      score: Math.round(((r.conditions || []).filter(c => c.status === 'satisfied').length / Math.max(1, (r.conditions || []).length)) * 100),
      missingFields: (r.conditions || []).filter(c => c.status === 'missing_information').map(c => c.name.toLowerCase().replace(/\s+/g, ''))
    }));
  }

  function normalizeGapAnalysis(raw, profile) {
    if (!raw || !raw.results) return SAH.engine.evalAll(profile);
    return raw.results.map(r => ({
      scheme: SAH.SCHEME_MAP[r.scheme_id] || { id: r.scheme_id, name: r.scheme_name, icon: 'file' },
      status: r.eligibility_status === 'match' ? 'eligible' : r.eligibility_status === 'potential_match' ? 'potential' : 'not',
      results: [
        ...(r.satisfied_conditions || []).map(c => ({ rule: { label: c.name }, status: 'pass', reason: c.reason })),
        ...(r.failed_conditions || []).map(c => ({ rule: { label: c.name }, status: 'fail', reason: c.reason })),
        ...(r.missing_information || []).map(c => ({ rule: { label: c.name }, status: 'unknown', reason: c.reason })),
        ...(r.verification_required || []).map(c => ({ rule: { label: c.name }, status: 'unknown', reason: c.reason }))
      ],
      passed: (r.satisfied_conditions || []).length,
      failed: (r.failed_conditions || []).length,
      unknown: (r.missing_information || []).length + (r.verification_required || []).length,
      missingFields: [...(r.missing_information || []).map(c => c.field), ...(r.verification_required || []).map(c => c.field)]
    }));
  }

  async function request(path, { method = 'GET', body } = {}) {
    const ctl = new AbortController();
    const t = setTimeout(() => ctl.abort(), CONFIG.TIMEOUT_MS);
    try {
      const res = await fetch(CONFIG.BASE_URL + path, {
        method,
        signal: ctl.signal,
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: body ? JSON.stringify(body) : undefined
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail?.message || `HTTP ${res.status}`);
      }
      return await res.json();
    } finally {
      clearTimeout(t);
    }
  }

  async function call(real, mock) {
    if (CONFIG.USE_MOCK) {
      await wait(CONFIG.MOCK_DELAY_MS);
      return { data: await mock(), source: 'mock' };
    }
    try {
      return { data: await real(), source: 'api' };
    } catch (err) {
      console.warn('[SAHAYAK] API unavailable, using mock data:', err.message);
      return { data: await mock(), source: 'mock-fallback' };
    }
  }

  SAH.api = {
    config: CONFIG,
    mode: () => CONFIG.USE_MOCK ? 'Mock data' : 'Live API',

    async health() {
      return call(
        () => request(ENDPOINTS.health),
        () => ({ status: 'ok', mode: 'mock' })
      );
    },

    // Ensure SAH.SCHEME_MAP is populated with backend data
    async loadSchemes() {
      if (SAH.SCHEME_MAP && Object.keys(SAH.SCHEME_MAP).length) return SAH.SCHEME_MAP;
      const r = await this.getSchemes();
      return SAH.SCHEME_MAP;
    },

    async getSchemes() {
      const r = await call(
        async () => {
          const raw = await request(ENDPOINTS.schemes);
          return normalizeSchemes(raw.results || raw);
        },
        async () => SAH.SCHEMES
      );
      SAH.SCHEME_MAP = Object.fromEntries(r.data.map(s => [s.id, s]));
      return r.data;
    },

    async getSchemeDetail(schemeId) {
      const r = await call(
        async () => {
          const raw = await request(ENDPOINTS.schemeDetail(schemeId));
          return normalizeSchemes([raw.scheme])[0];
        },
        async () => SAH.SCHEME_MAP[schemeId]
      );
      return r.data;
    },

    async matchSchemes(frontendProfile) {
      const backendProfile = profileF2B(frontendProfile);
      const r = await call(
        async () => {
          const raw = await request(ENDPOINTS.match, { method: 'POST', body: backendProfile });
          return normalizeMatches(raw, frontendProfile);
        },
        async () => SAH.engine.evalAll(frontendProfile)
      );
      return r.data;
    },

    async analyzeGaps(frontendProfile) {
      const backendProfile = profileF2B(frontendProfile);
      const r = await call(
        async () => {
          const raw = await request(ENDPOINTS.analyze, { method: 'POST', body: backendProfile });
          return normalizeGapAnalysis(raw, frontendProfile);
        },
        async () => SAH.engine.evalAll(frontendProfile)
      );
      return r.data;
    },

    async simulate(simulatedProfile, originalProfile) {
      // Frontend calls simulate({...sim}) where sim is the simulated profile.
      // The page compares the result against baseEv (original evaluation).
      const backendProfile = profileF2B(simulatedProfile);
      const r = await call(
        async () => {
          // If we have the original profile, use the full simulation endpoint
          if (originalProfile) {
            const backendOriginal = profileF2B(originalProfile);
            const changes = {};
            for (const [fKey, bKey] of Object.entries(FIELD_MAP_F2B)) {
              if (!bKey) continue;
              const orig = originalProfile[fKey];
              const sim = simulatedProfile[fKey];
              if (orig !== sim && sim !== '' && sim !== undefined && sim !== null) {
                changes[bKey] = transformValue(fKey, sim);
              }
            }
            const raw = await request(ENDPOINTS.simulate, {
              method: 'POST',
              body: { profile: backendOriginal, changes }
            });
            return normalizeMatches({ results: raw.simulated_results }, simulatedProfile);
          }
          // Fallback: just evaluate the simulated profile directly
          const raw = await request(ENDPOINTS.match, { method: 'POST', body: backendProfile });
          return normalizeMatches(raw, simulatedProfile);
        },
        async () => SAH.engine.evalAll(simulatedProfile)
      );
      return r.data;
    },

    async saveProfile(frontendProfile) {
      const backendProfile = profileF2B(frontendProfile);
      if (frontendProfile.name) {
        backendProfile.name = frontendProfile.name;
      }
      const r = await call(
        async () => {
          const raw = await request(ENDPOINTS.profile, { method: 'POST', body: backendProfile });
          const result = raw.profile ? profileB2F(raw.profile) : frontendProfile;
          if (frontendProfile.name) result.name = frontendProfile.name;
          return result;
        },
        async () => {
          SAH.store.saveProfile(frontendProfile);
          return { ok: true };
        }
      );
      // Always persist to localStorage as well (name is a frontend-only field)
      SAH.store.saveProfile(frontendProfile);
      return r.data;
    },

    async getProfile() {
      const r = await call(
        async () => {
          const raw = await request(ENDPOINTS.profile);
          if (!raw.profile) return null;
          const result = profileB2F(raw.profile);
          // Merge with localStorage for frontend-only fields (name)
          const local = SAH.store.getProfile();
          if (local && local.name) result.name = local.name;
          return result;
        },
        async () => SAH.store.getProfile()
      );
      return r.data;
    },

    async clearProfile() {
      const r = await call(
        async () => request(ENDPOINTS.profile, { method: 'DELETE' }),
        async () => { SAH.store.clearProfile(); return { ok: true }; }
      );
      return r.data;
    },

    async getDocuments(schemeId) {
      const r = await call(
        async () => {
          const raw = await request(ENDPOINTS.documents(schemeId));
          return raw.required_documents || [];
        },
        async () => (SAH.SCHEME_MAP[schemeId]?.docs || [])
      );
      return r.data;
    },

    async checkDocuments(schemeId, availableDocuments) {
      const r = await call(
        async () => {
          const raw = await request(ENDPOINTS.documentsCheck, {
            method: 'POST',
            body: { scheme_id: schemeId, available_documents: availableDocuments }
          });
          return {
            required_documents: raw.required_documents,
            documents_held: raw.documents_held,
            missing_documents: raw.missing_documents,
            readiness_percentage: raw.readiness_percentage,
            message: raw.message
          };
        },
        async () => {
          const scheme = SAH.SCHEME_MAP[schemeId];
          if (!scheme) throw new Error('Scheme not found');
          const required = scheme.docs;
          const held = availableDocuments.filter(d => required.includes(d));
          const missing = required.filter(d => !held.includes(d));
          const pct = required.length ? Math.round((held.length / required.length) * 100) : 100;
          return { required_documents: required, documents_held: held, missing_documents: missing, readiness_percentage: pct, message: '' };
        }
      );
      return r.data;
    },

    async compareSchemes(schemeIds) {
      const r = await call(
        async () => {
          const raw = await request(ENDPOINTS.compare, { method: 'POST', body: { scheme_ids: schemeIds } });
          return raw.schemes.map(s => ({
            scheme_id: s.scheme_id,
            scheme_name: s.scheme_name,
            category: s.category,
            government_level: s.government_level,
            state: s.state,
            benefits: s.benefits,
            eligibility_summary: s.eligibility_summary,
            required_documents: s.required_documents,
            application_process: s.application_process,
            official_website: s.official_website
          }));
        },
        async () => schemeIds.map(id => SAH.SCHEME_MAP[id]).filter(Boolean)
      );
      return r.data;
    }
  };
})();