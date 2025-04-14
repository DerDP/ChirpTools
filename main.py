from flask import Flask, request,  url_for
import json
from   chirpstack_api import api
import grpc
from google.protobuf.json_format import MessageToJson
from flask import render_template
import json
from datetime import datetime
from collections import defaultdict
import requests
from config import config
import re

app = Flask(__name__)
app.config.from_object(__name__)

skipped = 0
server  = config.CHIRP_URL
tenant = config.CHIRP_TENANT
api_token = config.CHIRP_API_KEY
snipe = config.SNIPE_URL
snipe_api_token = config.SNIPE_API_KEY
toolTitle = config.TITLE

snipe_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {snipe_api_token}"
    }

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

# Context processor to inject variables into all templates
@app.context_processor
def inject_globals():
    return {
        'title': toolTitle,
        'tenant': tenant
    }


# Searches SnipeIT for ProfileID info. If found it will return Model ID needed for the import

def get_models(search):
    
    snipe_url = f"https://{snipe}/api/v1/models?search="+search
    if snipe:
        models = requests.get(snipe_url, headers=snipe_headers).json()
    else:
        return "snipeNotDefined"
    if models["total"] == 0:
       return "empty"
    elif models["total"] == 1:
       return models["rows"][0]["id"]
    else:
       return "check"
    
# Check if Device is in SnipeIT

def check_snipe(search):

    snipe_url = f"https://{snipe}/api/v1/hardware?search={search}"
    if snipe:
        models = requests.get(snipe_url, headers=snipe_headers).json()
    else:
        return "snipeNotDefined"
    if models["total"] == 0:
       return True
    else:
       return False    
    
# Check if Device is in Chirpstack

def check_chirp(device):
    check = 0
    global skipped

    channel = grpc.secure_channel(server, grpc.ssl_channel_credentials())
    client  = api.DeviceServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    try:
        req = api.GetDeviceRequest()
        req.dev_eui = str(device)
        
        check = 1
        skipped += 1
    except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INTERNAL:
                print('Testing for: ',device,' Error: ', e)
    return check     



# SnipeIT Import function

def snipe_import(asset_tag, status_id, model_id, name, appkey, serial):

    snipe_url = f"https://{snipe}/api/v1/hardware"
    if snipe:
        payload = {
        "asset_tag": asset_tag,
        "status_id": status_id,
        "model_id": model_id,
        "name": "Imported: "+name,
        "serial": serial,
        "_snipeit_appkey_3" : appkey
        }

        device_import = requests.post(snipe_url, json=payload, headers=snipe_headers)
        response_data = device_import.json()
        import_id = response_data["payload"]["id"]
        return(import_id)
    else:
        return 0


    

# Resedual?

def toJson(self):
    return json.dumps(self, default=lambda o: o.__dict__)

#List all apps in tenant_id

def list_app():
    

    channel = grpc.secure_channel(server, grpc.ssl_channel_credentials())
    client  = api.ApplicationServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    try:
        req = api.ListApplicationsRequest()
        req.limit = 10000
        req.tenant_id = tenant
        resp = client.List(req, metadata=auth_token)

    except grpc.RpcError as e:
        print('error:',type(e))
        if e.code() == grpc.StatusCode.INTERNAL:
            print('\n Error while fetching the Apps: ', e)      
    return json.loads(json.dumps(MessageToJson(resp)))
    
#List all devices for given app
    
def list_dev(id):
   

    channel = grpc.secure_channel(server, grpc.ssl_channel_credentials())
    client  = api.DeviceServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    try:
        req = api.ListDevicesRequest()

        req.limit = 10000
        req.application_id = id
        resp = client.List(req, metadata=auth_token)
    except grpc.RpcError as e:
        print('error:',type(e))
        if e.code() == grpc.StatusCode.INTERNAL:
            print('\n Error while fetching the device with ID {id}: ', e)   
    return json.loads(json.dumps(MessageToJson(resp)))


#Get Application Key for selected Device

def get_key(id):
   

    channel = grpc.secure_channel(server, grpc.ssl_channel_credentials())
    client  = api.DeviceServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    try:
        req = api.GetDeviceKeysRequest()
        req.dev_eui = id
        resp = client.GetKeys(req, metadata=auth_token)
    except grpc.RpcError as e:
        print('error:',type(e))
        if e.code() == grpc.StatusCode.INTERNAL:
            print('Error getting keys: ', e)
    return resp.device_keys.nwk_key

# Get Device info for selected Device


def get_profile(id):
   

    channel = grpc.secure_channel(server, grpc.ssl_channel_credentials())
    client  = api.DeviceServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    try:
        req = api.GetDeviceRequest()
        req.dev_eui = id
        resp = client.Get(req, metadata=auth_token)
    except grpc.RpcError as e:
        print('error:',type(e))
        if e.code() == grpc.StatusCode.INTERNAL:
            print('\n Device check Error',id,'\n!\n\n Error: ', e)
    return MessageToJson(resp)

# Get Device profile for selected Device

# Write info

def get_app(app_id):

   channel = grpc.secure_channel(server, grpc.ssl_channel_credentials())
   client  = api.ApplicationServiceStub(channel)
   auth_token = [("authorization", "Bearer %s" % api_token)]
   
   try:
       req = api.GetApplicationRequest()
       req.id = app_id
       resp = client.Get(req, metadata=auth_token)
   
   except grpc.RpcError as e:
       print('error:',type(e))
       if e.code() == grpc.StatusCode.INTERNAL:
           print('Error fetching app: ', e)
   return MessageToJson(resp)

def delete_dev(id):
   
    channel = grpc.secure_channel(server, grpc.ssl_channel_credentials())
    client  = api.DeviceServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    try:
        req = api.DeleteDeviceRequest()

        req.dev_eui = id
        resp = client.Delete(req, metadata=auth_token)
    except grpc.RpcError as e:
        print('error:',type(e))
        if e.code() == grpc.StatusCode.INTERNAL:
            print('Error deleting device: ', e)
    return json.loads(json.dumps(MessageToJson(resp)))


def move_dev(id, new_application_id):
   
    channel = grpc.secure_channel(server, grpc.ssl_channel_credentials())
    client  = api.DeviceServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]
    
    try:

        # Step 1: Get the current device using GetDeviceRequest
        get_req = api.GetDeviceRequest(dev_eui=id)
        get_resp = client.Get(get_req, metadata=auth_token)
        device = get_resp.device

        # Step 2: Update the application ID
        device.application_id = new_application_id
        
        # Step 3: Update the device with the new application ID
        update_req = api.UpdateDeviceRequest(device=device)
        update_resp = client.Update(update_req, metadata=auth_token)
        # Step 4: Return the response as JSON
        return json.loads(json.dumps(MessageToJson(update_resp)))
    except grpc.RpcError as e:
        print('error:', type(e))
        if e.code() == grpc.StatusCode.INTERNAL:
            print(f"\nError moving device {id} to application {new_application_id}!\nError: ", e)
        return None

def grpc_import(devices):
    
    #channel = grpc.insecure_channel(server)
    channel = grpc.secure_channel(server, grpc.ssl_channel_credentials())
    client  = api.DeviceServiceStub(channel)
    auth_token = [("authorization", "Bearer %s" % api_token)]
    skipped = 0
    grpc_result = []
    grpc_result.append("<tr>")
    
    # Method for checking if device from the list is in Chirp
    
    def check_device(device):
        check = 0
        global skipped
        
        try:
            req = api.GetDeviceRequest()
            req.dev_eui = str(device)
            resp = client.Get(req, metadata=auth_token)
            check = 1
            skipped += 1
            print ("Device", skipped,"skipped",device," already in Chirp")
            # grpc_result.append(("Gerät '{}' übersprungen (gefunden in ChirpStack)").format(device))
            grpc_result.append('<td style="text-align: center;background: #ffc107;color: #2256d2;opacity: 0.7;cursor: help;" data-tooltip="Device skipped (found in ChirpStack)">Skipped</td>')
        except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.INTERNAL:
                    print('Testing for: ',device,' Error: ', e)
        return check    
    
    try:
        for dev in devices:
            # Check if device is already in Chirp
            skipped = 0
            try:
               eui = devices[dev]['eui']
               device_eui = str(devices[dev]['eui'].strip())
               device_name = str(devices[dev]['name'].rstrip())
               device_appId = str(devices[dev]['appid'].rstrip())
               device_profileID = str(devices[dev]['device_profile'].rstrip())
               device_appKey = str(devices[dev]['appkey'].rstrip())
               
               grpc_result.append("<td>"+device_name+"</td>")
               if (check_device(eui)) == 0:
                   req = api.CreateDeviceRequest()
                   print(' Creating Device with DevEUI:',devices[dev]['eui'])

                   req.device.dev_eui           = device_eui
                   req.device.name              = device_name
                   req.device.description       = str('imported device')
                   req.device.application_id    = device_appId
                   req.device.device_profile_id = device_profileID
                   
                   resp = client.Create(req, metadata=auth_token)
                   req = api.CreateDeviceKeysRequest()
                   
                   print(' Creating keys for device DevEUI:',devices[dev]['eui'].rstrip())
                   req.device_keys.dev_eui = device_eui
                   req.device_keys.nwk_key = device_appKey
                   resp = client.CreateKeys(req, metadata=auth_token)
                   
                   model = get_models(device_profileID)
                   # grpc_result.append(('<a href="https://{{server}}/#/tenants/{{tenant}}/applications/{}/devices/{}/" target="_blank">Gerät "{}" wurde in ChirpStack importiert</a>').format(device_appId, device_eui, device_name))
                   grpc_result.append(f'<td class="passed" title="Location B Import Successful"><a href="https://{server}/#/tenants/{tenant}/applications/{device_appId}/devices/{device_eui}/" target="_blank" class="passed" title="Location A Import Successful">Imported</a></td>')
                   
                   if(check_snipe(device_eui)):
                   
                        if model == 'check':
                            # grpc_result.append(("Gerät mit DevEUI '{}' wurde nicht in SnipeIT importiert,<br><br> Geräteprofil '{}' hat zwei oder mehr passende Einträge in SnipeIT").format(device_eui, device_profileID ))
                            grpc_result.append('<td class="failed" data-tooltip="Device profile {device_profileID} has two or more matching entries in SnipeIT">Error</td>')
                        
                        elif model == 'empty':
                            import_id = snipe_import(device_eui, '2', '16', device_name, device_appKey, device_eui) 
                            # grpc_result.append(('<a href="https://{{snipe}}/hardware/" target="_blank">Das Gerät "{}" wurde in SnipeIT im Fallback-Modell "Import" importiert.</a>').format(device_name))
                            grpc_result.append(f'<td class="passed" title="Location B Import Successful"><a href="https://{snipe}/hardware/{str(import_id)}" target="_blank" class="passed" title="Device import to SnipeIT was successful">Imported</a></td>')
                            
                            
                        else:
                            import_id = snipe_import(device_eui, '2', model, device_name, device_appKey, device_eui)   
                            # grpc_result.append(('<a href="https://{{snipe}}/models/{}" target="_blank">Gerät "{}" wurde in SnipetIT importiert</a>').format(model, device_name))   
                            grpc_result.append(f'<td class="passed" title="Location B Import Successful"><a href="https://{snipe}/hardware/{str(import_id)}" target="_blank" class="passed" title="Device import to SnipeIT was successful">Imported</a></td>')
                            

                    
                   else:
                        # grpc_result.append(("Gerät '{}' übersprungen (gefunden in SnipeIT)").format(device_eui))
                        grpc_result.append('<td style="text-align: center;background: #ffc107;color: #2256d2;opacity: 0.7;cursor: help;" data-tooltip="Device skipped (found in SnipeIT)"">Skipped</td>')
                   
               else:
                   
                   model = get_models(device_profileID)
                   
                   if(check_snipe(device_eui)):
                   
                        if model == 'check':
                            # grpc_result.append(("Gerät mit DevEUI '{}' wurde nicht in SnipeIT importiert,<br><br> Geräteprofil '{}' hat zwei oder mehr passende Einträge in SnipeIT").format(device_eui, device_profileID ))
                            grpc_result.append('<td class="failed" data-tooltip="Device profile {device_profileID} has two or more matching entries in SnipeIT">Error</td>')
                        
                        elif model == 'empty':
                            import_id = snipe_import(device_eui, '2', '16', device_name, device_appKey, device_eui) 
                            # grpc_result.append(('<a href="https://{{snipe}}/models/16" target="_blank">Das Gerät "{}" wurde in SnipeIT im Fallback-Modell "Import" importiert.</a>').format(device_name))
                            grpc_result.append(f'<td class="passed" title="Location B Import Successful"><a href="https://{snipe}/hardware/{str(import_id)}" target="_blank" class="passed" title="Device import to SnipeIT was successful">Imported</a></td>')
                            
                            
                        else:
                            import_id = snipe_import(device_eui, '2', model, device_name, device_appKey, device_eui)   
                            # grpc_result.append(('<a href="https://{{snipe}}/models/{}" target="_blank">Gerät "{}" wurde in SnipetIT importiert</a>').format(model, device_name))   
                            grpc_result.append(f'<td class="passed" title="Location B Import Successful"><a href="https://{snipe}/hardware/{str(import_id)}" target="_blank" class="passed" title="Device import to SnipeIT was successful">Imported</a></td>')
                            
                        
                    
                   else:
                        # grpc_result.append(("Gerät '{}' übersprungen (gefunden in SnipeIT)").format(device_eui))
                        grpc_result.append('<td  style="text-align: center;background: #ffc107;color: #2256d2;opacity: 0.7;cursor: help;" data-tooltip="Device skipped (found in SnipeIT)"">Skipped</td>')
                
               grpc_result.append("</tr>")
                        
                                
            except KeyError:
               grpc_result.clear()           
               grpc_result.append("Problem with the device import")            
               grpc_result.append("Check that the number of devices in the text field matches")
               pass               
    except grpc.RpcError as e:
        #print('error:',type(e))
        if e.code() == grpc.StatusCode.INTERNAL:
            print('\n Import error device',devices[dev]['eui'],'\n Import aborted! Double check APP ID and Device Profile ID!\n\n Error: ', e)
            grpc_result.append(('Import error: Device {} Import canceled!. <br>Double-check the APP ID and device profile ID!<br><br> Error: <br>"{}"').format(devices[dev]['eui'], e))
    return grpc_result    




#Homepage

@app.route('/')
def app_list():
    result = json.loads(list_app())
    app_list = []
    if result:
        for app in result["result"]:
            id = app["id"]
            name = app["name"]
            url = url_for('list_devices', id=id)
            createdAt =datetime.strptime(app['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S") 
            app_list.append(f'<tr class="ant-table-row ant-table-row-level-0"><td class="ant-table-cell"><a onclick="loading();" href="{url}">{name}</a></td><td class="ant-table-cell">{createdAt}</td></tr>')
    else:
        app_list.append(f'<tr class="ant-table-row ant-table-row-level-0"><td class="ant-table-cell"><p style="text-align: center;font-size: 15px;">No Apps found!</p></td><td class="ant-table-cell"><p style="font-size: 15px;">Check your tenant in <a href="https://{server}/#/tenants/{tenant}/applications" target="_blank">Chirpstack</a></p></td></tr>')
    return render_template('apps.html', result=app_list) 
    
    
@app.route('/import')
def import_device():

    return render_template('import.html') 



# Check if device is in Chirp and/or Snipe

@app.route('/check', defaults={'devEUI': None})
@app.route('/check/<devEUI>')
def check(devEUI):
    dev_check = ""
    if devEUI:
        snipe_check = check_snipe(devEUI)
        chirp_check = bool(check_chirp(devEUI))
    if devEUI:
        dev_check = '<td>'+devEUI+'</td><td class="snipe-info">'+str(chirp_check)+'</td><td class="snipe-info">'+str(not snipe_check)+'</td>'
        dev_check = '<tr class="ant-table-row ant-table-row-level-0"><td class="ant-table-cell">'+devEUI+'</a></td><td class="snipe-info ant-table-cell">'+str(chirp_check)+'</td><td class="snipe-info ant-table-cell">'+str(not snipe_check)+'</td></tr>'
    return render_template('check.html', devEUI=devEUI, dev_check=dev_check) 

# Define a custom Jinja2 filter for regex search
@app.template_filter('regex_search')
def regex_search(value, pattern):
    match = re.search(pattern, value)
    if match:
        return match.group(1)  # Return the first match group
    return None
#Device page for given app

@app.route('/list/<id>', defaults={'snipeIT': None})
@app.route('/list/<id>/<snipeIT>')
def list_devices(id, snipeIT):
    devices = json.loads(list_dev(id))
    apps = json.loads(list_app())
    app_id = id
    get_app_name = json.loads(get_app(id))

    current_app_name = get_app_name["application"]["name"]
    
    app_list = []
    device_list = []
    try:
        for dev in devices["result"]:
            name = dev["name"]
            devEui = dev["devEui"]
            createdAt = datetime.strptime(dev['createdAt'], "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M:%S")
            description = dev.get("description", "-")
            deviceProfile = dev["deviceProfileName"]
            if snipeIT:
                snipe = check_snipe(devEui)
                device_list.append(f'<tr><td><label class="label-container"><input class="checkbox" type="checkbox" id="{name}" name="device" value="{devEui}"><span class="checkmark"></span></label></td><td>{name}</td><td><a target="_blank" href="https://{server}/#/tenants/{tenant}/applications/{id}/devices/{devEui}">{devEui} <svg xmlns="http://www.w3.org/2000/svg" height="10" width="10" viewBox="0 0 512 512"><path d="M320 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l82.7 0L201.4 265.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L448 109.3l0 82.7c0 17.7 14.3 32 32 32s32-14.3 32-32l0-160c0-17.7-14.3-32-32-32L320 0zM80 32C35.8 32 0 67.8 0 112L0 432c0 44.2 35.8 80 80 80l320 0c44.2 0 80-35.8 80-80l0-112c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 112c0 8.8-7.2 16-16 16L80 448c-8.8 0-16-7.2-16-16l0-320c0-8.8 7.2-16 16-16l112 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L80 32z"/></svg></a></td><td>{createdAt}</td></td><td>{description}</td></td><td>{deviceProfile}</td><td class="snipe-info">{str(not snipe)}</td></tr>')
            else:
                 device_list.append(f'<tr><td><label class="label-container"><input class="checkbox" type="checkbox" id="{name}" name="device" value="{devEui}"><span class="checkmark"></span></label></td><td>{name}</td><td><a target="_blank" href="https://{server}/#/tenants/{tenant}/applications/{id}/devices/{devEui}">{devEui} <svg xmlns="http://www.w3.org/2000/svg" height="10" width="10" viewBox="0 0 512 512"><path d="M320 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l82.7 0L201.4 265.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L448 109.3l0 82.7c0 17.7 14.3 32 32 32s32-14.3 32-32l0-160c0-17.7-14.3-32-32-32L320 0zM80 32C35.8 32 0 67.8 0 112L0 432c0 44.2 35.8 80 80 80l320 0c44.2 0 80-35.8 80-80l0-112c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 112c0 8.8-7.2 16-16 16L80 448c-8.8 0-16-7.2-16-16l0-320c0-8.8 7.2-16 16-16l112 0c17.7 0 32-14.3 32-32s-14.3-32-32-32L80 32z"/></svg></a></td><td>{createdAt}</td><td>{description}</td></td><td>{deviceProfile}</td></tr>')
        for app in apps["result"]:
            app_id = app["id"]
            app_name = app["name"]
            app_list.append('<option value="'+app_id+'" id="'+app_name+'">'+app_name+'</option>')
    except KeyError as ke:
        device_list.append('No devices')
        app_list.append('')       

    devices = device_list
    apps = app_list
    return render_template('devices.html', devices=devices, apps=apps, app_id=app_id, current_app_name=current_app_name, id=id, snipeIT=snipeIT )
 

#Update database

@app.route('/update', methods=[ 'POST'])
def index():
    ip_addr = request.remote_addr
    number = 0
    skipped = 0
    action = ''
    if request.method == 'POST': 
        if request.form['submit'] == 'move':
            devices = request.form.getlist('device')
            newApp = request.form.getlist('newApp')
            action = 'move'
            for device in devices:
                move_dev(device,newApp[0])
                number+=1

            return render_template('success.html', devices=devices, newApp=newApp, number=number, action=action, server=server, tenant=tenant)     
        
        if  request.form['submit'] == 'delete':
            action = 'delete'
            devices = request.form.getlist('device')
            for device in devices:
                number+=1
                delete_dev(device)

        if  request.form['submit'] == 'snipeImport':
            action = 'importSnipe'
            devices = request.form.getlist('device')
            snipeImport = []
            for device in devices:
                deviceResult = json.loads(get_profile(device))
                deviceProfile = deviceResult["device"]["deviceProfileId"]
                device_name = deviceResult["device"]["name"]
                model = get_models(deviceProfile)
                device_appKey = get_key(device)
                if(not check_snipe(device)):
                    skipped+=1

                elif(check_snipe(device) and model != 'check'):

                    if model == 'empty':
                        import_id = snipe_import(device, '2', '16', device_name, device_appKey, device) 
                        # grpc_result.append(('<a href="https://{{snipe}}/hardware/" target="_blank">Das Gerät "{}" wurde in SnipeIT im Fallback-Modell "Import" importiert.</a>').format(device_name))
                        snipeImport.append('<td class="passed" title="Location B Import Successful"><a href="https://{{snipe}}/hardware/'+str(import_id)+'" target="_blank" class="passed" title="Location A Import Successful">'+device+'</a></td>')
                        number+=1
                        
                    else:
                        import_id = snipe_import(device, '2', model, device_name, device_appKey, device)   
                        # grpc_result.append(('<a href="https://{{snipe}}/models/{}" target="_blank">Gerät "{}" wurde in SnipetIT importiert</a>').format(model, device_name))   
                        snipeImport.append(('<td class="passed" title="Location B Import Successful"><a href="https://{{snipe}}/hardware/'+str(import_id)+'" target="_blank" class="passed" title="Location A Import Successful">'+device+'</a></td>').format(model))
                        number+=1
            return render_template('success.html', snipeImport=snipeImport, number=number,skipped=skipped, action=action, server=server, tenant=tenant)
                

        
        return render_template('success.html', devices=devices, number=number, action=action, server=server, tenant=tenant) 




#Import Device
        
@app.route('/db_import', methods=[ 'POST'])
def import_device_db():
    if request.method == 'POST': 
   
        import_values = defaultdict(dict)
        action = 'import'
        euis = request.form.get('eui').splitlines()
        appids = request.form.get('appid').splitlines()
        device_profiles = request.form.get('device_profile').splitlines()
        names = request.form.get('name').splitlines()
        appkeys = request.form.get('appkey').splitlines()
        
        checkbox = request.form.get('checkbox')
        
        print(checkbox)
        
        for device, eui in enumerate(euis):
            import_values[device]['eui'] = eui
            
        for device, appid in enumerate(appids):
            import_values[device]['appid'] = appid
            
        for device, device_profile in enumerate(device_profiles):
            import_values[device]['device_profile'] = device_profile     
            
        for device, name in enumerate(names):
            import_values[device]['name'] = name
            
        for device, appkey in enumerate(appkeys):
            import_values[device]['appkey'] = appkey            
        
        final = grpc_import(import_values)

        return render_template('success.html', final = final, action=action)
    

if __name__ == '__main__':
    app.run(debug=True)        
    
    
    
    