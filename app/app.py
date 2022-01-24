import os
import re
import pytesseract
import boto3
from PIL import Image
import urllib.parse
import json


def lambda_handler(event, context):

    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    print(bucket_name)
    print(file)
    print("Execution started!")
    # pytesseract.pytesseract.tesseract_cmd = r'tesseract/3.4.0/bin/tesseract'


    session = boto3.Session()
    s3_client = session.client('s3')
    # bucket_name = 'rekognition-sample-12012022'
    # s3_folder = 'images'

    lambda_write_path = '/tmp/'

    print("File is downloading")

    dest_pathname = os.path.join(lambda_write_path, file)
    if not os.path.exists(os.path.dirname(dest_pathname)):
        os.makedirs(os.path.dirname(dest_pathname))
    s3_client.download_file(bucket_name, file, dest_pathname)
    print("File downloaded")


    try:
        print("Image Path")
        image_path = '/tmp/'+file
        print(image_path)
        img = Image.open(image_path)

        # Converted = True

        print("Before reading image")
        text = pytesseract.image_to_string(img)
        print(text)
        os.remove(image_path)
        print("File deleted successfullly!")

        new_dict = {}
        print('***************************************************')
        for line in text.split('\n'):
            # print(line.strip())
            # print(type(line))
            if 'Name' in line:
                new_dict['Name'] = line.split(' ', maxsplit=1)[1]

            if 'Member' in line:
                new_dict['Id'] = line.split(' ')[-1]

            if re.search(r'\bGroup\b', line):
                new_dict['Group'] = line.split(' ', maxsplit=1)[1:][0]

            if 'Region' in line:
                new_dict['Region'] = line.split(' ', maxsplit=1)[-1]

            if 'PCP' in line:
                new_dict['Clinic'] = (line.split(' ', maxsplit=2)[-1]).split(' ', maxsplit=2)[0] + ' ' + \
                                     (line.split(' ', maxsplit=2)[-1]).split(' ', maxsplit=2)[1]

            if 'Phone' in line:
                new_dict['ClinicPhone'] = line.split('Phone')[1].split(' ')[1]

            if 'Copay' in line:
                new_dict['Copay'] = str.join(' ', line.split(' ')[1:])

            if 'RXBin' in line:
                new_dict['RXBin'] = line.split(' ')[1]
                new_dict['RXGroup'] = line.split(' ')[3] + " " + line.split(' ')[4]

            if 'State ID' in line:
                new_dict['StateId'] = line.split(' ')[-1]

        print(new_dict)

        output_prefix = 'output/' + file.split('.')[0] + '.json'
        s3 = boto3.resource('s3')
        object = s3.Object(bucket_name, output_prefix)
        object.put(Body=json.dumps(new_dict).encode())
        print("Execution Completed!")

    except Exception as e:
        print(e)
