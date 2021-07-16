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

### List 'Stations'
```
InternalName              TypeDisplayName
------------              ---------------
AP_Name                   Single line of text
SSID                      Single line of text
MAC_ADDR                  Single line of text
IP_ADDR                   Single line of text
Hostname                  Single line of text
CHAN                      Number
TX_RATE                   Single line of text
RX_RATE                   Single line of text
POW_SNR                   Single line of text
ASSOC_TIME                Single line of text
PHYMODE                   Single line of text
STATION_STATE             Single line of text
IFNAME                    Single line of text
ASSOC_MODE                Single line of text
CIPHER                    Single line of text
VLAN                      Single line of text
AUTH                      Single line of text
UPID                      Single line of text
LDPC                      Single line of text
TX_STBC                   Single line of text
RX_STBC                   Single line of text
SM_PS                     Single line of text
CHAN_WIDTH                Single line of text
MUMIMO                    Single line of text
RELEASE                   Single line of text
```

### List 'AccessPoints'
```
InternalName              TypeDisplayName
------------              ---------------
AP_Name                   Single line of text
Model                     Single line of text
Uptime                    Single line of text
CPU_Total                 Single line of text
CPU_User                  Single line of text
CPU_System                Single line of text
Wifi0_Channel             Single line of text
Wifi0_TX_Power            Single line of text
Wifi1_Channel             Single line of text
Wifi1_TX_Power            Single line of text
wifi0_RX_Bytes            Single line of text
wifi0_TX_Bytes            Single line of text
wifi1_RX_Bytes            Single line of text
wifi1_TX_Bytes            Single line of text
wifi0_RX_Drops            Single line of text
wifi0_TX_Drops            Single line of text
wifi1_RX_Drops            Single line of text
wifi1_TX_Drops            Single line of text
wifi0_RX_Errors           Single line of text
wifi0_TX_Errors           Single line of text
wifi1_RX_Errors           Single line of text
wifi1_TX_Errors           Single line of text
```

### List 'Neighbors'
```
InternalName              TypeDisplayName
------------              ---------------
AP_Name                   Single line of text
BSSID                     Single line of text
RSSI                      Single line of text
SSID                      Single line of text
CU                        Single line of text
CRC                       Single line of text
STA                       Single line of text
MODE                      Single line of text
CHANNEL                   Single line of text
AEROHIVE                  Single line of text
CHANNEL_WIDTH             Single line of text
DECORATED_CHANNEL         Single line of text
```