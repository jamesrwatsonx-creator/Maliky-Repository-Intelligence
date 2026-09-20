"""Record the LEAN SEMANTIC REVIEW of Google-skills at its existing pinned commit.

112 canonical skills live under skills/<area>/<skill>/; 57 further SKILL entities are byte-identical
copies bundled inside plugins/cloud/*/skills. The copies are removed as duplicates (each plugin
manifest keeps CONTAINS_SKILL edges to the canonical skill). Skill asset packages (sample app
package.json) are implementation details. Set GS_TARBALL to the pinned tarball; files are SHA-verified.
"""
from __future__ import annotations
import re,collections
from lean_review_lib import LeanReview

CATS=['category:skills','category:cloud-infrastructure']
STUDIOS=['studio:deployment-ci']
DATA=('google-skills-google-cloud-data','Google Cloud data skills',['BigQuery Spanner Cloud SQL AlloyDB Bigtable guidance'])
OBS=('google-skills-google-cloud-observability','Google Cloud observability skills',['logging monitoring alerts on Google Cloud'])
AGENT=('google-skills-gemini-enterprise-agent-platform','Gemini Enterprise Agent Platform skills',['deploy tune evaluate models on Agent Platform'])
ADS=('google-skills-google-ads-and-analytics','Google Ads and Analytics API skills',['Google Ads API','Data Manager API','Google Analytics API'])
GROUPS=[('gke-',('google-skills-gke','Google Kubernetes Engine skills',['GKE guidance','Kubernetes on Google Cloud'])),
        ('agent-platform-',AGENT),('gemini-',AGENT),('google-agents-cli',AGENT),
        ('bigquery',DATA),('alloydb',DATA),('bigtable',DATA),('spanner',DATA),('cloud-sql',DATA),('datalineage',DATA),('managed-airflow',DATA),
        ('cloud-logging',OBS),('cloud-monitoring',OBS),('google-cloud-slo',OBS),('google-cloud-networking-observability',OBS),
        ('google-cloud-waf',('google-skills-google-cloud-well-architected','Google Cloud Well-Architected skills',['Well-Architected Framework reviews'])),
        ('google-cloud-solution',('google-skills-google-cloud-solution-guides','Google Cloud solution guide skills',['reference architectures on Google Cloud'])),
        ('data-manager-api',ADS),('google-ads',ADS),('google-mobile-ads',ADS),('ima-',ADS),('google-analytics',ADS),
        ('detection-engineering',('google-skills-google-cloud-security-operations','Google Cloud security operations skills',['detection engineering coverage']))]
DEFAULT=('google-skills-google-cloud-core-and-infrastructure','Google Cloud core and infrastructure skills',['gcloud onboarding auth IAM Cloud Run Firebase Storage'])
SENSITIVE=re.compile(r'iam-helper|recipe-auth|audience-ingestion|event-ingestion|^gcloud$|platform-security|workload-security')

def group_for(name):
    for prefix,group in GROUPS:
        if name.startswith(prefix): return group
    return DEFAULT

def main():
    review=LeanReview('jamesrwatsonx-creator/Google-skills','1af77752950126ae12dec176a0a3b27a16b7f5f7','GS_TARBALL')
    skills=[e for e in review.existing if e['entity_type']=='SKILL']
    canonical={e['name']:e for e in skills if e['source']['source_path'].startswith('skills/')}
    copies=[e for e in skills if e['source']['source_path'].startswith('plugins/')]
    for copy in copies:
        if canonical[copy['name']]['source']['blob_sha']!=copy['source']['blob_sha']: raise ValueError('Plugin copy differs from canonical skill: '+copy['name'])
    scripts=collections.Counter(p.split('/')[2] for p in review.files if p.startswith('skills/') and p.endswith(('.py','.sh','.js')))
    for name,entity in sorted(canonical.items()):
        extra={}
        if SENSITIVE.search(name): extra['sensitivity']='touches IAM, authentication, privileged access or ads audience data; review outputs before applying'
        if scripts.get(name): extra['bundled_scripts']=scripts[name]
        review.finish(entity,entity['description'],[group_for(name)],'USE EXISTING SKILL','operational:14' if 'gke' in name or 'cloud' in name else 'operational:12','SKILL','PARTIAL',
                      ['Agent host that loads SKILL.md skills','Google Cloud project and credentials'+(' (skill bundles helper scripts)' if scripts.get(name) else '')],'',CATS,STUDIOS,extra=extra)
    plugins=[e for e in review.existing if e['entity_type']=='PLUGIN']
    for plugin in sorted(plugins,key=lambda e:e['id']):
        host='Claude Code' if '.claude-plugin' in plugin['source']['source_path'] else 'Codex'
        directory=plugin['source']['source_path'].split('/')[2]
        skill_names=sorted({c['name'] for c in copies if c['source']['source_path'].split('/')[2]==directory})
        review.finish(plugin,plugin['description']+' ('+host+' plugin manifest).',[group_for(skill_names[0]) if skill_names else DEFAULT],'USE DIRECTLY','operational:14','MODULE','YES',[host+' plugin support (skills also usable individually)'],'',CATS,STUDIOS,extra={'bundles_skills':skill_names})
        for name in skill_names: review.relate('CONTAINS_SKILL',plugin['id'],canonical[name]['id'],'plugins/cloud/'+directory+'/skills/'+name+'/SKILL.md')
    for copy in copies: review.drop(copy)
    for package in [e for e in review.existing if e['entity_type']=='PACKAGE']: review.drop(package)
    findings=('Skills are markdown guidance; 19 skills bundle 67 helper scripts. Static scan found no rm -rf, curl|sh or sudo; subprocess use in 8 files, one `gcloud ... delete` in agent-platform-deploy/scripts/config_gcloud_cli.sh and one eval/exec in developer-device-platform-basics/scripts/demo_adb_forwarder.py. '
              'IAM, auth and ads-audience skills are flagged in metadata.')
    print(review.finalize(CATS,STUDIOS,'USE DIRECTLY','operational:14',
        {'SKILL':'112 canonical skills retained; 57 byte-identical plugin-bundled copies removed as duplicates','PLUGIN':'12 host manifests retained (6 plugins x Claude Code and Codex)','PACKAGE':'Removed sample-app package.json assets inside a skill'},
        deep_review=findings,details=['skill assets, references and bundled helper scripts','plugin marketplace manifests','README and CONTRIBUTING']))
if __name__=='__main__':main()
