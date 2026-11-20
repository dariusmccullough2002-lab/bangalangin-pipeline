// Small, dependency-free Excel exports of the currently rendered list.
import {findDoorPlayer} from './knocking-door.js';
const xml=value=>String(value??'').replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g,'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const encoder=new TextEncoder();
const colName=index=>{let name='';for(let n=index+1;n;n=Math.floor((n-1)/26))name=String.fromCharCode(65+(n-1)%26)+name;return name;};
const crcTable=Array.from({length:256},(_,n)=>{for(let k=0;k<8;k++)n=n&1?0xedb88320^(n>>>1):n>>>1;return n>>>0;});
const crc32=bytes=>{let crc=0xffffffff;for(const byte of bytes)crc=crcTable[(crc^byte)&255]^(crc>>>8);return (crc^0xffffffff)>>>0;};
function zip(files){
 const parts=[],central=[];let offset=0,centralSize=0;
 for(const [name,text] of files){
  const path=encoder.encode(name),data=encoder.encode(text),crc=crc32(data);
  const local=new Uint8Array(30+path.length),v=new DataView(local.buffer);
  v.setUint32(0,0x04034b50,true);v.setUint16(4,20,true);v.setUint32(14,crc,true);v.setUint32(18,data.length,true);v.setUint32(22,data.length,true);v.setUint16(26,path.length,true);local.set(path,30);
  const entry=new Uint8Array(46+path.length),c=new DataView(entry.buffer);
  c.setUint32(0,0x02014b50,true);c.setUint16(4,20,true);c.setUint16(6,20,true);c.setUint32(16,crc,true);c.setUint32(20,data.length,true);c.setUint32(24,data.length,true);c.setUint16(28,path.length,true);c.setUint32(42,offset,true);entry.set(path,46);
  parts.push(local,data);central.push(entry);offset+=local.length+data.length;centralSize+=entry.length;
 }
 const end=new Uint8Array(22),v=new DataView(end.buffer);v.setUint32(0,0x06054b50,true);v.setUint16(8,files.length,true);v.setUint16(10,files.length,true);v.setUint32(12,centralSize,true);v.setUint32(16,offset,true);
 return new Blob([...parts,...central,end],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
}
export function excelWorkbook(headers,rows,title='Pipeline'){
 const width=headers.length,last=colName(Math.max(0,width-1)),end=Math.max(1,rows.length+1);
 const cell=(value,r,c)=>{const ref=colName(c)+r;if(typeof value==='number'&&Number.isFinite(value))return `<c r="${ref}"${r===1?' s="1"':''}><v>${value}</v></c>`;return `<c r="${ref}" t="inlineStr"${r===1?' s="1"':''}><is><t xml:space="preserve">${xml(String(value??'').slice(0,32767))}</t></is></c>`;};
 const sheet=`<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><dimension ref="A1:${last}${end}"/><sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews><cols>${headers.map((h,c)=>{const max=Math.max(String(h).length,...rows.slice(0,1000).map(r=>String(r[c]??'').length));return `<col min="${c+1}" max="${c+1}" width="${Math.min(64,Math.max(12,max+2))}" customWidth="1"/>`;}).join('')}</cols><sheetData>${[headers,...rows].map((r,i)=>`<row r="${i+1}">${r.map((v,c)=>cell(v,i+1,c)).join('')}</row>`).join('')}</sheetData><autoFilter ref="A1:${last}${end}"/></worksheet>`;
 const ns='http://schemas.openxmlformats.org/package/2006/relationships';
 return zip([
  ['[Content_Types].xml','<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/><Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/></Types>'],
  ['_rels/.rels',`<Relationships xmlns="${ns}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>`],
  ['xl/workbook.xml',`<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="${xml(title.replace(/[\\/*?:\[\]]/g,' ').slice(0,31)||'Pipeline')}" sheetId="1" r:id="rId1"/></sheets></workbook>`],
  ['xl/_rels/workbook.xml.rels',`<Relationships xmlns="${ns}"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>`],
  ['xl/styles.xml','<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><color rgb="FFFFFFFF"/><sz val="11"/><name val="Calibri"/></font></fonts><fills count="3"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill><fill><patternFill patternType="solid"><fgColor rgb="FF153E39"/><bgColor indexed="64"/></patternFill></fill></fills><borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="2"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/><xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1"/></cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles></styleSheet>'],
  ['xl/worksheets/sheet1.xml',sheet]
 ]);
}
const cleanText=el=>{
 if(!el)return '';
 const copy=el.cloneNode(true);copy.querySelectorAll('svg,button,[aria-hidden="true"],.sr-only,.list-export-tools').forEach(n=>n.remove());
 copy.querySelectorAll('br').forEach(n=>n.replaceWith(' · '));copy.querySelectorAll('small').forEach(n=>n.prepend(' · '));copy.querySelectorAll('span').forEach(n=>n.append(' '));
 return copy.textContent.replace(/\s+/g,' ').trim();
};
const value=text=>/^-?\d+(\.\d+)?$/.test(text)&&!/^0\d/.test(text)?Number(text):text;
const url=anchor=>anchor?new URL(anchor.getAttribute('href'),location.href).href:'';
export function tableData(table){
 const headers=[...table.querySelectorAll('thead tr:last-child th')].map(cleanText);
 const rows=[...table.querySelectorAll('tbody tr')].filter(r=>!r.hidden&&!r.querySelector('[colspan]')).map(r=>[...r.cells].map(c=>value(cleanText(c))));
 if(!headers.length||!rows.length)return {headers,rows:[]};
 const links=[...table.querySelectorAll('tbody tr')].filter(r=>!r.hidden&&!r.querySelector('[colspan]')).map(r=>url(r.querySelector('a[href*="player/"]')));
 if(links.some(Boolean)){headers.push('Profile URL');rows.forEach((r,i)=>r.push(links[i]));}
 return {headers,rows};
}
export function cardData(container,kind){
 if(kind==='dsl')return {headers:['Rank / status','Prospect','Position / MLB / B-T','Age','Nation','BangaLangin organization','Profile URL'],rows:[...container.querySelectorAll('.dsl-card')].map(c=>[cleanText(c.querySelector('.dsl-rank')),cleanText(c.querySelector('h2')),cleanText(c.querySelector('.dsl-card-copy > .muted')),cleanText(c.querySelector('.dsl-bio span:first-child')).replace(/^Age\s*/,''),cleanText(c.querySelector('.dsl-bio span:nth-child(2)')).replace(/^Nation\s*/,''),cleanText(c.querySelector('.dsl-owner b')),url(c.querySelector('.dsl-card-copy a'))])};
 if(kind==='pro')return {headers:['Rank / status','Prospect','Position / club / league / country','Arrival status','Profile URL'],rows:[...container.querySelectorAll('.pro-card')].map(c=>[cleanText(c.querySelector('.dsl-rank')),cleanText(c.querySelector('h2')),cleanText(c.querySelector('.pro-card-copy > .muted')),cleanText(c.querySelector('.badge')),url(c.querySelector('h2 a'))])};
 if(kind==='door')return {headers:['Prospect','Position','MLB organization','Roster path','Role','Window','League rank (saved)','Profile URL'],rows:[...container.querySelectorAll('.door-card,.door-player-list > li')].map(c=>{const tile=c.matches('.door-card'),a=c.querySelector(tile?'.door-card-name':'.door-list-player'),id=a?.getAttribute('href')?.split('/')[1],p=findDoorPlayer({playerId:decodeURIComponent(id??'')});return [p?.name??cleanText(c.querySelector(tile?'h2':'.door-list-player strong')),p?.position??'',p?.mlbOrg??'',cleanText(c.querySelector(tile?'.door-path':'.door-list-path > span')),p?.role??'',p?.window??'',p?.leagueRank??'',url(a)];})};
 if(kind==='depth')return {headers:['Player','Position appearances / performance','Profile URL'],rows:[...container.querySelectorAll('ul > li')].map(c=>[cleanText(c.querySelector('strong')),cleanText(c.querySelector('.door-depth-usage')),url(c.querySelector('strong a'))])};
 return {headers:['Organization / list','Details','URL'],rows:[...container.querySelectorAll(':scope > a.card')].map(c=>[cleanText(c.querySelector('h3')),cleanText(c.querySelector('p')),url(c)])};
}
function download(data,title){
 if(!data.rows.length)return;
 const blob=excelWorkbook(data.headers,data.rows,title),href=URL.createObjectURL(blob),a=document.createElement('a');a.href=href;
 a.download=`BangaLangin-${title.normalize('NFD').replace(/\p{M}/gu,'').replace(/[^a-zA-Z0-9]+/g,'-').replace(/^-|-$/g,'')}-${new Date().toLocaleDateString('en-CA',{timeZone:'America/New_York'})}.xlsx`;
 document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(href),30000);
}
export function activateListExports(app){
 const style=document.createElement('style');style.textContent=`.list-export-tools{display:flex;justify-content:flex-end;align-items:center;margin:0 0 .35rem;gap:.5rem}.list-export-heading{display:flex;align-items:center;justify-content:space-between;gap:1rem}.list-export-heading .list-export-button{margin-left:auto}.list-export-count{display:flex;align-items:center;justify-content:space-between;gap:.6rem}.list-export-button{display:inline-flex!important;align-items:center;justify-content:center;flex:none;width:32px;min-width:32px;height:32px;padding:6px!important;border:1px solid currentColor!important;border-radius:6px!important;background:transparent!important;color:inherit!important;opacity:.78;cursor:pointer;vertical-align:middle;line-height:1}.list-export-button:hover{opacity:1;background:color-mix(in srgb,currentColor 8%,transparent)!important}.list-export-button:focus-visible{outline:2px solid currentColor;outline-offset:3px}.list-export-button:disabled{opacity:.3;cursor:default}.list-export-button svg{width:18px;height:18px;display:block}.list-export-status{position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%)}`;
 document.head.append(style);
 let scheduled=false;const attached=new Map();
 const scan=()=>{
  scheduled=false;
  const title=cleanText(app.querySelector('h1'))||'Pipeline';
  const targets=[...app.querySelectorAll('table')].filter(t=>t.tHead).map(el=>({el,read:()=>tableData(el)}));
  const cards=[['#dsl-grid:has(.dsl-card)','dsl'],['#pro-candidates:has(.pro-card)','pro'],['#pro-watchlist:has(.pro-card)','pro'],['.door-deck','door'],['.door-roster-depth','depth'],['.grid:has(> a.card)','organizations']];
  for(const [selector,kind]of cards)for(const el of app.querySelectorAll(selector))targets.push({el,kind,read:()=>cardData(el,kind)});
  const active=new Set(targets.map(t=>t.el));
  for(const [el,button]of attached)if(!active.has(el)){const tools=button.closest('.list-export-tools');if(tools)tools.remove();else button.remove();attached.delete(el);el._excelButton=null;}
  for(const target of targets){
   const {el,read,kind}=target;
   if(el._excelButton?.isConnected){el._excelButton.disabled=!read().rows.length;continue;}
   const label=kind?(kind==='pro'?cleanText(el.querySelector(':scope > h2')):kind==='depth'?'Roster depth':kind==='organizations'?'Organization directory':title):cleanText(el.querySelector('caption'))||el.closest('[aria-label]')?.getAttribute('aria-label')||title;
   const button=document.createElement('button');button.type='button';button.className='list-export-button';button.title='Download this list as Excel';button.setAttribute('aria-label',`Download ${label} as Excel`);
   button.innerHTML='<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4"/></svg>';
   button.disabled=!read().rows.length;
   button.onclick=()=>{try{download(read(),label===title?title:`${title} - ${label}`);}catch(error){console.error('Excel export failed',error);button.title='Download failed — please try again';}};
   // Counts already sit beside the filters; reuse their line when available.
   const countId=kind==='dsl'?'dsl-count':kind==='door'?'door-count':el.querySelector('#oct-rows')?'oct-count':el.querySelector('#am-rows')?'am-count':el.querySelector('#afl-rows')?'afl-count':el.querySelector('#cps-rows')?'cps-count':el.querySelector('#cpi-rows')?'cpi-count':el.querySelector('#roster-rows')?'roster-count':null;
   const count=countId&&app.querySelector('#'+countId);
   const boardHeading=kind==='pro'?el.querySelector(':scope > h2'):null;
   if(boardHeading){boardHeading.classList.add('list-export-heading');boardHeading.append(button);}else if(count){count.classList.add('list-export-count');count.append(button);}else{
    const tools=document.createElement('div');tools.className='list-export-tools';tools.append(button);
    const anchor=el.matches('table')?(el.closest('.tablewrap,.dsl-table-scroll')||el):el;
    anchor.before(tools);
   }
   el._excelButton=button;attached.set(el,button);
  }
 };
 const observer=new MutationObserver(()=>{if(!scheduled){scheduled=true;queueMicrotask(scan);}});
 observer.observe(app,{childList:true,subtree:true});scan();
}
if(typeof document!=='undefined'){const app=document.querySelector('#app');if(app)activateListExports(app);}
