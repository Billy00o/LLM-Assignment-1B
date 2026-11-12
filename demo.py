from src.model import load_model, get_response, build_messages

def main():
    try:
        model, tokenizer = load_model()
    except FileNotFoundError as error:
        raise SystemExit(str(error)) from None
    history, mode = [], "general"
    print("Gemma Study Helper: /general /explain /quiz /reset /quit")
    while True:
        try: prompt = input("You: ").strip()
        except (EOFError, KeyboardInterrupt): break
        if prompt in ("quit", "/quit"): break
        if prompt == "/reset":
            history.clear()
            print("History cleared.")
            continue
        if prompt in ("/general", "/explain", "/quiz"):
            mode = prompt[1:]
            history.clear()
            print("Mode:", mode)
            continue
        if not prompt: continue
        try:
            reply = get_response(prompt, model, tokenizer, history=history, mode=mode)
            history = build_messages(prompt, history, mode) + [{"role": "assistant", "content": reply}]
            history = history[-8:]
            print("Gemma:", reply)
        except ValueError as error: print(error)

if __name__ == "__main__": main()
