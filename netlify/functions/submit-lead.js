'use strict';

const MAX_BODY_BYTES = 12_000;
const ALLOWED_PRODUCTS = new Set(['멀티자판기','냉동자판기','SAFE24 무인매장','상담 후 결정']);
const ALLOWED_QUANTITIES = new Set(['미정','1대','2~3대','4~5대','6대 이상']);
const ALLOWED_TIMELINES = new Set(['미정','1개월 이내','1~3개월','3개월 이후']);
const response = (statusCode, payload) => ({
  statusCode,
  headers: {'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff'},
  body:JSON.stringify(payload)
});
const valid = (v, max, required = true) => typeof v === 'string' && v.trim().length <= max && (!required || v.trim().length > 0);

exports.handler = async function (event) {
  if (event.httpMethod !== 'POST') return response(405,{ok:false,error:'허용되지 않은 요청 방식입니다.'});
  if (!process.env.GOOGLE_SHEET_WEBHOOK_URL || !process.env.LEAD_WEBHOOK_SECRET) {
    return response(503,{ok:false,error:'상담 접수 시스템을 연결하는 중입니다. 잠시 후 다시 시도해 주세요.'});
  }
  if (!event.body || Buffer.byteLength(event.body,'utf8') > MAX_BODY_BYTES) {
    return response(413,{ok:false,error:'입력 내용이 너무 깁니다.'});
  }
  let data;
  try { data = JSON.parse(event.isBase64Encoded ? Buffer.from(event.body,'base64').toString('utf8') : event.body); }
  catch { return response(400,{ok:false,error:'신청서 형식이 올바르지 않습니다.'}); }
  if (!data || Array.isArray(data) || typeof data !== 'object') return response(400,{ok:false,error:'신청서 형식이 올바르지 않습니다.'});
  // Honeypot: avoid forwarding robot-created personal data into the Sheet.
  if (data.website_url) return response(200,{ok:true,id:'접수 완료'});
  const fields = [['company',80],['representative',40],['phone',25],['email',120],['address',200]];
  if (fields.some(([k,m]) => !valid(data[k],m)) || !valid(data.message || '',1000,false))
    return response(400,{ok:false,error:'필수 항목을 확인해 주세요.'});
  if (!/^\S+@\S+\.\S+$/.test(data.email) || !/^[0-9()+\-\s]{8,25}$/.test(data.phone))
    return response(400,{ok:false,error:'이메일 또는 연락처 형식을 확인해 주세요.'});
  if (!ALLOWED_PRODUCTS.has(data.product) || !ALLOWED_QUANTITIES.has(data.quantity || '미정') || !ALLOWED_TIMELINES.has(data.timeline || '미정'))
    return response(400,{ok:false,error:'제품 또는 선택 항목을 확인해 주세요.'});
  if (data.collect_agree !== 'yes' || data.share_agree !== 'yes' || !valid(data.consentVersion || '',50))
    return response(400,{ok:false,error:'개인정보 필수 동의를 확인해 주세요.'});
  for (const key of ['sourcePage','utmSource','utmMedium','utmCampaign']) {
    if (!valid(data[key] || '',400,false)) return response(400,{ok:false,error:'입력 형식을 확인해 주세요.'});
  }
  const payload = {};
  for (const key of [...fields.map(x=>x[0]),'product','quantity','timeline','message','sourcePage','utmSource','utmMedium','utmCampaign','consentVersion','collect_agree','share_agree'])
    payload[key] = String(data[key] || '').trim();
  payload.secret = process.env.LEAD_WEBHOOK_SECRET;
  try {
    const abort = new AbortController();
    const timeout = setTimeout(() => abort.abort(), 12_000);
    let upstream;
    try {
      upstream = await fetch(process.env.GOOGLE_SHEET_WEBHOOK_URL, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(payload),
        signal:abort.signal,
        redirect:'follow'
      });
    } finally {clearTimeout(timeout);}
    if (!upstream.ok) throw new Error('Google Apps Script HTTP '+upstream.status);
    const text = await upstream.text();
    const result = JSON.parse(text);
    if (!result.ok) {
      if (result.code === 'duplicate') return response(409,{ok:false,error:'같은 연락처로 최근 접수된 문의가 있습니다. 중복 접수 여부를 확인해 주세요.'});
      throw new Error('Apps Script rejected request');
    }
    return response(200,{ok:true,id:String(result.id || '')});
  } catch (error) {
    // Never echo private data or secrets; Netlify logs retain only failure type.
    console.error('Lead submission backend error:',error instanceof Error ? error.name : 'unknown');
    return response(502,{ok:false,error:'접수 시스템에 연결할 수 없습니다. 잠시 후 다시 시도해 주세요.'});
  }
};
