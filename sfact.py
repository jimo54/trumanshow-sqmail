import smtplib, random
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

spam = []
f = open('spam_samples.txt')
line = f.readline()
count = 0
sender = subj = body = ''
html = ''
while line:
    count += 1
    if line[:4] == '++++':
        if count <= 1:
            continue
        else:
            html += '''</p>
            </body>
            </html>'''
            spam.append([sender, subj, html, body])
        body = ''
        html = '''<html>
        <head></head>
        <body>
        <p>'''
    elif line[:4] == 'From':
        sender = line[6:]
    elif line[:4] == 'Subj':
        subj = line[9:]
    else:
        body += line
        html += line.strip() + '<br />'
    line = f.readline()
html += '''</p>
</body>
</html>'''
spam.append([sender, subj, html, body])
f.close()

item = random.choice(spam)
sender = item[0]
subject = item[1]
to = 'jim@elko.26maidenlane.net'
server = to.split('@')[1]
# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = sender
msg['To'] = to

# Create the body of the message (a plain-text and an HTML version).
html = item[2]
text = item[3]

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

# Send the message via local SMTP server.
s = smtplib.SMTP(server)
# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
s.sendmail(sender, to, msg.as_string())
s.quit()
