# OS_Proxy rest API

This rest API is used to interfece with the OpenStack API to modify network parameters. It uses OpenStack SDK as its main component. The Server must be configured in **~/.config/openstack/clouds.yaml**.

Configuration options:
Config is stored in the **./config** dir. Use the sample file to create a custom one. 

    [api]
    # IP to listen on
    listen = 0.0.0.0
    
    # Port to listen on
    port = 8090
    
    # Cloud name.
    # Such name must be configured on the ~/.config/openstack/clouds.yaml
    # Refer to
    # https://docs.openstack.org/python-openstackclient/pike/configuration/index.html
    cloud_name = openstack4
    
    # qos_context paramter refers to how to apply the qos rules. Possible values are:
    #   - switch_context
    #   - endpoint_context
    # If Switch context is used keys incoming and outgoing are applied from the point of view of the switch
    #       incoming = ingress direction on the switch, egress direction on the server
    #       outgoing = egress direction on the switch, ingress direction on the server
    #
    # If Endpoint context is used, rules are applied in the opposite direction from the point of view of the endpoint
    #       incoming = ingress direction on the endpoint, egress direction on the switch
    #       outgoing = egress direction on the endpoint, ingress direction on the switch
    qos_context = endpoint_context


## Get list of Servers with QoS

### Request

`GET /api/qos/`

### Response

    [
	    {
	        "ports": [
	            {
	                "fixed_ips": [
	                    {
	                        "subnet_id": "a5fcc51f-780b-49df-a6c2-46d9c3f80c48",
	                        "ip_address": "172.16.3.5"
	                    }
	                ],
	                "id": "17a9fb3b-12f3-47a5-a4ad-78e1cca1111d",
	                "name": ""
	            }
	        ],
	        "project_id": "1ea1f0457702486390a279f37eb33d88",
	        "name": "tomas_client",
	        "id": "69cd745d-7c59-4656-8280-a42d0ae5f01b"
	    },
	    {
	        "ports": [
	            {
	                "fixed_ips": [
	                    {
	                        "subnet_id": "a5fcc51f-780b-49df-a6c2-46d9c3f80c48",
	                        "ip_address": "172.16.3.9"
	                    }
	                ],
	                "id": "2fb879fc-bce8-4bf5-ba0a-e8596aef3687",
	                "name": ""
	            },
	            {
	                "fixed_ips": [
	                    {
	                        "subnet_id": "872b730d-0737-4465-a76f-f3e64d7d5846",
	                        "ip_address": "192.168.124.10"
	                    }
	                ],
	                "id": "aa218efe-f8c2-42dd-a793-8c8c21c6d127",
	                "name": ""
	            }
	        ],
	        "project_id": "1ea1f0457702486390a279f37eb33d88",
	        "name": "tomas1",
	        "id": "238551db-0fe2-44df-8277-1b7d948fddf0"
	    }
	]

## Get server QoS details

### Request

`GET /api/qos/<string:ip_address>`

### Response

    [
	    {	
	        "ports": [
	            {
	                "fixed_ips": [
	                    {
	                        "subnet_id": "a5fcc51f-780b-49df-a6c2-46d9c3f80c48",
	                        "ip_address": "172.16.3.5"
	                    }
	                ],
	                "id": "17a9fb3b-12f3-47a5-a4ad-78e1cca1111d",
	                "name": ""
	            }
	        ],
	        "project_id": "1ea1f0457702486390a279f37eb33d88",
	        "name": "tomas_client",
	        "id": "69cd745d-7c59-4656-8280-a42d0ae5f01b"
	    }
	]

## Get a list of QoS Policies

### Request

`GET /api/qos/policy`

### Response

    [
	    {
	        "is_shared": false,
	        "description": "Policy assigned to server dane_server, Orchestrated by OS proxy",
	        "rules": [],
	        "is_default": false,
	        "location": null,
	        "project_id": "1ea1f0457702486390a279f37eb33d88",
	        "id": "2cb8d744-e167-43e1-b308-097d13b2c87c",
	        "name": "osproxy_dane_server_policy"
	    }
	]

## Create a QoS Policy

### Request

`POST /api/qos/policy`

    body: {
    	name: "dane_server",
    	ip: "172.16.3.5"
    }

### Response

    {
	    "is_shared": false,
	    "description": "Policy assigned to server dane_server, Orchestrated by OS proxy",
	    "rules": [],
	    "is_default": false,
	    "location": null,
	    "project_id": "1ea1f0457702486390a279f37eb33d88",
	    "id": "5c77df26-1ab4-4dd7-9135-91c1c038ed8f",
	    "name": "osproxy_dane_server_policy"
	}

## Create a QoS Policy Rule

### Request

`POST /api/qos/policy/<string:policy_name>`

    body: {
    	action: "add",
    	type: "bw",
    	direction: "incoming",
    	max_kbps: 100000,
    	max_burst_kbps: 0
    }

### Response

    {
	    "is_shared": false,
	    "description": "Policy assigned to server dane_server, Orchestrated by OS proxy",
	    "rules": [
	        {
	            "max_kbps": 5000,
	            "direction": "ingress",
	            "qos_policy_id": "f56f608a-e0e4-4014-bb3f-6dacf96b96d2",
	            "type": "bandwidth_limit",
	            "id": "e142abcd-0731-4d94-ba94-495ec24ea45e",
	            "max_burst_kbps": 0
	        }
	    ],
	    "is_default": false,
	    "location": null,
	    "project_id": "1ea1f0457702486390a279f37eb33d88",
	    "id": "f56f608a-e0e4-4014-bb3f-6dacf96b96d2",
	    "name": "osproxy_dane_server_policy"
	}


## Delete a QoS Policy Rule

### Request

`POST /api/qos/policy/<string:policy_name>`

    body: {
    	action: "delete",
    	type: "bw",
    	direction: "incoming",
    }

### Response

	{
	    "is_shared": false,
	    "description": "Policy assigned to server dane_server, Orchestrated by OS proxy",
	    "rules": [],
	    "is_default": false,
	    "location": null,
	    "project_id": "1ea1f0457702486390a279f37eb33d88",
	    "id": "f56f608a-e0e4-4014-bb3f-6dacf96b96d2",
	    "name": "osproxy_dane_server_policy"
	}

