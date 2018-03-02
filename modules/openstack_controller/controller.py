import openstack


class OpenStackController(object):
    def __init__(self, modelname='openstack4'):
        self.conn = openstack.connect(cloud=modelname)

    def getQoSPolicies(self, filter_ip=None):
        qos = []

        for server in self.conn.compute.servers():
            add = False
            ser = server.to_dict()

            srv = dict()
            srv['name'] = ser['name']
            srv['id'] = ser['id']
            srv['project_id'] = ser['project_id']

            srv['ports'] = []
            for interface in self.conn.compute.server_interfaces(server=server):
                iface = interface.to_dict()
                port = self.conn.network.get_port(iface['port_id'])
                prt = port.to_dict()

                pr = dict()
                pr['id'] = prt['id']
                pr['name'] = prt['name']

                pr['fixed_ips'] = prt['fixed_ips']

                if not filter_ip:
                    add = True
                else:
                    for fixed_ip in prt['fixed_ips']:
                        if fixed_ip['ip_address'] == filter_ip:
                            add = True

                if prt['qos_policy_id']:
                    qos_policy = self.conn.network.get_qos_policy(prt['qos_policy_id'])
                    qos = qos_policy.to_dict()

                    qps = dict()
                    qps['description'] = qos['description']
                    qps['id'] = qos['id']
                    qps['name'] = qos['name']
                    qps['rules'] = []

                    for rule in self.conn.network.qos_bandwidth_limit_rules(qos_policy):
                        rl = rule.to_dict()
                        qps['rules'].append(rl)

                    pr['qos_policy'] = qps

                srv['ports'].append(pr)

            if add:
                qos.append(srv)

        return qos



