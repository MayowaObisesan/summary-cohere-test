import re

import requests
from bs4 import BeautifulSoup, NavigableString, CData, TemplateString

# URL of the webpage you want to fetch
# url = 'https://github.com'
url = 'https://jarchives.com/'

# Send an HTTP GET request to the URL
response = requests.get(url)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the content you want to save to a file
    page_title = soup.title.string
    # body_content = soup.find('body').get_text()
    # cleaned_body_content = ' '.join(body_content.split())
    # cleaned_body_content = soup.get_text(separator="\n", strip=True,
    #                                      types=(NavigableString, CData, TemplateString))
    page_text = soup.get_text(separator="\n", strip=True,
                              types=(NavigableString, CData, TemplateString))

    # Remove some unnecessary
    page_text_list: list = list()
    for _ in page_text.split("."):
        # _ = _.replace("\n", " ")
        _ = re.sub(r'\s{1,}', ' ', _)
        if len(_.split(" ")) <= 4:
            continue
        page_text_list.append(_)
    cleaned_body_content = "".join(page_text_list)
    # print(soup.contents)

    # You can extract more data as needed

    # Define the filename for the output file
    output_filename = 'webpage_content.txt'

    # Write the extracted content to the output file
    with open(output_filename, 'w', encoding='utf-8') as output_file:
        # output_file.write("Page Title: " + page_title + '\n')
        output_file.write(cleaned_body_content)
        # You can write more data to the file as needed
        print(f"Data written to '{output_filename}'")
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)
