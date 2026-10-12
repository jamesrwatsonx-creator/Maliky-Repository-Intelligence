"""Lean semantic review for zero-declaration video-model repositories.

All evidence is read from the already pinned, blob-verified source cache. Source
code is never imported or executed.
"""
from __future__ import annotations

import json
from lean_review_lib import LeanReview
import registry as r


CATEGORIES=['category:machine-learning-models','category:generative-ai','category:creative-tools']
STUDIOS=['studio:video-studio']


def complete(review, result):
    repo=review.repo
    repo.update({'state':'COMPLETE','next_phase':'COMPLETE'})
    repo.setdefault('phases',{}).update({
        'structure':True,'entity_extraction':True,'capability_analysis':True,'validation':True,
    })
    r.write(r.repo_file(repo),repo)
    return {**result,'state':'COMPLETE'}


def review_hunyuan():
    review=LeanReview('jamesrwatsonx-creator/HunyuanVideo','e260ed40c88d104801a8b1de05d2ab81e965a9ef')
    model=review.make('MODEL','HunyuanVideo','hyvideo/modules/models.py',396)
    review.finish(model,
        'Tencent HunyuanVideo 13B text-to-video diffusion transformer with dual-stream then single-stream multimodal fusion, an MLLM text encoder and high-resolution video generation.',
        [('text-to-video-generation','Text-to-video generation',['text conditioned video generation','T2V']),
         ('video-diffusion-transformer-inference','Video diffusion transformer inference',['video DiT inference','diffusion video model'])],
        'LICENSE REVIEW REQUIRED','operational:09','CORE','PARTIAL',
        ['Tencent Hunyuan community-licensed model weights','PyTorch and CUDA','45-60 GB minimum GPU memory at documented resolutions','external Hunyuan text encoders'],
        'Alternative to other owned text-to-video foundation models; newer upstream HunyuanVideo 1.5 is referenced but not contained here.',CATEGORIES,STUDIOS,
        extra={'parameters':'over 13B','license':'Tencent Hunyuan Community License','runtime_evidence':'Source and model card reviewed; weights and runtime not tested'})

    pipeline=review.make('COMPONENT','HunyuanVideoPipeline','hyvideo/diffusion/pipelines/pipeline_hunyuan_video.py',144)
    review.finish(pipeline,
        'Diffusers-style HunyuanVideo inference pipeline that encodes prompts, denoises video latents and decodes generated frames.',
        [('video-diffusion-inference-pipeline','Video diffusion inference pipeline',['video generation pipeline','diffusers video pipeline'])],
        'LICENSE REVIEW REQUIRED','operational:09','MODULE','PARTIAL',
        ['HunyuanVideo transformer weights','text encoders and tokenizers','causal 3D VAE','scheduler','PyTorch/CUDA'],
        'Complements the HunyuanVideo model and its command-line sampler.',CATEGORIES,STUDIOS)

    vae=review.make('COMPONENT','HunyuanVideo Causal 3D VAE','hyvideo/vae/vae.py',32)
    review.finish(vae,
        'Causal 3D variational autoencoder implementation for spatial-temporal compression and reconstruction of image and video tensors.',
        [('causal-3d-video-vae','Causal 3D video VAE',['video latent compression','spatiotemporal VAE','CausalConv3D video autoencoder'])],
        'LICENSE REVIEW REQUIRED','operational:09','MODULE','PARTIAL',
        ['PyTorch','matching pretrained VAE weights'],
        'Reusable inside compatible latent-video pipelines; tensor and weight compatibility must be verified.',CATEGORIES,STUDIOS)

    cli=review.make('CLI','sample_video.py','sample_video.py',12)
    review.finish(cli,
        'Command-line entry point for loading HunyuanVideo checkpoints and generating video samples from text prompts.',
        [('command-line-text-to-video-inference','Command-line text-to-video inference',['video generation CLI','T2V command line'])],
        'LICENSE REVIEW REQUIRED','operational:09','COMPONENT','PARTIAL',
        ['HunyuanVideo checkpoints','PyTorch/CUDA runtime','repository Python dependencies'],
        'Thin operational surface over the HunyuanVideo inference stack.',CATEGORIES,STUDIOS)

    result=review.finalize(CATEGORIES,STUDIOS,'LICENSE REVIEW REQUIRED','operational:09',
        {'MODEL':'One foundation MODEL retained','COMPONENT':'Inference pipeline and causal 3D VAE retained','CLI':'Sampling entry point retained'},
        deep_review='LICENSE trigger reviewed narrowly: LICENSE.txt is the custom Tencent Hunyuan Community License, excludes use in the EU, UK and South Korea, and requires legal review before reuse.',
        details=['Gradio demo','low-level transformer blocks','scheduler internals','test and utility modules'])
    repo=review.repo
    repo['review_reason']='Custom model/code license has geographic and use restrictions; legal disposition remains unresolved.'
    repo['next_phase']='LICENSE_REVIEW'
    r.write(r.repo_file(repo),repo)
    return {**result,'state':'NEEDS_REVIEW','blocker':'LICENSE_REVIEW'}


def review_longcat():
    review=LeanReview('jamesrwatsonx-creator/LongCat-Video','6b3f4b8582a8bc3f20f795735f5383716c4ba794')
    base=review.make('MODEL','LongCat-Video','longcat_video/modules/longcat_video_dit.py',124)
    review.finish(base,
        'Meituan LongCat-Video 13.6B foundation model unifying text-to-video, image-to-video, video continuation, interactive generation and minutes-long 720p video generation.',
        [('text-to-video-generation','Text-to-video generation',['text conditioned video generation','T2V']),
         ('image-to-video-generation','Image-to-video generation',['image conditioned video generation','I2V']),
         ('video-continuation-generation','Video continuation generation',['extend video','video continuation']),
         ('long-video-generation','Long-form video generation',['minutes-long video generation','long video'])],
        'USE DIRECTLY','operational:09','CORE','PARTIAL',
        ['LongCat-Video model weights','PyTorch 2.6/CUDA','FlashAttention 2, 3 or xFormers','text encoder and VAE weights'],
        'Alternative to HunyuanVideo for foundation video generation; broader native task coverage and long-video continuation.',CATEGORIES,STUDIOS,
        extra={'parameters':'13.6B','license':'MIT','weights_license':'MIT','runtime_evidence':'Source and model card reviewed; weights and runtime not tested'})

    avatar=review.make('MODEL','LongCat-Video-Avatar','longcat_video/modules/avatar/longcat_video_dit_avatar.py',194)
    review.finish(avatar,
        'Audio-driven LongCat avatar video model supporting audio-text-to-video, audio-image-to-video, video continuation, single- and multi-speaker audio, plus v1.5 Whisper audio encoding and distilled inference.',
        [('audio-driven-avatar-video-generation','Audio-driven avatar video generation',['talking avatar video','audio to character video','lip synchronized video']),
         ('multi-speaker-avatar-video-generation','Multi-speaker avatar video generation',['multi-audio character video','multi-character talking video'])],
        'USE DIRECTLY','operational:09','CORE','PARTIAL',
        ['LongCat-Video-Avatar or 1.5 weights','Wav2Vec2 or Whisper-large-v3 audio encoder','PyTorch/CUDA','ffmpeg and librosa'],
        'Specialized complement to the base LongCat-Video model.',CATEGORIES,STUDIOS,
        extra={'license':'MIT','supported_variants':['Avatar 1.0','Avatar 1.5'],'runtime_evidence':'Source and model card reviewed; weights and runtime not tested'})

    pipeline=review.make('COMPONENT','LongCatVideoPipeline','longcat_video/pipeline_longcat_video.py',59)
    review.finish(pipeline,
        'Inference pipeline for prompt encoding, conditioning, flow-matching denoising and decoding across LongCat text, image and continuation video tasks.',
        [('video-diffusion-inference-pipeline','Video diffusion inference pipeline',['video generation pipeline','flow-matching video pipeline'])],
        'EXTRACT','operational:09','MODULE','PARTIAL',
        ['LongCatVideoTransformer3DModel','AutoencoderKLWan','scheduler','text encoders','PyTorch/CUDA'],
        'Primary integration surface for the base LongCat model.',CATEGORIES,STUDIOS)

    avatar_pipeline=review.make('COMPONENT','LongCatVideoAvatarPipeline','longcat_video/pipeline_longcat_video_avatar.py',105)
    review.finish(avatar_pipeline,
        'Avatar inference pipeline combining text, reference imagery and one or more audio streams for lip-synchronized character video generation and continuation.',
        [('audio-conditioned-video-inference-pipeline','Audio-conditioned video inference pipeline',['avatar video pipeline','audio-image-to-video pipeline'])],
        'EXTRACT','operational:09','MODULE','PARTIAL',
        ['LongCatVideoAvatarTransformer3DModel','audio encoder','AutoencoderKLWan','scheduler','PyTorch/CUDA'],
        'Primary integration surface for LongCat avatar variants.',CATEGORIES,STUDIOS)

    sparse=review.make('COMPONENT','LongCat Block-Sparse Video Attention','longcat_video/block_sparse_attention/bsa_interface.py',612)
    review.finish(sparse,
        'Triton/PyTorch block-sparse 3D attention implementation with top-k and CDF block selection for efficient high-resolution video inference.',
        [('block-sparse-video-attention','Block-sparse video attention',['sparse 3D attention','efficient high-resolution video attention'])],
        'EXTRACT','operational:15','MODULE','PARTIAL',
        ['PyTorch','Triton','CUDA','FlashAttention'],
        'Reusable optimization module, subject to tensor-layout and GPU-kernel compatibility.',CATEGORIES,STUDIOS)

    parallel=review.make('COMPONENT','LongCat Ulysses Context Parallelism','longcat_video/context_parallel/ulysses_wrapper.py',108)
    review.finish(parallel,
        'Ulysses-style all-to-all wrapper that shards attention sequence dimensions across a distributed process group for multi-GPU video inference.',
        [('distributed-video-context-parallelism','Distributed video context parallelism',['Ulysses attention parallelism','multi-GPU video attention'])],
        'EXTRACT','operational:15','MODULE','PARTIAL',
        ['torch.distributed','initialized context-parallel process group','compatible attention function'],
        'Complements LongCat pipelines and may adapt to compatible transformer attention stacks.',CATEGORIES,STUDIOS)

    quant=review.make('COMPONENT','LongCat INT8 DiT Quantization','longcat_video/modules/quantization.py',60)
    review.finish(quant,
        'Weight-only INT8 linear-layer conversion, serialization and checkpoint loading utilities for reducing LongCat diffusion-transformer memory use.',
        [('int8-video-transformer-quantization','INT8 video transformer quantization',['INT8 DiT loading','video model memory reduction'])],
        'EXTRACT','operational:15','MODULE','PARTIAL',
        ['PyTorch','compatible LongCat diffusion transformer checkpoints'],
        'Complements LongCat Avatar 1.5 and other structurally compatible DiT models.',CATEGORIES,STUDIOS)

    enhancer=review.make('MODEL_ADAPTER','LongCat Video Prompt Enhancer','longcat_video/utils/prompt_enhancer.py',106)
    review.finish(enhancer,
        'OpenAI-compatible chat adapter and bilingual prompt templates for expanding text-to-video prompts and image-conditioned video prompts.',
        [('video-generation-prompt-enhancement','Video-generation prompt enhancement',['T2V prompt rewriting','I2V prompt rewriting','video prompt expansion'])],
        'WRAP','operational:15','COMPONENT','PARTIAL',
        ['OpenAI Python client','configured API key','gpt-4.1-compatible multimodal endpoint','Pillow for image prompts'],
        'Optional preprocessing complement to LongCat video pipelines; placeholder credentials must be configured externally.',CATEGORIES,STUDIOS,
        extra={'credential_handling':'APPKEY is a placeholder constant; supply a secret without committing it','network_service':'OpenAI-compatible chat completions'})

    result=review.finalize(CATEGORIES,STUDIOS,'USE DIRECTLY','operational:09',
        {'MODEL':'Base and avatar model families retained','COMPONENT':'Pipelines and reusable inference optimizations retained','MODEL_ADAPTER':'Optional prompt enhancer retained'},
        deep_review='License and credential triggers reviewed narrowly: README and LICENSE state MIT for code and weights; prompt enhancer contains only a placeholder APPKEY and requires external secret configuration.',
        details=['demo entry points','low-level transformer blocks','audio preprocessing helpers','scheduler and bucket configuration'])
    return complete(review,result)


def main():
    result=[review_hunyuan(),review_longcat()]
    r.build()
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
