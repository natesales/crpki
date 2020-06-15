#!/usr/bin/python3
import shutil
import sys

import requests


class Color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


if len(sys.argv) != 2:
    print(Color.RED + "[!]" + Color.END + " Usage: crpki [PREFIX]")
    exit(1)

prefix = sys.argv[1]

query = """
        query {
          bgp(prefixFilters:{prefix:\"""" + prefix + """\", moreSpecific: true}) {
            asn
            prefix
            validation {
              state
              covering {
                asn
                prefix {
                  maxLength
                  prefix
                }
              }
            }
          }
        }"""

print("Running query for " + prefix, end="\r")
for i in range(0, 5):
    response = requests.post("https://rpki.cloudflare.com/api/graphql", json={"query": query})
    if response.status_code == 200:
        if response.json()["data"]["bgp"] is None:
            print(Color.RED + "[!]" + Color.END + " Prefix " + prefix + " doesn't look like a valid prefix.")
            exit(1)

        if not response.json()["data"]["bgp"]:
            print(Color.RED + "[!]" + Color.END + " No ROAs found for " + prefix + ", try the parent prefix.")
            exit(1)

        print(Color.BOLD + prefix + Color.END + (" " * (shutil.get_terminal_size().columns - len(prefix))))

        for origin in response.json()["data"]["bgp"]:
            state = origin["validation"]["state"]
            if state == "Valid":
                state = Color.GREEN + "Valid" + Color.END
            elif state == "Invalid":
                state = Color.RED + "Invalid" + Color.END

            print("  AS" + str(origin["asn"]) + (" " * (8 - len(str(origin["asn"])))) + state)

            for roa in origin["validation"]["covering"]:
                print("    - " + roa["prefix"]["prefix"] + " max length " + str(roa["prefix"]["maxLength"]))

        exit(0)
print(Color.ERROR, "Maximum tries exceeded, last HTTP status code " + str(response.status_code))
