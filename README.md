# Aerohive-toSharepoint
Python based on Aeromiko and shareplum to keep update Aerohive AP stats in Sharepoint

## Setup Sharepoint/Azure Credentials
https://github.com/vgrem/Office365-REST-Python-Client/blob/master/examples/sharepoint/ConnectionWithCert.md

## Save Sharepoint Deailts to Sharepoint.config
```
AzureTenantID
ClientID-From above
CertificateThumbprint-From above
/home/pi/privateKey.key
https://tenant.sharepoint.com/sites/AerohiveMonitor
https://tenant.sharepoint.com
```

## Setup APList Config File
```
Hostname,IPAddress,Username,Password
AP-KITCHEN,192.168.1.22,admin,xxxx
AP-BEDROOM,192.168.1.20,admin,xxxx
AP-HALLWAY,192.168.1.24,admin,xxxx
```

## Setup Sharepoint Lists/Fields
