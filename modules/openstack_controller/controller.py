import openstack
import re


class OpenStackController(object):
    def __init__(self, modelname='openstack4'):
        self.conn = openstack.connect(cloud=modelname)

    def listServers(self, filter_ip=None):
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
                    qos_dict = qos_policy.to_dict()

                    qps = dict()
                    qps['description'] = qos_dict['description']
                    qps['id'] = qos_dict['id']
                    qps['name'] = qos_dict['name']
                    qps['rules'] = []

                    for rule in self.conn.network.qos_bandwidth_limit_rules(qos_policy):
                        rl = rule.to_dict()
                        qps['rules'].append(rl)

                    pr['qos_policy'] = qps

                srv['ports'].append(pr)

            if add:
                qos.append(srv)

        return qos

    def listOrchestratorPolicies(self):
        policies = []

        for qpolicy in self.conn.network.qos_policies():
            pol = qpolicy.to_dict()
            if re.match(r'^osproxy_.*_policy$', pol['name']):
                policies.append(pol)
        return policies

    def getPolicy(self, name):
        return self.conn.network.find_qos_policy(name+"_policy")


    def createPolicy(self, policy):
        listpolicy = self.conn.network.find_qos_policy(name_or_id=policy['name']+"_policy")
        if not listpolicy:
            qpolicy = self.conn.network.create_qos_policy(name=policy['name']+ "_policy", description="Sets Bandwidth Limit, Orchestrated by OS proxy")
            rule = self.conn.network.create_qos_bandwidth_limit_rule(qos_policy=qpolicy, type='bandwidth_limit', direction='egress', max_burst_kbps=0, max_kbps=policy['bw'])
            qpolicy = self.conn.network.get_qos_policy(qpolicy)
            return qpolicy.to_dict()
        else:
            return listpolicy.to_dict()

    def deletePolicy(self, name):
        qpolicy = self.conn.network.find_qos_policy(name_or_id=name+"_policy")
        if qpolicy:
            try:
                self.conn.network.delete_qos_policy(qpolicy)
            except Exception as e:
                str(e)
                return False
            return True
        else:
            return False

    def assignPolicyToServer(self, ip, policy):
        updated = False

        policyobj = self.getPolicy(policy)
        pol = policyobj.to_dict()

        print policyobj

        if not policyobj:
            return None

        for server in self.conn.compute.servers():
            for interface in self.conn.compute.server_interfaces(server=server):
                iface = interface.to_dict()
                port = self.conn.network.get_port(iface['port_id'])
                prt = port.to_dict()
                for fixed_ip in prt['fixed_ips']:
                    if fixed_ip['ip_address'] == ip:
                        self.conn.network.update_port(port, qos_policy_id=pol['id'])
                        updated = True

        if updated:
            return self.listServers(filter_ip=ip)
        else:
            return None

    def unassignPolicyFromServer(self, ip):
        for server in self.conn.compute.servers():
            for interface in self.conn.compute.server_interfaces(server=server):
                iface = interface.to_dict()
                port = self.conn.network.get_port(iface['port_id'])
                prt = port.to_dict()
                for fixed_ip in prt['fixed_ips']:
                    if fixed_ip['ip_address'] == ip:
                        self.conn.network.update_port(port, qos_policy_id=None)

        return self.listServers(filter_ip=ip)
