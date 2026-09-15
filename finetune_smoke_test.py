"""Day 1 smoke test for the fine-tuning stack.

Not real training. The model is tiny and the data is nonsense -- the only
thing being verified is that transformers + bitsandbytes (4-bit load) +
peft (LoRA) + trl (training loop) + accelerate (GPU placement) all work
together on this machine, before real time gets spent on Day 3-5's actual
dataset and target model.
"""
import torch
from datasets import Dataset
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model
from trl import SFTTrainer, SFTConfig

MODEL_NAME = "HuggingFaceTB/SmolLM2-135M-Instruct"

toy_data = [
    {"messages": [{"role": "user", "content": "Say hello in French"},
                  {"role": "assistant", "content": "Bonjour"}]},
    {"messages": [{"role": "user", "content": "Say hello in Spanish"},
                  {"role": "assistant", "content": "Hola"}]},
    {"messages": [{"role": "user", "content": "Say hello in German"},
                  {"role": "assistant", "content": "Hallo"}]},
    {"messages": [{"role": "user", "content": "Say hello in Italian"},
                  {"role": "assistant", "content": "Ciao"}]},
    {"messages": [{"role": "user", "content": "Say hello in Japanese"},
                  {"role": "assistant", "content": "Konnichiwa"}]},
]
dataset = Dataset.from_list(toy_data)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    quantization_config=bnb_config,
    device_map="auto",
)

lora_config = LoraConfig(
    r=8,
    lora_alpha=16,
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

sft_config = SFTConfig(
    output_dir="./smoke_test_output",
    max_steps=5,
    per_device_train_batch_size=1,
    logging_steps=1,
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    args=sft_config,
    train_dataset=dataset,
)

trainer.train()
print("Smoke test complete -- training loop ran without crashing.")
