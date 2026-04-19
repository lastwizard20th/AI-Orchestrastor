let currentSession = 'default';
let sessions = ['default'];
let currentProfile = 'default';
let chatMode = 'private';

const $ = id => document.getElementById(id);

let audioUnlocked = false;
let audioQueue = [];
let audioBusy = false;
let currentAudio = null;

/* =========================
   AUDIO ENGINE
========================= */

function unlockAudio(){
  if(audioUnlocked) return;

  const a = new Audio();
  a.volume = 0;
  a.play()
    .then(()=>{
      audioUnlocked = true;
    })
    .catch(()=>{});
}

document.addEventListener('click', unlockAudio, {once:true});
document.addEventListener('keydown', unlockAudio, {once:true});


function enqueueVoice(url){
  if(!url) return;

  audioQueue.push(url);
  processAudioQueue();
}

async function processAudioQueue(){
  if(audioBusy) return;
  if(audioQueue.length === 0) return;

  audioBusy = true;

  const url = audioQueue.shift();

  try{
    await playAudio(url);
  }catch(e){
    console.log('audio error', e);
  }

  audioBusy = false;

  if(audioQueue.length > 0){
    setTimeout(processAudioQueue, 250);
  }
}

function stopCurrentAudio(){
  if(currentAudio){
    currentAudio.pause();
    currentAudio.src = '';
    currentAudio = null;
  }
}

function clearVoiceQueue(){
  audioQueue = [];
}

function playNow(url){
  clearVoiceQueue();
  stopCurrentAudio();
  enqueueVoice(url);
}

function playAudio(url){
  return new Promise((resolve,reject)=>{

    const audio = new Audio(url + '?t=' + Date.now());
    currentAudio = audio;

    audio.preload = 'auto';
    audio.volume = 1.0;

    audio.onended = ()=>{
      currentAudio = null;
      resolve();
    };

    audio.onerror = (e)=>{
      currentAudio = null;
      reject(e);
    };

    audio.play().catch(reject);
  });
}

const teamModels = [
  {name:'Main AI', role:'Leader'},
  {name:'Gemini', role:'Advisor'},
  {name:'Codex', role:'Coder'},
  {name:'Planner Agent', role:'Task Agent'}
];

function switchMainView(name){
  document.querySelectorAll('.view').forEach(v=>v.classList.add('hidden'));
  $('view-' + name).classList.remove('hidden');
}

function toggleSettings(){
  $('settingsDrawer').classList.toggle('hidden');
}

function switchChatMode(mode){
  chatMode = mode;

  $('tabPrivate').classList.remove('active');
  $('tabTeam').classList.remove('active');

  if(mode === 'private'){
    $('tabPrivate').classList.add('active');
    $('chatTitle').innerText = 'Talking with Main AI';
  }else{
    $('tabTeam').classList.add('active');
    $('chatTitle').innerText = 'AI Team Room';
  }

  loadHistory();
}

function renderSessions(){
  $('sessions').innerHTML = '';
  sessions.forEach(s=>{
    const d=document.createElement('div');
    d.className='item';
    d.innerText=s;
    d.onclick=()=>switchSession(s);
    $('sessions').appendChild(d);
  });
}

function renderTeamMembers(){
  $('teamMembers').innerHTML = '';
  $('activeModels').innerHTML = '';

  teamModels.forEach(m=>{
    $('teamMembers').innerHTML += `
      <div class="item">
        <b>${m.name}</b><br>${m.role}
      </div>
    `;

    $('activeModels').innerHTML += `
      <div class="card">
        ${m.name}<br><small>${m.role}</small>
      </div>
    `;
  });
}

function newSession(){
  const id='chat-'+Date.now();
  sessions.push(id);
  renderSessions();
  switchSession(id);
}

async function switchSession(id){
  currentSession=id;
  await loadHistory();
}

function addMsg(role,text,sender=''){
  const d=document.createElement('div');

  if(role==='user'){
    d.className='msg user';
    d.innerText=text;
  }else{
    d.className = sender ? 'msg member' : 'msg ai';

    let html='';
    if(sender){
      html += `<div class="msg-header">${sender}</div>`;
    }
    html += marked.parse(text || '');
    d.innerHTML = html;
  }

  $('chat').appendChild(d);
  d.scrollIntoView();
}

async function sendMsg(){
  const text = $('msg').value.trim();
  if(!text) return;

  $('msg').value = '';

  addMsg('user', text);
  addMsg('ai', '_Thinking..._');

  const payload = {
    message: text,
    session_id: currentSession,
    mode: $('mode').value,
    profile: currentProfile,
    room_type: chatMode
  };

  const r = await fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });

  const data = await r.json();

  $('chat').lastChild.remove();

  $('intent').innerText = data.intent || '-';
  $('provider').innerText = data.provider || '-';
  $('voiceBubble').innerText = data.voice_text || 'Ready';

  if(chatMode === 'private'){
    addMsg('ai', data.response || '');
  }else{
    if(Array.isArray(data.team_messages)){
      data.team_messages.forEach(x=>{
        addMsg('ai', x.text, x.sender);
      });
    }else{
      addMsg('ai', data.response || '', 'Main AI');
    }
  }

  if(data.audio_b64){
    playBase64Audio(data.audio_b64);
  }
}

async function loadHistory(){
  $('chat').innerHTML='';

  const r = await fetch('/history/' + currentSession);
  const data = await r.json();

  data.forEach(x=>{
    if(x.role === 'user'){
      addMsg('user', x.text);
    }else{
      addMsg('ai', x.text);
    }
  });
}

/* TASKS */
async function addTask(){
  await fetch('/task/add',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      title:$('taskTitle').value
    })
  });
  $('taskTitle').value='';
  loadTasks();
}

async function loadTasks(){
  const r=await fetch('/tasks');
  const data=await r.json();

  $('tasks').innerHTML='';

  data.forEach(t=>{
    $('tasks').innerHTML += `
      <div class="card">
        <b>#${t.id}</b> ${t.title}<br>
        ${t.status}<br><br>
        <button onclick="runTask(${t.id})">Run</button>
      </div>
    `;
  });
}

async function runTask(id){
  await fetch('/task/run',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({id})
  });
  loadTasks();
}

async function runPending(){
  await fetch('/tasks/run_pending',{method:'POST'});
  loadTasks();
}

/* MEMORY */
async function loadMemories(){
  const r=await fetch('/memories');
  const data=await r.json();

  $('memories').innerHTML = data.map(m=>`
    <div class="card">${m.text}</div>
  `).join('');
}

async function searchMemory(){
  const r=await fetch('/memory/search',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      query:$('memQuery').value
    })
  });

  const d=await r.json();
  $('memResult').innerText = d.result || '';
}

/* FILES */
async function loadFiles(){
  const p = $('filePath').value;

  const r = await fetch('/files?path=' + encodeURIComponent(p));
  const d = await r.json();

  $('files').innerHTML = d.map(x=>`
    <div class="item">${x}</div>
  `).join('');
}

/* PROFILES */
async function loadProfiles(){
  const r = await fetch('/profiles');
  const data = await r.json();

  $('profileList').innerHTML='';

  Object.keys(data).forEach(k=>{
    $('profileList').innerHTML += `<option>${k}</option>`;
  });

  $('profileList').onchange = ()=>selectProfile($('profileList').value,data);

  selectProfile(currentProfile,data);
}

function selectProfile(name,data){
  currentProfile=name;

  const c=data[name] || {};

  $('profileName').value=name;
  $('systemPrompt').value=c.system_prompt || '';
  $('prefProvider').value=c.provider || 'auto';
}

async function saveProfile(){
  await fetch('/profile/save',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      name:$('profileName').value,
      config:{
        system_prompt:$('systemPrompt').value,
        provider:$('prefProvider').value
      }
    })
  });

  loadProfiles();
}

async function deleteProfile(){
  await fetch('/profile/delete',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      name:$('profileName').value
    })
  });

  loadProfiles();
}

/* INIT */
renderSessions();
renderTeamMembers();
loadHistory();
loadTasks();
loadMemories();
loadProfiles();

/* PROVIDERS */
let providerCache = {};

async function loadProviders(){
  const r = await fetch('/providers');
  const data = await r.json();

  providerCache = data;
  $('providerList').innerHTML = '';

  Object.keys(data).forEach(k=>{
    const p = data[k];

    $('providerList').innerHTML += `
      <div class="provider-row" onclick="selectProvider('${k}')">
        <b>${p.name}</b><br>
        ${p.type} · ${p.model}
      </div>
    `;
  });
}

function newProvider(){
  $('pv_name').value = '';
  $('pv_type').value = 'ollama';
  $('pv_url').value = '';
  $('pv_key').value = '';
  $('pv_model').value = '';
  $('pv_enabled').checked = true;
  $('providerStatus').innerText = '';
}

function selectProvider(name){
  const p = providerCache[name];
  if(!p) return;

  $('pv_name').value = p.name || '';
  $('pv_type').value = p.type || 'ollama';
  $('pv_url').value = p.url || '';
  $('pv_key').value = p.api_key || '';
  $('pv_model').value = p.model || '';
  $('pv_enabled').checked = !!p.enabled;
}

async function saveProvider(){
  const payload = {
    name: $('pv_name').value.trim(),
    type: $('pv_type').value,
    url: $('pv_url').value.trim(),
    api_key: $('pv_key').value.trim(),
    model: $('pv_model').value.trim(),
    enabled: $('pv_enabled').checked
  };

  const r = await fetch('/provider/save',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(payload)
  });

  await r.json();
  loadProviders();

  $('providerStatus').innerText = 'Saved.';
}

async function testProvider(){
  const name = $('pv_name').value.trim();
  if(!name) return;

  const r = await fetch('/provider/test',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({name})
  });

  const d = await r.json();

  $('providerStatus').innerText =
    d.ok ? ('✅ ' + d.message) : ('❌ ' + d.error);
}

async function deleteProviderUI(){
  const name = $('pv_name').value.trim();
  if(!name) return;

  await fetch('/provider/delete',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({name})
  });

  newProvider();
  loadProviders();
}

loadProviders();

function b64ToBlob(base64, mime='audio/mp3'){
  const byteChars = atob(base64);
  const byteNumbers = new Array(byteChars.length);

  for(let i = 0; i < byteChars.length; i++){
    byteNumbers[i] = byteChars.charCodeAt(i);
  }

  const byteArray = new Uint8Array(byteNumbers);
  return new Blob([byteArray], { type: mime });
}

function playBase64Audio(b64){
  if(!b64) return;

  const blob = b64ToBlob(b64, 'audio/mp3');
  const url = URL.createObjectURL(blob);

  playNow(url);

  setTimeout(()=>{
    URL.revokeObjectURL(url);
  }, 30000);
}