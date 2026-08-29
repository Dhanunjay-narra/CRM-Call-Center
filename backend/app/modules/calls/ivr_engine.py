from typing import Dict, List

class IVRMenuNode:
    def __init__(self, prompt: str, options: Dict[str, str]):
        self.prompt = prompt
        self.options = options

    def process_dtmf_input(self, digit: str) -> str:
        return self.options.get(str(digit), "DEFAULT_AGENT_QUEUE")
