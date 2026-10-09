const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export function etaInfo(player,records){
 const evidence=records[player.fantraxId];
 if(!evidence)return {value:'TBD',description:'Unavailable: no traceable published ETA in the saved evidence. No new model estimate assigned.'};
 return {value:String(evidence.value),description:`Published ${evidence.source} estimate · ${evidence.date?'dated '+evidence.date:'publication date unavailable'} · snapshot ${evidence.retrievedDate}. Arrival is uncertain; this field does not change rankings or valuations.`,url:evidence.url};
}
export function etaCell(player,records){const info=etaInfo(player,records);return `<span class="eta-value" title="${esc(info.description)}" tabindex="0" aria-label="MLB ETA ${esc(info.value)}. ${esc(info.description)}">${esc(info.value)}</span>`;}
