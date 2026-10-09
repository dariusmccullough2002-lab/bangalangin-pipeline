"""Rebuild role sensitivities after opportunity guard without repeating historical training."""
import sys
from pathlib import Path
main=Path(__file__).resolve().with_name(sys.argv[3]);s=main.read_text();env={'__file__':str(main),'__name__':'role_current_rebuild'}
exec(compile(s.split('cases=[];manifest=[]')[0],str(main),'exec'),env)
name='Quality_Aware_Cases.json.gz' if main.name.startswith('quality') else 'Role_Aware_Cases.json.gz'
env['cases']=env['json'].loads(env['gzip'].decompress((main.parent/name).read_bytes()))
exec(compile(s[s.index('# Current diagnostic comparisons'):],str(main),'exec'),env)
