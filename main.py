import cv2
import numpy as np
import face_recognition
import os

from email.mime.multipart import MIMEMultipart  # MIMEMultipart is for saying "I have more than one part", and then listing the parts
from email.mime.text import MIMEText  # MimeText is used for sending text emails.
import smtplib
import ssl  # SSL stands for Secure Sockets Layer and is designed to create secure connection between client and server datetime
from datetime import date

today=date.today()
path="ImagesAttendance"
Img_Names = os.listdir(path)
images=[]
imgWithmail=[]
sep=[]
only_emails=[]
only_names=[]
mail_info={}
present=[]
absent=[]
receiver_email=[]
defaulter=[]
defaulter_mail=[]
# defaulter_percentage=[]
t=0


def names_mails():   #seprates the names and emails from the name of image
    for cl in Img_Names:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        imgWithmail.append(os.path.splitext(cl)[0])
    for i in imgWithmail:
        j=i.split('_')
        sep.append(j)
    for i in sep:
        only_names.append(i[0])
        only_emails.append(i[1])
    return only_names, only_emails

print(names_mails())

for i in range(len(only_names)):
    mail_info[only_names[i]]=only_emails[i]
print(mail_info)

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markPresent(name):
    f=open(f"{name}.txt","a")
    f.write(f"Present on {today}\n")
    f.close
    present.append(name)


def markAbsent():
    for i in only_names:
        if i not in present:
            f = open(f"{i}.txt", "a")
            f.write(f"Absent on {today}\n")
            receiver_email.append(mail_info[i])
            f.close


def percentage(): # calculate the total percentage of attendance for all students. Runs when defaulter option is selected
    t = 0
    for i in only_names:
        f = open(f"{i}.txt", "r")
        data = f.read()
        occurenceP = data.count("Present")
        occurenceA = data.count("Absent")
        sum = occurenceA + occurenceP
        x = len(f.readlines())
        p=(occurenceP/sum)*100
        if p<(75):
            defaulter.append(i)
            # defaulter_percentage.append(p)
        with open("All_Class",'a') as file:
            if t==0:
                file.write(f"\n{today}\n")
                t+=1
            file.write(f'Total percentage attendance of {i} is {p}% \n')
        f.close


def send_mail(body, subject):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls  #Modern email servers use port 587 for the secure submission of email for delivery.
    sender_email = "owaisraza7297@gmail.com"  # TODO: replace with your email address
    password = 'qkgtmwqrblkrvgfp'  # TODO: replace with your 16-digit-character password

    today_date = date.today()

    # initialise message instance    msg = MIMEMultipart()
    msg["Subject"] = f"{subject}"
    msg["From"] = sender_email
    msg['To'] = ", ".join(receiver_email)
    ## Plain text
    # text = f"""
    # This mail is about your child's attendance in college."""
    #
    # body_text = MIMEText(text, 'plain')  #
    # msg.attach(body_text)  # attaching the text body into msg

    html = """
    <html>
      <body>
        <p>Dear Sir/Mam,<br>
        <br>
        {} <br>
        Thank you. <br>
        </p>
      </body>
    </html>
    """

    body_html = MIMEText(html.format(body), 'html')  # parse values into html text
    msg.attach(body_html)  # attaching the text body into msg

    context = ssl.create_default_context()
    # Try to log in to server and send email

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo()  # check connection
        server.starttls(context=context)  # Secure the connection
        server.ehlo()  # check connection
        server.login(sender_email, password)
        # Send email here
        print(receiver_email)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Msg sent")
    except Exception as e:
        print("Error in sending mail!")
    finally:
        server.quit()
encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)


while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)
        print(matchIndex)
        if faceDis[matchIndex]<(0.6):
            if matches:
                name = only_names[matchIndex]
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

                if name not in present:
                    markPresent(name)

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) & 0xff == ord("a"):
        markAbsent()
        for i in only_names:
            if i not in present:
                absent.append(i)
        print(absent)
        string=f'This is to inform Your son/daughter is absent in the college on {today}.'
        subject_att='Regarding attendance'
        #send_mail(string, subject_att)
        break

a=input("To generate defaulter list (press Y otherwise press N): ").lower()

if a=='y':
    b = input("Do you want to send defaulter info to parents (press Y otherwise press N)").lower()
    percentage()
    for i in defaulter:
        defaulter_mail.append(mail_info[i])
    for i in only_names:
        with open(f"{i}.txt", "w") as f:
            f.write('')
    print(defaulter)
    string_defaulter=f"Your son/daughter is defaulter in today's defaulter release of {today}."
    subject_defaulter='Regarding college defaulter list'
    receiver_email = defaulter_mail
    if b=='y':
        send_mail(string_defaulter, subject_defaulter)
    else:
        pass

else:
    print('Have a good day!')



with open("Teachers.txt", 'a') as f:
    f.write(f"\n\n{today}\nPresent list\n")
    for i in present:
        f.write(f"{i}\n")
    f.write("\nAbsent list\n")
    for j in absent:
        f.write(f"{j}\n")
