#!/usr/bin/python3
import sys
import shutil
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
        print(Color.BOLD + prefix + Color.END + (" " * (shutil.get_terminal_size().columns - len(prefix))))
        if response.json()["data"]["bgp"] is None:
            print(Color.RED + "[!]" + Color.END + " Prefix " + prefix + " doesn't look like a valid prefix.")
            exit(1)

        for origin in response.json()["data"]["bgp"]:
            state = origin["validation"]["state"]
            if state == "Valid":
                state = Color.GREEN + "Valid" + Color.END
            elif state == "Invalid":
                state = Color.RED + "Invalid" + Color.END

            print("  AS" + str(origin["asn"]) + " " + state)

            for roa in origin["validation"]["covering"]:
                print("    - " + roa["prefix"]["prefix"] + " max length " + str(roa["prefix"]["maxLength"]))

        exit(0)
print(Color.ERROR, "Maximum tries exceeded, last HTTP status code " + str(response.status_code))
