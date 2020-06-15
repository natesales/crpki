import requests


class Color:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


prefix = "2a09:11c0:130::/44"

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
        print(Color.BOLD + prefix + Color.END + (" " * len(prefix)))
        for origin in response.json()["data"]["bgp"]:
            state = origin["validation"]["state"]
            if state == "Valid":
                state = Color.GREEN + "Valid" + Color.END
            elif state == "Invalid":
                state = Color.RED + "Invalid" + Color.END
            for roa in origin["validation"]["covering"]:
                print("  " + state + " for AS" + str(origin["asn"]) + " " + roa["prefix"]["prefix"] + " max length " + str(roa["prefix"]["maxLength"]))

        exit(0)
print(Color.ERROR, "Maximum tries exceeded, last HTTP status code " + str(response.status_code))
