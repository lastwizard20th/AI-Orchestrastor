const days=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
const slots=48; const rowH=24;
const root=document.getElementById('planner');
const nowLine=document.getElementById('nowLine');
let tasks=[]; let weekOffset=0;

function timeLabel(i){let h=String(Math.floor(i/2)).padStart(2,'0');return `${h}:${i%2?'30':'00'}`}
function div(c,t=''){const x=document.createElement('div');x.className=c;x.innerText=t;return x;}

function getWeekDates(){
 const d=new Date(); d.setDate(d.getDate()+weekOffset*7);
 const day=(d.getDay()+6)%7; d.setDate(d.getDate()-day);
 let arr=[]; for(let i=0;i<7;i++){let n=new Date(d);n.setDate(d.getDate()+i);arr.push(n)} return arr;
}
function build(){
 root.innerHTML='';
 const dates=getWeekDates();
 document.getElementById('weekLabel').innerText=dates[0].toLocaleDateString()+' - '+dates[6].toLocaleDateString();
 root.appendChild(div('head',''));
 dates.forEach((dt,i)=>{
   let h=div('head'+(isToday(dt)?' today':''),days[i]+' '+dt.getDate()); root.appendChild(h);
 });
 for(let r=0;r<slots;r++){
   root.appendChild(div('time',timeLabel(r)));
   for(let c=0;c<7;c++){
     const cell=div('cell'); cell.dataset.day=c; cell.dataset.slot=r;
     cell.ondblclick=()=>createTask(c,r);
     cell.ondragover=e=>e.preventDefault();
     cell.ondrop=e=>dropTask(e,c,r);
     root.appendChild(cell);
   }
 }
 drawNowLine();
}
function isToday(d){const n=new Date();return d.toDateString()===n.toDateString();}
function drawNowLine(){
 const n=new Date(); const mins=n.getHours()*60+n.getMinutes();
 nowLine.style.top=(24 + (mins/30)*rowH)+'px';
}
setInterval(drawNowLine,60000);

async function load(){const r=await fetch('/tasks');tasks=await r.json();render();}
function render(){build();tasks.forEach(drawTask)}

function drawTask(t){
 const idx=8 + t.start_slot*8 + t.day_index;
 const cell=root.children[idx]; if(!cell)return;
 const b=div('block '+(t.status||'queue'),t.title);
 b.draggable=true;
 b.style.height=(t.duration_slots*rowH-4)+'px';
 b.ondragstart=e=>e.dataTransfer.setData('id',t.id);
 b.ondblclick=()=>editTask(t);
 const rz=div('resize');
 rz.onmousedown=e=>resizeStart(e,t);
 b.appendChild(rz);
 cell.appendChild(b);
}
async function createTask(day,slot){let title=prompt('Task');if(!title)return;
await fetch('/task/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title,day_index:day,start_slot:slot,duration_slots:2})});load();}
async function editTask(t){
 let title=prompt('Title',t.title); if(title===null)return;
 let status=prompt('queue/ongoing/done/cancel',t.status||'queue');
 await fetch('/task/update',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:t.id,title,status})});load();}
async function dropTask(e,day,slot){e.preventDefault();const id=e.dataTransfer.getData('id');
await fetch('/task/move',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id,day_index:day,start_slot:slot})});load();}

function resizeStart(e,t){
 e.stopPropagation(); const startY=e.clientY; const start=t.duration_slots;
 document.onmousemove=async ev=>{};
 document.onmouseup=async ev=>{
   const diff=Math.round((ev.clientY-startY)/rowH);
   const dur=Math.max(1,start+diff);
   await fetch('/task/resize',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:t.id,duration_slots:dur})});
   document.onmousemove=null;document.onmouseup=null;load();
 }
}
function changeWeek(n){weekOffset+=n;render();}
async function autoSchedule(){alert('Hook AI scheduler API here');}
load();