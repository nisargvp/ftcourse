import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
import torch
from cog import BasePredictor
from vllm import LLM, SamplingParams

def prompt(nlq, cols):
    return f"""Honeycomb is an observability platform that allows you to write queries to inspect trace data. You are an assistant that takes a natural language query (NLQ) and a list of valid columns and produce a Honeycomb query.

### Instruction:

NLQ: "{nlq}"

Columns: {cols}

### Response:
"""

class Predictor(BasePredictor):
        
    def setup(self):
        n_gpus = torch.cuda.device_count()
        # you usually would let these be set by the user, but for this specific model, I know the best settings.
        self.sampling_params = SamplingParams(stop_token_ids=[2], temperature=0, ignore_eos=True, max_tokens=2500)
        self.llm = LLM(model='parlance-labs/hc-mistral-alpaca-merged', 
                       tensor_parallel_size=n_gpus)

    def predict(self, nlq: str, cols: str) -> str:        
        _p = prompt(nlq, cols)
        out = self.llm.generate(_p, sampling_params=self.sampling_params, use_tqdm=False)
        return out[0].outputs[0].text.strip().strip('"')
