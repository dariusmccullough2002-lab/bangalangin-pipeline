import {cp,mkdir,rm} from 'node:fs/promises';
import {dirname,join} from 'node:path';
import {publicAssets} from './public-assets.js';
const output=process.argv[2]??'dist';
await rm(output,{recursive:true,force:true});await mkdir(output,{recursive:true});
for(const file of publicAssets){const destination=join(output,file);await mkdir(dirname(destination),{recursive:true});await cp(file,destination);}
console.log('Static publication built from the deployment allowlist.');
