/* Shared AI copilot for the FMCG portfolio demos — one key works across every page.
   The key is entered by the user, stored ONLY in this browser (localStorage), and sent
   ONLY to OpenRouter over HTTPS. Never to this site's server, never committed. */
(function(){
  if(window.__FMCGAI__) return; window.__FMCGAI__=1;
  var KEY="fmcg_or_key", MODEL="fmcg_or_model", ONF="fmcg_ai_on";
  var st={key:"",model:"openai/gpt-4o-mini",on:false,busy:false};
  function load(){try{st.key=localStorage.getItem(KEY)||"";st.model=localStorage.getItem(MODEL)||"openai/gpt-4o-mini";st.on=!!st.key&&localStorage.getItem(ONF)!=="0";}catch(e){}}
  function calls(){return +(localStorage.getItem("fmcg_or_calls")||0);}
  function tokens(){return +(localStorage.getItem("fmcg_or_tokens")||0);}
  load();
  var CSS="#fai *{box-sizing:border-box}#fai .btn{position:fixed;right:18px;bottom:18px;z-index:9998;background:linear-gradient(135deg,#b3282d,#8a1f23);color:#fff;border:0;border-radius:999px;padding:12px 17px;font:700 13.5px ui-sans-serif,system-ui;box-shadow:0 8px 24px rgba(0,0,0,.28);cursor:pointer;display:flex;gap:7px;align-items:center}#fai .btn .d{width:8px;height:8px;border-radius:50%;background:#7ee2a8;box-shadow:0 0 0 0 rgba(126,226,168,.6);animation:faip 2s infinite}#fai .btn.off .d{background:#c9c2ba;animation:none}@keyframes faip{0%{box-shadow:0 0 0 0 rgba(126,226,168,.5)}70%{box-shadow:0 0 0 7px rgba(126,226,168,0)}}#fai .panel{position:fixed;right:18px;bottom:74px;z-index:9999;width:min(384px,92vw);height:min(540px,74vh);background:#fff;border:1px solid #e7e2db;border-radius:16px;box-shadow:0 24px 60px rgba(0,0,0,.32);display:none;flex-direction:column;overflow:hidden;font:14px ui-sans-serif,system-ui;color:#171412}#fai.open .panel{display:flex}#fai .hd{background:linear-gradient(135deg,#1c1917,#2a2420);color:#f3ede9;padding:11px 13px;display:flex;align-items:center;gap:8px}#fai .hd b{font-size:14px}#fai .sw{margin-left:auto;display:flex;gap:8px;align-items:center}#fai .tg{width:40px;height:21px;border-radius:999px;background:#5a534d;position:relative;cursor:pointer;border:0;flex:0 0 auto}#fai .tg.on{background:#15803d}#fai .tg span{position:absolute;top:2px;left:2px;width:17px;height:17px;border-radius:50%;background:#fff;transition:.15s}#fai .tg.on span{left:21px}#fai .ic{background:none;border:0;color:#e7dcd6;cursor:pointer;font-size:15px;padding:2px}#fai .log{flex:1;overflow-y:auto;padding:13px;background:#f7f4f0}#fai .b{max-width:90%;margin-bottom:10px;padding:9px 12px;border-radius:13px;font-size:13.5px;line-height:1.5;white-space:pre-wrap;word-wrap:break-word}#fai .b.u{margin-left:auto;background:#171412;color:#fff;border-bottom-right-radius:4px}#fai .b.a{background:#fff;border:1px solid #e7e2db;border-bottom-left-radius:4px}#fai .hint{color:#6f675e;font-size:12.5px;text-align:center;margin-top:10px}#fai .in{display:flex;gap:8px;padding:10px;border-top:1px solid #e7e2db;background:#fff}#fai .in input{flex:1;border:1.5px solid #e7e2db;border-radius:10px;padding:9px 11px;font:14px ui-sans-serif;min-height:42px}#fai .in button{border:0;background:#b3282d;color:#fff;border-radius:10px;padding:0 14px;font-weight:800;cursor:pointer}#fai .set{padding:14px;display:none;background:#fff;overflow-y:auto;flex:1}#fai.settings .set{display:block}#fai.settings .log,#fai.settings .in{display:none}#fai .set label{display:block;font-size:12px;font-weight:700;margin:10px 0 4px}#fai .set input,#fai .set select{width:100%;border:1.5px solid #e7e2db;border-radius:9px;padding:9px 10px;font:14px ui-sans-serif;min-height:42px}#fai .set .note{font-size:11.5px;color:#403a35;background:#faf8f5;border:1px solid #e7e2db;border-left:3px solid #c99a2e;border-radius:8px;padding:9px 10px;margin-top:11px;line-height:1.45}#fai .set .save{margin-top:12px;width:100%;border:0;background:#b3282d;color:#fff;border-radius:10px;padding:11px;font-weight:800;cursor:pointer}#fai .set .clr{margin-top:8px;width:100%;border:1px solid #e7e2db;background:#f4f2ef;color:#171412;border-radius:10px;padding:9px;font-weight:700;cursor:pointer}";
  var st_el=document.createElement("style");st_el.textContent=CSS;document.head.appendChild(st_el);
  var el=document.createElement("div");el.id="fai";
  el.innerHTML='<button class="btn" id="faibtn"><span class="d"></span>Ask AI</button>'+
   '<div class="panel"><div class="hd"><b>🤖 AI copilot</b><div class="sw"><button class="tg" id="faitog" title="AI on/off"><span></span></button><button class="ic" id="faigear" title="Settings">⚙</button><button class="ic" id="faicls" title="Close">✕</button></div></div>'+
   '<div class="log" id="failog"></div>'+
   '<div class="set" id="faiset"><div style="font-size:13px;color:#403a35">Paste your <b>OpenRouter</b> key once — it works across <b>every demo</b> on this site and stays only in this browser.</div>'+
   '<label>API key</label><input id="faikey" type="password" placeholder="sk-or-v1-…" autocomplete="off" spellcheck="false">'+
   '<label>Model</label><select id="faimodel"><option value="openai/gpt-4o-mini">openai/gpt-4o-mini — cheap</option><option value="deepseek/deepseek-chat">deepseek/deepseek-chat — cheapest</option><option value="google/gemini-flash-1.5">google/gemini-flash-1.5</option><option value="anthropic/claude-3.5-haiku">anthropic/claude-3.5-haiku</option></select>'+
   '<div class="note">🔒 Stored in this browser only, sent only to OpenRouter over HTTPS — never to this site or the repo. Avoid on a shared computer. <span id="faiusage"></span></div>'+
   '<button class="save" id="faisave">Save &amp; connect</button><button class="clr" id="faiclr">Clear key</button></div>'+
   '<div class="in"><input id="faiq" placeholder="Ask about this page…"><button id="faisend">Ask</button></div></div>';
  document.addEventListener("DOMContentLoaded",function(){document.body.appendChild(el);wire();});
  if(document.readyState!=="loading"){document.body.appendChild(el);wire();}
  var log,q;
  function $(id){return document.getElementById(id);}
  function wire(){
    log=$("failog");q=$("faiq");
    $("faibtn").onclick=function(){el.classList.toggle("open");if(el.classList.contains("open")&&!st.key)el.classList.add("settings");paint();};
    $("faicls").onclick=function(){el.classList.remove("open");};
    $("faigear").onclick=function(){el.classList.toggle("settings");paint();};
    $("faitog").onclick=function(){if(!st.key){el.classList.add("settings");paint();return;}st.on=!st.on;try{localStorage.setItem(ONF,st.on?"1":"0");}catch(e){}paint();};
    $("faisave").onclick=function(){st.key=$("faikey").value.trim();st.model=$("faimodel").value;st.on=!!st.key;try{if(st.key)localStorage.setItem(KEY,st.key);else localStorage.removeItem(KEY);localStorage.setItem(MODEL,st.model);localStorage.setItem(ONF,"1");}catch(e){}el.classList.remove("settings");paint();};
    $("faiclr").onclick=function(){st.key="";st.on=false;$("faikey").value="";try{localStorage.removeItem(KEY);}catch(e){}paint();};
    $("faisend").onclick=send;q.addEventListener("keydown",function(e){if(e.key==="Enter")send();});
    paint();
  }
  function paint(){
    $("faibtn").className="btn"+(st.on?"":" off");
    $("faitog").className="tg"+(st.on?" on":"");
    if($("faikey"))$("faikey").value=st.key;if($("faimodel"))$("faimodel").value=st.model;
    if($("faiusage"))$("faiusage").textContent=calls()?(" · "+calls()+" calls this browser"):"";
    if(log&&!log.children.length&&!el.classList.contains("settings"))log.innerHTML='<div class="hint">'+(st.on?"Ask me anything about this demo — the plan, a number, why something is flagged.":"Connect your OpenRouter key (⚙) to turn this on.")+"</div>";
  }
  function bub(cls,html){var d=document.createElement("div");d.className="b "+cls;d.innerHTML=html;log.appendChild(d);log.scrollTop=log.scrollHeight;return d;}
  function esc(s){return (s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");}
  function context(){
    var hint=window.FMCGAI_HINT||"An FMCG AI portfolio demo.";
    var body="";
    try{ body= (typeof window.FMCGAI_CONTEXT==="function") ? String(window.FMCGAI_CONTEXT()) : (document.body.innerText||"").slice(0,4000); }catch(e){ body=(document.body.innerText||"").slice(0,4000); }
    return "You are an AI copilot embedded in this page: \""+document.title+"\". "+hint+" Answer the user's question concisely and specifically, grounded ONLY in the content below; if it is not in the content, say so. Content:\n"+body;
  }
  async function send(){
    if(st.busy)return;var text=(q.value||"").trim();if(!text)return;
    if(!st.on){el.classList.add("settings");paint();return;}
    if(log.querySelector(".hint"))log.innerHTML="";
    bub("u",esc(text));q.value="";var out=bub("a",'<span style="color:#6d28d9">…</span>');st.busy=true;
    try{ await stream(context(),text,out); }
    catch(e){ out.innerHTML='⚠ '+esc(e.message); }
    st.busy=false;
  }
  async function stream(sys,user,out){
    var res=await fetch("https://openrouter.ai/api/v1/chat/completions",{method:"POST",headers:{"Authorization":"Bearer "+st.key,"Content-Type":"application/json","X-Title":"FMCG Portfolio"},body:JSON.stringify({model:st.model,stream:true,temperature:0.3,max_tokens:500,messages:[{role:"system",content:sys},{role:"user",content:user}]})});
    if(!res.ok){var t=await res.text();throw new Error("HTTP "+res.status+" "+t.slice(0,120));}
    var acc="",tok=0;
    if(res.body&&res.body.getReader){
      var rd=res.body.getReader(),dec=new TextDecoder(),buf="";
      while(true){var r=await rd.read();if(r.done)break;buf+=dec.decode(r.value,{stream:true});var lines=buf.split("\n");buf=lines.pop();
        for(var i=0;i<lines.length;i++){var ln=lines[i].trim();if(!ln||ln.indexOf("data:")!==0)continue;var data=ln.slice(5).trim();if(data==="[DONE]")continue;
          try{var j=JSON.parse(data);var d=j.choices&&j.choices[0]&&j.choices[0].delta&&j.choices[0].delta.content;if(d){acc+=d;out.innerHTML=esc(acc);log.scrollTop=log.scrollHeight;}if(j.usage&&j.usage.total_tokens)tok=j.usage.total_tokens;}catch(e){}}}
    } else { var j=await res.json();acc=(j.choices&&j.choices[0]&&j.choices[0].message&&j.choices[0].message.content)||"";out.innerHTML=esc(acc);tok=(j.usage&&j.usage.total_tokens)||0; }
    try{localStorage.setItem("fmcg_or_calls",calls()+1);localStorage.setItem("fmcg_or_tokens",tokens()+(tok||0));}catch(e){}
    if(!acc)out.innerHTML="(no response)";
  }
})();
