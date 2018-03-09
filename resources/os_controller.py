from flask_restful import fields, marshal, Resource, abort, reqparse
from modules.openstack_controller.controller import OpenStackController

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read('./config/config.conf')

import logging
LOGGER = logging.getLogger(__name__)

## this is not really needed anymore. We can marshall with server_resource_fields if needed
rule_resource_fields = {
    'qos_policy_id': fields.String,
    'id': fields.String,
    'type': fields.String,
    'direction': fields.String,
    'max_burst_kbps': fields.Integer,
    'max_kbps:': fields.Integer
}

qos_policy_resource_fields = {
    'description': fields.String,
    'id': fields.String,
    'name': fields.String,
    'rules': fields.List(fields.Nested(rule_resource_fields))
}

fixed_ip_resource_fields = {
    'subnet_id': fields.String,
    'ip_address': fields.String
}

port_resource_fields = {
    'id': fields.String,
    'name': fields.String,
    'fixed_ips': fields.List(fields.Nested(fixed_ip_resource_fields)),
    'qos_policy': fields.Nested(qos_policy_resource_fields)
}

server_resource_fields = {
    'name': fields.String,
    'id': fields.String,
    'project_id': fields.String,
    'ports': fields.List(fields.Nested(port_resource_fields))
}

OSController = OpenStackController(modelname=Config.get('api', 'cloud_name'))


class qos(Resource):
    def get(self):
        return OSController.listServers(filter_ip=None)


class qosDetail(Resource):
    def get(self, ip_address):
        return OSController.listServers(filter_ip=ip_address)


qosPolicyParser = reqparse.RequestParser()
qosPolicyParser.add_argument('name', type=str, required=True, help='Hostname required')
qosPolicyParser.add_argument('ip', type=str, required=True, help='IP address required')

class qosPolicy(Resource):
    def get(self):
        return OSController.listOrchestratorPolicies()

    def post(self):
        policy = qosPolicyParser.parse_args()
        return OSController.assignPolicyToServer(policy)


qosPolicyRuleParser = reqparse.RequestParser()
qosPolicyRuleParser.add_argument('action', type=str, required=True, help='Provide action, add or delete')
qosPolicyRuleParser.add_argument('type', type=str, required=True, help='Provide Rule Type. Currently only BW is supported for bandwidth limit')
qosPolicyRuleParser.add_argument('direction', type=str, required=True, help='Provide direction, Incoming or Outgoing')
qosPolicyRuleParser.add_argument('max_kbps', type=int, help='Provide bandwidth limit in kbps')
qosPolicyRuleParser.add_argument('max_burst_kbps', type=int, help='Provide burst limit in kbps')


class qosPolicyDetail(Resource):
    def post(self, name):
        rule = qosPolicyRuleParser.parse_args()
        if rule['action'] == 'add':
            if 'max_burst_kbps' not in rule or 'max_kbps' not in rule:
                abort(400, message='Define bw on action add')
        return OSController.executeRuleOnPolicy(policy_name=name, rule=rule, qos_context=Config.get("api", "qos_context"))

    def delete(self, name):
        if OSController.deletePolicy(name):
            return {'policy': name + " deleted"}
        else:
            abort(400, message='Policy not found or failed to delete. It might be assigned to an IP. Delete assotiation first or fix your test case')


