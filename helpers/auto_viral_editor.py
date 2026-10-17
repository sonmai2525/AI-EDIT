"""V9 Auto Viral Editor: one-command V2→V6 orchestration + QC/re-render.

This automates technical/creative heuristics; it does not guarantee virality.
Usage: python helpers/auto_viral_editor.py input.mp4 -o final.mp4 --target 20 --aspect 9:16
"""
from __future__ import annotations
import argparse,json,shutil,subprocess,sys
from pathlib import Path
from viral_qc import evaluate,repair

def run(cmd):
    print('>',' '.join(map(str,cmd))); subprocess.run(list(map(str,cmd)),check=True)

def main():
    ap=argparse.ArgumentParser(description='One-command short-form auto editor')
    ap.add_argument('video',type=Path); ap.add_argument('-o','--output',type=Path,required=True); ap.add_argument('--target',type=float,default=20); ap.add_argument('--aspect',choices=['9:16','16:9','1:1','source'],default='9:16')
    ap.add_argument('--workdir',type=Path); ap.add_argument('--caption-style',default='visual_dynamic'); ap.add_argument('--preview',action='store_true'); ap.add_argument('--no-subtitles',action='store_true'); ap.add_argument('--no-auto-repair',action='store_true')
    a=ap.parse_args(); video=a.video.resolve(); output=a.output.resolve(); root=Path(__file__).resolve().parent; work=(a.workdir or output.parent/(output.stem+'_v7')).resolve(); work.mkdir(parents=True,exist_ok=True)
    analysis=work/'analysis.json'; edl=work/'edl.json'; visual=work/'director.v5.json'; creative=work/'creative.v6.json'; semantic=work/'semantic.v8.json'; story=work/'story.v9.json'; story10=work/'story.v10.json'; first=work/'first_pass.mp4'; qc1=work/'qc.first.json'
    run([sys.executable,root/'analyze_short.py',video,'-o',analysis])
    run([sys.executable,root/'make_short_edl.py',analysis,'-o',edl,'--target',a.target,'--aspect',a.aspect])
    run([sys.executable,root/'ai_director.py',video,analysis,'-o',visual,'--edl',edl,'--apply'])
    run([sys.executable,root/'creative_director.py',analysis,'-o',creative,'--director',visual,'--edl',edl,'--apply','--target',a.target])
    run([sys.executable,root/'semantic_vision_director.py',video,analysis,'-o',semantic,'--edl',edl,'--apply'])
    run([sys.executable,root/'story_reframe_v9.py',video,analysis,'-o',story,'--semantic',semantic,'--edl',edl,'--apply'])
    run([sys.executable,root/'multimodal_story_v10.py',video,analysis,story,'-o',story10,'--semantic',semantic,'--assets-dir',work/'v10_storyboards','--edl',edl,'--apply','--target',a.target])
    cmd=[sys.executable,root/'render.py',edl,'-o',first]
    if a.preview: cmd.append('--preview')
    if a.no_subtitles: cmd.append('--no-subtitles')
    else: cmd += ['--build-subtitles','--caption-style',a.caption_style]
    run(cmd)
    ed=json.loads(edl.read_text()); rep=evaluate(first,ed); qc1.write_text(json.dumps(rep,ensure_ascii=False,indent=2)); print(f'V7 QC first pass: {rep["score"]}/100')
    final_src=first
    if not rep['pass'] and not a.no_auto_repair:
        repaired=work/'edl.repaired.json'; repaired.write_text(json.dumps(repair(ed,rep),ensure_ascii=False,indent=2))
        second=work/'second_pass.mp4'; cmd=[sys.executable,root/'render.py',repaired,'-o',second]
        if a.preview: cmd.append('--preview')
        if a.no_subtitles: cmd.append('--no-subtitles')
        else: cmd += ['--build-subtitles','--caption-style',a.caption_style]
        run(cmd); rep2=evaluate(second,json.loads(repaired.read_text())); (work/'qc.second.json').write_text(json.dumps(rep2,ensure_ascii=False,indent=2)); print(f'V7 QC repaired pass: {rep2["score"]}/100'); final_src=second if rep2['score']>=rep['score'] else first
    output.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(final_src,output)
    manifest={'version':10,'input':str(video),'output':str(output),'workdir':str(work),'target_seconds':a.target,'aspect':a.aspect,'auto_repair':not a.no_auto_repair,'selected_pass':final_src.name}
    (work/'v7.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)); print(f'\ndone V10 → {output}')
if __name__=='__main__': main()
