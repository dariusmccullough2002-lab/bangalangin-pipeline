// Match the compact class displayed on profiles, without asserting eligibility.
export function internationalClass(p){
 if(p.classYear===2026)return '2026';
 if(p.classYear===2027||/^2027(?:\s|$)/.test(p.classLabel??''))return '2027';
 return 'other';
}
export const matchesInternationalClass=(p,value='')=>!value||internationalClass(p)===value;
