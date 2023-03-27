from email.message import EmailMessage
from email.policy import SMTPUTF8
from jinja2 import Environment, FileSystemLoader

def create_email(from_addr: str, from_name: str, tabmaster_greeting: str, to_addr: str, first_name: str, tablink: str, tournament_name: str) -> EmailMessage:
    """
    Creates an EmailMessage object for sending over SMTP.
    Compiles `body_template` to a plaintext body.
    """
    message = EmailMessage(policy=SMTPUTF8)
    #message.set_charset('utf-8')
    # Email headers
    message["Subject"] = f"{tournament_name} - dein persönlicher Tablink"
    message["From"] = f'{from_name} <{from_addr}>'
    message["To"] = to_addr

    # compile email template (plain text)
    jinja_env = Environment(loader=FileSystemLoader("templates/"), autoescape=True)
    template = jinja_env.get_template("tablink_email")
    text = template.render(name=first_name, link=tablink, tabmaster_greeting=tabmaster_greeting, tournament=tournament_name)
    message.set_payload(text)

    return message