from flask_restful import fields, marshal, Resource, abort, reqparse
from modules.openstack_controller.controller import OpenStackController

import logging
LOGGER = logging.getLogger(__name__)

RULE_NAME_PREFIX = "osproxy_"


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

OSController = OpenStackController()


class qos(Resource):
    def get(self):
        return OSController.listServers(filter_ip=None)


qosDetailParser = reqparse.RequestParser()
qosDetailParser.add_argument('policy', type=str, required=True, help='Please Define Policy name, osproxy_{name}_policy are prepended and appended automatically')

class qosDetail(Resource):
    def get(self, ip_address):
        return OSController.listServers(filter_ip=ip_address)

    def post(self, ip_address):
        policy = qosDetailParser.parse_args()
        res = OSController.assignPolicyToServer(ip_address, RULE_NAME_PREFIX + policy['policy'])

        if res:
            return res
        else:
            abort(400, message='Failed to assign policy ' + RULE_NAME_PREFIX + policy['policy'] +'_policy on IP ' + ip_address)

    def delete(self, ip_address):

        res = OSController.unassignPolicyFromServer(ip_address)

        if res:
            return res
        else:
            abort(400, message='Failed to unassign policy')



qosPolicyParser = reqparse.RequestParser()
qosPolicyParser.add_argument('name', type=str, required=True, help='Name required')
qosPolicyParser.add_argument('bw', type=int, required=True, help='BW must be integer in kbps')


class qosPolicy(Resource):
    def get(self):
        return OSController.listOrchestratorPolicies()


    def post(self):
        policy = qosPolicyParser.parse_args()
        policy['name'] = RULE_NAME_PREFIX + policy['name']
        return OSController.createPolicy(policy)


class qosPolicyDetail(Resource):
    def delete(self, name):
        if OSController.deletePolicy(RULE_NAME_PREFIX + name):
            return {'policy': RULE_NAME_PREFIX + name + "_policy deleted"}
        else:
            abort(400, message='Policy not found or failed to delete. It might be assigned to an IP. Delete assotiation first or fix your test case')
