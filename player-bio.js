// Display ages follow verified DOB; publication/model age inputs stay dated.
export function currentAge(p, asOf=new Date().toISOString().slice(0,10), precision=1){
 const dob=p?.birthDate??p?.bio?.birthDate??p?.identity?.birthDate;
 if(!/^\d{4}-\d{2}-\d{2}$/.test(dob??'')||!/^\d{4}-\d{2}-\d{2}$/.test(asOf??''))return '—';
 const born=new Date(dob+'T00:00:00Z'),now=new Date(asOf+'T00:00:00Z');
 if(!Number.isFinite(born.getTime())||!Number.isFinite(now.getTime())||now<born)return '—';
 if(precision===0)return String(now.getUTCFullYear()-born.getUTCFullYear()-(asOf.slice(5)<dob.slice(5)?1:0));
 return ((now-born)/(365.2425*86400000)).toFixed(precision);
}
