import smtplib
def send_email(message: str, address: str):

    # Credentials
    username = 'timemanagement131@gmail.com'
    password = 'cmpe131f17'

    # mail is being sent :
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    print("MESSAGE - logging into gmail...")
    server.login(username,password)
    print("MESSAGE - sending mail: ADDRESS: %s CONTENTS: %s" % (address, message))
    server.sendmail(username, address, message)
    server.quit()

if __name__ == "__main__":
    send_email("hello", "7206337812@vzwpix.com")
