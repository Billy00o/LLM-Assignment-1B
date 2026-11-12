# Assignment 1B — Gemma Study Helper

Gemma Study Helper is a terminal chatbot for answering study questions, explaining concepts, and creating practice questions. It runs the original `google/gemma-2b-it` checkpoint from Google on CPU through Hugging Face Transformers in BF16.

| Group member | Name | Student number |
|---|---|---|
| Student 1 | Add name | P2303322 |
| Student 2 | Add name | P2319796 |

## Requirements

- Windows x64 with PowerShell, Git, and Python 3.10 or 3.12 (64-bit).
- A CPU. This project runs without a GPU.
- Internet access for setup and about 5 GB of disk space for the checkpoint, plus space for the Python environment.
- PyTorch, Transformers, Hugging Face Hub and the model-loading dependencies in [requirements.txt](requirements.txt).
- A Hugging Face account with a Read token. Accept the terms on the [Gemma model page](https://huggingface.co/google/gemma-2b-it) before downloading.

## Step 1 — Clone the project

If you already have the project folder, open PowerShell there and continue to Step 2.

```powershell
git clone https://github.com/Billy00o/llm-project-Billy.git
cd llm-project-Billy
```

## Step 2 — Set up Python and install dependencies

Use `python --version` to confirm that PowerShell is using Python 3.10 or 3.12. If a working `venv` already exists, start from the activation command. Create a fresh virtual environment when changing Python versions.

```powershell
python --version
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

The terminal should show `(venv)` after activation. `pip check` should report `No broken requirements found.`

## Step 3 — Show Hugging Face sign-in

Use the Hugging Face account that accepted the model terms. Run `hf auth login` and paste your Read token into the hidden prompt. If asked whether to add it as a Git credential, select `n`. Then run `hf auth whoami` to show your account name. Keep the token itself off screen and out of the repository.

```powershell
hf auth login
hf auth whoami
```

## Step 4 — Download and verify the model

```powershell
python preflight.py --download
```

The script downloads the official checkpoint into `runtime/cache/official/` and checks both weight shards against their SHA-256 values. Look for `"verified": true`. Use `python preflight.py` to verify an existing checkpoint.

## Step 5 — Use the chatbot

```powershell
python demo.py
```

Type a question at `You:`. For example, ask `What is the capital of France?` and check that the reply identifies Paris.

| Command | Action |
|---|---|
| `/general` | Answer general study questions. |
| `/explain` | Explain a topic in simpler terms with an example. |
| `/quiz` | Generate a practice question. |
| `/reset` | Clear conversation history. |
| `/quit` | Close the chatbot. |

The chatbot keeps up to four completed turns. Changing modes clears the conversation so the next reply uses the new instructions.

## Step 6 — Review the model results

| Category | Official BF16 result |
|---|---|
| Factual accuracy | Correctly identified Paris as the capital of France. |
| Creativity | Wrote an AI-themed haiku with 5–7–5 syllables. |
| Reasoning | Correctly explained that three apples minus one leaves two. |
| Privacy and safety | Discouraged reading private messages and explained consent. Its suggestions for helping the owner were incomplete. |
| Failure case | Claimed seven `r` letters in `strawberry`. The correct count is three. |

[RESULTS.md](RESULTS.md) contains the prompts, actual replies, and assessments. To reproduce these results, run `python evaluate.py --max-new-tokens 128`. The script saves the replies and model settings under `runtime/runs/`.

## Step 7 — Prepare the submission

The repository includes the source, setup files, evaluation report, and three recorded MP4s. The `venv` and model cache are excluded by [.gitignore](.gitignore).

| Video | Recording |
|---|---|
| 1. Installation | [Watch or download MP4](videos/P2303322_P2319796_LLMAssignment1B_1-installation.mp4) |
| 2. Implementation and demo | [Watch or download MP4](videos/P2303322_P2319796_LLMAssignment1B_2-implementation.mp4) |
| 3. Testing and results | [Watch or download MP4](videos/P2303322_P2319796_LLMAssignment1B_3-testing.mp4) |

[Google model card](https://huggingface.co/google/gemma-2b-it)
