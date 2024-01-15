import re

import requests
from bs4 import BeautifulSoup, TemplateString, CData, NavigableString

from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser


def robots_data(url):
    parsed_uri = urlparse(url)
    base_url = f"{parsed_uri.scheme}://{parsed_uri.netloc}/"
    robots_url = urljoin(base_url, 'robots.txt')

    robot_parser = RobotFileParser()
    robot_parser.set_url(robots_url)
    robot_parser.read()
    rrate = robot_parser.request_rate("*")
    # Request rate to limit the behaviour of of fetching multiple pages simultaneously
    robot_request_rate = rrate.requests if rrate else None
    robot_request_seconds = rrate.seconds if rrate else None
    # Used to limit crawlers from hitting the site too frequently.
    robot_crawl_delay = robot_parser.crawl_delay("*")

    can_fetch_site = robot_parser.can_fetch("*", url)

    return {
        "request_rate_requests": robot_request_rate,
        "request_rate_seconds": robot_request_seconds,
        "crawl_delay": robot_crawl_delay,
        "can_fetch": can_fetch_site
    }


# def can_fetch(url, user_agent='*'):
#     from io import StringIO
#     from robotexclusionrulesparser import RobotExclusionRulesParser
#     parsed_uri = urlparse(url)
#     base_url = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
#     robots_url = urljoin(base_url, 'robots.txt')
#
#     response = requests.get(robots_url)
#     if response.status_code != 200:
#         return False
#
#     rerp = RobotExclusionRulesParser()
#     rerp.parse(StringIO(response.text))
#
#     return rerp.is_allowed(user_agent, url)
#
#
# # # Test
# # url = 'https://www.example.com'
# # print(can_fetch(url))

def is_url(url: str) -> bool:
    """ Return a boolean value if the url looks like a URL. """
    if ":" not in url:
        return False
    scheme = url.split(":", 1)[0].lower()
    if scheme:
        return scheme in ["http", "https", "file", "ftp"]
    return False


def get_html_from_url(url):
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Max-Age": "3600",
    }
    if not is_url(url):
        raise TypeError("URL is invalid")
    response = requests.get(url, headers)
    return response.content


def parse_html(url):
    """ This function parses the html returned by the url param
    :param url: The url to fetch and parse.
    :return: A list of important html tags with their corresponding contents.
    :rtype: A List.
    :rformat: [{"head": "head content", "title": "title content", "meta": {"meta contents"}, "body": "body
    content"}]
    :Date: September 7, 2022.
    """
    html_parsed_dict = dict()
    print("SUMMARY HTML PARSER")
    html_doc = get_html_from_url(url)
    # soup = BeautifulSoup(html_doc, 'html.parser')
    soup = BeautifulSoup(html_doc, 'lxml')
    # soup.footer.decompose()
    styles = soup.style
    # print(styles)
    scripts = soup.script
    # Remove scripts and styles from the html content
    styles.decompose() if styles else ...
    scripts.decompose() if scripts else ...
    html_parsed_dict.update({"head": soup.head})
    html_parsed_dict.update({"title": soup.title})
    # html_parsed_dict.update(("meta", {_: _} for _ in soup.findall("meta")))
    # body_content = soup.body.footer.decompose()
    # soup.smooth()
    # html_parsed_dict.update({"body": soup.body})
    html_parsed_dict.update({"body": soup.get_text()})
    return html_parsed_dict


def html_body_content(url, squeeze=False):
    html_data = parse_html(url)
    res = "".join([_ for _ in html_data.get("body", None).strings])
    # res = "".join([_ for _ in html_data.get("body", None).stripped_strings])
    # return re.sub(r"\s+", " ", re.sub(r"\n", " ", res)) if squeeze else re.sub(r"\n\s*", "\n", res)
    return {
        'title': html_data.get('title', '').string if html_data.get('title') is not None else '',
        # 'body': re.sub(r"\s+|<.*>", " ", res) if squeeze else re.sub(r"\n\s*", "\n", res)
        'body': clean_text(res)
    }
    # return res.replace("\n", " ").replace('\t', ' ') if squeeze else res


def remove_negligible_tags(html_body: str):
    """
    Removes certain html tags which can be tagged as unnecessary
    with respect to the web body content
    1. <img />
    2. <forms></forms>
    3. <legend></legend>
    4. <footer></footer>
    @type html_body: str
    """


def clean_text(text: str):
    """
    Code copied from medium post.
    https://towardsdatascience.com/create-a-simple-search-engine-using-python-412587619ff5
    :param text:
    :return:
    :Date: November 26, 2022.
    """
    # Remove Unicode
    cleaned_text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    # Remove Mentions
    cleaned_text = re.sub(r'@\w+', '', cleaned_text)
    # Lowercase the document
    # cleaned_text = cleaned_text.lower()
    # Remove punctuations
    # cleaned_text = re.sub(r'[%s]' % re.escape(string.punctuation), ' ', cleaned_text)
    # Lowercase the numbers
    # cleaned_text = re.sub(r'[0-9]', '', cleaned_text)
    # Remove the doubled space
    cleaned_text = re.sub(r'\s{2,}', '\n', cleaned_text)
    # Remove HTML tags - January 14, 2023.
    cleaned_text = re.sub("<.*?>", "", cleaned_text)
    # cleaned_text = re.sub(r'\b[^\S{1}]\w+(\r\n|\r|\n){1}', '<one>\n', cleaned_text)
    # cleaned_text = re.sub(r'\b[^ ]{1}[\w+]\s[^ ]*\b', '<one>\n', cleaned_text, flags=re.MULTILINE)
    # cleaned_text = re.sub(r'\b\W+\b', '<one>\n', cleaned_text, flags=re.MULTILINE)
    # Remove single words from the body of text
    cleaned_text = remove_n_lineword(cleaned_text, 4, flatten=True)
    # print(cleaned_text)
    return cleaned_text


def remove_n_lineword(text, n, flatten=False) -> str:
    """
    Removes newline words that are n words
    :param text: Text to remove from
    :param n: Number of new line words to remove
    :param flatten: Whether to flatten the result. i.e., remove all newline characters.
    :return: filtered text.
    """
    # print(text.split('\n'))
    filtered_text = filter(lambda x: len(x.split(' ')) > n, text.split('\n'))
    # print(list(filtered_text))
    return " ".join(filtered_text) if flatten else "\n".join(filtered_text)


def how_to_clean_html_definition(tag):
    forbidden_tags = "img form a nav script style comment svg footer button".split()
    accepted_tags = "html body section article div span header h1 h2 h3 h4 h5 h6 p b i ul li main details label " \
                    "summary template table strong turbo-frame readme-toc".split()
    check: bool = False
    if tag.has_attr('hidden'):
        check = check or True
    if tag.string:
        if re.compile(r"^{+[A-Za-z_.{} ]+}$").search(tag.string):
            check = check or True
    if tag.name not in accepted_tags:
        check = check or True
    return check


def html_parsed_content(url):
    html_doc = get_html_from_url(url)
    soup = BeautifulSoup(html_doc, 'lxml')
    # Remove all the tags which are negligible
    [_.decompose() for _ in soup.find_all(how_to_clean_html_definition)]
    # print(soup.stripped_strings)
    soup.smooth()
    return soup.get_text(separator=" ", strip=True, types=(NavigableString, CData, TemplateString))


async def get_text_content_from_html(html_content) -> str:
    """
    This function gets text from html contents passed as a string
    It uses beautifulsoup for parsing the html contents
    :param: html_content -> the already fetched html page content
    :return: the text from the html_content
    :rtype: str
    """
    # Add BS parsing here, and return it.
    soup = BeautifulSoup(str(html_content), 'lxml')
    page_icon = soup.find("link", attrs={'rel': 'icon'})
    # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon'})
    # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '128x128'})
    # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '96x96'})
    # page_icon = soup.find("link", attrs={'rel': 'apple-touch-icon', 'size': '256x256'})
    [_.decompose() for _ in soup.find_all(how_to_clean_html_definition)]
    page_text = soup.get_text(separator="\n", strip=True, types=(NavigableString, CData, TemplateString))

    # Remove some unnecessary
    page_text_list: list = list()
    for _ in page_text.split("."):
        # _ = _.replace("\n", " ")
        _ = re.sub(r'\s{1,}', ' ', _)
        if len(_.split(" ")) <= 4:
            continue
        page_text_list.append(_)
    return "".join(page_text_list)
