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
        return self.conn.network.find_qos_policy("osproxy_" + name + "_policy")

    def assignPolicyToServer(self, policy):
        qpolicy = self.conn.network.create_qos_policy(name="osproxy_" + policy['name'] + "_policy", description="Policy assigned to server "+policy['name']+", Orchestrated by OS proxy")
        qos = qpolicy.to_dict()

        for server in self.conn.compute.servers():
            for interface in self.conn.compute.server_interfaces(server=server):
                iface = interface.to_dict()
                port = self.conn.network.get_port(iface['port_id'])
                prt = port.to_dict()
                for fixed_ip in prt['fixed_ips']:
                    if fixed_ip['ip_address'] == policy['ip']:
                        self.conn.network.update_port(port, qos_policy_id=qos['id'])

        return qpolicy.to_dict()

    def deletePolicy(self, name):
        for qpolicy in self.conn.network.qos_policies(name="osproxy_" + name + "_policy"):
            pol = qpolicy.to_dict()
            self.unassingPolicyFromEverywhere(policy_id=pol['id'])
            self.conn.network.delete_qos_policy(qpolicy)

        return True

    def findRuleQuery(self, policy, action_type):
        if action_type == 'bw':
            return self.conn.network.qos_bandwidth_limit_rules(policy)

    def deleteRule(self, policy, action_type, rule):
        if action_type == 'bw':
            self.conn.network.delete_qos_bandwidth_limit_rule(qos_rule=rule, qos_policy=policy)

    def addRule(self, policy, **kwargs):
        if kwargs['type'] == 'bw':
            self.conn.network.create_qos_bandwidth_limit_rule(qos_policy=policy, type='bandwidth_limit',
                                                              direction=kwargs['direction'],
                                                              max_burst_kbps=kwargs['max_burst_kbps'],
                                                              max_kbps=kwargs['max_kbps'])

    def executeRuleOnPolicy(self, policy_name, rule):
        policyobj = self.getPolicy(policy_name)
        rule['direction'] = 'egress' if rule['direction'] == 'incoming' else 'ingress'

        for obj in self.findRuleQuery(policy=policyobj, action_type=rule['type']):
            objdict = obj.to_dict()
            if objdict['direction'] == rule['direction']:
                self.deleteRule(policy=policyobj, action_type=rule['type'], rule=obj)

        if rule['action'] == 'add':
            self.addRule(policy=policyobj, **rule)

        return self.getPolicy(policy_name).to_dict()

    def unassingPolicyFromEverywhere(self, policy_id):
        for port in self.conn.network.ports():
            por = port.to_dict()
            if por['qos_policy_id'] == policy_id:
                self.conn.network.update_port(port, qos_policy_id=None)


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
