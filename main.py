from bot_utilities.ai_utils import generate_response


def main():
    # Open the file in read mode
    with open('instructions/guardian.txt', 'r') as file:
        # Read the content of the file into the variable
        instructions = file.read()

    while True:
        user_input = input('>>>')
        generate_response(instructions, {'id': 0, 'message': user_input, 'user_name': 'Tyrael', 'ai_name': 'Guardian'})


if __name__ == "__main__":
    main()
