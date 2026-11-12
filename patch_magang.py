# Pemakaian: python patch_magang.py index.html  -> hasil: index_magang.html
# Semua perubahan dicek dulu; kalau satu anchor tidak cocok, file TIDAK ditulis.
import sys,re
src=sys.argv[1]
h=open(src,encoding='utf-8',newline='').read().replace('\r\n','\n')
def rep(old,new,n=1):
    global h
    c=h.count(old)
    if c!=n: sys.exit(f'GAGAL: anchor ditemukan {c}x (harus {n}x):\n{old[:90]}')
    h=h.replace(old,new)
def span(a,b,new):
    global h
    i=h.find(a);j=h.find(b,i)
    if i<0 or j<0: sys.exit('GAGAL span: '+a[:60])
    h=h[:i]+new+h[j+len(b):]

# ---------- CSS ----------
rep('</style>','''body.mg{background:linear-gradient(180deg,#ccfbf1 0,#f8fafc 260px) fixed}
body.mg .top{background:linear-gradient(135deg,#134e4a,#0f766e 60%,#14b8a6)}body.mg .top .mut{color:#99f6e4}
body.mg .btn{background:linear-gradient(135deg,#0d9488,#14b8a6)}
body.mg .btn.o{background:#fff}body.mg .btn.r{background:var(--errb)}
body.mg .top .btn.o{background:rgba(255,255,255,.14)}
body.mg .tabs button.on{background:linear-gradient(135deg,#0d9488,#14b8a6)}
</style>''')

# ---------- HTML ----------
rep('<select id="fUser" class="hidden"></select>','<select id="fUser" class="hidden"></select><select id="fGrp" class="hidden"><option value="ALL">Semua grup</option><option value="INTI">Karyawan Inti</option><option value="MAGANG">Magang</option></select>')
rep('<option value="OD">Tertinggal / belum beres</option>','<option value="REVIEW">Menunggu review (Magang)</option><option value="OD">Tertinggal / belum beres</option>')
rep('<section id="t-dash">','<section id="t-dash"><div id="revBox" class="card hidden" style="background:var(--warnb);border-color:#fde68a"><div class="row sp"><span><b id="revN">0</b> kerjaan magang menunggu review admin.</span><button class="btn" id="revGo" type="button">Buka antrian review</button></div></div>')
rep('<option value="ADMIN">Admin (semua data & kelola user)</option></select>','<option value="ADMIN">Admin (semua data & kelola user)</option></select><label for="uGrp">Grup</label><select id="uGrp" style="width:100%"><option value="INTI">Karyawan Inti</option><option value="MAGANG">Magang</option></select>')
rep('<th>Departemen</th><th>Role</th><th>Aksi</th>','<th>Departemen</th><th>Grup</th><th>Role</th><th>Aksi</th>')
rep('<tr><td colspan="5" class="mut">Tidak ada user','<tr><td colspan="6" class="mut">Tidak ada user')

# ---------- SOP magang + state ----------
rep("const S={me:null,users:[],tasks:[],from:'',to:'',uid:'ALL'};",'''const JMC=[['Menulis refleksi harian: apa yang dipelajari hari ini.','none','Medium'],['Mengerjakan tugas tambahan dari admin.','none','High']];
const JM={
 'CRM':[['Observasi & belajar alur penyimpanan data customer ke CRM.','none','Medium'],['Membantu follow up customer melalui chat.','none','Medium'],['Membantu input pesanan ke Webot.','none','High']],
 'Customer Service':[['Belajar menangani lead baru bersama CS senior.','none','Medium'],['Membantu follow up customer melalui chat.','none','Medium'],['Membantu labeling customer.','none','Low']],
 'Advertiser Shopee':[['Belajar membaca performa iklan Shopee.','none','Medium'],['Membantu input laporan budget harian.','none','Medium']],
 'Advertiser Tiktokshop':[['Belajar membaca performa iklan TikTok Shop.','none','Medium'],['Membantu input laporan budget harian.','none','Medium']],
 'Advertiser Meta':[['Belajar membaca performa Meta Ads.','none','Medium'],['Membantu input laporan budget harian.','none','Medium']],
 'Finance':[['Belajar rekonsiliasi mutasi bank bersama tim Finance.','none','Medium'],['Membantu input laporan kas harian.','none','Medium']]
};
const sopFor=u=>u.grp==='MAGANG'?(JM[u.division]||[]).concat(JMC):(J[u.division]||[]);
const S={me:null,users:[],tasks:[],from:'',to:'',uid:'ALL',grp:'ALL'};
const staffList=()=>S.users.filter(u=>u.role!=='ADMIN'&&(S.grp==='ALL'||(u.grp||'INTI')===S.grp));''')

# ---------- enter() ----------
rep("$('who').textContent=me.name+' · '+(isAdmin()?'Admin':me.division);","$('who').textContent=me.name+' · '+(isAdmin()?'Admin':me.division+(me.grp==='MAGANG'?' · Magang':''));")
rep('S.me=me;S.users=us;','S.me=me;S.users=us;S.grp=\'ALL\';')
span("  const staff=us.filter(u=>u.role!=='ADMIN');","pm.disabled=!isAdmin();",
"""  if(isAdmin()){$('fUser').classList.remove('hidden');$('fGrp').classList.remove('hidden');$('fGrp').value='ALL'}
  $('pMember').disabled=!isAdmin();
  document.body.classList.toggle('mg',!isAdmin()&&me.grp==='MAGANG');
  rebuildPickers();""")
rep('/* ---------- DATA ---------- */','''/* ---------- DATA ---------- */
function rebuildPickers(){
  const staff=staffList();
  if(isAdmin()){
    if(S.uid!=='ALL'&&!staff.some(u=>u.id===S.uid))S.uid='ALL';
    $('fUser').innerHTML='<option value="ALL">Semua anggota ('+staff.length+')</option>'+staff.map(u=>`<option value="${u.id}">${esc(u.name)} — ${esc(u.division)}${u.grp==='MAGANG'?' (Magang)':''}</option>`).join('');
    $('fUser').value=S.uid;
  }
  const pv=$('pMember').value,list=isAdmin()?staff:[S.me];
  $('pMember').innerHTML=list.map(u=>`<option value="${u.id}">${esc(u.name)} (${esc(u.division)}${u.grp==='MAGANG'?', Magang':''})</option>`).join('');
  if(list.some(u=>u.id===pv))$('pMember').value=pv;
  fillSop();
}''')
rep("if(S.uid!=='ALL')q=q.eq('member_id',S.uid);","""if(S.uid!=='ALL')q=q.eq('member_id',S.uid);
  else if(isAdmin()&&S.grp!=='ALL'){
    const ids=staffList().map(u=>u.id);
    if(!ids.length){S.tasks=[];render();return}
    q=q.in('member_id',ids);
  }""")

# ---------- KPI ----------
span('function metrics(list){','/* ---------- RENDER',"""const isMg=t=>{const u=S.users.find(x=>x.id===t.member_id);return !!u&&u.grp==='MAGANG'};
const isPend=t=>t.status==='Done'&&isMg(t)&&t.review_status!=='APPROVED';
function metrics(list){
  const m={total:list.length,ok:0,no:0,prog:0,pend:0,over:0,max:0,pts:0,rev:0};
  list.forEach(t=>{
    const w=W[t.priority]||2;m.max+=w;
    if(t.status!=='Done'&&t.task_date<today())m.over++;
    if(t.status==='Done'){
      if(isPend(t))m.rev++;
      else if(proofOk(t)){m.ok++;m.pts+=w}else{m.no++;m.pts+=w*.5}
    }
    else if(t.status==='In Progress')m.prog++;else m.pend++;
  });
  m.kpi=m.max?Math.round(m.pts/m.max*100):0;return m;
}

/* ---------- RENDER""")

# ---------- dashboard ----------
rep("$('kTotal').textContent=m.total;","$('revN').textContent=m.rev;$('revBox').classList.toggle('hidden',!(isAdmin()&&m.rev>0));$('kTotal').textContent=m.total;")
rep("+'% selesai · '+m.no+' kurang bukti';","+'% selesai · '+m.no+' kurang bukti'+(m.rev?' · '+m.rev+' menunggu review':'');")
rep("(isAdmin()?S.users.filter(u=>u.role!=='ADMIN'):[S.me]).filter(","(isAdmin()?staffList():[S.me]).filter(")
rep("<td>${esc(u.division)}</td><td>${s.total}</td>","<td>${esc(u.division)}${u.grp==='MAGANG'?' <span class=\"tag warn\">Magang</span>':''}</td><td>${s.total}</td>")
rep("const cnt=[m.ok,m.no,m.prog,m.pend]","const cnt=[m.ok,m.no,m.rev,m.prog,m.pend]")
rep("labels:['Done sah','Done kurang bukti','In Progress','Pending']","labels:['Done sah','Done kurang bukti','Menunggu review','In Progress','Pending']")
rep("data:has?cnt:[1,0,0,0],backgroundColor:has?['#10b981','#f43f5e','#f59e0b','#94a3b8']:['#e2e8f0','#e2e8f0','#e2e8f0','#e2e8f0']","data:has?cnt:[1,0,0,0,0],backgroundColor:has?['#10b981','#f43f5e','#38bdf8','#f59e0b','#94a3b8']:['#e2e8f0','#e2e8f0','#e2e8f0','#e2e8f0','#e2e8f0']")

# ---------- kartu kerjaan ----------
rep("  const canDel=isAdmin()||(mine&&!t.is_locked);","""  const canDel=isAdmin()||(mine&&!t.is_locked);
  const mg=isMg(t),rs=t.review_status||'NONE',pend=isPend(t),appr=mg&&t.status==='Done'&&rs==='APPROVED';
  let rev='';
  if(appr)rev='<div><span class="tag ok">Disetujui admin</span></div>';
  else if(pend)rev='<div><span class="tag warn">Menunggu review admin</span></div>';
  else if(mg&&rs==='REJECTED')rev='<div><span class="tag err">Ditolak admin, mohon perbaiki</span> <span class="mut">'+esc(t.review_note||'')+'</span></div>';
  let lockBtn;
  if(!mine)lockBtn='<span class="mut">Hanya lihat</span>';
  else if(appr&&!isAdmin())lockBtn='<span class="mut">Sudah disetujui admin, terkunci</span>';
  else lockBtn=`<button class="btn ${t.is_locked?'o':''}" data-lock="${t.id}" type="button">${t.is_locked?'Buka kunci (edit)':(mg?'Ceklis & ajukan review':'Ceklis & kunci')}</button>`;
  if(isAdmin()&&pend)lockBtn+=`<div class="row"><button class="btn" data-apr="${t.id}" type="button">✔ Setujui</button><button class="btn r" data-rej="${t.id}" type="button">✖ Tolak</button></div>`;""")
rep('<select data-st="${t.id}"${dis}>','${rev}<select data-st="${t.id}"${dis}>')
span("${mine?`<button class=\"btn ${t.is_locked?'o':''}\" data-lock","</span>'}","${lockBtn}")
rep("(f==='OD'?","(f==='REVIEW'?isPend(t):f==='OD'?")

# ---------- event ----------
rep("  if(b.dataset.lock){","""  if(b.dataset.apr||b.dataset.rej){
    const id=b.dataset.apr||b.dataset.rej;if(!isAdmin())return;
    if(b.dataset.apr){
      const n=prompt('Catatan untuk magang (boleh kosong):');if(n===null)return;
      await patch(id,{review_status:'APPROVED',review_note:n.trim(),reviewed_at:new Date().toISOString()});
    }else{
      const n=prompt('Alasan penolakan (akan dilihat magang):');if(n===null)return;
      await patch(id,{review_status:'REJECTED',status:'In Progress',is_locked:false,review_note:n.trim(),reviewed_at:new Date().toISOString()});
    }
    return;
  }
  if(b.dataset.lock){""")
rep("await patch(t.id,t.is_locked?{is_locked:false}:{status:'Done',is_locked:true});","await patch(t.id,t.is_locked?{is_locked:false,review_status:'NONE'}:{status:'Done',is_locked:true,review_status:isMg(t)?'PENDING':'NONE'});")
rep("$('fUser').onchange=e=>{S.uid=e.target.value;loadTasks()};","""$('fUser').onchange=e=>{S.uid=e.target.value;loadTasks()};
$('fGrp').onchange=e=>{S.grp=e.target.value;rebuildPickers();loadTasks()};
$('revGo').onclick=()=>{$('fStatus').value='REVIEW';document.querySelector('.tabs button[data-tab="upd"]').click();renderList()};""")

# ---------- SOP ----------
rep("const m=curMember(),jobs=J[m.division]||[];","const m=curMember(),jobs=sopFor(m);")
rep("const j=(J[curMember().division]||[])[e.target.value];","const j=sopFor(curMember())[e.target.value];")
rep("const targets=isAdmin()?S.users.filter(u=>u.role!=='ADMIN'):[S.me];","const targets=isAdmin()?staffList():[S.me];")
rep("const withSop=targets.filter(u=>(J[u.division]||[]).length);","const withSop=targets.filter(u=>sopFor(u).length);")
rep("const skipped=targets.filter(u=>!(J[u.division]||[]).length);","const skipped=targets.filter(u=>!sopFor(u).length);")
rep("(J[u.division]||[]).forEach(j=>{","sopFor(u).forEach(j=>{")

# ---------- menu user ----------
span("  const staff=data.filter(u=>u.role!=='ADMIN');","fillSop();renderUsers();","  rebuildPickers();renderUsers();")
rep("$('uId').value='';$('uName').value='';$('uEmail').value='';","$('uId').value='';$('uName').value='';$('uEmail').value='';$('uGrp').value='INTI';")
rep("<td>${esc(u.email)}</td><td>${esc(u.division)}</td>","<td>${esc(u.email)}</td><td>${esc(u.division)}</td><td><span class=\"tag ${u.grp==='MAGANG'?'warn':''}\">${u.grp==='MAGANG'?'Magang':'Inti'}</span></td>")
rep("let role=$('uRole').value;if(division==='Admin')role='ADMIN';","let role=$('uRole').value;if(division==='Admin')role='ADMIN';\n  let grp=$('uGrp').value;if(role==='ADMIN')grp='INTI';")
rep("{name,email,division,role}","{name,email,division,role,grp}",2)
rep("$('uDiv').value=u.division;$('uRole').value=u.role;","$('uDiv').value=u.division;$('uRole').value=u.role;$('uGrp').value=u.grp||'INTI';")

# ---------- CSV ----------
rep("'Foto Bukti','Keterangan'];","'Foto Bukti','Keterangan','Grup','Status Review','Catatan Review'];")
rep("t.proof_image_path?'Ada':'',t.notes||''];","t.proof_image_path?'Ada':'',t.notes||'',m.grp==='MAGANG'?'Magang':'Inti',m.grp==='MAGANG'?(t.review_status||'NONE'):'',t.review_note||''];")

out=src.rsplit('.',1)[0]+'_magang.html'
open(out,'w',encoding='utf-8').write(h)
print('OK ->',out)
