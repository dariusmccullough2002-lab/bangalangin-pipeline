"""Rebuild current sensitivities without repeating completed historical tests."""
import json
from pathlib import Path
main=Path(__file__).resolve().with_name('opportunity_models.py');s=main.read_text();env={'__file__':str(main),'__name__':'current_rebuild'}
exec(compile(s.split('devscores={};test=[];selected={};training_manifest=[]')[0],str(main),'exec'),env)
env['selected']=json.loads((main.parent/'Opportunity_Validation.json').read_text())['selected_by_development']
exec(compile(s[s.index('# Current impact, first-year only;'):],str(main),'exec'),env)
