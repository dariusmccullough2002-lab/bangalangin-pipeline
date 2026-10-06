// Reviewed MLBAM identities connect DSL entries to existing profiles.
export function resolveDslProfile(player,edition,organizations=[]){
 const matches=(edition?.rankings??[]).filter(p=>Number(p.mlbamId)===Number(player.mlbamId));
 const current=matches.length===1?matches[0]:null;
 const organizationId=current?.organizationId??player.fantasyOrganizationId;
 const organization=organizations.find(o=>o.id===organizationId);
 const owner=organization?.currentName??organization?.name??current?.organization??player.fantasyOrganizationName;
 return {current,route:current?`#october-player/${current.playerId}`:`#dsl-player/${player.id}`,owner:owner??'BangaLangin free agent',organizationId};
}
