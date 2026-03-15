"""
paraphrase_local.py — Local paraphrase engine using T5.

Rewrites text to reduce similarity with existing content.
Runs on CPU by default, GPU with USE_CUDA=1.

No external API calls.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Callable, Optional

log = logging.getLogger("seo_agent.paraphrase_local")

PARAPHRASE_MODEL = os.getenv("PARAPHRASE_MODEL", "Vamsi/T5_Paraphrase_Paws")
DEVICE = 0 if os.getenv("USE_CUDA", "0") == "1" else -1

_pipe = None


def _init_paraphraser():
    """Lazy-load paraphrase pipeline."""
    global _pipe
    if _pipe is None:
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
            log.info(f"Loading paraphrase model: {PARAPHRASE_MODEL} (device={DEVICE})")
            tokenizer = AutoTokenizer.from_pretrained(PARAPHRASE_MODEL)
            model = AutoModelForSeq2SeqLM.from_pretrained(PARAPHRASE_MODEL)
            _pipe = pipeline(
                "text2text-generation",
                model=model,
                tokenizer=tokenizer,
                device=DEVICE,
            )
            log.info("Paraphrase model loaded")
        except ImportError:
            log.warning("transformers not installed — using stub paraphraser")
            _pipe = "stub"
        except Exception as e:
            log.error(f"Failed to load paraphrase model: {e}")
            _pipe = "stub"
    return _pipe


def paraphrase_once(
    text: str,
    num_return_sequences: int = 2,
    max_length: int = 256,
) -> list[str]:
    """Generate paraphrase candidates for text."""
    pipe = _init_paraphraser()

    if pipe == "stub":
        return _stub_paraphrase(text, num_return_sequences)

    prompt = f"paraphrase: {text}"
    outputs = pipe(
        prompt,
        max_length=max_length,
        num_return_sequences=num_return_sequences,
        do_sample=True,
        top_k=50,
        temperature=0.7,
    )
    return [o["generated_text"].strip() for o in outputs]


def _stub_paraphrase(text: str, n: int = 2) -> list[str]:
    """Simple stub that shuffles words for testing without transformers."""
    words = text.split()
    results = []
    for i in range(n):
        # Reverse chunks to simulate paraphrase
        mid = len(words) // 2
        if i % 2 == 0:
            shuffled = words[mid:] + words[:mid]
        else:
            shuffled = list(reversed(words))
        results.append(" ".join(shuffled))
    return results


# Type alias for similarity checker function
SimilarityChecker = Callable[[str], tuple[float, list]]


def iterative_paraphrase(
    text: str,
    similarity_checker: SimilarityChecker,
    max_iters: int = 3,
    target_threshold: float = 0.35,
) -> dict:
    """
    Iteratively paraphrase text until similarity drops below threshold.
    
    Args:
        text: original text to paraphrase
        similarity_checker: fn(text) -> (max_similarity, top_matches)
        max_iters: maximum paraphrase attempts
        target_threshold: similarity target to reach
    
    Returns:
        {
            "original": str,
            "result": str,
            "success": bool,
            "final_similarity": float,
            "iterations": int,
            "top_matches": list,
        }
    """
    current = text
    best_text = text
    best_sim = 1.0

    for iteration in range(max_iters):
        max_sim, matches = similarity_checker(current)

        if max_sim <= target_threshold:
            return {
                "original": text,
                "result": current,
                "success": True,
                "final_similarity": max_sim,
                "iterations": iteration + 1,
                "top_matches": matches,
            }

        # Track best attempt
        if max_sim < best_sim:
            best_sim = max_sim
            best_text = current

        # Generate candidates
        candidates = paraphrase_once(current, num_return_sequences=2)

        # Pick candidate with lowest similarity
        for cand in candidates:
            cand_sim, cand_matches = similarity_checker(cand)
            if cand_sim < best_sim:
                best_sim = cand_sim
                best_text = cand

        current = best_text
        time.sleep(0.3)  # throttle

    # Final check
    final_sim, final_matches = similarity_checker(best_text)
    return {
        "original": text,
        "result": best_text,
        "success": final_sim <= target_threshold,
        "final_similarity": final_sim,
        "iterations": max_iters,
        "top_matches": final_matches,
    }


def check_and_rewrite(
    candidate_text: str,
    similarity_check_fn: SimilarityChecker,
    deny_threshold: float = 0.70,
    rewrite_threshold: float = 0.50,
    accept_threshold: float = 0.35,
) -> dict:
    """
    Full pipeline: check similarity → auto-rewrite if needed → return decision.
    
    Returns:
        {
            "allowed": bool,
            "action": "accept" | "rewritten" | "denied",
            "text": str (final text),
            "similarity": float,
            "reason": str,
        }
    """
    max_sim, matches = similarity_check_fn(candidate_text)

    # Hard deny
    if max_sim >= deny_threshold:
        return {
            "allowed": False,
            "action": "denied",
            "text": candidate_text,
            "similarity": max_sim,
            "reason": f"Too similar (sim={max_sim:.2f} >= deny={deny_threshold})",
            "top_matches": matches,
        }

    # Accept immediately
    if max_sim < rewrite_threshold:
        return {
            "allowed": True,
            "action": "accept",
            "text": candidate_text,
            "similarity": max_sim,
            "reason": f"Sufficiently unique (sim={max_sim:.2f})",
            "top_matches": matches,
        }

    # Try rewrite
    log.info(f"Attempting paraphrase (sim={max_sim:.2f}, target<{accept_threshold})")
    result = iterative_paraphrase(
        candidate_text,
        similarity_check_fn,
        max_iters=3,
        target_threshold=accept_threshold,
    )

    if result["success"]:
        return {
            "allowed": True,
            "action": "rewritten",
            "text": result["result"],
            "similarity": result["final_similarity"],
            "reason": f"Rewritten in {result['iterations']} iterations",
            "top_matches": result["top_matches"],
        }

    return {
        "allowed": False,
        "action": "denied",
        "text": result["result"],
        "similarity": result["final_similarity"],
        "reason": f"Could not differentiate after {result['iterations']} iterations",
        "top_matches": result["top_matches"],
    }
