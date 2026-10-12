(function(root){
 'use strict';
 function normalize(p,now=new Date()) {
   if(!p||!/^[-\w]{1,100}$/.test(p.testId)||!/^\d{1,6}$/.test(p.attempt)||typeof p.name!=='string'||!p.name.trim()||p.name.length>300||![p.score,p.max,p.accuracy].every(Number.isFinite)||p.max<=0||p.score < -p.max||p.score>p.max||p.accuracy<0||p.accuracy>100) throw Error('Invalid Testbook result');
   const weak=Array.isArray(p.sections)?p.sections.filter(s=>s&&typeof s.name==='string'&&s.name.length<=100&&Number.isFinite(s.accuracy)&&s.accuracy>=0&&s.accuracy<70&&!/^(test|total|overall)$/i.test(s.name)).slice(0,20).map(s=>s.name).join(', '):'';
   const date=`${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
   return {id:`testbook-${p.testId}-${p.attempt}`,name:p.name.trim(),platform:'Testbook',date,score:p.score,max:p.max,accuracy:p.accuracy,weak,created:now.getTime(),notes:'Imported from Testbook result page. Date shown is import date; original test date was not available.'+(weak?' Focus areas: sections below 70% accuracy.':' Section-level weak areas were not available.')};
 }
 function upsert(mocks,result){const index=mocks.findIndex(m=>m.id===result.id);if(index<0)mocks.push(result);else mocks[index]={...result,date:mocks[index].date,created:mocks[index].created};}
 root.TestbookSync={normalize,upsert};
 if(typeof module!=='undefined')module.exports=root.TestbookSync;
})(typeof window!=='undefined'?window:globalThis);
