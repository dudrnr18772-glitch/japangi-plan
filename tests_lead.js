'use strict';
// Offline integration checks for the deployed Netlify Function. No personal data leaves CI.
const assert = require('node:assert/strict');
const {handler} = require('./netlify/functions/submit-lead.js');
const required = {
  company: '테스트 상호', representative: '테스트',
  phone: '010-1234-5678', address: '서울시 테스트구',
  product: '멀티자판기', collect_agree: 'yes', share_agree: 'yes',
  consentVersion: '2026-11-v1', quantity: '미정', timeline: '미정'
};
const submit = (payload) => handler({
  httpMethod:'POST', isBase64Encoded:false, body:JSON.stringify(payload)
});
(async () => {
  process.env.GOOGLE_SHEET_WEBHOOK_URL = 'https://example.com/exec';
  process.env.LEAD_WEBHOOK_SECRET = 'test-only-secret';
  const upstream = [];
  global.fetch = async (_url, options) => {
    upstream.push(JSON.parse(options.body));
    return {ok:true,status:200,text:async () => JSON.stringify({ok:true,id:'TEST-01',notificationSent:true})};
  };
  let r=await submit(required);
  assert.equal(r.statusCode,200,'email omitted should be accepted');
  assert.equal(upstream.at(-1).email,'','omitted email should be forwarded as empty');
  r=await submit({...required,email:''});
  assert.equal(r.statusCode,200,'empty email should be accepted');
  r=await submit({...required,email:'sample@example.com'});
  assert.equal(r.statusCode,200,'valid optional email should be accepted');
  r=await submit({...required,email:'not-an-email'});
  assert.equal(r.statusCode,400,'invalid provided email must be rejected');
  r=await submit({...required,collect_agree:'no'});
  assert.equal(r.statusCode,400,'missing consent must be rejected');
  r=await submit({...required,phone:'wrong'});
  assert.equal(r.statusCode,400,'invalid phone must be rejected');
  global.fetch=async()=>({ok:true,status:200,text:async()=>JSON.stringify({ok:false,code:'duplicate'})});
  r=await submit(required);
  assert.equal(r.statusCode,409,'duplicate response must be preserved');
  delete process.env.LEAD_WEBHOOK_SECRET;
  r=await submit(required);
  assert.equal(r.statusCode,503,'missing environment variable must block intake');
  console.log('PASS: 8 offline consultation function checks');
})().catch(error=>{console.error(error);process.exitCode=1;});
