"""V14 Auto Viral Editor — retention-first, fast/smart/max.

Fast-quality preserves a good source edit and spends compute where viewers notice it:
scene/beat analysis, concise EDL, visual text, light creative motion, render and one QC.
Full-ai keeps the V5→V10 semantic/story pipeline.
"""
from __future__ import annotations
import argparse,json,shutil,subprocess,sys,time
from pathlib import Path
from viral_qc import evaluate,repair
from watermark_cleanup import clean as clean_watermark, parse_box

def run(cmd):
    print('>',' '.join(map(str,cmd))); subprocess.run(list(map(str,cmd)),check=True)

def main():
    ap=argparse.ArgumentParser(description='V13.1 one-command retention-first short-form editor')
    ap.add_argument('video',type=Path); ap.add_argument('-o','--output',type=Path,required=True)
    ap.add_argument('--target',type=float,default=20); ap.add_argument('--aspect',choices=['9:16','16:9','1:1','source'],default='9:16')
    ap.add_argument('--mode',choices=['fast','smart','max','fast-quality','full-ai'],default='smart')
    ap.add_argument('--workdir',type=Path); ap.add_argument('--caption-style',default='visual_dynamic'); ap.add_argument('--preview',action='store_true'); ap.add_argument('--no-subtitles',action='store_true'); ap.add_argument('--no-auto-repair',action='store_true')
    ap.add_argument('--watermark-box',help='optional x,y,w,h pixels; edge marks are cropped cleanly, never blurred'); ap.add_argument('--max-watermark-crop',type=float,default=.12)
    a=ap.parse_args(); started=time.time();
    if a.mode=='fast-quality': a.mode='fast'
    if a.mode=='full-ai': a.mode='max'
    original=a.video.resolve(); output=a.output.resolve(); root=Path(__file__).resolve().parent; work=(a.workdir or output.parent/(output.stem+'_v131')).resolve(); work.mkdir(parents=True,exist_ok=True)
    video=original; wm_report=None
    if a.watermark_box:
        cleaned=work/'source.clean.mp4'; wm_report=clean_watermark(original,cleaned,parse_box(a.watermark_box),'auto',a.max_watermark_crop); (work/'watermark.json').write_text(json.dumps(wm_report,ensure_ascii=False,indent=2)); video=cleaned if wm_report.get('applied') else original
        print('watermark:',wm_report.get('method'),wm_report.get('reason',''))
    analysis=work/'analysis.json'; edl=work/'edl.json'; first=work/'first_pass.mp4'; qc1=work/'qc.first.json'
    run([sys.executable,root/'analyze_short.py',video,'-o',analysis])
    run([sys.executable,root/'make_short_edl.py',analysis,'-o',edl,'--target',a.target,'--aspect',a.aspect])
    if a.mode=='fast':
        # One visual pass + one light creative pass. Skip V8/V9/V10 storyboard generation.
        visual=work/'director.v5.json'; creative=work/'creative.v6.json'
        run([sys.executable,root/'ai_director.py',video,analysis,'-o',visual,'--edl',edl,'--apply'])
        run([sys.executable,root/'creative_director.py',analysis,'-o',creative,'--director',visual,'--edl',edl,'--apply','--target',a.target])
    else:
        visual=work/'director.v5.json'; creative=work/'creative.v6.json'; semantic=work/'semantic.v8.json'; story=work/'story.v9.json'
        run([sys.executable,root/'ai_director.py',video,analysis,'-o',visual,'--edl',edl,'--apply'])
        run([sys.executable,root/'creative_director.py',analysis,'-o',creative,'--director',visual,'--edl',edl,'--apply','--target',a.target])
        run([sys.executable,root/'semantic_vision_director.py',video,analysis,'-o',semantic,'--edl',edl,'--apply'])
        run([sys.executable,root/'story_reframe_v9.py',video,analysis,'-o',story,'--semantic',semantic,'--edl',edl,'--apply'])
        if a.mode=='max':
            story10=work/'story.v10.json'
            run([sys.executable,root/'multimodal_story_v10.py',video,analysis,story,'-o',story10,'--semantic',semantic,'--assets-dir',work/'v10_storyboards','--edl',edl,'--apply','--target',a.target])
    # V12: score multiple edit candidates from one analysis and render only the winner.
    viral12=work/'viral.v12.json'
    run([sys.executable,root/'viral_engine_v12.py',analysis,edl,'-o',viral12,'--target',a.target,'--apply'])
    story13=work/'story.v13.json'
    run([sys.executable,root/'story_intelligence_v13.py',video,analysis,edl,'-o',story13,'--target',a.target,'--apply'])
    finish131=work/'finish.v13.1.json'
    run([sys.executable,root/'story_intelligence_v131.py',video,edl,'-o',finish131,'--target',a.target,'--apply'])
    creative14=work/'creative.v14.json'
    run([sys.executable,root/'creative_director_v14.py',edl,'-o',creative14,'--target',a.target,'--apply'])
    voice14=work/'voice.v14.json'
    run([sys.executable,root/'voice_director_v14.py',edl,'-o',voice14])
    cmd=[sys.executable,root/'render.py',edl,'-o',first]
    if a.preview: cmd.append('--preview')
    if a.no_subtitles: cmd.append('--no-subtitles')
    else: cmd += ['--build-subtitles','--caption-style',a.caption_style]
    run(cmd)
    ed=json.loads(edl.read_text()); rep=evaluate(first,ed); qc1.write_text(json.dumps(rep,ensure_ascii=False,indent=2)); print(f'QC first pass: {rep["score"]}/100')
    final_src=first
    # Fast mode only pays for a second render when QC is genuinely poor (<76/error).
    repair_threshold=74 if a.mode=='fast' else (80 if a.mode=='smart' else 84)
    needs_repair=(rep['score']<repair_threshold or any(x.get('severity')=='error' for x in rep.get('issues',[])))
    if needs_repair and not a.no_auto_repair:
        repaired=work/'edl.repaired.json'; repaired.write_text(json.dumps(repair(ed,rep),ensure_ascii=False,indent=2)); second=work/'second_pass.mp4'; cmd=[sys.executable,root/'render.py',repaired,'-o',second]
        if a.preview: cmd.append('--preview')
        if a.no_subtitles: cmd.append('--no-subtitles')
        else: cmd += ['--build-subtitles','--caption-style',a.caption_style]
        run(cmd); rep2=evaluate(second,json.loads(repaired.read_text())); (work/'qc.second.json').write_text(json.dumps(rep2,ensure_ascii=False,indent=2)); final_src=second if rep2['score']>=rep['score'] else first
    output.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(final_src,output)
    manifest={'version':'14.0','mode':a.mode,'input':str(original),'effective_source':str(video),'output':str(output),'workdir':str(work),'target_seconds':a.target,'aspect':a.aspect,'selected_pass':final_src.name,'elapsed_seconds':round(time.time()-started,2),'watermark':wm_report,'viral_plan':str(viral12),'story_plan_v13':str(story13),'finish_plan_v131':str(finish131),'creative_plan_v14':str(creative14),'voice_plan_v14':str(voice14)}
    (work/'v13.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)); print(f'\ndone V14 {a.mode} → {output} | {manifest["elapsed_seconds"]}s')
if __name__=='__main__': main()
