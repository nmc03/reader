async function purgeLegacyServiceWorker(){
  try{
    if("serviceWorker" in navigator){
      const regs=await navigator.serviceWorker.getRegistrations();
      await Promise.all(regs.map(r=>r.unregister()));
    }
    if("caches" in window){
      const keys=await caches.keys();
      await Promise.all(keys.map(k=>caches.delete(k)));
    }
  }catch(_){}
}
purgeLegacyServiceWorker();
const $=id=>document.getElementById(id); const audio=$("audio");
const st={mode:"normal",chunks:[],i:0,playing:false,gen:0,cache:new Map()};
const books=["Génesis","Éxodo","Levítico","Números","Deuteronomio","Josué","Jueces","Rut","Samuel","Reyes","Crónicas","Esdras","Nehemías","Ester","Job","Salmos","Salmo","Proverbios","Eclesiastés","Cantar de los Cantares","Isaías","Jeremías","Lamentaciones","Ezequiel","Daniel","Oseas","Joel","Amós","Abdías","Jonás","Miqueas","Nahúm","Habacuc","Sofonías","Ageo","Zacarías","Malaquías","Mateo","Marcos","Lucas","Juan","Hechos","Romanos","Corintios","Gálatas","Efesios","Filipenses","Colosenses","Tesalonicenses","Timoteo","Tito","Filemón","Hebreos","Santiago","Pedro","Judas","Apocalipsis"];
function norm(s){return s.replace(/\r\n?/g,"\n").replace(/[ \t]+/g," ").replace(/\n{3,}/g,"\n\n").trim()}
function clean(s){let o=s;const b=new RegExp(String.raw`(?:\b[1-3]\s*)?(?:${books.join("|")})\s+\d{1,3}:\d{1,3}(?:[-–]\d{1,3})?(?:\s*[,;]\s*\d{1,3}(?::\d{1,3})?(?:[-–]\d{1,3})?)*`,"gi");o=o.replace(new RegExp(String.raw`\(\s*${b.source}\s*\)`,"gi"),"").replace(b,"").replace(/\[(?:\d+|nota(?:\s+\d+)?)\]/gi,"").replace(/\bhttps?:\/\/\S+/gi,"").replace(/[ \t]+([,.;:!?])/g,"$1").replace(/\(\s*\)/g,"");return norm(o)}
function chunks(s,max=2800){const out=[];for(const p of norm(s).split(/\n{2,}/).filter(Boolean)){if(p.length<=max){out.push(p);continue}const ss=p.match(/[^.!?…]+[.!?…]+(?:["»”’])?|[^.!?…]+$/g)||[p];let c="";for(const r of ss){const x=r.trim();if((c+" "+x).trim().length<=max)c=(c+" "+x).trim();else{if(c)out.push(c);for(let i=0;i<x.length;i+=max)out.push(x.slice(i,i+max));c=""}}if(c)out.push(c)}return out}
function mode(m){st.mode=m;$("normal").classList.toggle("active",m==="normal");$("clean").classList.toggle("active",m==="clean");const r=norm($("text").value);$("info").textContent=m==="clean"&&r?(clean(r)!==r?"Se omitirán las referencias detectadas.":"No se han detectado referencias para omitir."):""}
function prepare(){stop();const raw=norm($("text").value);if(!raw){$("info").textContent="Pega primero algún texto.";return}const t=st.mode==="clean"?clean(raw):raw;st.chunks=chunks(t);st.i=0;st.cache.clear();renderChunks();$("reader").hidden=false;$("editor").hidden=true;render();scrollTo({top:0,behavior:"smooth"})}
function renderChunks(){const v=$("view");v.replaceChildren();st.chunks.forEach((t,i)=>{const d=document.createElement("div");d.className="chunk";d.textContent=t;d.onclick=()=>jump(i,true);v.appendChild(d)})}
function render(){const n=st.chunks.length;$("count").textContent=n?`${st.i+1} / ${n}`:"0 / 0";$("play").textContent=st.playing?"⏸":"▶";$("prev").disabled=st.i<=0;$("next").disabled=!n||st.i>=n-1;$("bar").style.width=n?`${(st.i+1)/n*100}%`:"0";[...$("view").children].forEach((e,i)=>e.classList.toggle("current",i===st.i));if(st.playing)$("view").children[st.i]?.scrollIntoView({behavior:"smooth",block:"center"});if("mediaSession"in navigator)navigator.mediaSession.playbackState=st.playing?"playing":"paused"}
function rate(){const x=Number($("speed").value),p=Math.round((x-1)*100);return `${p>=0?"+":""}${p}%`}
async function url(t){const k=$("speed").value+":"+t;if(st.cache.has(k))return st.cache.get(k);const p=fetch("/api/tts",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:t,rate:rate()})}).then(async r=>{const d=await r.json();if(!r.ok)throw Error(d.detail||`HTTP ${r.status}`);return d.audio_url});st.cache.set(k,p);try{return await p}catch(e){st.cache.delete(k);throw e}}
function browser(t,g){speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(t);u.lang="es-ES";u.rate=Number($("speed").value);const vs=speechSynthesis.getVoices();u.voice=vs.find(v=>v.lang?.toLowerCase()==="es-es")||vs.find(v=>v.lang?.toLowerCase().startsWith("es"))||null;u.onend=()=>ended(g);u.onerror=e=>fail(Error(e.error||"error de voz"),g);speechSynthesis.speak(u)}
async function start(g){const t=st.chunks[st.i];if(!t||!st.playing||g!==st.gen)return;if($("tts").value==="browser")return browser(t,g);try{audio.src=await url(t);if(!st.playing||g!==st.gen)return;audio.currentTime=0;audio.onended=()=>ended(g);audio.onerror=()=>fail(Error("fallo de audio"),g);await audio.play();const nx=st.chunks[st.i+1];if(nx)url(nx).catch(()=>{})}catch(e){fail(e,g)}}
async function toggle(){if(!st.chunks.length)return;if(st.playing){st.playing=false;audio.pause();if("speechSynthesis"in window)speechSynthesis.pause();render();return}st.playing=true;render();if($("tts").value==="browser"&&speechSynthesis.paused)speechSynthesis.resume();else await start(st.gen)}
function stop(){st.gen++;st.playing=false;audio.pause();audio.removeAttribute("src");audio.load();if("speechSynthesis"in window)speechSynthesis.cancel()}
async function jump(i,auto=false){if(i<0||i>=st.chunks.length)return;stop();st.i=i;render();if(auto){st.playing=true;render();await start(st.gen)}}
async function move(d){const keep=st.playing;stop();st.i=Math.max(0,Math.min(st.chunks.length-1,st.i+d));render();if(keep){st.playing=true;render();await start(st.gen)}}
function ended(g){if(!st.playing||g!==st.gen)return;if(st.i>=st.chunks.length-1){st.playing=false;render();return}st.i++;render();start(g)}
function fail(e,g){if(g!==st.gen)return;if($("tts").value==="server"&&"speechSynthesis"in window){$("info").textContent="Voz del servidor no disponible; usando voz del dispositivo.";$("tts").value="browser";browser(st.chunks[st.i],g);return}st.playing=false;$("info").textContent=`Error: ${e.message}`;render()}
$("normal").onclick=()=>mode("normal");$("clean").onclick=()=>mode("clean");$("prepare").onclick=prepare;$("play").onclick=toggle;$("prev").onclick=()=>move(-1);$("next").onclick=()=>move(1);$("edit").onclick=()=>{stop();$("reader").hidden=true;$("editor").hidden=false};$("settings").onclick=()=> $("dlg").showModal();$("font").onchange=()=>document.documentElement.style.setProperty("--scale",$("font").value);$("speed").onchange=()=>{stop();st.cache.clear();render()};$("tts").onchange=()=>{stop();render()};$("text").oninput=()=>mode(st.mode);window.addEventListener("beforeunload",()=>localStorage.setItem("reader-text",$("text").value));$("text").value=localStorage.getItem("reader-text")||"";
if("mediaSession"in navigator){navigator.mediaSession.setActionHandler("play",()=>{if(!st.playing)toggle()});navigator.mediaSession.setActionHandler("pause",()=>{if(st.playing)toggle()});navigator.mediaSession.setActionHandler("nexttrack",()=>move(1));navigator.mediaSession.setActionHandler("previoustrack",()=>move(-1))}
mode("normal");render();
