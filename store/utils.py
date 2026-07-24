import requests

def send_sms(number, message):

    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "route": "q",
        "message": message,
        "language": "english",
        "numbers": number
    }

    headers = {
        "authorization": "YOUR_FAST2SMS_API_KEY"
    }

    requests.post(url, data=payload, headers=headers)