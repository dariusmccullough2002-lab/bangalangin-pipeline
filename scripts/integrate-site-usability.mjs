import fs from 'node:fs';
export function integrateSiteUsability(output){
 const path=`${output}/trade-analyzer-beta/index.html`;let html=fs.readFileSync(path,'utf8');
 const main=fs.readFileSync(`${output}/index.html`,'utf8');const nav=main.split('<nav aria-label="Main">')[1].split('</nav>')[0].replaceAll('href="#','href="/#');
 html=html.replace(/<nav aria-label="Main">.*?<\/nav>/,'<nav aria-label="Main">'+nav+'</nav>').replace('Download comparison</button>','Download Excel comparison</button>');
 const match=html.match(/script\.textContent\s*=\s*("(?:[^"\\]|\\.)*")/);if(!match)throw Error('Workbook script target missing');let code=JSON.parse(match[1]);
 const old="const url=URL.createObjectURL(new Blob([JSON.stringify(out,null,2)],{type:'application/json'})),link=el('a');link.href=url;link.download='BangaLangin_Experimental_Trade.json';link.click();URL.revokeObjectURL(url)";
 if(!code.includes(old))throw Error('Workbook download hook missing');code=code.replace(old,'window.PipelineTradeWorkbook.download(out)');html=html.replace(match[1],JSON.stringify(code));
 const init='DATA=JSON.parse(await new Response(stream).text());';if(!html.includes(init))throw Error('Workbook bootstrap missing');html=html.replace(init,init+"window.PipelineTradeWorkbook=await import('/trade-analyzer-beta/trade-workbook.js');");fs.writeFileSync(path,html);
}
