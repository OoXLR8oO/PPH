import win32com.client

ol = win32com.client.Dispatch("Outlook.Application")

olmailitem = 0x0

newmail = ol.CreateItem(olmailitem)
newmail.Subject = "Testing Custom Mail"
newmail.To = "kartikpunna5@outlook.com"

newmail.Body = """
Hello, this is a test email to showcase how to send emails from Python and Outlook V3.
"""

newmail.Display()
newmail.Send()
