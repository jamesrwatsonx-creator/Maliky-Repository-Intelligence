"""Record the LEAN SEMANTIC REVIEW of Kimi-K3 at its existing pinned commit.

The repository is a model card (README.md) for Moonshot AI's open-weight Kimi K3; it has no code.
One MODEL entity is catalogued from README sections 1, 2 and 5-7.
"""
from __future__ import annotations
from lean_review_lib import LeanReview

def main():
    review=LeanReview('jamesrwatsonx-creator/Kimi-K3','3cb39dfd32e51c3328e2e4b4af21341247d06c43')
    model=review.make('MODEL','Kimi K3','README.md')
    review.finish(model,'Moonshot AI Kimi K3: open-weight native multimodal (text, image, video) agentic mixture-of-experts model, 2.8T total and 104B activated parameters, 93 layers, 16 of 896 experts active, 1M-token context, native MXFP4 quantization; always-on thinking with reasoning_effort low/high/max; API (model kimi-k3) is OpenAI/Anthropic-compatible on platform.kimi.ai.',
                  [('open-weight-multimodal-agentic-llm','Open-weight multimodal agentic LLM',['Kimi K3','frontier open weights model','1M context multimodal model','long-horizon coding model'])],
                  'LICENSE REVIEW REQUIRED','operational:15','CORE','PARTIAL',
                  ['Kimi K3 License (custom; repository license is NOASSERTION)','inference engine: vLLM, SGLang or TokenSpeed, or the hosted API','preserved-thinking usage: pass the full assistant message (reasoning_content, tool_calls) back on multi-turn calls'],
                  'Comparable to other frontier open-weight models; Kimi Code CLI is the recommended agent framework',['category:machine-learning-models','category:llm-projects','category:generative-ai'],
                  extra={'license':'Kimi K3 License (custom terms; not reviewed here)','reasoning_effort':['low','high','max'],'recommended_inference':['vLLM','SGLang','TokenSpeed'],'weights_location':'https://huggingface.co/moonshotai/Kimi-K3'})
    print(review.finalize(['category:machine-learning-models','category:llm-projects','category:generative-ai'],[],'LICENSE REVIEW REQUIRED','operational:15',
        {'MODEL':'Model card only; one MODEL entity'},details=['Benchmark tables, tech report PDF and logo assets','LICENSE terms were not read (file not in the read set); custom license requires review before commercial use']))
if __name__=='__main__':main()
