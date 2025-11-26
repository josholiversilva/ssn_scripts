import random
import smtplib
import json
import time
from email.message import EmailMessage
from users import Users

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

    while ssn_name == receiver_name or receiver_name in receivers or received_previously(ssn_name, receiver_name, previous_secret_santas):
        receiver_name_and_email = random.choice(receiver_names_and_emails)
        receiver_name, receiver_email = receiver_name_and_email.split(",")

        if sorted(ssn_name+receiver_name) in [sorted("irissusan"), sorted("vincentiris"), sorted("irisbryan")]:
            continue

        
    receivers.add(receiver_name)
    return receiver_name_and_email

def received_previously(ssn_name, receiver_name, previous_secret_santas):
    for pairings in previous_secret_santas:
        if pairings.get(ssn_name) == receiver_name:
            return True

    return False

def send_emails(pairings):
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

def girl_no_match_girl(ssn_name, receiver):
    if ssn_name not in Users.get_girls_to_rig():
        return False

    # skip if girl should be rigged
    if ssn_name in Users.get_girls():
        if receiver in Users.get_girls():
            return False

    return True

def get_previous_secret_santas():
    with open('pairings.json', 'r') as file:
        data = json.load(file)["ssn"]
    
    pairings = [item["pairings"] for item in data]

    return pairings

if __name__ == '__main__':
    names_and_emails = get_names_and_emails()
    pairings = create_pairings(names_and_emails)
    print(pairings)
    # send_emails(pairings)
