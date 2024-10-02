from requests_toolbelt import MultipartEncoder
import requests
import json

png_endpoint_url = 'https://api.pdfrest.com/png'

# Function to download the PDF file from the given URL
def download_pdf(pdf_url):
    response = requests.get(pdf_url)
    if response.status_code == 200:
        return response.content
    else:
        print("Failed to download PDF:", response.status_code, response.text)
        return None

# Specify the PDF URL
pdf_url = 'https://craftmypdf-gen.s3.ap-southeast-1.amazonaws.com/0cd136a6-04cc-43e3-9865-4450607c40b8/output.pdf?AWSAccessKeyId=AKIA6ENCBKJYLWJUD36X&Expires=1727886873&Signature=urZiz%2Bu1FQa5b3oqBKFskGQWRG4%3D'

# Download the PDF
pdf_content = download_pdf(pdf_url)

if pdf_content:
    # The /png endpoint can take a single PDF file or id as input and turn them into PNG image files.
    mp_encoder_png = MultipartEncoder(
        fields={
            'file': ('file_name.pdf', pdf_content, 'application/pdf'),
            'pages': '1-last',
            'resolution': '600',
            'color_model': 'gray',
            'output': 'example_png_out',
        }
    )

    # Set the headers that the png endpoint expects.
    headers = {
        'Accept': 'application/json',
        'Content-Type': mp_encoder_png.content_type,
        'Api-Key': '69eecc29-eae0-4a44-b1bd-62ba14945513'  # Place your API key here
    }

    print("Sending POST request to png endpoint...")
    response = requests.post(png_endpoint_url, data=mp_encoder_png, headers=headers)

    print("Response status code: " + str(response.status_code))

    if response.ok:
        response_json = response.json()
        print(json.dumps(response_json, indent=2))
    else:
        print("Error:", response.text)
else:
    print("No PDF content available for conversion.")
