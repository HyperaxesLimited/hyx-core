"""
Conversational LLM interface for HyperAxes Core.

Author: Nicola Sabino
Company: Hyperaxes
Date: 2025-12-07
"""

import argparse
import json
import logging
from typing import List, Dict

from pcd_hyperaxes_core.llm.state import ConversationState
from pcd_hyperaxes_core.llm.executor import HyperAxesFunctionExecutor
from pcd_hyperaxes_core.llm.tools import HYPERAXES_TOOLS

logger = logging.getLogger(__name__)


SYSTEM_PROMPT_TEMPLATE = """You are HyperAxes Assistant, an expert in point cloud analysis.
You help users analyze and compare 3D point cloud data from LAS, LAZ, PLY, PCD, and XYZ files.

Your approach is STEP-BY-STEP and GUIDED:
1. First, ask the user for source and target file paths
2. Then, explain default parameters or ask if they want to customize them
3. Confirm the configuration before running the analysis
4. Present results clearly with statistics and summaries
5. Offer to save results or create visualizations

Always use your available functions to interact with the HyperAxes system.
Be conversational, helpful, and explain technical concepts in simple terms.
When file paths are provided, always use absolute paths.

Current state: {state_summary}"""


WELCOME_BANNER = """
================================================================
  ⚡ HyperAxes Point Cloud Analysis - LLM Chat Interface
================================================================

Welcome to the HyperAxes conversational interface!

Type your requests in natural language to analyze point clouds.
Commands:
  - Type 'quit', 'exit', or 'bye' to end the conversation
  - Type 'status' to see current configuration

Let's get started! 🚀
"""


class HyperAxesChat:
    """Conversational LLM interface for HyperAxes Core."""

    def __init__(self, model: str = "llama3.1"):
        """
        Initialize the chat interface.

        Args:
            model: Ollama model to use
        """
        self.model = model
        self.state = ConversationState()
        self.executor = HyperAxesFunctionExecutor(self.state)
        self.logger = logging.getLogger(__name__)

    def start(self):
        """Start the conversational loop."""
        print(WELCOME_BANNER)

        # Verify Ollama is available
        try:
            import ollama

            ollama.list()
            self.logger.info(f"Connected to Ollama, using model: {self.model}")
        except Exception as e:
            print(f"\n❌ Error: Could not connect to Ollama.")
            print(f"   {str(e)}")
            print(f"\n   Make sure Ollama is running:")
            print(f"   1. Install Ollama from https://ollama.ai")
            print(f"   2. Start the server: ollama serve")
            print(f"   3. Pull the model: ollama pull {self.model}")
            return

        # Main loop
        while True:
            try:
                user_input = input("\n💬 You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit", "bye"]:
                    print("\n👋 Goodbye! Analysis session ended.\n")
                    break

                if user_input.lower() == "status":
                    print(f"\n📊 Current state: {self.state.get_summary()}\n")
                    continue

                # Process message
                response = self._chat(user_input)
                print(f"\n🤖 Assistant: {response}")

            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted. Type 'quit' to exit cleanly.")
                continue
            except Exception as e:
                self.logger.error(f"Error in chat loop: {e}", exc_info=True)
                print(f"\n❌ Error: {e}")

    def _chat(self, user_message: str) -> str:
        """
        Process a user message and return assistant response.

        Args:
            user_message: User's input message

        Returns:
            Assistant's response
        """
        import ollama

        # Add user message to history
        self.state.conversation_history.append({"role": "user", "content": user_message})

        # Prepare messages with system prompt
        messages = self._build_messages()

        try:
            # First call to Ollama
            self.logger.debug(f"Calling Ollama with {len(messages)} messages")
            response = ollama.chat(model=self.model, messages=messages, tools=HYPERAXES_TOOLS)

            # Check if there are tool calls
            if response.get("message", {}).get("tool_calls"):
                self.logger.info(f"LLM requested {len(response['message']['tool_calls'])} tool call(s)")

                # Add assistant message with tool calls to history
                self.state.conversation_history.append(response["message"])

                # Execute each tool
                for tool_call in response["message"]["tool_calls"]:
                    function_name = tool_call["function"]["name"]
                    arguments = tool_call["function"]["arguments"]

                    self.logger.info(f"Executing: {function_name}({arguments})")
                    result = self.executor.execute_function(function_name, arguments)

                    # Add tool result to history
                    self.state.conversation_history.append({"role": "tool", "content": json.dumps(result)})

                # Second call to Ollama to get final response
                messages = self._build_messages()
                final_response = ollama.chat(model=self.model, messages=messages)
                assistant_message = final_response["message"]["content"]

            else:
                # No tool calls, direct response
                assistant_message = response["message"]["content"]

            # Save assistant response to history
            self.state.conversation_history.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            self.logger.error(f"Error in chat: {e}", exc_info=True)
            return f"I encountered an error: {str(e)}"

    def _build_messages(self) -> List[Dict[str, str]]:
        """
        Build message list with system prompt for Ollama.

        Returns:
            List of messages
        """
        system_message = {
            "role": "system",
            "content": SYSTEM_PROMPT_TEMPLATE.format(state_summary=self.state.get_summary()),
        }

        return [system_message] + self.state.conversation_history


def main():
    """Entry point for pcd-hyperaxes-chat command."""
    parser = argparse.ArgumentParser(
        prog="pcd-hyperaxes-chat",
        description="Conversational LLM interface for HyperAxes point cloud analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pcd-hyperaxes-chat
  pcd-hyperaxes-chat --model mistral
  pcd-hyperaxes-chat --model qwen2.5

For more information, visit: https://github.com/hyperaxes/pcd-hyperaxes
        """,
    )

    parser.add_argument(
        "--model",
        default="llama3.1",
        help="Ollama model to use (default: llama3.1)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")

    # Start chat
    chat = HyperAxesChat(model=args.model)
    chat.start()


if __name__ == "__main__":
    main()
