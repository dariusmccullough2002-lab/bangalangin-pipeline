const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
// Team-specific road/alternate concepts; player numbers come from dated affiliate records.
const teams={
 BOS:[111,'RED SOX','#d4d6d8','#bd3039','#0c2340','BOSTON'],
 TEX:[140,'RANGERS','#003278','#ffffff','#c0111f','TEXAS'],
 MIL:[158,'BREWERS','#12284b','#ffc52f','#ffffff','Brewers'],
 SEA:[136,'MARINERS','#005c5c','#ffffff','#0c2c56','MARINERS'],
 TB:[139,'RAYS','#8fbce6','#092c5c','#ffffff','Rays'],
 CWS:[145,'WHITE SOX','#f5f4ed','#111111','#c4ced4','Sox','stripe'],
 ATH:[133,'ATHLETICS','#003831','#efb21e','#ffffff','Athletics'],
 COL:[115,'ROCKIES','#333366','#ffffff','#c4ced4','COLORADO'],
 CLE:[114,'GUARDIANS','#0c2340','#ffffff','#e31937','CLEVELAND'],
 STL:[138,'CARDINALS','#f7f1df','#c41e3a','#0c2340','Cardinals'],
 CHC:[112,'CUBS','#0e3386','#ffffff','#cc3433','CHICAGO'],
 CIN:[113,'REDS','#c6011f','#ffffff','#111111','CINCINNATI'],
 BAL:[110,'ORIOLES','#df4601','#111111','#ffffff','Orioles'],
 NYY:[147,'YANKEES','#c4ced3','#0c2340','#ffffff','NEW YORK'],
 NYM:[121,'METS','#f3f3ee','#002d72','#ff5910','Mets','stripe'],
 PHI:[143,'PHILLIES','#f4eee5','#e81828','#ffffff','Phillies','stripe'],
 LAD:[119,'DODGERS','#f5f5f1','#005a9c','#ffffff','Dodgers'],
 LAA:[108,'ANGELS','#ba0021','#ffffff','#003263','ANGELS'],
 ARI:[109,'D-BACKS','#a71930','#ffffff','#30ced8','D-BACKS'],
 DET:[116,'TIGERS','#c4ced4','#0c2340','#fa4616','DETROIT'],
 HOU:[117,'ASTROS','#002d62','#ffffff','#eb6e1f','ASTROS'],
 KC:[118,'ROYALS','#004687','#ffffff','#bd9b60','Royals'],
 WSH:[120,'NATIONALS','#ab0003','#ffffff','#14225a','WASHINGTON'],
 PIT:[134,'PIRATES','#27251f','#fdb827','#ffffff','PIRATES'],
 SD:[135,'PADRES','#f4ead5','#2f241d','#ffc425','SAN DIEGO','stripe'],
 SF:[137,'GIANTS','#f5ead7','#111111','#fd5a1e','GIANTS'],
 TOR:[141,'BLUE JAYS','#134a8e','#ffffff','#e8291c','BLUE JAYS'],
 MIN:[142,'TWINS','#002b5c','#ffffff','#d31145','Twins'],
 ATL:[144,'BRAVES','#f5f0e8','#ce1141','#13274f','Braves'],
 MIA:[146,'MARLINS','#00a3e0','#111111','#ffffff','MIAMI']
};
teams.CHW=teams.CWS;teams.OAK=teams.ATH;
const jerseyPath='M57 23 35 30 9 61 29 82 44 69v112q46 13 92 0V69l15 13 20-21-26-31-22-7q-33 18-66 0Z';
export function jerseySvg(p){
 const [id,label,body,ink,outline,wordmark,stripe]=teams[p.mlbOrg]??[null,p.mlbOrg??'PROSPECT','#e8e4d8','#153e38','#d5bf83','PIPELINE'];
 const surname=(p.surname??p.name?.split(' ').slice(-1)[0]??'').toUpperCase();
 const number=/^\d{1,3}$/.test(String(p.number??''))?String(p.number):'';
 // Both faces use the same silhouette. A front view reveals the club wordmark and button placket on hover/focus.
 const shirt=`<path d="${jerseyPath}" fill="${body}" stroke="${outline}" stroke-width="1.7"/>${stripe?Array.from({length:11},(_,i)=>`<path d="M${48+i*8} 44v135" stroke="${ink}" stroke-opacity=".28" stroke-width=".8"/>`).join(''):''}<path d="M57 23q33 28 66 0l-5-6q-28 17-56 0Z" fill="${outline}"/><path d="m14 60 18 17m116 0 18-17" stroke="${outline}" stroke-width="4"/><path d="m16 62 14 14m120 0 14-14" stroke="${ink}" stroke-width="1.2"/><path d="M49 80v94m82-94v94M53 179q37 8 74 0" stroke="${outline}" stroke-opacity=".24" stroke-width="1"/><path d="m51 35-8 23m84-23 9 23" stroke="#fff" stroke-opacity=".2" stroke-width="2"/>`;
 return `<svg class="club-jersey" aria-hidden="true" viewBox="0 0 180 205"><g class="jersey-back">${shirt}<rect x="85" y="34" width="10" height="5" rx="1" fill="${outline}" opacity=".8"/><text x="90" y="65" text-anchor="middle" fill="${ink}" stroke="${outline}" stroke-width=".65" paint-order="stroke" font-family="Arial,sans-serif" font-size="${surname.length>11?11:14}" font-weight="800" letter-spacing="1.1">${esc(surname)}</text><text x="90" y="155" text-anchor="middle" fill="${ink}" stroke="${outline}" stroke-width="3.5" paint-order="stroke" stroke-linejoin="round" font-family="'Barlow Condensed',Impact,sans-serif" font-weight="700" font-size="94">${number}</text></g><g class="jersey-front">${shirt}<path d="M82 40v142m12-142v142" stroke="${p.mlbOrg==='BOS'?'#bd3039':outline}" stroke-width="1.4"/>${[55,77,99,121,143,165].map(y=>`<circle cx="88" cy="${y}" r="1.4" fill="${outline}"/>`).join('')}<text x="90" y="89" text-anchor="middle" textLength="${wordmark.length>8?106:88}" lengthAdjust="spacingAndGlyphs" fill="${ink}" stroke="${outline}" stroke-width="1" paint-order="stroke" font-family="${/[a-z]/.test(wordmark)?'Georgia,serif':'Arial,sans-serif'}" font-style="${/[a-z]/.test(wordmark)?'italic':'normal'}" font-size="25" font-weight="900">${wordmark}</text><text x="113" y="139" text-anchor="middle" fill="${ink}" stroke="${outline}" stroke-width="1.5" paint-order="stroke" font-family="'Barlow Condensed',Impact,sans-serif" font-size="35" font-weight="700">${number}</text></g></svg>`;
}
export function jerseyLink(p){
 const label=teams[p.mlbOrg]?.[1]??p.mlbOrg;
 return `<a class="highlight-jersey" href="${esc(p.route)}" aria-label="View ${esc(p.name)}’s profile" title="${esc(p.name)} · ${esc(label)} organization jersey concept${p.number?` · ${esc(p.numberTeam??'affiliate')} number ${esc(p.number)}`:''}">${jerseySvg(p)}<strong>${esc(p.name)}</strong><span>${esc(p.caption??label)}</span></a>`;
}
