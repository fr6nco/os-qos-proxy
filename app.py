from flask import Flask
from flask_restful import Api
from gevent import monkey, wsgi

from resources.os_controller import qos, qosDetail, qosPolicy, qosPolicyDetail

monkey.patch_all()

app = Flask(__name__)
api = Api(app)

api.add_resource(qos, '/api/qos')
api.add_resource(qosPolicy, '/api/qos/policy')
api.add_resource(qosPolicyDetail, '/api/qos/policy/<string:name>')
api.add_resource(qosDetail, '/api/qos/<string:ip_address>')

if __name__ == '__main__':
    app.run(debug=False)
