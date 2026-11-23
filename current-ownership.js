import {scoreFarms} from './current-farm-model.js';
let pending;
export async function loadCurrentOwnership(){pending??=fetch('/data/ownership-snapshots/current.json').then(r=>{if(!r.ok)throw Error('Current ownership unavailable');return r.json();}).catch(e=>{pending=null;throw e;});return pending;}
const clean=id=>String(id??'').replaceAll('*','').replace(/^fantrax-/,'');
export function ownershipIndex(snapshot){return new Map(snapshot.teams.flatMap(t=>t.players.map(p=>[p.fantraxId,{...p,organization:t.name,organizationId:t.organizationId}])));}
export function applyCurrentEdition(edition,snapshot,organizations){
 const out=structuredClone(edition),owners=ownershipIndex(snapshot);
 for(const key of ['rankings','excluded','reviewQueue'])for(const p of out[key]??[]){const current=owners.get(clean(p.fantraxId??p.playerId));p.editionOrganization=p.organization;p.editionOrganizationId=p.organizationId;p.organization=current?.organization??'Free agent';p.organizationId=current?.organizationId??null;p.ownershipAsOf=snapshot.capturedDate;if(current)p.status=current.status;}
 for(const org of organizations){out.rankings.filter(p=>p.organizationId===org.id).sort((a,b)=>a.leagueRank-b.leagueRank).forEach((p,i)=>{p.organizationRank=i+1;});}
 out.farms=scoreFarms(out.rankings,organizations);out.ownershipSnapshotId=snapshot.id;out.ownershipAsOf=snapshot.capturedDate;return out;
}
export async function currentEdition(edition,organizations){return applyCurrentEdition(edition,await loadCurrentOwnership(),organizations);}
export function applyAnalyzerOwnership(data,snapshot){
 const owners=ownershipIndex(snapshot),canonical=name=>name==='Island'?'EpSkenes Island':name;let changed=0;
 for(const a of data.assets){if(a.audit?.kind==='pick'||a.group==='Picks'||a.group==='Hypothetical picks')continue;const p=owners.get(clean(a.id));const owner=p?canonical(p.organization):'Free agent';if(a.owner!==owner)changed++;a.owner=owner;a.ownerAsOf=snapshot.capturedDate;a.rosterStatus=p?.status??null;a.rosterPosition=null;}
 for(const t of data.teams){const roster=data.assets.filter(a=>a.audit?.kind!=='pick'&&a.owner===t.name);t.players=roster.length;t.modeledPlayers=roster.filter(a=>Number.isFinite(a.values?.neutral?.display)).length;t.asOf=snapshot.capturedDate;t.complete='Reconciled to supplied league-wide player export';t.warning='Roster status observed; exact active-slot positions not supplied.';}
 data.playerOwnershipAsOf=snapshot.capturedDate;data.asOf=snapshot.capturedDate;data.ownershipRefresh={asOf:snapshot.capturedDate,changed,players:snapshot.teams.reduce((n,t)=>n+t.players.length,0),pickPolicy:'Only the explicitly supplied Arroyo / Sandlot 2027 Round 2 transaction is applied; other pick ownership remains dated.'};
 // Exact supplied pick transfer. Do not change original franchise, slot or valuation.
 for(const a of data.assets)if(a.audit?.kind==='pick'&&a.originalOwner==='The Sandlot Sluggers'&&String(a.year??a.audit?.year)==='2027'&&Number(a.round??a.audit?.round)===2){a.owner='Shea Stadiums';a.ownerAsOf='2026-10-01';a.ownershipStatus='Verified supplied October 1 trade; audited November 23';}
 for(const t of data.teams)t.picks=data.assets.filter(a=>a.group==='Picks'&&a.owner===t.name).length;
 return data;
}
export function applyLegacyOwnership(data,snapshot){const owners=ownershipIndex(snapshot);for(const p of data.players){const current=owners.get(clean(p.id));p.owner=current?.organization==='Island'?'EpSkenes Island':current?.organization??'Free agent';p.ownerAsOf=snapshot.capturedDate;}data.ownershipAsOf=snapshot.capturedDate;return data;}
