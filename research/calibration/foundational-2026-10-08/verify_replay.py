"""Verify selected inputs without refitting or re-evaluating models."""
import shutil,pathlib,zipfile,json,gzip,subprocess,sys,tempfile
P=pathlib.Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='foundational-replay-',dir=P.parent) as tmp:
 t=pathlib.Path(tmp);(t/'results').mkdir()
 for n in ['parse_rankings.py','identities.py','historical_features.py']:shutil.copy2(P/n,t/n)
 with zipfile.ZipFile(P/'replay-inputs.zip') as z:z.extractall(t)
 for n in ['parse_rankings.py','identities.py']:subprocess.run([sys.executable,str(t/n)],check=True,capture_output=True)
 a=json.load(open(P/'results/resolved-rankings.json'));b=json.load(open(t/'results/resolved-rankings.json'));assert a==b
 sys.path.insert(0,str(P));import historical_features as h
 full,audit=h.minor_features();h.P=t;filtered,audit2=h.minor_features();assert audit==audit2
 ids={r['mlbamId'] for r in a}|{r['mlbamId'] for r in json.load(open(h.BASE/'results/cohort.json'))}
 assert {k:v for k,v in full.items() if k[1] in ids}==filtered
 original=json.load(gzip.open(P/'raw/game-inputs.json.gz','rt'));selected=json.load(gzip.open(t/'raw/game-inputs.json.gz','rt'))
 assert selected['annual_QA3']==original['annual_QA3']
 assert selected['weekly']=={w:v for w,v in original['weekly'].items() if w.startswith(('2018','2024'))}
 assert selected['positions']=={y:v for y,v in original['positions'].items() if y in ['2017','2023']}
 (P/'results/replay-integrity.json').write_text(json.dumps({'status':'PASS','resolved_rankings_match':len(a),'selected_minor_feature_rows_match':len(filtered),'full_source_audits_match':True,'weekly_and_annual_game_inputs_match':True,'models_refitted_for_this_check':False},indent=2));print('PASS selected replay inputs reproduce identities and feature aggregation; no model refit')
