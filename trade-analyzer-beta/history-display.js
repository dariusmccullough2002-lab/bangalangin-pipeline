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
export function renderHistory(seasons, document) {
 return historyTables(seasons).map(([headers,...rows]) => {
  const wrapper=document.createElement('div');wrapper.className='history-table-scroll';wrapper.tabIndex=0;wrapper.setAttribute('role','region');wrapper.setAttribute('aria-label','Season statistics; scroll horizontally for all columns');
  const table=document.createElement('table');const head=document.createElement('thead');const header=document.createElement('tr');
  for(const value of headers){const cell=document.createElement('th');cell.scope='col';cell.textContent=value;header.append(cell);}head.append(header);table.append(head);
  const body=document.createElement('tbody');for(const values of rows){const row=document.createElement('tr');for(const value of values){const cell=document.createElement('td');cell.textContent=value;row.append(cell);}body.append(row);}table.append(body);wrapper.append(table);return wrapper;
 });
}
