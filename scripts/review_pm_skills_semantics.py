"""Record the LEAN SEMANTIC REVIEW of pm-skills at its existing pinned commit.

Skills and plugins were already catalogued; the 42 slash commands (chained workflows over the
skills) and the plugin validator were missed by the declaration scan and are added here.
Set PM_TARBALL to the pinned tarball; each file is blob-SHA verified.
"""
from __future__ import annotations
import json,re
from lean_review_lib import LeanReview

REVIEW=None
DOMAINS={'pm-ai-shipping':('ai-built-software-shipping-guidance','AI-built software shipping guidance',['ship vibe-coded software','AI shipping kit for PMs']),
         'pm-data-analytics':('product-data-analysis','Product data analysis',['A/B test analysis','cohort analysis','SQL query generation']),
         'pm-execution':('product-execution-documents','Product execution documents',['write a PRD','OKRs roadmap sprint planning','user stories']),
         'pm-go-to-market':('go-to-market-planning','Go-to-market planning',['GTM strategy','ideal customer profile','competitive battlecard']),
         'pm-market-research':('product-market-research','Product market research',['user personas','market sizing','competitor analysis']),
         'pm-marketing-growth':('product-marketing-and-growth-ideation','Product marketing and growth ideation',['value proposition','north star metric','positioning']),
         'pm-product-discovery':('product-discovery-and-experimentation','Product discovery and experimentation',['opportunity solution tree','assumption testing','customer interviews']),
         'pm-product-strategy':('product-strategy-frameworks','Product strategy frameworks',['product vision','lean canvas','SWOT analysis']),
         'pm-toolkit':('pm-productivity-toolkit','PM productivity toolkit',['proofread','NDA and privacy policy drafts','resume review'])}
CATS=['category:skills','category:agent-workflows']

def frontmatter(text,key):
    m=re.search(r'^'+key+r':\s*(.+)$',text,flags=re.M)
    return m.group(1).strip().strip('"\'') if m else ''

def main():
    review=LeanReview('jamesrwatsonx-creator/pm-skills','18468a95b427e70e258b51389796367c6f684e7d','PM_TARBALL')
    def cap_of(path): return DOMAINS[path.split('/')[0]]
    for entity in sorted(review.existing,key=lambda e:e['id']):
        kind=entity['entity_type'];path=entity['source']['source_path']
        if kind=='SKILL':
            review.finish(entity,entity['description'],[cap_of(path)],'USE EXISTING SKILL','operational:01','SKILL','YES',['Agent host that loads SKILL.md skills'],categories=CATS)
        elif kind=='PLUGIN':
            text=review.files.get(path,'');description=(json.loads(text).get('description') if text else '') or entity['description']
            review.finish(entity,description,[cap_of(path)],'USE DIRECTLY','operational:01','MODULE','YES',['Claude Code plugin support (skills and commands also usable individually)'],categories=CATS)
        elif kind=='WORKFLOW':
            review.finish(entity,entity['name']+' GitHub Actions workflow validating or releasing the marketplace.',[('ci-test-and-release-pipeline','CI test and release pipeline',[])],'REFERENCE ONLY','operational:14','COMPONENT','NO',['GitHub Actions'],categories=['category:ci-cd'])
        else: review.drop(entity)
    commands=sorted(n for n in review.files if re.fullmatch(r'pm-[a-z-]+/commands/[^/]+\.md',n))
    for path in commands:
        text=review.files[path];stem=path.rsplit('/',1)[1][:-3]
        entity=review.make('WORKFLOW','/'+stem,path)
        review.finish(entity,frontmatter(text,'description') or 'Slash command /'+stem+'.',[cap_of(path)],'USE DIRECTLY','operational:01','MODULE','PARTIAL',['Claude Code slash-command support','skills of the same plugin'],categories=CATS,extra={'kind':'slash command chaining skills'})
    validator=review.make('TOOL','validate_plugins','validate_plugins.py')
    review.finish(validator,'Python validator for the marketplace: checks plugin manifests, skill and command frontmatter and cross-file consistency (exercised by tests/test_validator.py and tests/test_consistency.py).',[('claude-plugin-marketplace-validation','Claude plugin marketplace validation',['validate plugin marketplace','skill frontmatter validation'])],'EXTRACT COMPONENTS','operational:23','COMPONENT','YES',['Python >=3.11'],categories=['category:developer-tools'])
    result=review.finalize(CATS,['studio:idea-studio'],'USE DIRECTLY','operational:01',
        {'WORKFLOW':'2 CI workflows retained plus 42 slash commands added from the commands folders','TOOL':'Marketplace validator added from validate_plugins.py','SKILL':'All 68 skills retained','PLUGIN':'All 9 plugins retained'},
        details=['README, docs images, CHANGELOG, marketplace.json index and tests are implementation details'])
    print(result)
if __name__=='__main__':main()
