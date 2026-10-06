import {mkdir,cp,rm} from 'node:fs/promises';
await rm('dist',{recursive:true,force:true});await mkdir('dist');
for(const file of ['index.html','app.js','styles.css','data'])await cp(file,`dist/${file}`,{recursive:true});
console.log('Static publication built in dist/');
