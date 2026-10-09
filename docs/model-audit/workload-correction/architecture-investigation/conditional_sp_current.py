"""Current-only continuation; never repeat historical fits."""
import sys,json
from pathlib import Path
main=Path(__file__).resolve().with_name('conditional_sp_followup.py');s=main.read_text()
env={'__file__':str(main),'__name__':'current_helpers'}
exec(compile(s.split('dev={m:[] for m in METHODS};manifest=[]')[0],str(main),'exec'),env)
env['chosen']=json.loads((main.parent/'Conditional_SP_Validation.json').read_text())['selected_by_development']
exec(compile(s[s.index('# General current sensitivities;'):],str(main),'exec'),env)
