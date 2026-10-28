async function req(path,opts={}){const r=await fetch(path,opts);const d=await r.json().catch(()=>({}));if(!r.ok)throw new Error(d.detail||'Request failed. Is the backend running?');return d}
export const getDashboard=()=>req('/api/dashboard'); export const getAnalyses=()=>req('/api/analyses');
export const postForm=(p,f)=>req(p,{method:'POST',body:f});
export const postJson=(p,b)=>req(p,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});