from prompts import training_example
import json
from datasets import Dataset
import db
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
MODEL_NAME= "HuggingFaceTB/SmolLM2-1.7B-Instruct"

def load_split(filename):
    with open(db.DATA_DIR / filename) as f:
        labeled=json.load(f)
    return Dataset.from_list([training_example(item) for item in labeled])

if __name__ == "__main__":

    tokenizer= AutoTokenizer.from_pretrained(MODEL_NAME)

    train_dataset = load_split("train_labeled.json")
    eval_dataset = load_split("eval_labeled.json")

    example=train_dataset[0]

    # Training view: the full conversation including the answer.
    training_text=tokenizer.apply_chat_template(example["prompt"] + example["completion"], tokenize=False)
    print("Training Text: " + training_text)

    # Inference view: prompt only, ending at an open assistant turn
    inference_text= tokenizer.apply_chat_template(example["prompt"], tokenize=False, add_generation_prompt=True)

    print(repr(inference_text[-60:]))

    print("tokens in one example:", len(tokenizer(training_text)["input_ids"]))

    bnb_config = BitsAndBytesConfig( load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.float16)
    model= AutoModelForCausalLM.from_pretrained(MODEL_NAME, quantization_config=bnb_config, device_map="auto")

    print(f"model memory: {model.get_memory_footprint() / 1e9:.2f} GB")
    print("="*80)
    print(f"GPU memory in use: {torch.cuda.memory_allocated()/ 1e9:.2f} GB")