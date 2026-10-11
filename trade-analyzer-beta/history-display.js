// Display-only mapping. Never substitutes a different statistic for missing evidence.
const number = value => value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value)) ? Number(value).toFixed(1) : 'unavailable';
const value = (row, key, sourceKey) => row.stat?.[key] ?? (sourceKey ? row.skills?.[sourceKey] : undefined);
export function historyTables(seasons) {
 const pitching = seasons.filter(row => row.role !== 'H');
 const hitting = seasons.filter(row => row.role === 'H');
 const tables = [];
 if (hitting.length) tables.push([['Year','Level','Role','PA','HR','R','RBI','SB'], ...hitting.map(row => [row.year, row.level ?? 'MLB', row.role, ...['PA','HR','R','RBI','SB'].map(key => number(value(row,key)))])]);
 if (pitching.length) tables.push([['Year','Level','Role','GP','GS','IP','K','HR allowed','ER','QA3','SV','HLD'], ...pitching.map(row => [row.year, row.level ?? 'MLB', row.role, number(value(row,'GP','gamesPlayed')), number(value(row,'GS','gamesStarted')), number(value(row,'IP')), number(value(row,'K','strikeOuts')), number(value(row,'HR','homeRuns')), ...['ER','QA3','SV','HLD'].map(key => number(value(row,key)))])]);
 return tables;
}
