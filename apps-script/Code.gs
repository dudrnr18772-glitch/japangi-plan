/**
 * Google Sheets webhook for 자판기플랜.
 * Deploy: Google Sheets > Extensions > Apps Script > Deploy > New deployment > Web app
 * Execute as: Me; Who has access: Anyone. Never put the shared secret in website HTML.
 * Script Properties: SHEET_ID, LEAD_SECRET, NOTIFY_EMAIL.
 * New submissions are saved first, then an email alert is sent with MailApp.
 * Records older than one calendar year are removed by a daily time-driven trigger.
 */
const SHEET_NAME = '상담접수';
const HEADERS = [
  '접수시각','접수ID','상호명','대표자명','연락처','관심상품','이메일',
  '설치 예정 주소','희망 수량','도입 희망 시기','문의사항','유입 페이지',
  'UTM Source','UTM Medium','UTM Campaign','수집 이용 동의',
  '제3자 제공 동의','동의문서 버전','진행상태','비고'
];
const PRODUCTS = ['멀티자판기','냉동자판기','SAFE24 무인매장','상담 후 결정'];

function doGet() {
  return respond_({ok:false,code:'post_only'});
}
function doPost(e) {
  const props = PropertiesService.getScriptProperties();
  try {
    if (!props.getProperty('LEAD_SECRET') || !props.getProperty('SHEET_ID'))
      return respond_({ok:false,code:'not_configured'});
    const d = JSON.parse(e.postData.contents || '{}');
    if (typeof d.secret !== 'string' || d.secret !== props.getProperty('LEAD_SECRET'))
      return respond_({ok:false,code:'unauthorized'});
    const required = ['company','representative','phone','address','product','consentVersion'];
    if (required.some(k => typeof d[k] !== 'string' || !d[k].trim()))
      return respond_({ok:false,code:'bad_fields'});
    if (d.collect_agree !== 'yes' || d.share_agree !== 'yes' || PRODUCTS.indexOf(d.product) < 0)
      return respond_({ok:false,code:'missing_consent'});
    const lock = LockService.getScriptLock();
    lock.waitLock(15000);
    let id;
    try {
      const cache = CacheService.getScriptCache();
      const dedupe = Utilities.base64EncodeWebSafe(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256,
        (d.phone || '').replace(/\D/g,'')+'|'+d.company+'|'+d.product)).slice(0,32);
      if (cache.get(dedupe)) return respond_({ok:false,code:'duplicate'});
      const sheet = ensureSheet_(props.getProperty('SHEET_ID'));
      id = Utilities.formatDate(new Date(), 'Asia/Seoul','yyyyMMdd-HHmmss') + '-' + Utilities.getUuid().slice(0,8).toUpperCase();
      const row = [
        new Date(), id, d.company, d.representative, d.phone, d.product, d.email,
        d.address, d.quantity || '미정', d.timeline || '미정',d.message || '',
        d.sourcePage || '', d.utmSource || '',d.utmMedium || '',d.utmCampaign || '',
        '동의', '동의',d.consentVersion, '신규', ''
      ].map(safeCell_);
      sheet.appendRow(row);
      cache.put(dedupe,'1',300); // 5-minute duplicate prevention
    } finally { lock.releaseLock(); }
    const notified = sendEmailNotification_(id,d.product);
    if (!notified) console.log('Lead saved to Sheet; Gmail notification was not sent. Check NOTIFY_EMAIL, authorization and mail quota.');
    return respond_({ok:true,id:id,notificationSent:notified});
  } catch (error) {
    console.error('Lead webhook failed:',error && error.message ? error.message : String(error));
    return respond_({ok:false,code:'server_error'});
  }
}

function ensureSheet_(spreadsheetId) {
  const ss = SpreadsheetApp.openById(spreadsheetId);
  const sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
    sheet.getRange(1,1,1,HEADERS.length).setBackground('#102c3d').setFontColor('white').setFontWeight('bold');
    sheet.setColumnWidth(1,165);
    sheet.setColumnWidth(2,210);
    sheet.setColumnWidth(3,175);
    sheet.setColumnWidth(4,100);
    sheet.setColumnWidth(5,150);
    sheet.setColumnWidth(6,150);
    sheet.setColumnWidth(7,210);
    sheet.setColumnWidth(8,300);
    sheet.setColumnWidth(11,260);
    sheet.setColumnWidth(19,110);
  }
  return sheet;
}

function safeCell_(value) {
  if (value instanceof Date) return value;
  const v = String(value || '').slice(0,1000);
  return /^[=+\-@]/.test(v) ? "'" + v : v; // Prevent spreadsheet formula injection.
}
/** Sends an alert only after the spreadsheet row is successfully appended.
 * No customer name, phone number, email, or address is included in the alert.
 * The site visitor cannot choose the recipient; NOTIFY_EMAIL is stored server-side.
 */
function sendEmailNotification_(id, product) {
  const props = PropertiesService.getScriptProperties();
  const recipient = (props.getProperty('NOTIFY_EMAIL') || '').trim();
  if (!recipient || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(recipient)) return false;
  try {
    if (MailApp.getRemainingDailyQuota() < 1) {
      console.warn('Gmail notification quota exhausted');
      return false;
    }
    const sheetId = props.getProperty('SHEET_ID');
    const link = sheetId ? 'https://docs.google.com/spreadsheets/d/' + sheetId + '/edit' : '';
    MailApp.sendEmail({
      to: recipient,
      subject: '[자판기플랜] 신규 상담 접수',
      body: [
        '새로운 자판기 구매·설치 상담이 접수되었습니다.',
        '',
        '관심상품: ' + product,
        '접수번호: ' + id,
        '접수상태: 스프레드시트 저장 완료',
        '',
        '상담 정보를 확인하려면 구글 스프레드시트를 열어주세요.',
        link,
        '',
        '이 메일은 상담 접수 알림입니다. 고객 개인정보는 메일 본문에 포함하지 않습니다.'
      ].join('\n'),
      name: '자판기플랜'
    });
    return true;
  } catch (error) {
    console.error('Gmail notification failed: ' + (error && error.message ? error.message : String(error)));
    return false;
  }
}
/** Remove rows whose receipt timestamp is older than one calendar year.
 * Keep the header row; the trigger is installed from testSetup().
 */
function purgeExpiredLeads() {
  const id = PropertiesService.getScriptProperties().getProperty('SHEET_ID');
  if (!id) throw new Error('SHEET_ID 설정 필요');
  const sheet = SpreadsheetApp.openById(id).getSheetByName(SHEET_NAME);
  if (!sheet || sheet.getLastRow() < 2) return;
  const cutoff = new Date();
  cutoff.setFullYear(cutoff.getFullYear() - 1);
  const dates = sheet.getRange(2, 1, sheet.getLastRow() - 1, 1).getValues();
  for (let i = dates.length - 1; i >= 0; i--) {
    const d = dates[i][0];
    if (d instanceof Date && !isNaN(d.getTime()) && d.getTime() < cutoff.getTime()) {
      sheet.deleteRow(i + 2);
    }
  }
}

function installRetentionTrigger_() {
  const found = ScriptApp.getProjectTriggers().some(t => t.getHandlerFunction() === 'purgeExpiredLeads');
  if (!found) ScriptApp.newTrigger('purgeExpiredLeads').timeBased().everyDays(1).create();
}

function respond_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

/** Run once from the editor to authorize Sheets + MailApp. Sends a test email, but does NOT create a customer row. */
function testSetup() {
  const props=PropertiesService.getScriptProperties();
  if (!props.getProperty('SHEET_ID') || !props.getProperty('LEAD_SECRET') || !props.getProperty('NOTIFY_EMAIL')) throw new Error('SHEET_ID / LEAD_SECRET / NOTIFY_EMAIL 설정 필요');
  const sheet=ensureSheet_(props.getProperty('SHEET_ID'));
  Logger.log('Sheet ready: '+sheet.getName());
  installRetentionTrigger_();
  purgeExpiredLeads();
  if (!sendEmailNotification_('TEST-SETUP','연동 테스트')) {
    throw new Error('Gmail 테스트 메일 발송 실패: NOTIFY_EMAIL, 권한 및 MailApp 발송 한도 확인');
  }
  Logger.log('Gmail test notification sent: true');
  Logger.log('One-year retention cleanup trigger installed');
}
