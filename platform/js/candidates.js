/* 候選判決卡片：沿用原工具 clCaseHtml 樣式與欄位檢查 */
function clEscape(value) {return String(value == null ? '' : value).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function clValidDate(s) {if(typeof s!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(s))return false;var d=new Date(s+'T00:00:00Z');return Number.isFinite(d.getTime())&&d.toISOString().slice(0,10)===s;}
function clSource(url,jid) {try{var u=new URL(url);return u.protocol==='https:'&&u.hostname==='judgment.judicial.gov.tw'&&!u.port&&!u.username&&!u.password&&u.pathname.toLowerCase()==='/fjud/data.aspx'&&u.searchParams.get('id')===jid;}catch(e){return false;}}
function clOfficial(url) {try{var u=new URL(url);return u.protocol==='https:'&&!u.username&&!u.password&&!u.port&&(u.hostname==='judicial.gov.tw'||u.hostname.endsWith('.judicial.gov.tw'));}catch(e){return false;}}
function clValidateRow(input) {
    if(!input||typeof input!=='object'||Array.isArray(input))throw new Error('案例格式不正確。');
    var r={}, jid=String(input.jid||'');
    if(!/^[A-Z0-9]{2,10}[VMAPC],\d{1,4},[^,\x00-\x1f]{1,60},\d{1,12},\d{8},\d{1,6}$/.test(jid))throw new Error('裁判識別碼不正確。');
    if(!clValidDate(input.date)||input.date.replace(/-/g,'')!==jid.split(',')[4])throw new Error('裁判日期不正確或與識別碼不符。');
    if(!clSource(input.sourceUrl,jid))throw new Error('案例原文連結必須指向相同識別碼的司法院裁判。');
    r.jid=jid;r.date=input.date;r.sourceUrl=input.sourceUrl;
    var sizes={title:400,court:200,caseNo:150,cause:400,fetchedAt:60,sourceHash:64,summaryState:40,reviewStatus:200,conclusion:1000,mainText:4200,facts:1300,issues:1300,method:500,error:700,topic:50,topicHint:800,collectedAt:60,updatedAt:60};
    Object.keys(sizes).forEach(function(k){var v=input[k]===undefined?'':input[k];if(typeof v!=='string'||v.length>sizes[k])throw new Error('案例欄位過長或格式不正確：'+k);r[k]=v;});
    if(!r.title)throw new Error('案例缺少法院及案號。');
    if(r.sourceHash&&!/^[a-f0-9]{64}$/.test(r.sourceHash))throw new Error('原文版本識別不正確。');
    r.year=Number(jid.split(',')[1]);
    r.court=r.court||'尚待確認';r.caseNo=r.caseNo||jid.split(',')[2]+'字第'+jid.split(',')[3]+'號';
    [['reasons',5,750],['paymentText',10,750],['matchedKeywords',100,128],['lawReferences',30,100],['topics',30,60],['topicLabels',30,120]].forEach(function(config){var a=input[config[0]]||[];if(!Array.isArray(a)||a.length>config[1]||a.some(function(v){return typeof v!=='string'||v.length>config[2];}))throw new Error('案例清單欄位不正確：'+config[0]);r[config[0]]=a.slice();});
    r.entryId=input.entryId||'';if(r.entryId&&!/^OC\d{6,10}$/.test(r.entryId))throw new Error('案例庫編號不正確。');
    r.version=input.version===undefined?1:input.version;if(!Number.isInteger(r.version)||r.version<1||r.version>1000000)throw new Error('版本編號不正確。');
    r.workStatus=['搜尋摘要','已選案','分析完成'].indexOf(input.workStatus)>=0?input.workStatus:'搜尋摘要';
    r.verificationStatus=typeof input.verificationStatus==='string'?input.verificationStatus.slice(0,800):'官方來源已取得；自動節錄內容與個案解讀尚待確認。';
    r.finality='尚待確認';r.notes={};
    var notes=input.notes||{};if(typeof notes!=='object'||Array.isArray(notes))throw new Error('補充分析格式不正確。');
    ['shortTitle','summary','issues','management','insurance','verification','related','finalityEvidence','finalitySource'].forEach(function(k){var v=notes[k]||'';if(typeof v!=='string'||v.length>4000)throw new Error('人工補充欄位過長：'+k);r.notes[k]=v;});
    if(notes.finalityStatus==='已查得確定依據'){if(!r.notes.finalityEvidence||!clOfficial(r.notes.finalitySource))throw new Error('確認裁判確定須填依據與司法院來源網址。');r.notes.finalityStatus='已查得確定依據';r.finality='已查得確定依據（人工記錄）';}else r.notes.finalityStatus='尚待確認';
    if(input.previousVersions!==undefined&&!Array.isArray(input.previousVersions))throw new Error('版本紀錄格式不正確。');
    r.previousVersions=[];(input.previousVersions||[]).slice(-10).forEach(function(v){if(!v||!Number.isInteger(v.version)||v.version<1||typeof v.conclusion!=='string'||v.conclusion.length>1000)throw new Error('版本紀錄不正確。');r.previousVersions.push({version:v.version,changedAt:String(v.changedAt||'').slice(0,60),sourceHash:String(v.sourceHash||'').slice(0,64),conclusion:v.conclusion});});
    return r;
}
function clCaseHtml(r, index, controls) {
    var e=clEscape,notes=r.notes||{};
    var parts='<article class="cl-card" data-jid="'+e(r.jid)+'"><div class="cl-top"><div><span class="cl-kicker">'+e(r.entryId||('案例 '+(index+1)))+' · r'+r.version+'</span><h4>'+e(notes.shortTitle||r.cause||'職災相關裁判')+'</h4></div><div class="cl-status">工作進度：'+e(r.workStatus)+'<br>是否確定：'+e(r.finality)+'</div></div>';
    parts+='<div class="cl-meta"><span>'+e(r.title)+'</span><span>裁判日期 '+e(r.date)+'</span></div>';
    parts+='<div class="cl-decision"><strong>結論｜本次裁判主文節錄</strong><br>'+e(r.conclusion||'完整主文尚待確認')+'</div>';
    if(notes.summary)parts+='<p class="cl-notes"><strong>人工補充摘要：</strong>'+e(notes.summary)+'</p>';
    parts+='<p class="cl-status">'+e(r.verificationStatus)+'</p><details><summary>案情、理由與金額重點</summary>';
    if(r.error)parts+='<p class="cl-warning">'+e(r.error)+'</p>';
    parts+='<h5>案情摘錄｜當事人主張，非全部經法院認定</h5><blockquote>'+e(r.facts||'未能明確辨識主張段落，尚待確認；請閱讀官方原文。')+'</blockquote>';
    if(r.issues)parts+='<h5>爭點｜原文節錄</h5><blockquote>'+e(r.issues)+'</blockquote>';
    parts+='<h5>法院理由｜自動選句</h5>'+(r.reasons.length?r.reasons.map(function(x){return '<blockquote>'+e(x)+'</blockquote>';}).join(''):'<p>未能可靠定位理由段落，尚待確認。</p>');
    parts+='<h5>金額性質</h5>'+(r.paymentText.length?'<p>下列僅摘錄主文給付句；未合計本金、利息、假執行擔保或其他金額。</p>'+r.paymentText.map(function(x){return '<blockquote>'+e(x)+'</blockquote>';}).join(''):'<p>本次主文未擷取明確給付句；不表示損害、補償或前審給付金額為零。請求金額須與判給金額分開核對。</p>');
    parts+='<h5>原文引用法條字詞</h5><p>'+e(r.lawReferences.join('、')||'尚待確認')+'</p>';
    if(notes.issues)parts+='<h5>人工補充爭點</h5><p class="cl-notes">'+e(notes.issues)+'</p>';
    parts+='<h5>企業與團保檢視｜顧問整理提醒，非法院見解</h5><p class="cl-notes">'+e(notes.management||r.topicHint||'請核對事故經過、工作關聯、雇主義務、各項給付及後續審級。')+'</p><p class="cl-notes">'+e(notes.insurance||'逐項確認投保對象、保單條款、承保事故、除外責任及抵充依據；目前未取得本案保單，不判定一定理賠或可以全數抵充。')+'</p>';
    parts+='<h5>查核與關聯</h5><p class="cl-notes">'+e(notes.verification||'已取得：官方來源連結及裁判文字。尚待確認：完整上下文、主張與認定的界線、後續審級、裁判是否確定及保險條款。')+'</p><p>關聯案件：'+e(notes.related||'尚待確認；不同審級及不同裁判不合併成同一筆。')+'</p>';
    if(notes.finalityStatus==='已查得確定依據')parts+='<p>人工記錄確定依據：'+e(notes.finalityEvidence)+' <a href="'+e(notes.finalitySource)+'" target="_blank" rel="noopener noreferrer">查看依據 ↗</a></p>';
    if(r.previousVersions.length)parts+='<h5>原文變更紀錄（摘要）</h5><ul>'+r.previousVersions.map(function(v){return '<li>r'+v.version+'｜'+e(v.changedAt)+'｜當時主文摘要：'+e(v.conclusion)+'</li>';}).join('')+'</ul>';
    parts+='<details><summary>查看本次擷取主文與來源</summary><blockquote>'+e(r.mainText||'完整主文尚待確認')+'</blockquote><p class="cl-source"><a href="'+e(r.sourceUrl)+'" target="_blank" rel="noopener noreferrer">'+e(r.sourceUrl)+'</a></p><p class="cl-status">取得時間：'+e(r.fetchedAt||'尚待確認')+'<br>整理方式：'+e(r.method||'尚待確認')+'</p></details></details>';
    parts+='<div class="cl-actions"><a href="'+e(r.sourceUrl)+'" target="_blank" rel="noopener noreferrer">官方裁判原文 ↗</a>';
    if(controls)parts+='<button type="button" data-cl-action="report" data-jid="'+e(r.jid)+'">下載本案重點</button>';
    if(controls&&controls!=='book')parts+='<button type="button" data-cl-action="edit" data-jid="'+e(r.jid)+'">補充分析與核對</button>';
    return parts+'</div></article>';
}
