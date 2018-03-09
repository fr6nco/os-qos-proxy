from flask import Flask
from flask_restful import Api
from gevent import monkey

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read('./config/config.conf')

from resources.os_controller import qos, qosDetail, qosPolicy, qosPolicyDetail

monkey.patch_all()

app = Flask(__name__)
api = Api(app)

#DONE
api.add_resource(qos, '/api/qos')

#DONE
api.add_resource(qosDetail, '/api/qos/<string:ip_address>')

#DONE
api.add_resource(qosPolicy, '/api/qos/policy')

#DONE
api.add_resource(qosPolicyDetail, '/api/qos/policy/<string:name>')


if __name__ == '__main__':

    if Config.get('api', 'qos_context') not in ['switch_context', 'endpoint_context']:
        print 'Bad context option, set to switch_context or endpoint_context in ./config/config.conf'
        exit(1)

    app.run(debug=False, host=Config.get("api", "listen"), port=int(Config.get("api", "port")))

