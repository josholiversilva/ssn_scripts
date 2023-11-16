import random
import smtplib
from email.message import EmailMessage

PAIRINGS_LIST = "pairings_list.txt"
FROM_EMAIL = "secretsantaneyigas@gmail.com"

def get_names_and_emails():
    pairings_list = open(PAIRINGS_LIST, "r")
    content = pairings_list.readlines()

    pairings = []
    for line in content:
        clean_line = line.rstrip('\n')
        pairings.append(clean_line)
    pairings_list.close()

    return pairings

def create_pairings(names_and_emails):
    # receiver to secret santa
    pairings = {}
    receivers = set()
    previous_secret_santas = get_previous_secret_santas()

    for name_and_email in names_and_emails:
        name, email = name_and_email.split(",")
        receiver_name_and_email = choose_pairing(name_and_email, names_and_emails, previous_secret_santas, receivers)
        pairings[name_and_email] = receiver_name_and_email

    return pairings

def choose_pairing(ssn_name_and_email, receiver_names_and_emails, previous_secret_santas, receivers):
    ssn_name, ssn_email = ssn_name_and_email.split(",") 
    receiver_name_and_email = random.choice(receiver_names_and_emails)
    receiver_name, receiver_email = receiver_name_and_email.split(",")

    while ssn_name == receiver_name or receiver_name in receivers or previous_secret_santas.get(ssn_name, "") == receiver_name:
        receiver_name_and_email = random.choice(receiver_names_and_emails)
        receiver_name, receiver_email = receiver_name_and_email.split(",")

    receivers.add(receiver_name)
    return receiver_name_and_email

def send_email(pairings):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(FROM_EMAIL, "udsn orou ryhf zcmk")

    for ssn,receiver in pairings.items():
        ssn_name,ssn_email = ssn.split(",")
        receiver_name,_ = receiver.split(",")

        msg = EmailMessage()
        msg['Subject'] = "Secret Santa Pairings!!! <3"
        msg['From'] = FROM_EMAIL
        msg['To'] = ssn_email
        msg.set_content("Hi {}, you have: {}".format(ssn_name, receiver_name))
        s.send_message(msg)

    s.quit()

def get_previous_secret_santas():
    # change this to read from pairings.json as years go by
    return {
            "josh": "victoria",
            "iris": "ana",
            "victoria": "iris",
            "vincent": "eric",
            "eric": "melissa",
            "ana": "vincent",
            "brian": "ryan",
            "bryan": "brian",
            "shawn": "josh",
            "melissa": "bryan",
            "ryan": "shawn"
        }

if __name__ == '__main__':
    names_and_emails = get_names_and_emails()
    pairings = create_pairings(names_and_emails)
    send_email(pairings)

