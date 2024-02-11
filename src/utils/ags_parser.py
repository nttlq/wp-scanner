import argparse


def parser():
    parser = argparse.ArgumentParser(description="Process of scanning a wp site.")
    parser.add_argument(
        "url",
        metavar="URL",
        type=str,
        nargs=1,
        help="The URL of the site to scan.",
    )

    user_agents = ("rand", "win", "mac", "linux", "ipad", "iphone")
    parser.add_argument(
        "--user_agent",
        "-u",
        dest="user_agent",
        type=str,
        choices=user_agents,
        default=user_agents[0],
        nargs=1,
        help="The user agent to use when scanning the site.",
    )

    parser.add_argument(
        "--https",
        "-s",
        action="store_true",
        dest="https",
        default=False,
        help="Use https when scanning the site.",
    )

    args = parser.parse_args()
    return args
