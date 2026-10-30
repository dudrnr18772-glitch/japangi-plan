
// Lightweight consultation dialog. Native links remain usable when JavaScript is disabled.
const inquiryOverlay = document.getElementById('inquiry-overlay');
if (inquiryOverlay) {
  const inquiryDialog = inquiryOverlay.querySelector('.inquiry-dialog');
  const inquiryProduct = inquiryOverlay.querySelector('select[name="product"]');
  const mapProducts = {multi:'멀티자판기', frozen:'냉동자판기',safe24:'SAFE24 무인매장'};
  let previousFocus = null;
  function openInquiry(productHint) {
    previousFocus = document.activeElement;
    if (mapProducts[productHint]) inquiryProduct.value = mapProducts[productHint];
    else if (/multi-vending-machine|multi-purchase/.test(location.pathname)) inquiryProduct.value='멀티자판기';
    else if (/frozen-vending-machine/.test(location.pathname)) inquiryProduct.value='냉동자판기';
    else if (/unmanned-store/.test(location.pathname)) inquiryProduct.value='SAFE24 무인매장';
    else inquiryProduct.value='';
    inquiryOverlay.hidden = false;
    document.body.classList.add('dialog-open');
    inquiryDialog.focus();
  }
  function closeInquiry() {
    inquiryOverlay.hidden = true;
    document.body.classList.remove('dialog-open');
    if (previousFocus && typeof previousFocus.focus === 'function') previousFocus.focus();
  }
  document.addEventListener('click', event => {
    const anchor=event.target.closest('a[href]');
    if (anchor && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey) {
      let url;
      try { url=new URL(anchor.href, location.href); } catch { return; }
      if (url.origin === location.origin && /\/contact\/?$/.test(url.pathname)) {
        event.preventDefault();
        openInquiry(url.searchParams.get('product'));
      }
    }
    if (event.target.closest('[data-close-inquiry]')) closeInquiry();
  });
  document.addEventListener('keydown', event => {
    if (inquiryOverlay.hidden) return;
    if (event.key==='Escape') {event.preventDefault();closeInquiry();}
    if (event.key==='Tab') {
      const focusable=[...inquiryDialog.querySelectorAll('button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),a[href]')]
        .filter(el=>el.getClientRects().length);
      if (!focusable.length) {event.preventDefault();inquiryDialog.focus();return;}
      const first=focusable[0],last=focusable[focusable.length-1];
      if (event.shiftKey && (document.activeElement===first || document.activeElement===inquiryDialog)) {event.preventDefault();last.focus();}
      else if (!event.shiftKey && document.activeElement===last) {event.preventDefault();first.focus();}
    }
  });
}

const menuButton = document.querySelector('.menu-toggle');
const nav = document.querySelector('.site-nav');
if (menuButton && nav) {
  menuButton.addEventListener('click', () => {
    const isOpen = menuButton.getAttribute('aria-expanded') === 'true';
    menuButton.setAttribute('aria-expanded', String(!isOpen));
    nav.classList.toggle('open', !isOpen);
    menuButton.setAttribute('aria-label', isOpen ? '메뉴 열기' : '메뉴 닫기');
  });
  nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    menuButton.setAttribute('aria-expanded', 'false');
    nav.classList.remove('open');
  }));
}


const inquiryForm = document.getElementById('inquiry-form');
if (inquiryForm) {
  const status = document.getElementById('inquiry-status');
  const productSelect = inquiryForm.querySelector('#product');
  const requestedProduct = new URLSearchParams(location.search).get('product');
  const mapped = {multi:'멀티자판기', frozen:'냉동자판기',safe24:'SAFE24 무인매장'};
  if (mapped[requestedProduct]) productSelect.value = mapped[requestedProduct];
  inquiryForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const button = inquiryForm.querySelector('button[type=submit]');
    if (button.disabled || !inquiryForm.reportValidity()) return;
    button.disabled = true;
    status.textContent = '상담 내용을 접수하고 있습니다…';
    status.className = 'form-status';
    const raw = Object.fromEntries(new FormData(inquiryForm));
    const payload = {
      ...raw,
      consentVersion: inquiryForm.dataset.consentVersion,
      sourcePage: location.href,
      utmSource: new URLSearchParams(location.search).get('utm_source') || '',
      utmMedium: new URLSearchParams(location.search).get('utm_medium') || '',
      utmCampaign: new URLSearchParams(location.search).get('utm_campaign') || ''
    };
    try {
      const response = await fetch(inquiryForm.action, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(payload),
        credentials:'same-origin'
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok || !data.ok) throw new Error(data.error || '일시적으로 신청을 처리할 수 없습니다.');
      inquiryForm.reset();
      status.className = 'form-status form-success';
      status.textContent = `상담이 정상 접수되었습니다. 접수번호: ${data.id || '-'} / 담당자가 확인 후 연락드립니다.`;
      status.scrollIntoView({block:'nearest',behavior:'smooth'});
    } catch (error) {
      status.className = 'form-status form-error';
      status.textContent = `${error.message || '접수 오류가 발생했습니다.'} 제출 여부가 불확실하면 담당자에게 접수 여부를 먼저 확인해 주세요.`;
    } finally { button.disabled = false; }
  });
}
