import {renderDevers} from './devers.js';
let dataPromise;
export async function showPowerTranslation(app){
 if(!document.querySelector('#ptl-css')){const link=document.createElement('link');link.id='ptl-css';link.rel='stylesheet';link.href='power-translation.css';document.head.append(link);}
 app.innerHTML='<p role="status">Loading the Power Translation Lab…</p>';
 try{
  dataPromise??=Promise.all(['devers-research','devers-records'].map(async name=>{const response=await fetch(`data/research/${name}.json.gz`);if(!response.ok)throw Error('Player data unavailable');return new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json();}));
  const [model,records]=await dataPromise;if(location.hash.split('/')[0]!=='#power-translation-lab')return;
  app.innerHTML='<article class="ptl"><header class="ptl-head"><h1>Power Translation Lab</h1><p>Compare a hitter’s impact with his Chase + Whiff risk.</p></header><div id="ptl-devers"></div></article>';
  renderDevers(app.querySelector('#ptl-devers'),model,records);
 }catch(error){dataPromise=null;if(location.hash.startsWith('#power-translation-lab'))app.innerHTML='<h1>Power Translation Lab</h1><p>Player data could not load. Refresh to try again.</p>';console.error(error);}
}
