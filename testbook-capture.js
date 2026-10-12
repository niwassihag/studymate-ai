(() => {
  if (location.protocol !== 'https:' || !['testbook.com','www.testbook.com'].includes(location.hostname)) return;
  if (!document.getElementById('studymate-return')) {
    const a = document.createElement('a'); a.id='studymate-return';
    a.href='https://testbook.com/studymate-return'; a.textContent='← StudyMate';
    a.style.cssText='position:fixed;bottom:20px;right:16px;z-index:2147483647;background:#b9461c;color:white;padding:13px 18px;border-radius:24px;font:bold 15px sans-serif;box-shadow:0 3px 14px #0004';
    document.body.append(a);
  }
  if (window.studyMateWatching) return; window.studyMateWatching=true;
  let last='', stable=0;
  setInterval(() => {
    const route=location.pathname.match(/^\/attempted\/tests\/([a-zA-Z0-9_-]+)\/analysis\/?$/);
    if (!route) return;
    const score=document.querySelector('.analysis-summary--score h4')?.textContent.trim();
    const accuracy=document.querySelector('.analysis-summary--accuracy h4')?.textContent.trim();
    const pair=score?.match(/^(-?\d+(?:\.\d+)?)\s*\/\s*(\d+(?:\.\d+)?)$/);
    const acc=accuracy?.match(/^(\d+(?:\.\d+)?)\s*%$/);
    if (!pair || !acc) return;
    const title=document.querySelector('.d-none.d-md-block.text-truncate.ng-binding')?.textContent.trim();
    const sections=Array.from(document.querySelectorAll('table.table-grid--summary tbody tr')).map(r=>{
      const cells=Array.from(r.querySelectorAll('td')).map(c=>c.textContent.trim());
      return {name:cells[0]||'',accuracy:parseFloat(cells[3])};
    }).filter(s=>s.name && !/^(test|total|overall)$/i.test(s.name) && Number.isFinite(s.accuracy) && s.accuracy>=0 && s.accuracy<=100);
    const payload={testId:route[1],attempt:new URLSearchParams(location.search).get('attemptNo')||'1',name:title||'Testbook mock',score:Number(pair[1]),max:Number(pair[2]),accuracy:Number(acc[1]),sections};
    const serialized=JSON.stringify(payload);
    if (serialized!==last) {last=serialized;stable=0;return;}
    if (++stable===2) prompt('StudyMateSync',serialized);
  },1000);
})();
