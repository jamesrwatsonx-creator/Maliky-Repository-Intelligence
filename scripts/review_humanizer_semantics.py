"""Record the LEAN SEMANTIC REVIEW of humanizer at its existing pinned commit.

The SKILL entity was already VERIFIED with two capabilities and is retained unchanged. The plugin
manifest and the package-check workflow are reviewed here; scripts/validate-package.py and
agents/openai.yaml are packaging details of this one skill and are not catalogued.
"""
from __future__ import annotations
from lean_review_lib import LeanReview

def main():
    review=LeanReview('jamesrwatsonx-creator/humanizer','e2e92e7b4b8229253ed5c8e81dc65463fdeddda5')
    skill=review.find('SKILL','humanizer')[0]
    review.out[skill['id']]=skill
    plugin=review.find('PLUGIN','humanizer')[0]
    review.finish(plugin,'Claude Code plugin manifest (humanizer 2.11.2, MIT) exposing the humanizer skill from the repository root.',[('prompt-guided-prose-style-revision','Prompt-guided prose style revision',[])],'USE DIRECTLY','operational:01','MODULE','YES',['Claude Code plugin support (the skill also works on its own)'],categories=['category:skills'])
    workflow=review.find('WORKFLOW','Check package')[0]
    review.finish(workflow,'GitHub Actions check: validates package files with scripts/validate-package.py, checks skill discovery with the skills CLI and validates the Claude marketplace with `claude plugin validate`.',[('ci-test-and-release-pipeline','CI test and release pipeline',[])],'REFERENCE ONLY','operational:14','COMPONENT','NO',['GitHub Actions','Node 22','Python 3.12'],categories=['category:ci-cd'])
    print(review.finalize(['category:skills'],[],'USE DIRECTLY','operational:01',{'SKILL':'Already VERIFIED; retained unchanged','PLUGIN':'Retained','WORKFLOW':'Retained as CI reference'},
        details=['scripts/validate-package.py and agents/openai.yaml are packaging details of this single skill','README, AGENTS.md and marketplace.json']))
if __name__=='__main__':main()
