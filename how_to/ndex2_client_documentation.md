Ndex2 REST client
The Ndex2 class provides methods to interface with the NDEx REST Server API The Ndex2 object can be used to access an NDEx server either anonymously or using a specific user account. For each NDEx server and user account that you want to use in your script or application, you create an Ndex2 instance.

Example creating anonymous connection:

import ndex2.client
anon_ndex=ndex2.client.Ndex2()
Example creating connection with username and password:

import ndex2.client
my_account="your account"
my_password="your password"
my_ndex=ndex2.client.Ndex2("http://public.ndexbio.org", my_account, my_password)
classndex2.client.Ndex2(host=None, username=None, password=None, update_status=False, debug=False, user_agent='', timeout=30, skip_version_check=False)[source]
A class to facilitate communication with an NDEx server.

If host is not provided it will default to the NDEx public server. UUID is required

Creates a connection to a particular NDEx server.

Added in version 3.5.0: skip_version_check parameter added

Parameters
:
host (str) – The URL of the server.

username (str) – The username of the NDEx account to use. (Optional)

password (str) – The account password. (Optional)

update_status (bool) – If set to True tells constructor to query service for status

user_agent (str) – String to append to User-Agent header sent with all requests to server

timeout (float or tuple(float, float)) – The timeout in seconds value for requests to server. This value is passed to Request calls Click here for more information

skip_version_check (bool) – If True, it is assumed NDEx server supports v2 endpoints, otherwise NDEx server is queried to see if v2 endpoints are supported

add_networks_to_networkset(set_id, networks)[source]
Add networks to a network set. User must have visibility of all networks being added

Parameters
:
set_id (str) – network set id

networks (list) – networks (ids as str) that will be added to the set

Returns
:
None

Return type
:
None

create_networkset(name, description)[source]
Creates a new network set

Parameters
:
name (str) – Network set name

description (str) – Network set description

Returns
:
URI of the newly created network set

Return type
:
str

delete_network(network_id, retry=5)[source]
Deletes the specified network from the server

Parameters
:
network_id (str) – Network id

retry (int) – Number of times to retry if deleting fails

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

Returns
:
Error json if there is an error. Blank

Return type
:
str

delete_networks_from_networkset(set_id, networks, retry=5)[source]
Removes network(s) from a network set.

Parameters
:
set_id (str) – network set id

networks (list) – networks (ids as str) that will be removed from the set

retry (int) – Number of times to retry

Returns
:
None

Return type
:
None

delete_networkset(networkset_id)[source]
Deletes the network set, requires credentials

Parameters
:
networkset_id (str) – networkset UUID id

Raises
:
NDExInvalidParameterError – for invalid networkset id parameter

NDExUnauthorizedError – If no credentials or user is not authorized

NDExNotFoundError – If no networkset with id passed in found

NDExError – For any other error with contents of error in message

Returns
:
None upon success

get_id_for_user(username)[source]
Gets NDEx user Id for user

Added in version 3.4.0.

import ndex2.client
my_ndex = ndex2.client.Ndex2()
my_ndex.get_id_for_user('nci-pid')
Parameters
:
username (str) – Name of user on NDEx. If None user set in constructor of this client will be used.

Raises
:
NDExError – If there was an error on the server.

NDExInvalidParameterError – If username is empty string or is of type other then str.

Returns
:
Id of user on NDEx server.

Return type
:
str

get_neighborhood(network_id, search_string, search_depth=1, edge_limit=2500)[source]
Get the CX for a subnetwork of the network specified by UUID network_id and a traversal of search_depth steps around the nodes found by search_string.

Parameters
:
network_id (str) – The UUID of the network.

search_string (str) – The search string used to identify the network neighborhood.

search_depth (int) – The depth of the neighborhood from the core nodes identified.

edge_limit (int) – The maximum size of the neighborhood.

Returns
:
The CX json object.

Return type
:
response object

get_neighborhood_as_cx_stream(network_id, search_string, search_depth=1, edge_limit=2500, error_when_limit=True)[source]
Get a CX stream for a subnetwork of the network specified by UUID network_id and a traversal of search_depth steps around the nodes found by search_string.

Parameters
:
network_id (str) – The UUID of the network.

search_string (str) – The search string used to identify the network neighborhood.

search_depth (int) – The depth of the neighborhood from the core nodes identified.

edge_limit (int) – The maximum size of the neighborhood.

error_when_limit (bool) – Default value is true. If this value is true the server will stop streaming the network when it hits the edgeLimit, add success: false and error: “EdgeLimitExceeded” in the status aspect and close the CX stream. If this value is set to false the server will return a subnetwork with edge count up to edgeLimit. The status aspect will be a success, and a network attribute {“EdgeLimitExceeded”: “true”} will be added to the returned network only if the server hits the edgeLimit..

Returns
:
The response.

Return type
:
response object

get_network_as_cx2_stream(network_id, access_key=None)[source]
Get the existing network with UUID network_id from the NDEx connection as CX2 stream contained within a requests.Response object

Added in version 3.5.0.

Example usage:

from ndex2.client import Ndex2
client = Ndex2(skip_version_check=True)

# 7fc.. is UUID MuSIC v1 network: http://doi.org/10.1038/s41586-021-04115-9
client_resp = client.get_network_as_cx2_stream('7fc70ab6-9fb1-11ea-aaef-0ac135e8bacf')

# for HTTP status code, 200 means success
print(client_resp.status_code)

# for smaller networks one can get the CX2 by calling:
print(client_resp.json())
Note

For retrieving larger networks see requests.Response.iter_content()

This method sets stream=True in the request to avoid loading response into memory.

Parameters
:
network_id – The UUID of the network

access_key – Optional access key UUID

Raises
:
NDExError – If there was an error

Returns
:
Requests library response with CX2 in content and status code of 200 upon success

Return type
:
requests.Response

get_network_as_cx_stream(network_id)[source]
Get the existing network with UUID network_id from the NDEx connection as a CX stream.

Parameters
:
network_id (str) – The UUID of the network.

Returns
:
The response.

Return type
:
response object

get_network_aspect_as_cx_stream(network_id, aspect_name)[source]
Get the specified aspect of the existing network with UUID network_id from the NDEx connection as a CX stream.

For a list of aspect names look at Core Aspects section of CX Data Model Documentation

Parameters
:
network_id (str) – The UUID of the network.

aspect_name – The aspect NAME.

Returns
:
The response.

Return type
:
response object

get_network_ids_for_user(username, offset=0, limit=1000)[source]
Get the network UUIDs owned by the user as well as any networks shared with the user. As set via limit parameter only the first 1,000 ids are returned. The offset parameter combined with limit provides pagination support.

Changed in version 3.4.0: offset and limit parameters added.

Parameters
:
username (str) – NDEx username

offset (int) – Starting position of the query. If set, limit parameter must be set to a positive value.

limit (int) – Number of summaries to return starting from offset If set to None or 0 all summaries will be returned.

Raises
:
NDExInvalidParameterError – If offset/limit parameters are not of type int. If offset parameter is set to positive number and limit is 0 or negative.

Returns
:
List of uuids as str

Return type
:
list

get_network_set(set_id)[source]
Gets the network set information including the list of networks

Deprecated since version 3.2.0: Use get_networkset() instead.

Parameters
:
set_id (str) – network set id

Returns
:
network set information

Return type
:
dict

get_network_summary(network_id)[source]
Gets information and status of a network

Example usage:

from ndex2.client import Ndex2
client = Ndex2(skip_version_check=True)

# 7fc.. is UUID MuSIC v1 network: http://doi.org/10.1038/s41586-021-04115-9
net_sum = client.get_network_summary('7fc70ab6-9fb1-11ea-aaef-0ac135e8bacf')

print(net_sum)
Example result:

{
  "ownerUUID": "daa09f36-8cdd-11e7-a10d-0ac135e8bacf",
  "isReadOnly": true,
  "subnetworkIds": [],
  "isValid": true,
  "warnings": [],
  "isShowcase": true,
  "doi": "10.18119/N9188W",
  "isCertified": true,
  "indexLevel": "ALL",
  "hasLayout": true,
  "hasSample": false,
  "cxFileSize": 82656,
  "cx2FileSize": 68979,
  "visibility": "PUBLIC",
  "nodeCount": 70,
  "edgeCount": 87,
  "completed": true,
  "version": "1.0",
  "owner": "yue",
  "description": "<div><br/></div><div>Two central approaches for mapping cellular structure – protein fluorescent imaging and protein biophysical association – each generate extensive datasets but of distinct qualities and resolutions that are typically treated separately. The MuSIC map is designed to address this challenge, by integrating immunofluorescent images in the Human Protein Atlas with ongoing affinity purification experiments from the BioPlex resource. The result is a unified hierarchical map of eukaryotic cell architecture. In the MuSIC hierarchy, nodes represent systems and arrows indicate containment of the lower system by the upper. Node color indicates known (gold) or putative novel (purple) systems. The size of each circle is based on the number of proteins in the system. The relative height of each system in the layout is determined based on the predicted diameter of the system in MuSIC.<br/></div>",
  "name": "Multi-Scale Integrated Cell (MuSIC) v1",
  "properties": [
    {
      "subNetworkId": null,
      "predicateString": "author",
      "dataType": "string",
      "value": "Yue Qin"
    },
    {
      "subNetworkId": null,
      "predicateString": "rights",
      "dataType": "string",
      "value": "MIT license (MIT)"
    },
    {
      "subNetworkId": null,
      "predicateString": "rightsHolder",
      "dataType": "string",
      "value": "Yue Qin"
    },
    {
      "subNetworkId": null,
      "predicateString": "reference",
      "dataType": "string",
      "value": "Yue Qin, Edward L. Huttlin, Casper F. Winsnes, Maya L. Gosztyla, Ludivine Wacheul, Marcus R. Kelly, Steven M. Blue, Fan Zheng, Michael Chen, Leah V. Schaffer, Katherine Licon, Anna Bäckström, Laura Pontano Vaites, John J. Lee, Wei Ouyang, Sophie N. Liu, Tian Zhang, Erica Silva, Jisoo Park, Adriana Pitea, Jason F. Kreisberg, Steven P. Gygi, Jianzhu Ma, J. Wade Harper, Gene W. Yeo, Denis L. J. Lafontaine, Emma Lundberg, Trey Ideker<br><strong>A multi-scale map of cell structure fusing protein images and interactions</strong><br><i>Nature 600, 536–542 (2021).</i>, (2021)<br><a href="http://doi.org/10.1038/s41586-021-04115-9"  target="_blank">10.1038/s41586-021-04115-9</a>"
    }
  ],
  "externalId": "7fc70ab6-9fb1-11ea-aaef-0ac135e8bacf",
  "isDeleted": false,
  "modificationTime": 1630270298717,
  "creationTime": 1590539529001
}
Note

isvalid is a boolean to denote that the network was inspected, not that it is actually valid.

errorMessage Will be in result if there was an error parsing network

completed is set to True after all server tasks have completed and network is ready to be used

Parameters
:
network_id (str) – The UUID of the network

Returns
:
Summary information about network

Return type
:
dict

get_networkset(set_id)[source]
Gets the network set information including the list of networks

Parameters
:
set_id (str) – network set id

Returns
:
network set information

Return type
:
dict

get_networksets_for_user_id(user_id, summary_only=True, showcase=False, offset=0, limit=0)[source]
Gets a list of Network Set objects owned by the user identified by user_id

Added in version 3.4.0.

Example when summary_only is True or if Network Set does not contain any networks:

[
 {'name': 'test networkset',
  'description': ' ',
  'ownerId': '4f0a6356-ed4a-49df-bd81-098fee90b448',
  'showcased': False,
  'properties': {},
  'externalId': '956e31e8-f25c-471f-8596-2cae8348dcad',
  'isDeleted': False,
  'modificationTime': 1568844043868,
  'creationTime': 1568844043868
 }
]
When summary_only is False and Network Set does contain networks there will be an additional property named networks:

'networks': ['face63b6-aba7-11eb-9e72-0ac135e8bacf',
             'fae4d1e8-aba7-11eb-9e72-0ac135e8bacf']
Parameters
:
user_id (str) – Id of user on NDEx. To get Id of user see get_id_for_user()

summary_only (bool) – When True, the server will not return the list of network IDs in this Network Set

showcase (bool) – When True, only showcased Network Sets are returned

offset (int) – Index to first object to return. If 0/None no offset will be applied. If this parameter is set to a positive value then limit parameter must be set to a positive value or this offset will be ignored.

limit (int) – Number of objects to retrieve. If 0, None, or negative all results will be returned.

Raises
:
NDExInvalidParameterError – If user_id parameter is not of type str. If offset/limit parameters are not None or of type int. If offset parameter is set to positive number and limit is 0, None, or negative.

NDExError – If there is an error from server

Returns
:
list with dict objects containing Network Sets

Return type
:
list

get_sample_network(network_id)[source]
Gets the sample network

Parameters
:
network_id (str) – Network id

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

Returns
:
Sample network in CX format

Return type
:
list

get_task_by_id(task_id)[source]
Retrieves a task by id

Parameters
:
task_id (str) – Task id

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

Returns
:
Task

Return type
:
dict

get_user_by_id(user_id)[source]
Gets user matching id from NDEx server.

Added in version 3.4.0.

Result is a dict in format:

{'properties': {},
 'isIndividual': True,
 'userName': 'bsmith',
 'isVerified': True,
 'firstName': 'bob',
 'lastName': 'smith',
 'emailAddress': 'bob.smith@ndexbio.org',
 'diskQuota': 10000000000,
 'diskUsed': 3971183103,
 'externalId': 'f2c3a7ef-b0d9-4c61-bf31-4c9fcabe4173',
 'isDeleted': False,
 'modificationTime': 1554410147104,
 'creationTime': 1554410138498
}
Parameters
:
user_id (str) – Id of user on NDEx server

Raises
:
NDExError – If there was an error on the server

NDExInvalidParameterError – If user_id is not of type str or if empty str

Returns
:
user object. externalId is Id of user on NDEx server

Return type
:
dict

get_user_by_username(username)[source]
Gets user information from NDEx.

Example user information:

{'properties': {},
 'isIndividual': True,
 'userName': 'bsmith',
 'isVerified': True,
 'firstName': 'bob',
 'lastName': 'smith',
 'emailAddress': 'bob.smith@ndexbio.org',
 'diskQuota': 10000000000,
 'diskUsed': 3971183103,
 'externalId': 'f2c3a7ef-b0d9-4c61-bf31-4c9fcabe4173',
 'isDeleted': False,
 'modificationTime': 1554410147104,
 'creationTime': 1554410138498
}
Parameters
:
username (str) – User name

Returns
:
User information as dict

Return type
:
dict

get_user_network_summaries(username, offset=0, limit=1000)[source]
Get a list of network summaries for networks owned by specified user. It returns not only the networks that the user owns but also the networks that are shared with them directly. As set via limit parameter only the first 1,000 ids are returned. The offset parameter combined with limit parameter provides pagination support.

Parameters
:
username (str) – Username of the network owner

offset (int) – Starting position of the network search

limit (int) – Number of summaries to return starting from offset

Returns
:
List of uuids

Return type
:
list

grant_network_to_user_by_username(username, network_id, permission)[source]
Grants permission to network for the given user name

Parameters
:
username (str) – User name

network_id (str) – Network id

permission (str) – Network permission

Returns
:
Result

Return type
:
dict

grant_networks_to_group(groupid, networkids, permission='READ')[source]
Set group permission for a set of networks

Parameters
:
groupid (str) – Group id

networkids (list) – List of network ids

permission (str) – Network permission

Returns
:
Result

Return type
:
dict

grant_networks_to_user(userid, networkids, permission='READ')[source]
Gives read permission to specified networks for the provided user

Parameters
:
userid (str) – User id

networkids (list) – Network ids as str

permission (str (default is READ)) – Network permissions

Returns
:
None

Return type
:
None

make_network_private(network_id)[source]
Makes the network specified by the network_id private by invoking set_network_system_properties() with

{'visibility': 'PRIVATE'}

Parameters
:
network_id (str) – The UUID of the network.

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

requests.exception.HTTPError – If there is some other error

Returns
:
empty string upon success

Return type
:
str

make_network_public(network_id)[source]
Makes the network specified by the network_id public by invoking set_network_system_properties() with

{'visibility': 'PUBLIC'}

Parameters
:
network_id (str) – The UUID of the network.

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

requests.exception.HTTPError – If there is some other error

Returns
:
empty string upon success

Return type
:
str

save_cx2_stream_as_new_network(cx_stream, visibility=None)[source]
Create a new network from a CX2 stream

Added in version 3.5.0.

import io
import json
from ndex2.client import Ndex2
from ndex2.exceptions import NDExError

client = Ndex2(username=<NDEx USER NAME>,
               password=<NDEx PASSWORD>,
               skip_version_check=True)

# cx is set to an empty CX2 network
cx = [{"CXVersion":"2.0","hasFragments":false},
      {"status":[{"success":true}]}]

try:
    cx_stream = io.BytesIO(json.dumps(cx,
                                      cls=DecimalEncoder).encode('utf-8'))
    net_url = client.save_cx2_stream_as_new_network(cx_stream,
                                                    visibility='PUBLIC')
    print('Network URL: ' + str(net_url))
except NDExError as ne:
    print('Caught error: ' + str(ne))
Parameters
:
cx_stream (BytesIO like object) – IO stream of cx2

visibility (str) – Sets the visibility (PUBLIC or PRIVATE)

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

NDExError – if there is an error saving the network

Returns
:
Full URL to newly created network (ie http://ndexbio.org/v3/networks/XXXX)

Return type
:
str

save_cx_stream_as_new_network(cx_stream, visibility=None)[source]
Create a new network from a CX stream.

Parameters
:
cx_stream (BytesIO) – IO stream of cx

visibility (str) – Sets the visibility (PUBLIC or PRIVATE)

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

Returns
:
Response data

Return type
:
str or dict

save_new_cx2_network(cx, visibility=None)[source]
Create a new network (CX2) on the server

Added in version 3.5.0.

from ndex2.client import Ndex2
from ndex2.exceptions import NDExError

client = Ndex2(username=<NDEx USER NAME>,
               password=<NDEx PASSWORD>,
               skip_version_check=True)

# cx is set to an empty CX2 network
cx = [{"CXVersion":"2.0","hasFragments":false},
      {"status":[{"success":true}]}]

try:
    net_url = client.save_new_cx2_network(cx, visibility='PRIVATE')
    print('URL of new network: ' + str(net_url))
except NDExError as ne:
    print('Caught error: ' + str(ne))
Parameters
:
cx (list) – Network CX2 which is a list of dict objects

visibility (str) – Sets the visibility (PUBLIC or PRIVATE) If None sets visibility to PRIVATE

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

NDExInvalidCXError – if cx is None, not a list, or is an empty list

NDExError – if there is an error saving the network

Returns
:
Full URL to newly created network (ie http://ndexbio.org/v3/networks/XXXX)

Return type
:
str

save_new_network(cx, visibility=None)[source]
Create a new network (CX) on the server

Parameters
:
cx (list) – Network CX which is a list of dict objects

visibility (str) – Sets the visibility (PUBLIC or PRIVATE)

Raises
:
NDExInvalidCXError – For invalid CX data

Returns
:
Response data

Return type
:
str or dict

search_networks(search_string='', account_name=None, start=0, size=100, include_groups=False)[source]
Search for networks based on the search_text, optionally limited to networks owned by the specified account_name.

Parameters
:
search_string (str) – The text to search for.

account_name (str) – The account to search

start (int) – The number of blocks to skip. Usually zero, but may be used to page results.

size (int) – The size of the block.

include_groups

Returns
:
The response.

Return type
:
response object

set_network_properties(network_id, network_properties)[source]
Updates properties of network

Starting with version 2.5 of NDEx, any network properties not in the network_properties parameter are left unchanged.

Warning

name, description, version network attributes/properties cannot be updated by this method. Please use update_network_profile() to update these values.

The format of network_properties should be a list() of dict() objects in this format:

[{
    'subNetworkId': '',
    'predicateString': '',
    'dataType': '',
    'value': ''
}]
The predicateString field above is the network attribute/property name.

The dataType field above must be one of the following types

Regardless of dataType, value should be converted to str() or list() of str()

For more information please visit the underlying REST call documentation

Example to add two network properties (foo, bar):

[{
'subNetworkId': '',
'predicateString': 'foo',
'dataType': 'list_of_integer',
'value': ['1', '2', '3']
},{
'subNetworkId': '',
'predicateString': 'bar',
'dataType': 'string',
'value': 'a value for bar as str'
}]
Parameters
:
network_id (str) – Network id

network_properties (list or str) – List of NDEx property value pairs aka network properties to set on the network. This can also be a str() in JSON format

Raises
:
Exception – If network_properties is not a str() or list()

NDExUnauthorizedError – If credentials are invalid or not set

requests.HTTPError – If there is an error with the request or if name, version, description is set in network_properties as a value to predicateString

Returns
:
Empty string or 1

Return type
:
str or int

set_network_system_properties(network_id, network_properties, skipvalidation=False)[source]
Set network system properties on network with UUID specified by network_id

The network properties should be a dict() or a json string of a dict() in this format:

{'showcase': (boolean True or False),
 'visibility': (str 'PUBLIC' or 'PRIVATE'),
 'index_level': (str  'NONE', 'META', or 'ALL'),
 'readOnly': (boolean True or False)
}
Note

Omit any values from dict() that you do NOT want changed

Definition of showcase values:

True - means network will display in her home page for other users and False hides the network for other users. where other users includes anonymous users

Definition of visibility values:

‘PUBLIC’ - means it can be found or read by anyone, including anonymous users

‘PRIVATE’ - is the default, means that it can only be found or read by users according to their permissions

Definition of index_level values:

‘NONE’ - no index

‘META’ - only index network attributes

‘ALL’ - full index on the network

Definition of readOnly values:

True - means network is only readonly, False is NOT readonly

This method will validate network_properties matches above dict() unless skipvalidation is set to True in which case the code only verifies the network_properties is valid JSON

Parameters
:
network_id (str) – Network id

network_properties (dict or str) – Network properties as dict() or a JSON string of dict() adhering to structure above.

skipvalidation – If True, only verify network_properties can be parsed/converted to valid JSON

Raises
:
NDExUnsupportedCallError – If version of NDEx server is < 2

NDExUnauthorizedError – If credentials are invalid or not set

NDExInvalidParameterError – If invalid data is set in network_properties parameter

requests.exception.HTTPError – If there is some other error

Returns
:
empty string upon success

Return type
:
str

set_read_only(network_id, value)[source]
Sets the read only flag to value on the network specified by network_id

Parameters
:
network_id (str) – Network id

value (bool) – Must True for read only, False otherwise

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

NDExInvalidParameterError – If non bool is set in valid parameter

requests.exception.HTTPError – If there is some other error

Returns
:
empty string upon success

Return type
:
str

update_cx2_network(cx_stream, network_id)[source]
Update the network specified by UUID network_id using the CX2 stream cx_stream passed in

Added in version 3.5.0.

import io
import json
from ndex2.client import Ndex2
from ndex2.exceptions import NDExError

client = Ndex2(username=<NDEx USER NAME>,
               password=<NDEx PASSWORD>,
               skip_version_check=True)

# cx is set to an empty CX2 network
cx = [{"CXVersion":"2.0","hasFragments":false},
      {"status":[{"success":true}]}]

try:
    cx_stream = io.BytesIO(json.dumps(cx,
                                      cls=DecimalEncoder).encode('utf-8'))
    client.update_cx2_network(cx_stream, <UUID OF NETWORK TO UPDATE>)
    print('Success')
except NDExError as ne:
    print('Caught error: ' + str(ne))
Parameters
:
cx_stream – The network stream.

network_id (str) – The UUID of the network.

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

NDExError – If there is an error updating the network

Returns
:
Nothing is returned. To check status call get_network_summary()

update_cx_network(cx_stream, network_id)[source]
Update the network specified by UUID network_id using the CX stream cx_stream passed in

Parameters
:
cx_stream – The network stream.

network_id (str) – The UUID of the network.

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

Returns
:
The response.

Return type
:
response object

update_network_group_permission(groupid, networkid, permission)[source]
Updated group permissions

Parameters
:
groupid (str) – Group id

networkid (str) – Network id

permission (str) – Network permission

Returns
:
Result

Return type
:
dict

update_network_profile(network_id, network_profile)[source]
Updates the network profile Any profile attributes specified will be updated but attributes that are not specified will have no effect - omission of an attribute does not mean deletion of that attribute. The network profile attributes that can be updated by this method are: ‘name’, ‘description’ and ‘version’.

{
  "name": "string",
  "description": "string",
  "version": "string",
  "visibility": "string",
  "properties": [
    {
      "subNetworkId": "",
      "predicateString": "string",
      "dataType": "string",
      "value": "string"
    }
  ]
}
Parameters
:
network_id (str) – Network id

network_profile (dict) – Network profile

Raises
:
NDExUnauthorizedError – If credentials are invalid or not set

Returns
:
Return type
:
update_network_user_permission(userid, networkid, permission)[source]
Updated network user permission

Parameters
:
userid (str) – User id

networkid (str) – Network id

permission (str) – Network permission

Returns
:
Result

Return type
:
dict