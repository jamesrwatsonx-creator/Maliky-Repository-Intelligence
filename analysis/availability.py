"""Availability never controls whether semantic review may proceed."""
import shutil
SPECS={
 'aider':('aider','ADAPT ALGORITHM','Local reference-ranking map'),
 'continue':('cn','ADAPT ALGORITHM','Content/path/blob/version cache'),
 'semgrep':('semgrep','SUBPROCESS ADAPTER','Existing static candidate detector'),
 'scancode':('scancode','SUBPROCESS ADAPTER','Manifest/SPDX evidence; preserve prior license evidence'),
 'linguist':('github-linguist','ADAPT ALGORITHM','Extension/header classification; retain all files'),
 'repomix':('repomix','ADAPT ALGORITHM','Bounded local semantic packets'),
 'codeql':('codeql','REFERENCE IMPLEMENTATION ONLY','Preserve existing security evidence; no substitute dataflow analysis'),
 'repoagent':('repoagent','ADAPT ALGORITHM','Local Python AST definitions/call references'),
 'syft':('syft','SUBPROCESS ADAPTER','Manifest dependency evidence; no full SBOM claim')}

def statuses():
    output={}
    for tool,(executable,mode,fallback) in SPECS.items():
        available=shutil.which(executable) is not None
        output[tool]={'available':available,'unavailable':not available,'fallback_available':True,
                      'integration_mode':mode,'availability_scope':'native executable on PATH; not runtime certification',
                      'fallback':fallback,'installation_required':False,'status':'NOT_REQUESTED'}
    return output
