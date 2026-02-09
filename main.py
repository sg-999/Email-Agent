from src.agent import EmailAgent


def main():
    print("=" * 60)
    print("🤖 EMAIL AGENT - Interactive Mode")
    print("=" * 60)
    print("Commands:")
    print("  • Type your query naturally (e.g., 'show unread emails')")
    print("  • Type 'quit' or 'exit' to stop")
    print("=" * 60 + "\n")

    # Initialize agent
    agent = EmailAgent()

    while True:
        try:
            # Get user input
            user_query = input("\n💬 You: ").strip()

            # Check for exit commands
            if user_query.lower() in ["quit", "exit", "bye"]:
                print("\n👋 Goodbye!")
                break

            # Skip empty queries
            if not user_query:
                continue

            # Process query
            result = agent.process_query(user_query)

            # Display result
            print("\n" + "=" * 60)
            print("🤖 Agent Response:")
            print("=" * 60)
            print(result)
            print("=" * 60)

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again with a different query")


if __name__ == "__main__":
    main()
