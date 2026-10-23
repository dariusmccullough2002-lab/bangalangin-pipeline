import fs from 'node:fs';
import {gzipSync,gunzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {applySharedForecast} from '../trade-analyzer-beta/shared-forecast.js';
const ROOT=new URL('../',import.meta.url);
export function sharedForecastInputs(){
 const paths=['docs/research-layer-20261013/Evidence.json','docs/value-audit-20261012/inputs/model-evidence.json'];
 const raw=paths.map(path=>fs.readFileSync(new URL(path,ROOT)));
 return {evidence:JSON.parse(raw[0]),model:JSON.parse(raw[1]),hashes:Object.fromEntries(paths.map((p,i)=>[p,createHash('sha256').update(raw[i]).digest('hex')]))};
}
export function unpackCatalog(html){const m=html.match(/const packed='([^']+)'/);if(!m)throw Error('Packed forecast catalog unavailable');return JSON.parse(gunzipSync(Buffer.from(m[1],'base64')));}
export function integrateSharedForecast(path){
 const html=fs.readFileSync(path,'utf8'),data=unpackCatalog(html),{evidence,model,hashes}=sharedForecastInputs();
 const release=applySharedForecast(data,evidence,model);release.inputHashes=hashes;
 const packed=gzipSync(JSON.stringify(data),{mtime:0}).toString('base64');
 let output=html.replace(/const packed='[^']+'/,()=>`const packed='${packed}'`);
 const match=output.match(/script\.textContent\s*=\s*("(?:[^"\\]|\\.)*")/);
 if(!match)throw Error('Shared forecast UI integration target unavailable');
 const code=JSON.parse(match[1]),old="(100*q.first_year_above_elite_utility_probability).toFixed(1)+'%'";
 if(!code.includes(old))throw Error('Shared forecast uncertainty display hook missing');
 output=output.replace(match[1],JSON.stringify(code.replace(old,"Number.isFinite(q.first_year_above_elite_utility_probability)?(100*q.first_year_above_elite_utility_probability).toFixed(1)+'%':'Unavailable after quality adjustment'")));
 fs.writeFileSync(path,output);
 return release;
}
