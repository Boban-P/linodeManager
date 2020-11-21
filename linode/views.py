from django.shortcuts import render
from django.utils import timezone
from .models import VMclass, VMInstance, LinodeSetting
from linode_api4 import *
import paramiko
import json
# Create your views here.
client = False
settings = False

def getSetting(name:string):
    global settings
    if not settings:
        settings = {}
        for setting in LinodeSetting.objects.all():
            settings[setting.title] = setting.value
    return settings[name]

def getClient() -> LinodeClient:
    global client
    if not client:
        client = LinodeClient(getSetting("token"))
    return client

def getPublicKey():
    return getSetting('publickey')


def doNetwork(domain, subDomain, ip, linode: Instance):
    client = getClient()
    obj = client.domains(Domain.domain==domain)[0]
    record = obj.record_create(record_type='A', name=subDomain, target=ip, ttl_sec=300)
    # TODO: do a reverse dns enty
    # curl -H "Content-Type: application/json" \
    # -H "Authorization: Bearer $TOKEN \
    # -X PUT -d '{
    #   "rdns": "{subdomain}.{domain}"
    # }' \
    # https://api.linode.com/v4/linode/instances/{linode.id}/ips/{ip}
    return record

def removeNetwork(domain, subDomain):
    client = getClient()
    obj = client.domains(Domain.domain==domain)[0]
    for record in obj.records:
        if record.type == 'A' and record.name == subDomain:
            record.delete()

def createNewVM(classId):
    Class = VMclass.objects.get(id=classId)
    client = getClient()
    args = {}
    args['stackscript'] = int(Class.stackscript)
    args['stackscript_data'] = {
        "repourl" : Class.repourl,
        "repobranch" : Class.repobranch,
        "reponame" : Class.repoName,
        "project" : Class.project,
        "domain" : Class.domain,
        "subDomain" : Class.subDomain,
        "bucket" : Class.bucket,
        "systemBackup": Class.systemBackup,
        "backupFile" : Class.backupfile,
        "restoreFile": "default",
        "accessKey" : Class.bucketKey,
        "secretKey" : Class.bucketSecret,
    }
    args['private_ip'] = True
    args['label'] = Class.label

    ts = timezone.now()
    linode, password = client.linode.instance_create(Class.type, Class.region, Class.image, getPublicKey(), **args)
    doNetwork(Class.domain, linode.id, linode.ips.ipv4.public[0].address, linode)
    instance = VMInstance.objects.create(backupfile="{}.{}".format(linode.id, Class.backupfile), classInstance=Class, created=ts, lastrun=ts, rootPassword=password, state=1)
    return instance

def createVm(classId, instanceId):
    Class = VMclass.objects.get(id=classId)
    Instance = VMInstance.objects.get(classInstance=Class, id=instanceId)
    if Instance:
        client = getClient()
        args = {}
        args['stackscript'] = int(Class.stackscript)
        args['stackscript_data'] = {
            "repourl" : Class.repourl,
            "repobranch" : Class.repobranch,
            "reponame" : Class.repoName,
            "project" : Class.project,
            "domain" : Class.domain,
            "subDomain" : Class.subDomain,
            "bucket" : Class.bucket,
            "systemBackup": Class.systemBackup,
            "backupFile" : Instance.backupfile,
            "restoreFile": Instance.backupfile,
            "accessKey" : Class.bucketKey,
            "secretKey" : Class.bucketSecret,
        }
        args['private_ip'] = True
        args['label'] = Class.label
        args['root_password'] = Instance.rootPassword

        ts = timezone.now()
        linode, password = client.linode.instance_create(Class.type, Class.region, Class.image, getPublicKey(), **args)
        doNetwork(Class.domain, linode.id, linode.ips.ipv4.public[0].address, linode)
        Instance.lastrun = ts
        Instance.state = 1
        Instance.save()
    
    return Instance

def stopVM(classId, vmId):
    Class = VMclass.objects.get(id=classId)
    vmInstance = VMInstance.objects.get(classInstance=Class, id=vmId)
    client = getClient()
    try:
        linode = client.linode.instances(Instance.label==Class.label).first()
    except:
        linode = None
        pass
    # shutdown services.
    # backup data to bucket.
    # shutdown server.
    if linode:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(linode.ips.ipv4.public[0].address, username='root', password=vmInstance.rootPassword)
        stdin, stdout, stderr = ssh.exec_command('shutdown.sh')
        print(stdout)
        print(stderr)
        linode.delete()
    # remove ip address
    removeNetwork(Class.domain, Class.subDomain)
    vmInstance.state=2
    vmInstance.save()
    return vmInstance

def extendVm(vmId):
    Instance = VMInstance.objects.get(id=vmId)
    ts = timezone.now().timestamp()
    Instance.lastrun = ts
    Instance.save()
    return Instance

def shutdownPending():
    ts = timezone.now().timestamp() - 7200
    insts = VMInstance.objects.filter(lastrun__less_than=ts, state__less_than=2)
    for I in insts:
        try:
            obj = VMInstance.objects.get(id=I.pk, lastrun__greater_than=ts)
            stopVM(obj.classInstance, obj.pk)
        except :
            pass


# View functions.


def listVMClass(request):
    classes = VMclass.objects.all()
    count = classes.count()
    if count == 0:
        info = "No records found"
    else:
        info = ""
    return render(request, 'listClass.html.djt', {'list':classes, 'count': count, 'info': info})


def viewVM(request, id):
    Class = VMclass.objects.get(id=id)
    Instances = VMInstance.objects.filter(classInstance=Class).order_by('lastrun')
    active = Instances.filter(state=1).first()
    ts = timezone.now().timestamp()
    ts = 7200 + active.lastrun.timestamp() - ts if active else 0
    try:
        linode = client.linode.instances(Instance.label==Class.label).first()
    except:
        linode = None
        pass
    domain = "{}.{}".format(linode.id, Class.domain)
    return render(request, 'viewClass.html.djt', {'class': Class, 'Instances': Instances, 'active': active, 'remaining': ts, "domain" : domain})


def startVM(request, classId):
    # check weather the vm is shutdown.
    Class = VMclass.objects.get(id=classId)
    Instances = VMInstance.objects.filter(classInstance=Class).order_by('lastrun')
    active = Instances.filter(state=1).first()
    if not active:
        inst = createNewVM(classId)
    return viewVM(request, classId)

def extendVM(request, classId):
    # get active vm && extend
    Class = VMclass.objects.get(id=classId)
    Instances = VMInstance.objects.filter(classInstance=Class).order_by('lastrun')
    active = Instances.filter(state=1).first()
    if active:
        active.lastrun = timezone.now()
        active.save()
    return viewVM(request, classId)

def terminateVM(request, classId):
    # stop the active VM
    Class = VMclass.objects.get(id=classId)
    Instances = VMInstance.objects.filter(classInstance=Class).order_by('lastrun')
    active = Instances.filter(state=1).first()
    if active:
        stopVM(classId, active.pk)
    return viewVM(request, classId)

def restartVM(request, classId, vmId):
    # check weather vm is shutdown.
    Class = VMclass.objects.get(id=classId)
    Instances = VMInstance.objects.filter(classInstance=Class).order_by('lastrun')
    active = Instances.filter(state=1).first()
    inst = VMInstance.objects.get(id=vmId, classInstance=Class)
    if not active and inst:
        createVM(classId, vmId)
    return viewVM(request, classId)

def runcron(request):
    shutdownPending()
    return render(request, 'cron.html.djt', {})

