import {cp,mkdir,rm} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {publicAssets} from './public-assets.js';
const output=process.argv[2]??'dist';
await rm(output,{recursive:true,force:true});await mkdir(output,{recursive:true});
for(const file of publicAssets){const destination=join(output,file);await mkdir(dirname(destination),{recursive:true});await cp(file,destination);}
console.log('Static publication built from the deployment allowlist.');
// Responsive review surface exists only in protected Vercel previews.
if(process.env.VERCEL_ENV==='preview'){
 const {writeFile}=await import('node:fs/promises');
 await writeFile(join(output,'ui-review.html'),`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><title>V2.3D responsive review</title><style>body{font:14px Arial;margin:12px}label{display:inline-block;margin:0 16px 12px 0}iframe{display:block;border:1px solid #aaa;height:1100px}</style><label>Viewport width <select id="width"><option value="390">Mobile 390</option><option value="320">Mobile 320</option><option value="768">Tablet 768</option><option value="1366">Desktop 1366</option></select></label><label>Page <select id="page"><option value="/trade-analyzer-beta/">Trade Analyzer</option><option value="/">Home</option><option value="/#october">Rankings</option><option value="/#draft">Draft</option><option value="/#october-player/fantrax-0662o">Player profile</option></select></label><iframe id="review" title="Responsive page review" width="390" src="/trade-analyzer-beta/"></iframe><script>document.querySelector('#width').onchange=e=>document.querySelector('#review').width=e.target.value;document.querySelector('#page').onchange=e=>document.querySelector('#review').src=e.target.value;</script>`);
}
