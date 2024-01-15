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


# test_url: str = "https://www.jarsofclay.com/"
# test_url: str = "https://jarchives.com/"
test_url: str = "https://arisesister.com/index.php/2018/03/06/treasure-jars-clay/"
r_data = robots_data(test_url)
print(r_data.get("can_fetch"))
print(r_data.get("crawl_delay"))
