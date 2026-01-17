import os
import sys
from chat_session import ChatSession

def main():
    print("Welcome to the ChatGPT-from-Scratch CLI!")
    print("Type '/quit' to exit, '/save' to save history, '/new' for a new session.")
    print("-" * 50)

    # Initialize session
    # Assumes ANTHROPIC_API_KEY is set in environment variables
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set.")
        print("Please export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)

    session = ChatSession()

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if not user_input:
            continue

        if user_input.lower() in ['/quit', '/exit']:
            print("Goodbye!")
            break
        
        if user_input.lower() == '/save':
            filepath = session.save_session()
            print(f"Session saved to {filepath}")
            continue

        if user_input.lower() == '/new':
            session = ChatSession()
            print("Started a new session.")
            continue
            
        session.add_user_message(user_input)
        
        print("Assistant: ", end="", flush=True)
        # Handle streaming response
        response_generator = session.get_response(stream=True)
        
        if isinstance(response_generator, str):
            # Error case
            print(response_generator)
        else:
            for chunk in response_generator:
                print(chunk, end="", flush=True)
            print() # Newline after response

if __name__ == "__main__":
    main()
