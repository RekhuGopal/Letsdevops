import http.client
import json
import os
import base64
from base64 import b64encode

source_api_key= os.environ.get("source_api_key")
source_api_secret= os.environ.get("source_api_secret")
target_api_key= os.environ.get("target_api_key")
target_api_secret= os.environ.get("target_api_secret")
source_server= os.environ.get("source_server")
target_server= os.environ.get("target_server")
source_cluster_id=os.environ.get("source_cluster_id")
target_cluster_id=os.environ.get("target_cluster_id")
topics_deploy=os.environ.get("topic_list")
topic_deletelist=os.environ.get("topic_deletelist")
partitions_count=os.environ.get("partitions_count")
replication_factor=os.environ.get("replication_factor")
rentention_days=os.environ.get("rentention_days")

print("the list of topic to Delete",topic_deletelist)
print("the list of topic to create",topics_deploy)
topic_deletelist = topic_deletelist.split(",")
if topics_deploy != "full":
    if topics_deploy !='':
        topics_details=topics_deploy.split(",")
    else:
        topics_deploy= "empty"
else:
    print("All Topics needs to be created")

# Create Basic Authentication for Source And Target Confluent Cluster
src_auth=source_api_key + ':' + source_api_secret
source_auth_key = base64.b64encode(src_auth.encode()).decode()

# Target
tgt_auth=target_api_key + ':' + target_api_secret
target_auth_key = base64.b64encode(tgt_auth.encode()).decode()

source_conn = http.client.HTTPSConnection(source_server)
target_conn = http.client.HTTPSConnection(target_server)

source_headers = {'Authorization': 'Basic %s' % source_auth_key  }
target_headers = {'Authorization': 'Basic %s' % target_auth_key  }
#source_cluster_id="lkc-399xj"
#target_cluster_id="lkc-399xj"

def list_topic_details():
    
    source_conn.request("GET", "/kafka/v3/clusters/"+source_cluster_id+"/topics", headers=source_headers)
    res = source_conn.getresponse()
    data = res.read()
    savedata=data.decode("utf-8")
    return savedata

def topic_payload(topic_name,partitions_count,replication_factor,rententionpol):
    if topic_name != "":
        payload_value='{"topic_name":'+'"'+topic_name+'"'+','
    if partitions_count != "":
        payload_value+='"partitions_count":'+str(partitions_count)+","
    if replication_factor != "":
        payload_value+='"replication_factor":'+str(replication_factor)
    if rententionpol =="default":
        payload_value+="}"
        print("The selected Retention is Default Value")
    else:
        payload_value+=","
        if(rententionpol =="-1"):
            poltype='"name":'+'"retention.ms"'+","
            polValue='"value":"'+(str)(rententionpol)+'"'
            payload_value+='"configs":[{'+poltype+polValue+"}]}"
        else:
            valueinms= (int)(rententionpol)*86400000
            poltype='"name":'+'"retention.ms"'+","
            polValue='"value":"'+(str)(valueinms)+'"'
            payload_value+='"configs":[{'+poltype+polValue+"}]}"
    return payload_value

def create_topic(cluster_id,payload_json):

    #conn = http.client.HTTPSConnection("pkc-00000.region.provider.confluent.cloud")
    #json_value_ops=json.loads(payload_json)
    target_conn.request("POST", "/kafka/v3/clusters/"+cluster_id+"/topics", payload_json, target_headers)
    res = target_conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

def delete_topic(cluster_id,topic_name):

    #conn = http.client.HTTPSConnection("pkc-00000.region.provider.confluent.cloud")
    #json_value_ops=json.loads(payload_json)
    target_conn.request("DELETE", "/kafka/v3/clusters/"+cluster_id+"/topics/"+topic_name, headers=target_headers)
    res = target_conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    
######## Test ###################
#app_json=topic_payload('devops-cicd-test-2',6,3)
#create_topic(target_cluster_id,app_json)
################################################

#list all the Available topic in Source
list_topic_detail=list_topic_details()
#print("the Topic URL",list_topic_detail)
data = json.loads(list_topic_detail)
if topics_deploy != "empty":
    for i in data['data']:
        #print("The updated Topic Name is",topic_name_update)
        topic_name_update=i['topic_name']
        if partitions_count == 'default':
            partitions_count_value= i['partitions_count']
        else:
            partitions_count_value = partitions_count

        if replication_factor == 'default':
           replication_factor_value= i['replication_factor']
        else:
            replication_factor_value = replication_factor

        print("the Partition Count is ",partitions_count_value)
        print("the replication_factor_value Count is ",replication_factor_value) 
        #app_json=topic_payload(topic_name_update,i['partitions_count'],i['replication_factor'])
        app_json=topic_payload(topic_name_update,partitions_count_value,replication_factor_value,rentention_days)
        #app_json=topic_payload('devops-test',6,3)

        #print("the App json for Creating the Topic", app_json)
        if topics_deploy == "full":
            #print("Need to Deploy All topics")
            #print("Creating Topic Name",i['topic_name'])
            print("The Source Topic Name is",i['topic_name'])
            print("The Target Topic Name to Create is",topic_name_update)
            print("Creating Topic..",topic_name_update)
            #print("Here is the Application Json for Topic",app_json)
            create_topic(target_cluster_id,app_json)
        else:
            if i['topic_name'] in topics_details:
                print("The Source Topic Name is",i['topic_name'])
                print("The Target Topic Name to Create is",topic_name_update)
                #print("Here is the Application Json for Topic",app_json)
                print("Creating Topic..",topic_name_update)
                create_topic(target_cluster_id,app_json)
                #print("Selected Topic is not in List to Create")
                #print("Here is the Application Json for Topic",app_json)
            else:
                print("Topic is not selected for Sync",i['topic_name'])

for item in topic_deletelist:
    if item == '':
        print("there is no selected Topic to Delete")
    else:
        print("Delete the Topic",item)
        delete_topic(target_cluster_id,item)
