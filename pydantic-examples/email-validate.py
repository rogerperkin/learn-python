from pydantic import BaseModel, EmailStr, field_validator, ValidationError
from rich.console import Console
from rich.text import Text
from constants import Questions  # Importing the Question Enum

# Initialize the Rich console
console = Console()

class EmailModel(BaseModel):
    email: EmailStr

    # Custom validator to check if email ends with '@company.com'
    @field_validator('email')
    def check_company_email(cls, v):
        if not v.endswith('@company.com'):
            raise ValueError('Email must end with @company.com')
        return v

def ask_for_email():
    while True:  # Keep asking until a valid email is provided
        # Styled question with Rich
        question = Text(f"{Questions.EMAIL.value} (must end with @company.com): ", style="bold cyan")
        console.print(question, end="")

        # Input collection
        email_input = input().strip()

        try:
            # Create an EmailModel instance to validate the email
            email = EmailModel(email=email_input)
            success_msg = Text(f"Email '{email.email}' is valid.", style="bold green")
            console.print(success_msg)
            break  # Exit the loop once a valid email is entered
        except ValidationError:
            error_msg = Text("This email is invalid, try again.", style="bold red")
            console.print(error_msg)

if __name__ == "__main__":
    ask_for_email()
