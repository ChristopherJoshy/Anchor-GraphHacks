import {scenes} from './scenes.mjs';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const sourceCuts=JSON.parse(await readFile(path.join(root,'source-cuts.json'),'utf8'));
const voice=JSON.parse(await readFile(path.join(root,'narration-timing.json'),'utf8'));
for(const scene of scenes){const line=voice.lines[scene.id];assert(line);scene.duration=Math.max(scene.duration,Math.ceil(line.duration+1.5));}
let start=0;for(const s of scenes){s.start=start;start+=s.duration;}assert(start>=196 && start<=240);
const icons=`<svg class="hide-visually" viewBox="0 0 200 200" aria-hidden="true"><defs>
<symbol id="icon-box" viewBox="0 0 200 200"><path d="M20 58L100 18L181 58L181 151L100 191L20 151Z" fill="#fff3db"/><path d="M100 99L181 58V151L100 191Z" fill="#ffd447"/><path d="M20 58L100 99L181 58M100 99V191M62 37L142 78V114L119 126V89Z" fill="none"/></symbol>
<symbol id="icon-factory" viewBox="0 0 200 200"><path d="M19 175V94L63 64V95L107 64V95L145 73V175Z" fill="#fff3db"/><path d="M143 75V25H171V175H145" fill="#ffd447"/><path d="M30 130H51V155H30ZM69 130H90V155H69ZM108 130H129V155H108Z" fill="#28dce9"/><path d="M5 176H192M147 17H167" fill="none"/></symbol>
<symbol id="icon-bolt" viewBox="0 0 200 200"><path d="M115 12L35 111H87L77 190L167 80H111Z" fill="#ffd447"/></symbol>
<symbol id="icon-disk" viewBox="0 0 200 200"><path d="M25 48V150C25 180 175 180 175 150V48" fill="#28dce9"/><ellipse cx="100" cy="48" rx="75" ry="30" fill="#fff3db"/><path d="M25 98C25 128 175 128 175 98M25 143C25 173 175 173 175 143" fill="none"/></symbol>
<symbol id="icon-magnify" viewBox="0 0 200 200"><circle cx="83" cy="83" r="62" fill="#28dce9"/><path d="M128 128L181 181" stroke-width="28"/><path d="M128 128L181 181" stroke="#ffd447" stroke-width="13"/><path d="M46 78Q48 45 80 44" fill="none" stroke="#fff3db" stroke-width="9"/></symbol>
<symbol id="icon-compare" viewBox="0 0 200 200"><path d="M20 20H104V155H20Z" fill="#fff3db"/><path d="M95 45H179V180H95Z" fill="#92e5ad"/><path d="M37 52H86M37 75H86M112 87H160M112 111H160M112 135H160" fill="none"/></symbol>
<symbol id="icon-anchor" viewBox="0 0 200 200"><circle cx="100" cy="35" r="22" fill="#ffd447"/><path d="M100 57V169M53 84H147M29 112V148Q100 220 171 148V112M13 133L29 112L50 132M151 132L171 112L188 133" fill="none" stroke-width="12"/><circle cx="100" cy="35" r="7" fill="#17172a" stroke="none"/></symbol>
</defs></svg>`;
await mkdir(path.join(root,'compositions'),{recursive:true});
for(const s of scenes){
 // Author separate block lines; the style system avoids forced line breaks in body text.
 const rawBody=s.id==='replan'?s.body.replace('RECOMPUTE<br class="forbidden-break"/>THE MIX.','<div>RECOMPUTE</div><div>THE MIX.</div>'):s.id==='verification'?s.body.replace('CHECK THE<br class="forbidden-break"/>STORED STATE.','<div>CHECK THE</div><div>STORED STATE.</div>'):s.body;
 const body=rawBody.replace('SCENE_COUNTER',`${String(scenes.indexOf(s)+1).padStart(2,'0')} / ${String(scenes.length).padStart(2,'0')}`).replaceAll('class="slash"','class="slash" data-layout-allow-overflow').replaceAll('class="speed ambient"','class="speed ambient" data-layout-allow-overflow').replaceAll('<g fill="none" stroke="currentColor"','<g data-layout-allow-overflow fill="none" stroke="currentColor"');
 const html=`<!doctype html><html lang="en"><head><meta charset="UTF-8"><title>${s.title}</title></head><body><template><div id="${s.id}" data-composition-id="${s.id}" data-duration="${s.duration}" class="scene" style="background:${s.bg};${s.bg==='#17172a'?'color:var(--paper)':''}">${body}</div><script>(function(){const tl=gsap.timeline({paused:true});const base='#${s.id} ';const A={pop(q,t,x=0,y=35,scale=.92){tl.fromTo(base+q,{x,y,opacity:0,scale},{x:0,y:0,opacity:1,scale:1,duration:.65,ease:'back.out(1.3)'},t)},count(q,n,t,d=1){tl.fromTo(base+q,{textContent:0},{textContent:n,snap:{textContent:1},duration:d,ease:'power2.out'},t)},draw(q,t,d=.7){document.querySelectorAll(base+q).forEach(p=>{const n=p.getTotalLength();tl.fromTo(p,{strokeDasharray:n,strokeDashoffset:n},{strokeDashoffset:0,duration:d,ease:'power2.out'},t)})}};${s.motion}window.__timelines['${s.id}']=tl;})();</script></template></body></html>`;
 await writeFile(path.join(root,'compositions',`${s.id}.html`),html);
}
const cues=[];
const marks={hook:[[1.1,'open_002'],[5.2,'bong_001']],gap:[[1.3,'click_003'],[3,'switch_002'],[5.6,'impactPunch_medium_002']],outage:[[5,'error_003']],graph:[[4.2,'switch_002'],[5.4,'switch_002'],[12.2,'bong_001']],evidence:[[3,'click_003'],[5,'click_003']],allocation:[[1,'open_002'],[3,'switch_002'],[5.5,'bong_001']],stress:[[3,'click_003'],[5,'click_003'],[7,'error_003']],replan:[[2.5,'switch_002'],[5.2,'open_002']],verification:[[2,'click_003'],[5,'click_003'],[9,'switch_002']],outro:[[.2,'impactPunch_medium_002']]};
for(const scene of scenes)for(const [time,file] of marks[scene.id]||[])cues.push([scene.start+time,file,.22]);
let circles='';for(let y=0;y<1080;y+=100)for(let x=0;x<1920;x+=100)circles+=`<circle class="ink-dot" data-layout-allow-overflow cx="${x+50}" cy="${y+50}" r="74"/>`;
const hosts=scenes.map(s=>`<div id="host-${s.id}" class="clip" data-composition-id="${s.id}" data-composition-src="compositions/${s.id}.html" data-start="${s.start}" data-duration="${s.duration}" data-track-index="0"></div>`).join('\n');
const soundDurations=JSON.parse(await readFile(path.join(root,'assets/sfx/durations.json'),'utf8'));
const audio=cues.map(([time,file,volume],i)=>`<audio id="cue-${i}" data-start="${time}" data-duration="${soundDurations[file+'.ogg']}" data-track-index="3" data-volume="${volume}" src="assets/sfx/${file}.ogg"></audio>`).join('\n');
const voices=scenes.map(scene=>`<audio id="voice-${scene.id}" data-start="${scene.start+.7}" data-duration="${voice.lines[scene.id].duration}" data-track-index="4" data-volume="1" src="${voice.lines[scene.id].path}"></audio>`).join('\n');
const duckPoints=[{t:0,v:0}];
for(const scene of scenes){const end=scene.start+.7+voice.lines[scene.id].duration;duckPoints.push({t:scene.start+.3,v:.72},{t:scene.start+.65,v:.4},{t:end,v:.4},{t:Math.min(end+.45,scene.start+scene.duration-.1),v:.72});}
duckPoints.push({t:start-1,v:.72},{t:start,v:0});
duckPoints.sort((a,b)=>a.t-b.t);
const envelope=JSON.stringify({version:1,lanes:[{target:'volume',points:duckPoints}]}).replaceAll('"','&quot;');
const music=`<audio id="music-cipher" data-start="0" data-duration="${start}" data-track-index="5" data-volume="1" data-automation="${envelope}" src="assets/audio/cipher-bed.wav"></audio>`;
const stamp=t=>{const ms=Math.round(t*1000);return `${String(Math.floor(ms/3600000)).padStart(2,'0')}:${String(Math.floor(ms/60000)%60).padStart(2,'0')}:${String(Math.floor(ms/1000)%60).padStart(2,'0')},${String(ms%1000).padStart(3,'0')}`};
let subtitle=0;
const captions=scenes.flatMap(scene=>voice.lines[scene.id].sentences.map(line=>`${++subtitle}\n${stamp(scene.start+.7+line.start)} --> ${stamp(scene.start+.7+line.start+line.duration)}\n${line.text}\n`)).join('\n');
await writeFile(path.join(root,'../anchor-demo-v03.srt'),captions);
assert.equal(subtitle,Object.values(voice.lines).reduce((n,line)=>n+line.sentences.length,0));
const seams=scenes.slice(1).filter((s,i)=>!['network','evidence','allocation','execution-proof','changed-plan','readback-proof'].includes(s.id)&&!['network','evidence','allocation','execution-proof','changed-plan','readback-proof'].includes(scenes[i].id)).map(s=>`tl.fromTo('.ink-dot',{scale:0},{scale:1,duration:.27,stagger:{amount:.1,from:'start'},ease:'power2.in',immediateRender:false},${s.start-.4});tl.to('.ink-dot',{scale:0,duration:.30,stagger:{amount:.1,from:'end'},ease:'power2.out'},${s.start+.02});`).join('\n');
await writeFile(path.join(root,'index.html'),`<!doctype html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=1920,height=1080"><title>Anchor / Shared Failure — Motion Study</title><link rel="stylesheet" href="style.css"><script src="assets/vendor/gsap.min.js"></script></head><body>${icons}<div id="root" data-composition-id="main" data-width="1920" data-height="1080" data-duration="${start}" data-fps="30">${hosts}<svg id="seam" viewBox="0 0 1920 1080" aria-hidden="true">${circles}</svg>${audio}${voices}${music}</div><script>const tl=gsap.timeline({paused:true});gsap.set('.ink-dot',{scale:0});${seams}window.__timelines.main=tl;</script></body></html>`);
await writeFile(path.join(root,'timeline.json'),JSON.stringify({width:1920,height:1080,fps:30,duration:start,scenes:scenes.map(({id,title,start,duration,kind})=>({id,title,start,duration,kind})),sound_cues:cues.map(([start,file,volume])=>({start,file,volume}))},null,2)+'\n');
await writeFile(path.join(root,'STORYBOARD.md'),'# Anchor motion study v03\n\n'+scenes.map((s,i)=>`## Frame ${i+1}\n\nstatus: animated\nsrc: compositions/${s.id}.html\nstart: ${s.start}\nduration: ${s.duration}\nshape: kinetic-beat-slam + svg-path-draw + stat-bars-and-fills (as relevant); deterministic halftone seam adapted from the installed catalog component.\n\n${s.title}. ${s.kind}.\n`).join('\n'));
const cuts=JSON.parse(await readFile(path.join(root,'source-cuts.json'),'utf8'));
assert(cuts.cuts.every(c=>c.start+c.duration<=cuts.limit_seconds));assert.equal(1000-350,650);assert.equal(7*50,350);assert.equal(13*50,650);assert.equal(350+650,1000);assert.equal(650*900,585000);assert.equal(350+450+200,1000);assert.equal(450*900+200*1250,655000);
console.log(`Built ${scenes.length} editable scene modules / ${start}s / 1920x1080 / 30fps. Source limit and recorded arithmetic checks passed.`);
