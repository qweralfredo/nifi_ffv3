import io
import json
import requests
import ff 
from faker import Faker

def send_data(data, attributes, url):
    data_str = json.dumps(data)
    input_stream = io.BytesIO(data_str.encode())
    output_stream = io.BytesIO()    
    dff = ff.package_flowfile(input_stream, output_stream, attributes)    
    packaged_data = output_stream.getvalue()
    files = {"files": ('flowfile.bin', packaged_data, 'multipart/form-data')}    
    response = requests.post(url, files=files)
    response.raise_for_status()
    return response.text

for i in range(1000):      
    fake = Faker()
    data = {"name": fake.name(), "text": fake.text(), "address": fake.address(), "email": fake.email(), "phone": fake.phone_number(), "date": f'''{fake.date_time()}'''}
    attributes = {"filename": fake.file_name()+".json", "author": fake.name(), "source": fake.url(), "timestamp": f'''{fake.date_time()}'''}
    url = "http://nifi.learn-or-die.io:18333"
    print(send_data(data, attributes, url))