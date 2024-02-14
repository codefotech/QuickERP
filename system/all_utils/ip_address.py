import ipaddress


def get_ip_list_from_subnet(subnet):
    ip_list = []
    network = ipaddress.ip_network(subnet, strict=False)
    for ip in network.hosts():
        ip_list.append(str(ip))

    return ip_list


def ip_address_check_with_subnet(ip_address, subnet):
    ip = ipaddress.ip_interface(f"{ip_address}/{subnet}")
    network_address = ip.network.network_address
    subnet_mask = ip.network.netmask
    first_host = network_address+1
    prefix_length = sum(bin(int(x)).count('1') for x in str(subnet_mask).split('.'))
    return str(first_host)+'/'+str(prefix_length)
