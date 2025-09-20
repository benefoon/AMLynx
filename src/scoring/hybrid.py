import math
from dataclasses import dataclass

@dataclass
class FusionConfig:
    model_weight: float = 0.7
    rule_weight: float = 0.3
    bias: float = 0.0

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def fuse_scores(model_score: float, rule_score: float, cfg: FusionConfig = FusionConfig()) -> float:
    """
    Combine model_score and rule_score. Both inputs expected in [0,1].
    Returns final risk in [0,1].
    """
    # defensive clamp
    ms = max(0.0, min(1.0, float(model_score)))
    rs = max(0.0, min(1.0, float(rule_score)))

    # convert to logits (avoid extremes)
    eps = 1e-6
    def logit(p: float) -> float:
        p = min(max(p, eps), 1-eps)
        return math.log(p/(1.0-p))

    combined_logit = cfg.model_weight * logit(ms) + cfg.rule_weight * logit(rs) + cfg.bias
    return float(sigmoid(combined_logit))
