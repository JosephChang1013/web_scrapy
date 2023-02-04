import requests
import re


def get_proxy():
    response = requests.get("https://www.sslproxies.org/")

    proxy_ips = re.findall('\d+\.\d+\.\d+\.\d+:\d+', response.text)  # 「\d+」代表數字一個位數以上

    valid_ips = []
    for ip in proxy_ips:
        try:
            result = requests.get('https://ip.seeip.org/jsonip?',
                                  proxies={'http': ip, 'https': ip},
                                  timeout=3)
            print(result.json())
            valid_ips.append(ip)
        except:
            print(f"{ip} invalid")
            pass
    return valid_ips
    # with open('../proxy_list.txt', 'w') as file:
    #     for ip in valid_ips:
    #         file.write(ip + '\n')


def get_proxy_list():
    with open('tool/proxy_list.txt', 'r') as f:
        data = f.read().split('\n')
    return data


if __name__ == '__main__':
    get_proxy()
