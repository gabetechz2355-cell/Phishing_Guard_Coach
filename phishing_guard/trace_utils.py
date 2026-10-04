"""show_trace, copied from the class tutorial notebook (cell 12)."""

from agents import ItemHelpers


def show_trace(result):
    """Print the messages and tool events recorded in an agent result."""
    for item in result.new_items:
        print("\nEvent:", item.type)
        print("Agent:", item.agent.name)

        if item.type == "tool_call_item" and item.raw_item.type == "function_call":
            print("Tool:", item.raw_item.name)
            print("Arguments:", item.raw_item.arguments)
        elif item.type == "tool_call_output_item":
            print("Tool result:", item.output)
        elif item.type == "message_output_item":
            print("Message:", ItemHelpers.text_message_output(item))
