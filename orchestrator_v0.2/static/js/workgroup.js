// static/js/workgroup.js
let groupId = null;
let graph = {nodes:[], edges:[]};

const $ = id => document.getElementById(id);

let wireMode = false;
let wireSource = null;

async function loadGroups(){
    const r = await fetch('/workgroups');
    const data = await r.json();

    $('groupList').innerHTML = '';
    data.forEach(g=>{
        $('groupList').innerHTML += `<option value="${g.id}">${g.name}</option>`;
    });

    if(data.length){
        groupId = data[0].id;
        $('groupList').value = groupId;
        await loadGraph();
    }

    $('groupList').onchange = async ()=>{
        groupId = $('groupList').value;
        await loadGraph();
    };
}

async function loadGraph(){
    const r = await fetch('/workgroup/' + groupId);
    graph = await r.json();
    render();
}

function render(){
    $('canvas').innerHTML = '';
    $('lines').innerHTML = '';

    graph.edges.forEach(drawEdge);
    graph.nodes.forEach(drawNode);
}

function drawNode(n){
    const d = document.createElement('div');
    d.className = 'node ' + n.role;
    d.style.left = n.x + 'px';
    d.style.top = n.y + 'px';

    d.innerHTML = `
        <div class="title">${n.title}</div>
        <div class="meta">${n.role}</div>
        <div class="pin out"></div>
        <div class="pin in"></div>
    `;

    d.onmousedown = e=>{
        if(e.target.classList.contains('pin')) return;
        dragStart(e,n,d);
    };

    d.querySelector('.pin.out').onclick = (e)=>{
        e.stopPropagation();
        wireMode = true;
        wireSource = n.id;
    };

    d.querySelector('.pin.in').onclick = async (e)=>{
        e.stopPropagation();
        if(!wireMode || !wireSource || wireSource == n.id) return;

        const relation = prompt(
            "Relation: support/advisor/delegate/critique/voice/vision",
            "support"
        ) || "support";

        await fetch('/edge/add',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({
                workgroup_id: groupId,
                source_id: wireSource,
                target_id: n.id,
                relation
            })
        });

        wireMode = false;
        wireSource = null;
        loadGraph();
    };

    $('canvas').appendChild(d);
}

function drawEdge(e){
    const a = graph.nodes.find(x=>x.id == e.source_id);
    const b = graph.nodes.find(x=>x.id == e.target_id);
    if(!a || !b) return;

    const line = document.createElementNS("http://www.w3.org/2000/svg","line");
    line.setAttribute("x1", a.x + 180);
    line.setAttribute("y1", a.y + 45);
    line.setAttribute("x2", b.x);
    line.setAttribute("y2", b.y + 45);
    line.setAttribute("stroke", "#ffffff");
    line.setAttribute("stroke-width", "2");

    $('lines').appendChild(line);

    const txt = document.createElementNS("http://www.w3.org/2000/svg","text");
    txt.setAttribute("x", (a.x+b.x+180)/2);
    txt.setAttribute("y", (a.y+b.y+45)/2);
    txt.setAttribute("fill", "#fff");
    txt.setAttribute("font-size", "12");
    txt.textContent = e.relation;

    $('lines').appendChild(txt);
}

function dragStart(e,n,el){
    const ox = e.offsetX;
    const oy = e.offsetY;

    document.onmousemove = ev=>{
        n.x = ev.pageX - ox;
        n.y = ev.pageY - oy;
        el.style.left = n.x + 'px';
        el.style.top = n.y + 'px';
        render();
    };

    document.onmouseup = async ()=>{
        await fetch('/node/move',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({id:n.id,x:n.x,y:n.y})
        });

        document.onmousemove = null;
        document.onmouseup = null;
    };
}

async function addNode(){
    const title = prompt("AI name");
    if(!title) return;

    const role = prompt("core / sub / agent / voice / vision","core");

    await fetch('/node/add',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            workgroup_id: groupId,
            provider_id: 1,
            title,
            role,
            x: 120,
            y: 120
        })
    });

    loadGraph();
}

async function runGraph(){
    const message = prompt("User request");
    if(!message) return;

    const r = await fetch('/workgroup/run',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
            workgroup_id: groupId,
            message
        })
    });

    const data = await r.json();

    $('logBox').innerHTML = '';

    (data.logs || []).forEach(x=>{
        $('logBox').innerHTML += `
        <div class="log">
            <b>${x.speaker}</b> (${x.type})<br>
            ${escapeHtml(x.text)}
        </div>`;
    });

    $('finalBox').innerText = data.response || '';
}

function escapeHtml(s){
    return (s||'')
        .replaceAll('&','&amp;')
        .replaceAll('<','&lt;')
        .replaceAll('>','&gt;');
}

loadGroups();