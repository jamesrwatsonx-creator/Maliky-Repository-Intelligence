"""Record the LEAN SEMANTIC REVIEW of awesome-design-md at its existing pinned commit.

The 74 DESIGN_REFERENCE entities were catalogued from the pinned design-md/<brand>/DESIGN.md files
(descriptions come from each document's frontmatter or first paragraph). This review completes the
lean fields: capability, standalone status, mappings and use restrictions. No new entities.
"""
from __future__ import annotations
from lean_review_lib import LeanReview

CATS=['category:design-systems']
STUDIOS=['studio:design-studio']

def main():
    review=LeanReview('jamesrwatsonx-creator/awesome-design-md','8147538b4226ae41e2487a9179e3bcc1f68e8554')
    for entity in sorted(review.existing,key=lambda e:e['id']):
        if entity['entity_type']!='DESIGN_REFERENCE': review.drop(entity);continue
        review.finish(entity,entity['description'],[('brand-design-system-reference-for-agents','Brand design system reference for agents',['DESIGN.md brand design analysis','drop-in design system for coding agents','design inspiration by brand'])],
                      'REFERENCE ONLY','operational:17','REFERENCE','YES',['Coding agent that reads DESIGN.md context'],
                      'Independent per-brand analyses; overlaps in style with the other design references in this registry',CATS,STUDIOS,
                      extra={**entity['metadata'],'use_restriction':'Analyses inspired by third-party brands; use as design reference only, not to reproduce trademarks, logos or brand identity'})
    print(review.finalize(CATS,STUDIOS,'REFERENCE ONLY','operational:17',{'DESIGN_REFERENCE':'All 74 retained; each per-brand DESIGN.md is independently useful as a design reference'},
        details=['README, LICENSE and non-DESIGN.md assets']))
if __name__=='__main__':main()
