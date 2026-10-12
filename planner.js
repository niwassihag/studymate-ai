/* Deterministic, offline adaptive planner; also exported for verification. */
(function(root){
function makePlan(settings,mocks){
 const subjects=settings.subjects.length?settings.subjects:['General revision'];
 const weights=new Map(subjects.map(s=>[s,1]));
 const recent=[...mocks].sort((a,b)=>b.date.localeCompare(a.date)||b.created-a.created).slice(0,5);
 recent.forEach((m,i)=>{const factor=(5-i)/5; m.weak.split(',').map(s=>s.trim()).filter(Boolean).forEach(s=>weights.set(s,(weights.get(s)||1)+factor*(2+(100-m.accuracy)/50)));});
 const ranked=[...weights].sort((a,b)=>b[1]-a[1]);
 const total=settings.minutes;const practice=Math.max(10,Math.round(total*.25/5)*5);const review=Math.max(5,Math.round(total*.15/5)*5);let left=total-practice-review;
 const count=Math.min(3,ranked.length,Math.max(1,Math.floor(left/15)));const selected=ranked.slice(0,count);const sum=selected.reduce((n,s)=>n+s[1],0);
 const tasks=selected.map(([subject,weight],i)=>{const minutes=i===count-1?left:Math.max(5,Math.min(left-(count-i-1)*5,Math.round((total-practice-review)*weight/sum/5)*5));left-=minutes;return{id:'study-'+subject,title:'Study '+subject,minutes,reason:weight>1?'Prioritized from your recent weak areas':'Build your subject foundation',auto:true};});
 tasks.push({id:'practice',title:'Timed mixed practice',minutes:practice,reason:recent[0]?.accuracy<70?'Slow down, check accuracy, then build speed':'Apply today’s learning under time pressure',auto:true});
 tasks.push({id:'review',title:'Review mistakes & recall',minutes:review,reason:'Revisit your error log and recall key ideas',auto:true});return tasks;
}
root.StudyPlanner={makePlan};if(typeof module!=='undefined')module.exports={makePlan};
})(typeof window!=='undefined'?window:globalThis);
