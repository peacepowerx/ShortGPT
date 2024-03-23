from email_validator import validate_email, EmailNotValidError

def is_valid_email(email_address):
    """
    Validates an email address for both format correctness and deliverability.
    :param email_address: str, the email address to validate
    :return: bool, True if the email is valid and deliverable, False otherwise
    """
    try:
        # Validate and check for deliverability.
        validate_email(email_address, check_deliverability=True)
        return True
    except EmailNotValidError as e:
        # Email is not valid or not deliverable, exception message is human-readable.
        print(str(e))
        return False

# Example usage:
# email = "user@example.com"
# if is_valid_email(email):
#     print(f"The email address {email} is valid and deliverable.")
# else:
#     print(f"The email address {email} is not valid or not deliverable.")
