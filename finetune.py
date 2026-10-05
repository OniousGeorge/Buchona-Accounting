from prompts import training_example
import json
from datasets import Dataset
import db
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
MODEL_NAME= "HuggingFaceTB/SmolLM2-1.7B-Instruct"

def load_split(path):
    with open(path) as f:
        labeled=json.load(f)
    return Dataset.from_list([training_example(item) for item in labeled])

if __name__ == "__main__":

    tokenizer= AutoTokenizer.from_pretrained(MODEL_NAME)

    train_dataset = load_split(db.TRAIN_DATASET_PATH)
    eval_dataset = load_split(db.EVAL_DATASET_PATH)
    print(f"train: {len(train_dataset)}  eval: {len(eval_dataset)}")

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

    model= prepare_model_for_kbit_training(model)

    lora_config= LoraConfig(r=8, lora_alpha=16, target_modules=["q_proj", "k_proj", "v_proj", "o_proj"], lora_dropout=0.05, task_type="CAUSAL_LM")

    model= get_peft_model(model, lora_config)
    model.print_trainable_parameters()
