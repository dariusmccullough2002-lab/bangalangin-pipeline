"""Optional cached identity/birth-date download; no present-day fields used in features."""
import json,urllib.request
from pathlib import Path
p=Path(__file__).resolve().parent
ids=sorted(set(x['mlbamId'] for x in json.load(open(p/'results/cohort.json'))))
for i,start in enumerate(range(0,len(ids),100)):
 f=p/'raw'/f'bios-{i}.json'
 if not f.exists():f.write_bytes(urllib.request.urlopen('https://statsapi.mlb.com/api/v1/people?personIds='+','.join(map(str,ids[start:start+100])),timeout=40).read())
