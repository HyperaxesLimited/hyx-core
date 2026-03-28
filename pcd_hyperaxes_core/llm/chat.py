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


SYSTEM_PROMPT_TEMPLATE = """You are HyperAxes Assistant for point cloud analysis (LAS/LAZ/PLY/PCD/XYZ).

Guide users step-by-step. Be BRIEF and DIRECT - use 1-2 sentences max per response:
1. Ask for source/target paths
2. Confirm parameters
3. Present results (numbers only)
4. Offer save/visualize

CRITICAL: Keep responses SHORT. No explanations unless asked.
State: {state_summary}"""


WELCOME_BANNER = """
================================================================
  ⚡ HyperAxes Point Cloud Analysis - LLM Chat Interface
================================================================

Welcome to the HyperAxes conversational interface!

✨ Features: Streaming responses • Real-time progress • Step-by-step guidance

Commands:
  - Type 'quit', 'exit', or 'bye' to end the conversation
  - Type 'status' to see current configuration
  - Type 'help' to see what I can do

Let's get started! 🚀
"""


CAPABILITIES_RESPONSE = """I can help you analyze and compare 3D point clouds. Here's what I can do:

📂 **File Management**
   • Load point clouds (LAS, LAZ, PLY, PCD, XYZ formats)
   • Set source and target files for comparison

⚙️ **Configuration**
   • Configure preprocessing (voxel size, outlier removal)
   • Configure analysis parameters (distance/region thresholds)
   • Configure output format (JSON, CSV, GeoJSON, text)

🔍 **Analysis**
   • Register and align point clouds using ICP
   • Detect differences and changes between scans
   • Cluster change regions
   • Compute detailed statistics

📊 **Output & Visualization**
   • Save results in multiple formats
   • Generate 3D web visualization with three.js
   • Export GeoJSON for GIS applications

Just tell me what you want to do in natural language!"""


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

                # Check for help/capabilities request (predefined response to save latency)
                user_lower = user_input.lower()
                if any(
                    keyword in user_lower
                    for keyword in [
                        "help",
                        "what can you do",
                        "what do you do",
                        "capabilities",
                        "features",
                        "how can you help",
                        "what are you",
                        "cosa sai fare",
                        "cosa puoi fare",
                        "aiuto",
                    ]
                ):
                    print(f"\n{CAPABILITIES_RESPONSE}\n")
                    continue

                # Process message (prints streaming response)
                self._chat(user_input)

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
        import sys

        # Add user message to history
        self.state.conversation_history.append({"role": "user", "content": user_message})

        # Prepare messages with system prompt
        messages = self._build_messages()

        try:
            # Show thinking indicator
            print("\n🤔 Thinking...", end="", flush=True)

            # First call to Ollama (non-streaming to detect tool calls)
            self.logger.debug(f"Calling Ollama with {len(messages)} messages")
            response = ollama.chat(model=self.model, messages=messages, tools=HYPERAXES_TOOLS)

            # Clear thinking indicator
            print("\r" + " " * 20 + "\r", end="", flush=True)

            # Check if there are tool calls
            if response.get("message", {}).get("tool_calls"):
                self.logger.info(f"LLM requested {len(response['message']['tool_calls'])} tool call(s)")

                # Add assistant message with tool calls to history
                self.state.conversation_history.append(response["message"])

                # Execute each tool with progress indicator
                for i, tool_call in enumerate(response["message"]["tool_calls"], 1):
                    function_name = tool_call["function"]["name"]
                    arguments = tool_call["function"]["arguments"]

                    # Show function execution indicator
                    print(f"⚙️  Executing: {function_name}...", flush=True)

                    self.logger.info(f"Executing: {function_name}({arguments})")
                    result = self.executor.execute_function(function_name, arguments)

                    # Add tool result to history
                    self.state.conversation_history.append({"role": "tool", "content": json.dumps(result)})

                # Second call to Ollama with streaming
                print("\n🤖 Assistant: ", end="", flush=True)
                messages = self._build_messages()

                assistant_message = ""
                for chunk in ollama.chat(model=self.model, messages=messages, stream=True):
                    content = chunk["message"]["content"]
                    print(content, end="", flush=True)
                    assistant_message += content

                print()  # New line after streaming

            else:
                # No tool calls, direct response with streaming
                print("\n🤖 Assistant: ", end="", flush=True)

                assistant_message = ""
                for chunk in ollama.chat(
                    model=self.model, messages=messages, tools=HYPERAXES_TOOLS, stream=True
                ):
                    content = chunk["message"]["content"]
                    print(content, end="", flush=True)
                    assistant_message += content

                print()  # New line after streaming

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
  pcd-hyperaxes-chat                      # Use default llama3.1
  pcd-hyperaxes-chat --model llama3.2:3b  # Faster, smaller model
  pcd-hyperaxes-chat --model qwen2.5:3b   # Technical tasks

Note: Model MUST support function calling (tools).
      Models like phi3:mini do NOT work.

For more information, visit: https://github.com/hyperaxes/pcd-hyperaxes
        """,
    )

    parser.add_argument(
        "--model",
        default="llama3.1",
        help="Ollama model to use - MUST support function calling (default: llama3.1). Fast options: llama3.2:3b, qwen2.5:3b",
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
