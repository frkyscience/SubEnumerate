# Imports
from colorama import Fore
import requests
import argparse
from dns import resolver
import sys
import os
from os import path

# ASCII art
ascii_art = r'''
       ---_ ......._-_--.
      (|\ /      / /| \
      /  /     .'  -=-'   .
     /  /    .'             )
   _/  /   .'        _.)   /
  / o   o        _.-' /  .'
  \          _.-'    / .'*|
   \______.-'//    .'.' \*|
    \|  \ | //   .'.' _ |*|
        \|//  .'.'_ _ _|*|
      .  .// .'.'
      \-|\_/ /
       /'\__/
      /^|
     '        __                     __
   _______  __/ /_  _________  ____ _/ /_____
  / ___/ / / / __ \/ ___/ __ \/ __ / //_/ _ \
 (__  ) /_/ / /_/ (__  ) / / / /_/ / ,< /  __/
/____/\__,_/_.___/____/_/ /_/\__,_/_/|_|\___/  v0.3 by Jb
'''

# Print the ASCII art
print(Fore.GREEN + ascii_art)

def query_subdomains(domain):
    """Query for subdomains using a list of predefined subdomains."""
    subdomains = [
        "www", "mail", "ftp", "localhost", "webmail", "smtp", "blog", "webdisk",
        "ns1", "ns2", "cpanel", "whm", "autodiscover", "admin", "secure", "vpn",
        "shop", "api", "test", "dev", "demo", "imap", "pop", "support", "billing",
        "helpdesk", "login", "portal", "owa", "gateway", "firewall", "proxy",
        "router", "monitor", "backup", "cache", "cdn", "storage", "db", "database",
        "staging", "forums", "wiki", "download", "assets", "cdn", "en"
    ]
    found_subdomains = []

    for sub in subdomains:
        try:
            full_domain = f"{sub}.{domain}"
            answers = resolver.resolve(full_domain, 'A')
            for rdata in answers:
                found_subdomains.append(full_domain)
                print(Fore.GREEN + f"Found: {full_domain}")
        except resolver.NXDOMAIN:
            pass
        except Exception as e:
            print(Fore.RED + f"Error resolving {full_domain}: {str(e)}")

    return found_subdomains

def query_crtsh(domain):
    """Query crt.sh for subdomains."""
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            subdomains = set()
            for entry in response.json():
                name = entry.get('name_value')
                if name:
                    subdomains.update(name.split('\n'))
            return list(subdomains)
        else:
            print(Fore.RED + f"Error querying crt.sh: {response.status_code}")
            return []
    except Exception as e:
        print(Fore.RED + f"Error querying crt.sh: {str(e)}")
        return []

def save_to_file(filename, subdomains):
    """Save the subdomains to a file."""
    with open(filename, "a") as file:
        for subdomain in subdomains:
            file.write(subdomain + "\n")

def colorize_status_code(status_code):
    """Return colorized status code based on its class."""
    class_code = status_code // 100  # Get the class of the status code (2, 3, 4, etc.)
    color_map = {
        2: Fore.GREEN,   # 2xx codes (Successful)
        3: Fore.YELLOW,  # 3xx codes (Redirection)
        4: Fore.RED      # 4xx codes (Client Error)
    }
    color = color_map.get(class_code, Fore.RESET)  # Get color from the map, default to reset color
    return color + str(status_code)

def probe_status_codes(subdomains):
    """Probe and print HTTP status codes and headers for each subdomain with color coding."""
    for subdomain in subdomains:
        try:
            url = f"http://{subdomain}"
            response = requests.get(url, timeout=5, verify=True)
            print(f"{Fore.CYAN}{subdomain} - Status code: {colorize_status_code(response.status_code)} {response.status_code}")
            print(Fore.WHITE + "HTTP Headers:")
            for header, value in response.headers.items():
                print(f"  {header}: {value}")
        except requests.exceptions.RequestException as e:
            print(f"{Fore.CYAN}{subdomain} - Error: {str(e)}")

        try:
            url_https = f"https://{subdomain}"
            response_https = requests.get(url_https, timeout=5, verify=True)
            print(f"{Fore.CYAN}{subdomain} (HTTPS) - Status code: {colorize_status_code(response_https.status_code)} {response_https.status_code}")
            print(Fore.WHITE + "HTTPS Headers:")
            for header, value in response_https.headers.items():
                print(f"  {header}: {value}")
        except requests.exceptions.RequestException as e:
            print(f"{Fore.CYAN}{subdomain} (HTTPS) - Error: {str(e)}")


def main(domain, save=None, probe=False):
    found_subdomains = query_subdomains(domain)
    crtsh_subdomains = query_crtsh(domain)
    all_subdomains = set(found_subdomains + crtsh_subdomains)

    if probe:
        probe_status_codes(all_subdomains)

    for subdomain in all_subdomains:
        print(subdomain)

    if save and save.endswith(".txt"):
        save_to_file(save, all_subdomains)
        if path.exists(save):
            print(Fore.GREEN + "DONE! Results saved to {}".format(save))
        else:
            print(Fore.RED + "ERROR! Could not save results.")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subsnake: The Ultimate Subdomain Enumeration Tool",
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-s", required=True, help="Domain to enumerate subdomains for")
    parser.add_argument("--save", help="File to save the subdomains to (optional)")
    parser.add_argument("-pc", action="store_true", help="Probe subdomains for HTTP status codes")
    args = parser.parse_args()

    main(args.s, args.save, args.pc)