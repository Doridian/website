from data import GeoLoc, IPNet

geo_loc = GeoLoc(country="US", region="WA", city="Seattle", zip="")

subnets = set([
    IPNet(subnet="2a0e:7d44:f000::/40", loc=geo_loc),
    IPNet(subnet="2a0e:8f02:21c0::/44", loc=geo_loc),
])
