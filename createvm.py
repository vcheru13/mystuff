#!/usr/bin/env python

"""
Python program for creating VM on lab ESX and set up for PXE/kickstart
"""

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim

import atexit
import time
import ssl


def get_obj(content, vimtype, name):
    """
    Return an object by name, if name is None the
    first found object is returned
    """
    obj = None
    container = content.viewManager.CreateContainerView(
        content.rootFolder, vimtype, True)
    for c in container.view:
        if name:
            if c.name == name:
                obj = c
                break
        else:
            obj = c
            break

    return obj

def add_scsi_ctl(bus):
	"""
	Add SCSI controller numberd bus
	"""
	ctl_spec = vim.vm.device.VirtualDeviceSpec()
	ctl_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
	ctl_spec.device = vim.vm.device.ParaVirtualSCSIController( 
			sharedBus=vim.vm.device.VirtualSCSIController.Sharing.noSharing,
			busNumber=bus )
	return ctl_spec

def add_disk_to_ctl(ctldevice,unitNum,sizeGB):
	"""
	Add disk on controller
	"""
   	disk_size_kb = sizeGB * 1024 *1024
	disk_spec = vim.vm.device.VirtualDeviceSpec()
	disk_spec.fileOperation = "create"
	disk_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
	disk_spec.device = vim.vm.device.VirtualDisk()
	disk_spec.device.backing = vim.vm.device.VirtualDisk.FlatVer2BackingInfo()
	disk_spec.device.backing.thinProvisioned = True
	disk_spec.device.backing.diskMode = 'persistent'
	disk_spec.device.unitNumber = unitNum
	disk_spec.device.capacityInKB = disk_size_kb
	disk_spec.device.controllerKey = ctldevice.key
	return disk_spec


def add_vnic(network):
	"""
	Add vNIC
	"""
    	nic_spec = vim.vm.device.VirtualDeviceSpec()
    	nic_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add
    	nic_spec.device = vim.vm.device.VirtualVmxnet3()

    	nic_spec.device.deviceInfo = vim.Description()
    	nic_spec.device.deviceInfo.summary = 'My VMXnet'

    	nic_spec.device.backing = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
    	nic_spec.device.backing.useAutoDetect = False

    	nic_spec.device.backing.network = network
    	nic_spec.device.backing.deviceName = network.name

    	nic_spec.device.connectable = vim.vm.device.VirtualDevice.ConnectInfo()
    	nic_spec.device.connectable.startConnected = True
    	nic_spec.device.connectable.allowGuestControl = True
    	nic_spec.device.connectable.connected = True
    	nic_spec.device.connectable.status = 'ok'
    	nic_spec.device.addressType = 'generated'
	return nic_spec


def create_vm(vm_name,vCpus,ramMB,diskSizeGB,si,vm_folder,resource_pool,datastore,network):
	"""
	Create VM
	"""
	datastore_path = '[' + datastore.name + ']' + vm_name

	# bare VMX file config
	vmx_file = vim.vm.FileInfo(logDirectory=None,snapshotDirectory=None,suspendDirectory=None,
				vmPathName=datastore_path)

	config = vim.vm.ConfigSpec(name=vm_name,memoryMB=ramMB,numCPUs=vCpus,files=vmx_file,guestId='centos7_64Guest')

	dev_changes = []	# Array containing all new devices

	# Add SCSI controller
	ctl_spec = add_scsi_ctl(0)
	dev_changes.append(ctl_spec)

   	# Add VirtualDisk
	disk_spec = add_disk_to_ctl(ctl_spec.device,0,diskSizeGB)
	dev_changes.append(disk_spec)

   	# Add VirtualEthernet
	nic_spec = add_vnic(network)
	dev_changes.append(nic_spec)

	# Make config changes to main Spec
	config.deviceChange = dev_changes

	print "Creating VM",vm_name,
	
	task = vm_folder.CreateVM_Task(config=config,pool=resource_pool)
    	while task.info.state not in [vim.TaskInfo.State.success,vim.TaskInfo.State.error]:
	   print '.',
	   time.sleep(0.1)

	if task.info.state == vim.TaskInfo.State.success:
		print "VM Created successfully"
	else:
		print "VM Creation failed"

def main():
   """
   Main
   """
   esx_host = 'myesx.lab.local'
   esx_user = 'root'

   password = getpass.getpass(prompt='Enter password for host %s and '
                                        'user %s: ' % (esx_host,esx_user))

   context = ssl._create_unverified_context()
   si = SmartConnect(host=esx_host,user=esx_user,pwd=password,port=443,sslContext=context)
   if not si:
       print("Could not connect to the specified host using specified username and password")
       return -1

   atexit.register(Disconnect, si)	# disconnect from esx before exit of program

   content = si.RetrieveContent()	# retrieve content from ESX host

   datacenter = content.rootFolder.childEntity[0]
   vmfolder = datacenter.vmFolder
   resource_pool = get_obj(content,[vim.ResourcePool],None)
   datastore = get_obj(content,[vim.Datastore],'datastore1')		# retrieve datastore object
   network = get_obj(content,[vim.Network],'VM Network')		# retrieve network object

   create_vm('cent4.lab.local',1,2048,16,si,vmfolder,resource_pool,datastore,network)


# Start program
if __name__ == "__main__":
   main()
