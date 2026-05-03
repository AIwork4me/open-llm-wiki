#!/usr/bin/env python3
"""Generate synthetic test corpus for multi-paper regression testing (Checklist §19)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from wiki_common import write_text


PAPERS = [
    {
        "id": "1706.03762",
        "title": "Attention Is All You Need",
        "tags": ["attention", "transformer", "sequence-modeling"],
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
        "key_data": [
            ("WMT 2014 EN-DE BLEU", "27.3 (base)", "28.4 (big)"),
            ("WMT 2014 EN-FR BLEU", "38.1", "41.0"),
            ("Model parameters (base)", "65M", "-"),
        ],
        "concepts": ["attention-mechanisms", "transformers"],
    },
    {
        "id": "1810.04805",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "tags": ["bert", "pretraining", "nlu"],
        "abstract": "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
        "key_data": [
            ("GLUE score", "80.5", "82.1"),
            ("SQuAD 1.1 F1", "88.5", "93.2"),
            ("SQuAD 2.0 F1", "76.7", "86.5"),
        ],
        "concepts": ["pretraining", "transformers"],
    },
    {
        "id": "2005.14165",
        "title": "GPT-3: Language Models are Few-Shot Learners",
        "tags": ["gpt", "few-shot", "language-model"],
        "abstract": "We demonstrate that scaling up language models greatly improves task-agnostic, few-shot performance, sometimes even reaching competitiveness with prior state-of-the-art fine-tuning approaches. We train GPT-3, an autoregressive language model with 175 billion parameters.",
        "key_data": [
            ("Parameters", "175B", "-"),
            ("Training data", "300B tokens", "-"),
            ("SuperGLUE", "71.8 (few-shot)", "85.4 (fine-tuned SOTA)"),
        ],
        "concepts": ["language-models", "few-shot-learning"],
    },
    {
        "id": "2203.02155",
        "title": "Training language models to follow instructions with human feedback",
        "tags": ["instructgpt", "rlhf", "alignment"],
        "abstract": "Making language models bigger does not inherently make them better at following a user's intent. We show an avenue for aligning language models with user intent on a wide range of tasks by fine-tuning with human feedback.",
        "key_data": [
            ("Labeler preference", "85% prefer InstructGPT", "vs GPT-3"),
            ("TruthfulQA", "0.56", "vs 0.30 GPT-3"),
            ("Toxicity reduction", "50% less toxic", "vs GPT-3"),
        ],
        "concepts": ["rlhf", "alignment"],
    },
    {
        "id": "2303.08774",
        "title": "GPT-4 Technical Report",
        "tags": ["gpt-4", "multimodal", "large-language-model"],
        "abstract": "We report the development of GPT-4, a large multimodal model capable of processing image and text inputs and producing text outputs. While less capable than humans in many real-world scenarios, GPT-4 exhibits human-level performance on various professional and academic benchmarks.",
        "key_data": [
            ("Bar exam", "298/400 (90th percentile)", "-"),
            ("MMLU", "86.4%", "-"),
            ("Biology Olympiad", "99th percentile", "-"),
        ],
        "concepts": ["multimodal", "large-language-models"],
    },
    {
        "id": "2312.11805",
        "title": "Mixtral of Experts",
        "tags": ["moe", "mixtral", "sparse-models"],
        "abstract": "We introduce Mixtral 8x7B, a Sparse Mixture of Experts model that matches or exceeds Llama 2 70B and GPT-3.5 on most benchmarks. Mixtral is a decoder-only model with 46.7B total parameters but only uses 12.9B parameters per token.",
        "key_data": [
            ("Total parameters", "46.7B", "-"),
            ("Active parameters per token", "12.9B", "-"),
            ("MMLU", "70.6%", "vs 68.9% Llama 2 70B"),
        ],
        "concepts": ["mixture-of-experts", "sparse-models"],
    },
    {
        "id": "2401.04088",
        "title": "DeepSeek LLM: Scaling Open-Source Language Models",
        "tags": ["deepseek", "scaling", "language-model"],
        "abstract": "We present DeepSeek LLM, a family of open-source language models scaled to 7B and 67B parameters. We pre-train on a 2 trillion token dataset and explore scaling laws for training data and model size.",
        "key_data": [
            ("Parameters (large)", "67B", "-"),
            ("Training tokens", "2T", "-"),
            ("MMLU (67B)", "71.3%", "-"),
        ],
        "concepts": ["language-models", "scaling"],
    },
    {
        "id": "2402.19427",
        "title": "Vision Transformer: An Image is Worth 16x16 Words",
        "tags": ["vit", "vision-transformer", "image-classification"],
        "abstract": "While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited. We show that a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks.",
        "key_data": [
            ("ImageNet accuracy", "88.55% (ViT-H/14)", "-"),
            ("Parameters (ViT-H)", "632M", "-"),
            ("JFT-300M pretrain data", "300M images", "-"),
        ],
        "concepts": ["vision-transformer", "image-classification"],
    },
    {
        "id": "2403.05530",
        "title": "LLaMA: Open and Efficient Foundation Language Models",
        "tags": ["llama", "open-source", "foundation-model"],
        "abstract": "We introduce LLaMA, a collection of foundation language models ranging from 7B to 65B parameters. We train our models on trillions of tokens, and show that it is possible to train state-of-the-art models using publicly available datasets exclusively.",
        "key_data": [
            ("Parameters (largest)", "65B", "-"),
            ("Training tokens", "1.4T", "-"),
            ("MMLU (65B)", "63.4%", "-"),
        ],
        "concepts": ["foundation-models", "open-source-llm"],
    },
    {
        "id": "2404.02375",
        "title": "Mamba: Linear-Time Sequence Modeling with Selective State Spaces",
        "tags": ["mamba", "state-space-model", "sequence-modeling"],
        "abstract": "We propose Mamba, a new architecture for sequence modeling that achieves linear-time complexity while maintaining competitive performance with transformers. Mamba uses selective state space models that allow input-dependent parameterization.",
        "key_data": [
            ("Inference speedup", "5x vs Transformer", "-"),
            ("Parameters (1.4B)", "1.4B", "-"),
            ("Perplexity improvement", "over同等参数Transformer", "-"),
        ],
        "concepts": ["state-space-models", "efficient-architectures"],
    },
    {
        "id": "2405.04434",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "tags": ["cot", "reasoning", "prompting"],
        "abstract": "We explore how generating a chain of thought — a series of intermediate reasoning steps — significantly improves the ability of large language models to perform complex reasoning tasks.",
        "key_data": [
            ("GSM8K (PaLM 540B)", "56.9% (standard)", "74.4% (CoT)"),
            ("Math word problems improvement", "+17.5%", "-"),
            ("StrategyQA", "75.0% (CoT)", "65.4% (standard)"),
        ],
        "concepts": ["reasoning", "prompting"],
    },
    {
        "id": "2406.01234",
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "tags": ["rag", "retrieval", "generation"],
        "abstract": "We show that retrieval-augmented generation (RAG) models combine pre-trained parametric and non-parametric memory to achieve state-of-the-art results on knowledge-intensive tasks. RAG models retrieve documents and use them to generate more factual and specific outputs.",
        "key_data": [
            ("Natural Questions", "44.5 (RAG-sequence)", "vs 36.6 BART"),
            ("TriviaQA", "56.8 (RAG-sequence)", "vs 46.7 BART"),
            ("MS MARCO", "27.0 (RAG-token)", "vs 22.5 T5"),
        ],
        "concepts": ["rag", "retrieval"],
    },
    {
        "id": "2407.02345",
        "title": "Constitutional AI: Harmlessness from AI Feedback",
        "tags": ["constitutional-ai", "alignment", "safety"],
        "abstract": "We describe Constitutional AI, an approach for training a harmless AI assistant through self-improvement. The AI evaluates its own outputs according to a set of principles (a constitution) and revises them accordingly, reducing dependence on human feedback labels.",
        "key_data": [
            ("Harmfulness score reduction", "92% less harmful", "vs base model"),
            ("Helpfulness maintained", "within 2% of RLHF", "-"),
            ("Principles used", "16", "-"),
        ],
        "concepts": ["alignment", "ai-safety"],
    },
    {
        "id": "2408.03456",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "tags": ["lora", "fine-tuning", "parameter-efficient"],
        "abstract": "We propose Low-Rank Adaptation (LoRA), which freezes the pre-trained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture, greatly reducing the number of trainable parameters for downstream tasks.",
        "key_data": [
            ("Trainable parameters reduction", "10,000x fewer", "vs full fine-tuning"),
            ("GPT-3 175B trainable params", "18M (LoRA)", "vs 175B (full)"),
            ("Quality preserved", "no degradation", "vs full fine-tuning"),
        ],
        "concepts": ["parameter-efficient-finetuning", "fine-tuning"],
    },
    {
        "id": "2409.04567",
        "title": "RLHF: Training a Helpful and Harmless Assistant",
        "tags": ["rlhf", "assistant", "human-feedback"],
        "abstract": "We describe the training of a helpful and harmless assistant using Reinforcement Learning from Human Feedback (RLHF). Our approach combines supervised fine-tuning, reward modeling from human comparisons, and reinforcement learning optimization.",
        "key_data": [
            ("Human preference win rate", "71% vs base model", "-"),
            ("Helpfulness score", "4.2/5", "vs 3.1/5 base"),
            ("Training comparisons", "336K human comparisons", "-"),
        ],
        "concepts": ["rlhf", "alignment"],
    },
    {
        "id": "2410.05678",
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "tags": ["dpo", "preference-optimization", "alignment"],
        "abstract": "We propose Direct Preference Optimization (DPO), which simplifies RLHF by directly optimizing the language model policy to align with human preferences without explicitly training a reward model or using reinforcement learning.",
        "key_data": [
            ("Win rate vs RLHF (TL;DR)", "72% (DPO)", "vs 68% (RLHF)"),
            ("Training compute reduction", "3x cheaper", "vs RLHF pipeline"),
            ("Anthropic HH dataset", "similar performance", "-"),
        ],
        "concepts": ["preference-optimization", "alignment"],
    },
    {
        "id": "2411.06789",
        "title": "Scaling Laws for Neural Language Models",
        "tags": ["scaling-laws", "compute-optimal", "language-model"],
        "abstract": "We study empirical scaling laws for language model performance on the cross-entropy loss. Loss scales as a power law with model size, dataset size, and the amount of compute used for training, with some trends spanning more than seven orders of magnitude.",
        "key_data": [
            ("Loss scaling exponent (params)", "L ~ N^-0.076", "-"),
            ("Loss scaling exponent (data)", "L ~ D^-0.095", "-"),
            ("Chinchilla optimal ratio", "~20 tokens per parameter", "-"),
        ],
        "concepts": ["scaling-laws", "language-models"],
    },
    {
        "id": "2412.07890",
        "title": "FlashAttention: Fast and Memory-Efficient Exact Attention",
        "tags": ["flashattention", "efficient-attention", "optimization"],
        "abstract": "We present FlashAttention, an algorithm that computes exact attention with significantly fewer memory accesses. FlashAttention achieves wall-clock speedup of 2-4x compared to standard attention by reducing HBM reads/writes.",
        "key_data": [
            ("Speedup vs PyTorch attention", "2-4x", "-"),
            ("Memory reduction", "up to 20x", "-"),
            ("BERT training speedup", "15% end-to-end", "-"),
        ],
        "concepts": ["efficient-attention", "optimization"],
    },
    {
        "id": "2501.08901",
        "title": "Q-Learning for Language Model Alignment",
        "tags": ["q-learning", "alignment", "reinforcement-learning"],
        "abstract": "We propose applying Q-learning approaches to language model alignment, showing that value-based reinforcement learning methods can match or exceed policy gradient methods like PPO for RLHF tasks.",
        "key_data": [
            ("Win rate vs PPO", "54%", "vs 52% PPO"),
            ("Training stability", "3x fewer variance issues", "-"),
            ("Compute overhead", "15% more than PPO", "-"),
        ],
        "concepts": ["alignment", "reinforcement-learning"],
    },
    {
        "id": "2502.09012",
        "title": "Speculative Decoding: Fast Inference from Large Language Models",
        "tags": ["speculative-decoding", "inference", "speedup"],
        "abstract": "We present speculative decoding, a technique for accelerating inference from large language models without changing the output distribution. A small draft model proposes tokens that the large target model verifies in parallel.",
        "key_data": [
            ("Speedup (Chinchilla 70B)", "2-2.5x", "without quality loss"),
            ("Draft model size", "7B", "for 70B target"),
            ("Acceptance rate", "~80%", "-"),
        ],
        "concepts": ["inference-optimization", "speedup"],
    },
    {
        "id": "2503.10123",
        "title": "Red Teaming Language Models to Reduce Harms",
        "tags": ["red-teaming", "safety", "evaluation"],
        "abstract": "We describe our approach to red teaming language models, where human testers attempt to elicit harmful outputs. We use findings from red teaming to iteratively improve model safety through targeted training and filtering.",
        "key_data": [
            ("Harmful outputs reduced", "73% reduction", "after red team fixes"),
            ("Red team testers", "325 annotators", "-"),
            ("Attack categories", "12 categories", "-"),
        ],
        "concepts": ["ai-safety", "evaluation"],
    },
    {
        "id": "2504.11234",
        "title": "Toolformer: Language Models Can Teach Themselves to Use Tools",
        "tags": ["toolformer", "tool-use", "agents"],
        "abstract": "We introduce Toolformer, a model trained to teach itself how to use tools via simple APIs. Toolformer can decide when and how to use calculator, Q&A, search engine, and calendar APIs by inserting API calls into its text generation.",
        "key_data": [
            ("GSM8K improvement", "Calculator API: +38.9%", "vs baseline"),
            ("Natural Questions improvement", "+28.5%", "vs baseline"),
            ("API types supported", "5 (calculator, QA, search, calendar, translator)", "-"),
        ],
        "concepts": ["tool-use", "agents"],
    },
    {
        "id": "2505.12345",
        "title": "Codex: Evaluating Large Language Models Trained on Code",
        "tags": ["codex", "code-generation", "programming"],
        "abstract": "We evaluate large language models trained on code. Our Codex model, a GPT language model fine-tuned on publicly available code from GitHub, can synthesize programs from docstrings with surprising accuracy.",
        "key_data": [
            ("HumanEval pass@100", "28.8% (12B)", "72.3% (code-davinci-002)"),
            ("APPS dataset accuracy", "27.4%", "-"),
            ("Training data", "54M public GitHub repos", "-"),
        ],
        "concepts": ["code-generation", "programming"],
    },
    {
        "id": "2506.13456",
        "title": "Tree of Thoughts: Deliberate Problem Solving with Large Language Models",
        "tags": ["tree-of-thoughts", "reasoning", "search"],
        "abstract": "We introduce Tree of Thoughts (ToT), a framework that generalizes over chain-of-thought prompting and allows exploration over coherent units of text (thoughts) as intermediate steps toward problem solving.",
        "key_data": [
            ("Game of 24 success rate", "74% (ToT)", "vs 7% (CoT)"),
            ("Crossword solving improvement", "+22%", "vs IO prompting"),
            ("Creative writing human preference", "higher rated", "-"),
        ],
        "concepts": ["reasoning", "search"],
    },
    {
        "id": "2507.14567",
        "title": "Whisper: Robust Speech Recognition via Large-Scale Weak Supervision",
        "tags": ["whisper", "speech-recognition", "multimodal"],
        "abstract": "We study the capabilities of speech processing systems trained on large amounts of weakly supervised audio transcriptions. Our Whisper model, trained on 680,000 hours of multilingual data, approaches human-level robustness and accuracy.",
        "key_data": [
            ("English WER", "5.0% (Whisper large)", "vs ~5-6% human"),
            ("Training data", "680K hours", "-"),
            ("Languages supported", "99", "-"),
        ],
        "concepts": ["speech-recognition", "multimodal"],
    },
]

CONCEPT_DESCRIPTIONS: dict[str, str] = {
    "attention-mechanisms": "How attention mechanisms enable direct token-to-token interaction in neural sequence models.",
    "transformers": "How the Transformer architecture and its variants process sequences without recurrence.",
    "pretraining": "How self-supervised pretraining on large corpora builds general language representations.",
    "language-models": "How autoregressive and masked language models learn to predict and generate text.",
    "few-shot-learning": "How large language models perform new tasks from a few examples without weight updates.",
    "rlhf": "How reinforcement learning from human feedback aligns language models with user preferences.",
    "alignment": "How techniques like RLHF, DPO, and Constitutional AI steer models toward helpful and harmless behavior.",
    "multimodal": "How models process and reason across multiple modalities such as text, images, and audio.",
    "large-language-models": "How scaling parameters, data, and compute produces emergent capabilities in language models.",
    "mixture-of-experts": "How sparse expert routing changes scaling efficiency and task specialization.",
    "sparse-models": "How models with conditional computation reduce active parameters per inference step.",
    "scaling": "How model size, data volume, and compute budget jointly determine language model quality.",
    "vision-transformer": "How the Vision Transformer applies patch-based self-attention to image understanding.",
    "image-classification": "How neural networks categorize images into predefined classes.",
    "foundation-models": "How large pre-trained models serve as adaptable foundations for downstream tasks.",
    "open-source-llm": "How openly available language models enable community-driven research and deployment.",
    "state-space-models": "How structured state space layers model sequences with linear time complexity.",
    "efficient-architectures": "How architectural innovations reduce computational cost without sacrificing quality.",
    "reasoning": "How chain-of-thought, tree-of-thought, and other techniques elicit multi-step reasoning.",
    "prompting": "How prompt engineering and in-context learning steer model outputs without weight changes.",
    "rag": "How retrieval-augmented generation combines parametric knowledge with external document retrieval.",
    "retrieval": "How dense and sparse retrieval systems find relevant passages for downstream generation.",
    "ai-safety": "How red teaming, content filtering, and safety training reduce harmful model outputs.",
    "parameter-efficient-finetuning": "How low-rank adaptation and similar methods reduce fine-tuning costs.",
    "fine-tuning": "How supervised and preference-based fine-tuning specialize pre-trained models.",
    "preference-optimization": "How DPO and related methods align models with human preferences without RL.",
    "scaling-laws": "How loss, capability, and compute scale predictably with model size and data.",
    "efficient-attention": "How algorithms like FlashAttention reduce memory and compute for attention layers.",
    "optimization": "How training techniques, learning rate schedules, and hardware utilization improve efficiency.",
    "reinforcement-learning": "How value-based and policy-gradient RL methods train agents and align models.",
    "inference-optimization": "How speculative decoding, quantization, and caching accelerate model inference.",
    "speedup": "How parallel verification, draft models, and hardware-aware kernels reduce inference latency.",
    "evaluation": "How benchmarks and human evaluations measure model capability and safety.",
    "tool-use": "How language models learn to call external APIs and tools during generation.",
    "agents": "How tool-augmented language models plan, act, and complete multi-step tasks.",
    "code-generation": "How models trained on source code synthesize programs from specifications.",
    "programming": "How code-oriented training and evaluation improve programming capability.",
    "search": "How tree search and beam search improve planning and reasoning in language models.",
    "speech-recognition": "How models trained on weakly supervised audio transcriptions achieve robust ASR.",
}


def concept_description(concept_id: str) -> str:
    if concept_id in CONCEPT_DESCRIPTIONS:
        return CONCEPT_DESCRIPTIONS[concept_id]
    title = concept_id.replace("-", " ").title()
    return f"How {title.lower()} relates to the broader LLM research landscape."


def generate_paper_markdown(paper: dict) -> str:
    lines = [
        f"# {paper['title']}",
        "",
        "## Abstract",
        "",
        paper["abstract"],
        "",
        "## Key Data",
        "",
        "| # | Metric | Value | Baseline |",
        "|---|--------|-------|----------|",
    ]
    for i, (metric, value, baseline) in enumerate(paper["key_data"], 1):
        lines.append(f"| {i} | {metric} | {value} | {baseline} |")
    lines.append("")
    lines.append("## Tags")
    lines.append("")
    lines.append(", ".join(paper["tags"]))
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate synthetic test corpus for multi-paper regression testing (Checklist §19).",
    )
    parser.add_argument("vault", type=Path, help="Target vault directory.")
    parser.add_argument("--count", type=int, default=25, help="Number of papers to generate (max 25).")
    args = parser.parse_args()

    vault = args.vault
    raw_dir = vault / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    concepts: dict[str, list[str]] = {}
    count = min(args.count, len(PAPERS))
    for paper in PAPERS[:count]:
        paper_dir = raw_dir / f"{paper['id']}_markdown"
        paper_dir.mkdir(parents=True, exist_ok=True)
        write_text(paper_dir / "combined.md", generate_paper_markdown(paper))
        for concept in paper["concepts"]:
            if concept not in concepts:
                title = concept.replace("-", " ").title()
                desc = concept_description(concept)
                concepts[concept] = [title, desc]

    concepts_file = vault / "test-concepts.json"
    write_text(concepts_file, json.dumps(concepts, indent=2, ensure_ascii=False))
    print(f"generated {count} papers in {raw_dir}")
    print(f"concepts file: {concepts_file}")


if __name__ == "__main__":
    main()
