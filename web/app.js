'use strict';
let token=null,user=null,currentChip=null,currentConsult=null;
const $=id=>document.getElementById(id);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

async function api(path,data){
  const response=await fetch('/api/'+path,{method:data===undefined?'GET':'POST',headers:{'Content-Type':'application/json',...(token?{'Authorization':'Bearer '+token}:{})},...(data!==undefined?{body:JSON.stringify(data)}:{})});
  const result=await response.json();
  if(!response.ok)throw Error(result.error||'Verzoek mislukt');
  return result;
}
function start(){
  $('login').classList.add('hidden');
  $('workspace').classList.remove('hidden');
  $('admin-nav').classList.toggle('hidden',user.role!=='admin');
  $('user-name').textContent=user.display+' · '+user.practice_id;
  page('overview');
}
function heading(k,title,sub){return `<div class="page-heading"><div class="overline">${k}</div><h1>${title}</h1><p>${sub}</p></div>`;}
function page(id){
  document.querySelectorAll('.nav').forEach(x=>x.classList.toggle('active',x.dataset.tab===id));
  if(id==='admin'){renderAdmin();return;}
  let html='';
  if(id==='overview')html=heading('INZICHT MET ZORG','Beter herkennen begint hier.','Een omgeving voor het zorgvuldig beoordelen van fictieve signalen. Elke raadpleging vereist een vooraf vastgelegde behandelrelatie.')+`<div class="grid"><div class="card"><div class="overline">DEMO-DIERDOSSIERS</div><div class="large">02</div><span class="muted">Uitsluitend fictieve dossiers</span></div><div class="card"><div class="overline">TOEGANGSCONTROLE</div><div class="large">Rol + situatie</div><span class="muted">Toegang op basis van je functie, het doel en een vooraf goedgekeurde behandelrelatie.</span></div><div class="card"><div class="overline">PROFESSIONEEL OORDEEL</div><div class="large">Menselijk</div><span class="muted">Geen automatische verdenking</span></div></div><div class="two"><section class="banner"><div class="overline" style="color:#a8daba">VEILIG SIGNALEREN</div><h2>Feiten delen zonder conclusies op te dringen.</h2><p>Een verwonding betekent niet automatisch mishandeling. Context uit andere contacten kan helpen bij zorgvuldig vervolgonderzoek en het volgen van professionele richtlijnen.</p><div class="buttonrow"><button class="primary" data-go="lookup">Start chipcontrole →</button></div></section><section class="card"><div class="overline">PROEFCASUS</div><h2>Bowie · fictieve Labrador</h2><p>Voor deze testcase zijn twee observaties bij verschillende fictieve praktijken geregistreerd. Alleen gebruikers met de juiste consultrelatie mogen ze bekijken.</p><div class="alert">Voor arts.west: chipnummer <strong>999000000000001</strong> en consult <strong>CONS-W-1001</strong>.</div></section></div>`;
  if(id==='lookup')html=heading('VEILIGE RAADPLEGING','Chipnummer controleren.','De server controleert of je functie, het doel en de vooraf vastgelegde behandelrelatie toegang geven.')+`<div class="two"><section class="card"><h2>Gegevens raadpleging</h2><form id="lookup-form" class="form"><label>Chipnummer (15 cijfers)<input name="chip" required pattern="[0-9]{15}" value="999000000000001" inputmode="numeric"></label><label>Geregistreerde consultreferentie<input name="consultation" required value="CONS-W-1001"></label><label>Doel van raadpleging<select name="purpose" required><option value="clinical_care">Behandeling van het dier</option><option value="welfare_assessment">Welzijnsbeoordeling</option></select></label><div class="alert warn">Een zelf ingevulde consultreferentie geeft niet automatisch toegang. De server controleert of de relatie vooraf is vastgelegd voor deze dierenarts en dit dier.</div><button class="primary">Controleer toegang en raadpleeg →</button></form></section><section class="card"><div class="overline">RESULTAAT</div><div id="lookup-result"><div class="alert">Voer een raadpleging uit om de fictieve gegevens te bekijken.</div></div></section></div>`;
  if(id==='record')html=heading('ZORGVULDIGE REGISTRATIE','Signaal vastleggen.','Registreer waarnemingen, uitleg van de verzorger en professionele interpretatie afzonderlijk. Registraties blijven concepten.')+`<div class="two"><section class="card"><form id="record-form" class="form"><label>Chipnummer<input name="chip" value="${esc(currentChip||'999000000000001')}" required pattern="[0-9]{15}"></label><label>Goedgekeurde consultreferentie<input name="consultation" required value="${esc(currentConsult||'CONS-W-1001')}"></label><label>Feitelijke waarneming<textarea name="observed" maxlength="1200" required placeholder="Beschrijf uitsluitend wat is geobserveerd of vastgesteld."></textarea></label><label>Onderzoeksmethode / bron<input name="method" maxlength="1200" required placeholder="Bijvoorbeeld: radiografie"></label><label>Verklaring van de verzorger<textarea name="caretaker_statement" maxlength="1200" placeholder="Duidelijk markeren als verklaring, niet als bewezen feit."></textarea></label><label>Interpretatie en onzekerheden<textarea name="interpretation" maxlength="1200" required placeholder="Mogelijke verklaringen, onzekerheden en alternatieven."></textarea></label><label>Vervolgstap<select name="followup"><option>Collegiaal overleg</option><option>Vervolgonderzoek</option><option>Bespreken met verzorger indien veilig</option><option>Overwegen externe melding conform meldcode</option></select></label><button class="primary">Sla concept op →</button></form><div id="record-result"></div></section><section class="card"><div class="overline">KWALITEITSREGEL</div><h2>Niet ieder signaal is een verdenking.</h2><p>Een objectieve observatie, de verklaring van de eigenaar of verzorger en een professionele interpretatie hebben ieder een andere bewijswaarde.</p><div class="alert warn">Concepten zijn afzonderlijk opgeslagen en worden niet automatisch met andere praktijken gedeeld. Er is geen knop om publicatie of melding uit te voeren.</div><p>Registratie wordt alleen toegestaan voor een geverifieerde dierenarts met een goedgekeurde consultrelatie en het doel welzijnsbeoordeling.</p></section></div>`;
  if(id==='safety')html=heading('TRANSPARANT ONTWERP','Privacy & controle.','Belangrijkste architectuurkeuzes en de openstaande voorwaarden voor de juridische en technische beoordeling.')+`<div class="grid"><div class="card"><div class="overline">IDENTITEIT</div><h2>Aparte identiteitsservice</h2><p>Wachtwoordhashing, korte sessies en controle van de beroepsrol. De identiteitendatabase is gescheiden van signaleringen.</p></div><div class="card"><div class="overline">AUTORISATIE</div><h2>Server-side beleid</h2><p>Default deny. Goedkeuring alleen bij juiste rol, doel, chipnummer en vooraf goedgekeurde consultreferentie.</p></div><div class="card"><div class="overline">REGISTRATIE</div><h2>Controleerbare audit</h2><p>Serverlog met raadplegingen, toelatingsbesluiten en een hashketen ter demonstratie. Nog niet onveranderbaar of onafhankelijk.</p></div></div><div class="two"><div class="card"><h2>Wat er al werkt</h2><p>Twee aparte SQLite-databases, aparte services, gehashte sessietokens, gecontroleerde API-aanroepen, beperkte invoer en automatische integratietests.</p><h2>Wat vóór echte verwerking ontbreekt</h2><p>MFA, externe beroepsverificatie, beheer van behandelrelaties, productie-TLS, gecentraliseerde tamper-evident auditlogging, monitoring, back-upbeheer, formele bewaartermijnen en onafhankelijk onderzoek.</p></div><div class="card"><h2>Toetsing door juristen</h2><p>Rechtsgrond, beroepsgeheim, verantwoordelijken, proportionaliteit, informatieplichten, inzage- en correctierechten, gegevensdeling tussen praktijken en DPIA.</p><div class="alert warn">Deze pilot is geen bewijs van AVG-conformiteit of voldoende productiebeveiliging. Gebruik uitsluitend fictieve gegevens.</div></div></div>`;
  $('content').innerHTML=html;
  window.scrollTo(0,0);
}
function authPanel(id){
  ['login-panel','register-panel','reset-panel'].forEach(panel=>$(panel).classList.toggle('hidden',panel!==id));
  document.querySelectorAll('.error').forEach(el=>el.textContent='');
}
async function renderAdmin(){
  $('content').innerHTML=heading('BEHEER','Accounts en dieren beheren.','Alleen het beheerdersaccount kan dierenartsregistraties goedkeuren en fictieve honden- en kattendossiers onderhouden.')+`<div id="admin-feedback" class="alert hidden"></div><div class="two admin-columns"><section class="card"><div class="overline">DIERENARTSEN</div><h2>Accountbeheer</h2><p>Nieuwe registraties zijn niet actief tot ze zijn goedgekeurd.</p><div id="admin-users" class="table-wrap">Laden…</div><h3 id="vet-form-title">Dierenartsgegevens aanpassen</h3><form id="vet-form" class="form hidden"><label>Gebruikersnaam<input name="username" readonly required></label><label>Naam<input name="display" maxlength="100" required></label><label>Praktijknaam<input name="practice_id" maxlength="100" required></label><button class="primary">Gegevens opslaan →</button></form></section><section class="card"><div class="overline">HONDEN & KATTEN</div><h2>Dierbeheer</h2><div id="admin-animals" class="table-wrap">Laden…</div><h3 id="animal-form-title">Dier toevoegen</h3><form id="animal-form" class="form"><label>Chipnummer (15 cijfers)<input name="chip" pattern="[0-9]{15}" inputmode="numeric" required></label><label>Naam<input name="name" maxlength="100" required></label><label>Diersoort<select name="species" required><option value="Hond">Hond</option><option value="Kat">Kat</option></select></label><label>Ras<input name="breed" maxlength="100" required></label><button class="primary">Dier toevoegen →</button><button type="button" id="cancel-animal-edit" class="secondary hidden">Wijzigen annuleren</button></form></section></div><div class="alert warn">Beheeracties zijn bedoeld voor de fictieve pilot. Een eenmaal gekoppeld chipnummer kan niet worden verwijderd of gewijzigd.</div>`;
  try{
    const [users,animals]=await Promise.all([api('admin/users/list',{}),api('admin/animals/list',{})]);
    $('admin-users').innerHTML=users.users.length?`<table><thead><tr><th>Account</th><th>Praktijk</th><th>Status</th><th>Acties</th></tr></thead><tbody>${users.users.map(v=>`<tr><td>${esc(v.display)}<small>${esc(v.id)}</small></td><td>${esc(v.practice_id)}</td><td>${esc(v.status)}</td><td class="actions"><button class="small-button" data-edit-vet data-username="${esc(v.id)}" data-display="${esc(v.display)}" data-practice="${esc(v.practice_id)}">Gegevens</button>${v.active?`<button class="small-button" data-user-status="${esc(v.id)}" data-approved="false">Deactiveren</button><button class="small-button" data-reset-code="${esc(v.id)}">Herstelcode</button>`:`<button class="small-button" data-user-status="${esc(v.id)}" data-approved="true">Goedkeuren</button>`}</td></tr>`).join('')}</tbody></table>`:'Geen dierenartsaccounts.';
    $('admin-animals').innerHTML=animals.animals.length?`<table><thead><tr><th>Dier</th><th>Soort / ras</th><th>Chipnummer</th><th></th></tr></thead><tbody>${animals.animals.map(a=>`<tr><td>${esc(a.name)}</td><td>${esc(a.species)} · ${esc(a.breed)}</td><td>${esc(a.chip)}</td><td><button class="small-button" data-edit-animal data-chip="${esc(a.chip)}" data-name="${esc(a.name)}" data-species="${esc(a.species)}" data-breed="${esc(a.breed)}">Bewerken</button></td></tr>`).join('')}</tbody></table>`:'Nog geen dieren.';
  }catch(err){$('admin-feedback').textContent=err.message;$('admin-feedback').classList.remove('hidden');}
}
$('login-form').addEventListener('submit',async e=>{
  e.preventDefault();$('login-error').textContent='';
  try{const result=await api('login',{username:$('username').value,password:$('password').value});token=result.token;user=result.user;$('password').value='';start();}
  catch(err){$('login-error').textContent=err.message;}
});
$('register-form').addEventListener('submit',async e=>{
  e.preventDefault();const form=e.currentTarget;const data=Object.fromEntries(new FormData(form));
  try{const result=await api('register',data);$('register-result').textContent=result.message;form.reset();}
  catch(err){$('register-result').textContent=err.message;}
});
$('reset-form').addEventListener('submit',async e=>{
  e.preventDefault();const form=e.currentTarget;const data=Object.fromEntries(new FormData(form));
  try{const result=await api('password-reset',data);$('reset-result').textContent=result.message;form.reset();}
  catch(err){$('reset-result').textContent=err.message;}
});
$('show-register').addEventListener('click',()=>authPanel('register-panel'));
$('show-reset').addEventListener('click',()=>authPanel('reset-panel'));
document.querySelectorAll('.back-login').forEach(button=>button.addEventListener('click',()=>authPanel('login-panel')));
$('logout').addEventListener('click',async()=>{
  try{await api('logout',{});}catch{}
  token=null;user=null;currentChip=null;currentConsult=null;
  $('workspace').classList.add('hidden');$('login').classList.remove('hidden');$('password').value='';authPanel('login-panel');
});
document.addEventListener('click',async e=>{
  const tab=e.target.closest('[data-tab],[data-go]');
  if(tab&&token){page(tab.dataset.tab||tab.dataset.go);return;}
  const statusButton=e.target.closest('[data-user-status]');
  if(statusButton&&token&&user.role==='admin'){
    try{await api('admin/users/status',{username:statusButton.dataset.userStatus,approved:statusButton.dataset.approved==='true'});await renderAdmin();}
    catch(err){$('admin-feedback').textContent=err.message;$('admin-feedback').classList.remove('hidden');}
    return;
  }
  const resetButton=e.target.closest('[data-reset-code]');
  if(resetButton&&token&&user.role==='admin'){
    try{const result=await api('admin/users/reset-code',{username:resetButton.dataset.resetCode});$('admin-feedback').textContent=`Geef deze code veilig door aan ${resetButton.dataset.resetCode}: ${result.code} · geldig voor 15 minuten.`;$('admin-feedback').classList.remove('hidden');}
    catch(err){$('admin-feedback').textContent=err.message;$('admin-feedback').classList.remove('hidden');}
    return;
  }
  const editButton=e.target.closest('[data-edit-animal]');
  if(editButton&&token&&user.role==='admin'){
    const form=$('animal-form');
    for(const field of ['chip','name','species','breed'])form.elements[field].value=editButton.dataset[field];
    form.elements.chip.readOnly=true;form.dataset.mode='update';
    $('animal-form-title').textContent='Dier bewerken';form.querySelector('.primary').textContent='Wijzigingen opslaan →';$('cancel-animal-edit').classList.remove('hidden');
    form.scrollIntoView({behavior:'smooth',block:'start'});
    return;
  }
  const vetButton=e.target.closest('[data-edit-vet]');
  if(vetButton&&token&&user.role==='admin'){
    const form=$('vet-form');
    form.elements.username.value=vetButton.dataset.username;form.elements.display.value=vetButton.dataset.display;form.elements.practice_id.value=vetButton.dataset.practice;
    form.classList.remove('hidden');form.scrollIntoView({behavior:'smooth',block:'start'});
  }
});
document.addEventListener('submit',async e=>{
  const form=e.target;
  if(form.id==='vet-form'){
    e.preventDefault();const data=Object.fromEntries(new FormData(form));
    try{await api('admin/users/update',data);form.reset();form.classList.add('hidden');await renderAdmin();}
    catch(err){$('admin-feedback').textContent=err.message;$('admin-feedback').classList.remove('hidden');}
    return;
  }
  if(form.id==='animal-form'){
    e.preventDefault();const data=Object.fromEntries(new FormData(form));const mode=form.dataset.mode==='update'?'update':'create';
    try{await api('admin/animals/'+mode,data);form.reset();form.elements.chip.readOnly=false;delete form.dataset.mode;$('animal-form-title').textContent='Dier toevoegen';form.querySelector('.primary').textContent='Dier toevoegen →';$('cancel-animal-edit').classList.add('hidden');await renderAdmin();}
    catch(err){$('admin-feedback').textContent=err.message;$('admin-feedback').classList.remove('hidden');}
    return;
  }
  if(!['lookup-form','record-form'].includes(form.id))return;
  e.preventDefault();const data=Object.fromEntries(new FormData(form));
  try{
    if(form.id==='lookup-form'){
      const result=await api('lookup',data);currentChip=data.chip;currentConsult=data.consultation;
      $('lookup-result').innerHTML=`<div class="row"><span class="result-name">${esc(result.animal.name)}</span><span class="status">Geautoriseerd</span></div><p class="muted">${esc(result.animal.species)} · ${esc(result.animal.breed)} · ${esc(result.animal.chip)}</p><div class="overline" style="margin-top:25px">GEPUBLICEERDE WAARNEMINGEN</div>${result.signals.map(s=>`<article class="signal"><h3>${esc(s.practice_id)} · ${esc(s.created_at.slice(0,10))}</h3><p><strong>Feit:</strong> ${esc(s.observed)}</p><p><strong>Onderzoek:</strong> ${esc(s.method)}</p><p><strong>Verklaring:</strong> ${esc(s.caretaker_statement)}</p><p><strong>Interpretatie:</strong> ${esc(s.interpretation)}</p></article>`).join('')||'<p>Geen gedeelde signalen.</p>'}`;
    }else{
      data.purpose='welfare_assessment';const result=await api('signals',data);$('record-result').textContent='Concept '+result.id+' opgeslagen. Niet gepubliceerd of gedeeld.';
    }
  }catch(err){const target=form.id==='lookup-form'?'lookup-result':'record-result';$(target).textContent='Niet toegestaan: '+err.message;}
});
$('cancel-animal-edit').addEventListener('click',()=>{
  const form=$('animal-form');form.reset();form.elements.chip.readOnly=false;delete form.dataset.mode;
  $('animal-form-title').textContent='Dier toevoegen';form.querySelector('.primary').textContent='Dier toevoegen →';$('cancel-animal-edit').classList.add('hidden');
});
