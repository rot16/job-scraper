# Python code to illustrate Sending mail with attachments 
# from your Gmail account 

# libraries to be imported 
import json
import configparser
from datetime import datetime
import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

config = configparser.Configparser()
config.read('config.ini')

def applyForJob(toAddress, subject, message):
    
    # instance of MIMEMultipart 
    msg = MIMEMultipart() 
    
    # storing the senders email address 
    msg['From'] = config['Email'].get('from_address') 
    
    # storing the receivers email address 
    msg['To'] = toAddress 
    
    # storing the subject 
    msg['Subject'] = subject
    
    # string to store the body of the mail 
    #body = "Just checking to see if this works"
    
    # attach the body with the msg instance 
    msg.attach(MIMEText(message, 'plain')) 
    
    # open the file to be sent 
    filename = config['Email'].get('resume_file_name')
    attachment = open(config['Email'].get('resume_file_path'), "rb") 
    
    # instance of MIMEBase and named as p 
    p = MIMEBase('application/pdf', 'pdf') 
    
    # To change the payload into encoded form 
    p.set_payload((attachment).read()) 
    
    # encode into base64 
    encoders.encode_base64(p) 
    
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
    
    # attach the instance 'p' to instance 'msg' 
    msg.attach(p) 
    
    # creates SMTP session 
    s = smtplib.SMTP(config['Email'].get('smtp_server'), config['Email'].getint('smtp_port')) 
    
    # start TLS for security 
    s.starttls() 
    
    # Authentication 
    s.login(fromaddr, config['Email'].get('email_password')) 
    
    # Converts the Multipart msg into a string 
    text = msg.as_string() 
    
    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 
    
    # terminating the session 
    s.quit() 

def log(message):
  logfile = open(config['Files'].get('logfile_filename', 'a')
  now = datetime.now()
  timestamp = now.strftime("%Y/%m/%d %H:%M:%S - ")
  print(timestamp + message, file=logfile)
  logfile.close()

with open(config['Files'].get('queued_jobs_filename'), 'r') as f:
    jobDict = json.load(f)
    jobIDs = list(jobDist.keys())
    for jobID in jobIDs:
        job = jobDict.pop(jobID)
        applyForJob(job['email'], job['subject'], job['message']
        with open(config['Files'].get('queued_jobs_filename'), 'w') as g:
            json.dump(jobDict, g)
log('Applied for ' + len(jobIDs) + ' jobs.')
