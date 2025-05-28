# --- THIS FILE IS NOW CORRECT AND SAVED ---

# src/prompt.py

system_prompt = """
You are a medical expert. Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know. Keep the answer concise.
Context: {context}
"""

# THE FIX: Move the CLI code inside this block
if __name__ == '__main__':
    import fire
    # You might have other code here for testing the prompt from the command line
    fire.Fire()