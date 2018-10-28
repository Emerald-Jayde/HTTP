import click
import http.client
from urllib3 import util


@click.group()
def cli():
    """httpc is a curl-like application but supports the HTTP protocol."""
    pass


@cli.command()
@click.option("-v", is_flag=True, help="Prints the detail of the response such as protocol, status, and headers.")
@click.option("-h", multiple=True, help="Associates headers to HTTP Request with the format 'key:value'.")
@click.argument("url", type=str, required=True)
def get(url, v, h):
    """Get executes a HTTP GET request for a given URL."""

    conn = http.client.HTTPConnection(util.parse_url(url).host)

    # Stores the headers received from the command line in a dictionary
    flat_h = [item for i in h for item in i.split(":")]
    headers = dict(zip(*[iter(flat_h)] * 2))

    conn.request("GET", url, headers=headers)
    response = conn.getresponse()

    if v:
        print(response.version, response.status, response.reason)
        print(response.headers)
        print(response.read().decode('utf-8'))
    else:
        print(response.read().decode('utf-8'))

    conn.close()


@cli.command()
@click.option("-v", is_flag=True, help="Prints the detail of the response such as protocol, status, and headers.")
@click.option("-h", multiple=True, help="Associates headers to HTTP Request with the format 'key:value'.")
@click.option("-d", type=str, help="Associates an inline data to the body HTTP POST request.")
@click.option("-f", type=click.File('r'), help="Associates the content of a file to the body HTTP POST request.")
@click.argument("url", type=str, required=True)
def post(url, v, h, d, f):
    """Post executes a HTTP POST request for a given URL with inline data or from file."""

    conn = http.client.HTTPConnection(util.parse_url(url).host)

    # Stores the headers received from the command line in a dictionary
    flat_h = [item for i in h for item in i.split(":")]
    headers = dict(zip(*[iter(flat_h)] * 2))

    body = None

    if d and not f:
        body = d
    elif not d and f:
        body = f.read()

    conn.request("POST", url, body=body, headers=headers)
    response = conn.getresponse()

    if v:
        print(response.version, response.status, response.reason)
        print(response.headers)
        print(response.read().decode('utf-8'))
    else:
        print(response.read().decode('utf-8'))

    conn.close()


if __name__ == '__main__':
    cli()