module "openstack" {
  source = "git::https://gitrepo.service.rug.nl/cit-hpc/tofu-openstack-cluster.git//module"

  networks = {
    hpc-ger-v4-net = { subnets = {
      hpc-ger-v4-subnet = { cidr = "10.0.0.0/16", external = "external-v4", dns-nameservers = ["9.9.9.9"] }
    }}
    hpc-ger-v6-net = { subnets = {
      hpc-ger-v6-subnet = { ip-version = 6, ipv6-address-mode = "dhcpv6-stateful", ipv6-ra-mode = "dhcpv6-stateful",
        subnetpool = "external-v6-pool" , external = "external-v6", dns-nameservers = ["2620:fe::fe"] }
    }}
  }

  security-groups = {
    hpc-ger-sec-group = { rules = [
      { direction = "egress",  ethertype = "IPv4", /* no protocol == all */ remote-ip-prefix = "0.0.0.0/0" },
      { direction = "egress",  ethertype = "IPv6", /* no protocol == all */ remote-ip-prefix = "::/0" },
      { direction = "ingress", ethertype = "IPv4", /* no protocol == all */ remote-group     = "hpc-ger-sec-group" },
      { direction = "ingress", ethertype = "IPv4", protocol = "icmp",       remote-ip-prefix = "0.0.0.0/0" },
      { direction = "ingress", ethertype = "IPv4", protocol = "tcp",        remote-ip-prefix = "0.0.0.0/0",
            port-range-min = 22, port-range-max = 22, description = "Allow IPv4 SSH access" },
      { direction = "ingress", ethertype = "IPv6", /* no protocol == all */ remote-group     = "hpc-ger-sec-group" },
      { direction = "ingress", ethertype = "IPv6", protocol = "ipv6-icmp",  remote-ip-prefix = "::/0" },
      { direction = "ingress", ethertype = "IPv6", protocol = "udp",        remote-ip-prefix = "::/0",
            port-range-min = 546, port-range-max = 547, description = "Allow IPv6 DHCPv6 access" },
    ]}
  }

  default-security-groups = ["hpc-ger-sec-group"]

  ssh-public-key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJmWG8TpwHdU0DMEt6ItzwrV4cW4slwRAUWpaTgbCIor g.j.c.strikwerda@rug.nl"

  instances = {
       dh-salt-minion01  = { flavor = "gen.v2.vm-8-8", image = "almalinux-9", boot-volume = {size = 10},
                      ports = {hpc-ger-v4-net = {floating-ip = true}, hpc-ger-v6-net = {}}}
       dh-salt-master = { flavor = "gen.v2.vm-4-4", image = "almalinux-9", boot-volume = {size = 10},
                      ports = {hpc-ger-v4-net = {floating-ip = true}, hpc-ger-v6-net = {}}}
       ger-bakje = { flavor = "gen.v2.vm-4-4", image = "ubuntu-26.04-resolute", boot-volume = {size = 10},
                      ports = {hpc-ger-v4-net = {floating-ip = true}, hpc-ger-v6-net = {}}}

  }
  
}
