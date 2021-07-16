import aeromiko
import argparse
from csv import DictReader
import socket
import natsort
import operator
from pyfiglet import Figlet
import re
import sys
import warnings
import pprint
import os
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.listitems.caml.caml_query import CamlQuery

#                     #
#     ## #    ####   ##    # ##
#     # # #  #   #    #    ##  #
#     # # #  #   #    #    #   #
#     # # #  #  ##    #    #   #
#     #   #   ## #   ###   #   #


def main():
    if len(sys.argv) == 1:
        print("This script requires two arguments:")
        print("<Required> an APList file path. A csv file with a list of APs including Hostname,IPAddress,Username,Password")
        print("<Required> a Sharepoint Config file path. A plain text file with these details on each line, in order: AzureTenantID, AzureClientID, CertificateThumbprint, Private Key path, SiteURL, (optional)TenantRootURL")
        sys.exit(1)
        
    APListFile = str(sys.argv[1]).strip()
    #Test Path is Valid
    if not os.path.isfile(APListFile):
        print("<Invalid> The supplied csv file needs to contain a list of APs including Hostname,IPAddress,Username,Password (comma seperated)")
        sys.exit(1)

    sharepointConfigFile = str(sys.argv[2]).strip()
    #Test Path is Valid
    if not os.path.isfile(sharepointConfigFile):
        print("<Invalid> a Sharepoint Config file path is required. A plain text file with these details on each line, in order: AzureTenantID, AzureClientID, CertificateThumbprint, Private Key path, SiteURL, (optional)TenantRootURL")
        sys.exit(1)

    def isgoodipv4(s):
        pieces = s.split(".")
        if len(pieces) != 4:
            return False
        try:
            return all(0 <= int(p) < 256 for p in pieces)
        except ValueError:
            return False
                
    # open file in read mode
    with open(APListFile, 'r') as read_obj:
        # pass the file object to DictReader() to get the DictReader object
        dict_reader = DictReader(read_obj)
        # get a list of dictionaries from dct_reader
        APList = list(dict_reader)
        
    #Connect to Sharepoint
    configFile = open(sharepointConfigFile, 'r')
    configLines = configFile.readlines()
    if len(configLines) < 5 or len(configLines) > 6:
        print("The file Sharepoint.config needs to be created with five or six lines: TenantID, clientID, Certificate Thumbprint, Certificate path, site URL, and Sharepoint website URL")
        sys.exit(1)   
    sharepointTenantID = configLines[0].strip()
    sharepointClientID = configLines[1].strip()
    sharepointCertThumbprint = configLines[2].strip()
    sharepointCertPath = configLines[3].strip().format(os.path.dirname(__file__))
    sharepointSite = configLines[4].strip()
    if configLines[5]:
        website = configLines[5].strip()
    else:
        website = configLines[4].strip()
    global ctx
    authctx = AuthenticationContext(website).with_client_certificate(sharepointTenantID, sharepointClientID, sharepointCertThumbprint, sharepointCertPath)
    ctx = ClientContext(sharepointSite, authctx)
    web = ctx.web
    ctx.load(web)
    ctx.execute_query()

    for AP in APList:
        if isgoodipv4(AP['IPAddress']):
            get_info(AP)


def get_info(AP):
    # ignore self-signed cert error
    warnings.filterwarnings(action="ignore", module=".*paramiko.*")

    access_point = aeromiko.AP(AP['IPAddress'], AP['Username'], AP['Password'])
    access_point.connect()

    # get hostname via Aeromiko
    access_point.hostname = access_point.get_hostname()
    # get model# and uptime info via Aeromiko
    version_info = access_point.show_version()
    access_point.platform = version_info["PLATFORM"]
    access_point.uptime = version_info["UPTIME"]
    # get lldp information via Aeromiko
    #lldp_info = access_point.show_lldp_neighbor()
    #access_point.lldp_neighbor = lldp_info["SYSTEM_NAME"]
    #access_point.lldp_neighbor_port = lldp_info["PORT_DESC"]

    # get eth0 information via Aeromiko
    eth0_info = access_point.show_int_eth("eth0")
    access_point.link_duplex = eth0_info["DUPLEX"]
    access_point.link_speed = eth0_info["SPEED"]

    # get CPU Info via Aeromiko
    snapshot_cpu = access_point.show_cpu()
    access_point.cpu_total = snapshot_cpu["CPU_TOTAL"]
    access_point.cpu_system = snapshot_cpu["CPU_SYSTEM"]
    access_point.cpu_user = snapshot_cpu["CPU_USER"]

    # Get Channel information 
    access_point = ap_channels(access_point)
    # get Radio information
    access_point = ap_radios(access_point)

    print(str(access_point))
    sharepoint_update('AccessPoints', 
         {
             "AP_Name": access_point.hostname, 
             "Model": access_point.platform,
             "Uptime": access_point.uptime,
             "CPU_Total": access_point.cpu_total,
             "CPU_User": access_point.cpu_user,
             "CPU_System": access_point.cpu_system,
             "Wifi0_Channel": access_point.wifi0_Channel,	
             "Wifi0_TX_Power": access_point.wifi0_TX_Power,
             "Wifi1_Channel": access_point.wifi1_Channel,
             "Wifi1_TX_Power": access_point.wifi1_TX_Power,
             "wifi0_RX_Bytes": access_point.wifi0_rx_bytes,	
             "wifi0_TX_Bytes": access_point.wifi0_tx_bytes,
             "wifi1_RX_Bytes": access_point.wifi1_rx_bytes,
             "wifi1_TX_Bytes": access_point.wifi1_tx_bytes,
             "wifi0_RX_Drops": access_point.wifi0_RX_Drops,
             "wifi0_TX_Drops": access_point.wifi0_TX_Drops,
             "wifi1_RX_Drops": access_point.wifi1_RX_Drops,
             "wifi1_TX_Drops": access_point.wifi1_TX_Drops,
             "wifi0_RX_Errors": access_point.wifi0_RX_Errors,
             "wifi0_TX_Errors": access_point.wifi0_TX_Errors,
             "wifi1_RX_Errors": access_point.wifi1_RX_Errors,
             "wifi1_TX_Errors": access_point.wifi1_TX_Errors
         }, 
         "<Where><Eq><FieldRef Name='AP_Name' /><Value Type='Text'>"+access_point.hostname+"</Value></Eq></Where>"
    )

    ap_neighbors(access_point)
    ap_stations(access_point)


    #            #                                   ##
    #            #                                    #
    #      ####  ####    ####  # ##   # ##    ###     #     ####
    #     #      #   #  #   #  ##  #  ##  #  #   #    #    #
    #     #      #   #  #   #  #   #  #   #  #####    #     ###
    #     #      #   #  #  ##  #   #  #   #  #        #        #
    #      ####  #   #   ## #  #   #  #   #   ###    ###   ####


def ap_channels(access_point):
    # get and output channel and power information for each radio
    parsed_acsp = access_point.show_acsp()

    # for each
    for radio in parsed_acsp:
        for (key, value) in radio.items():
            key = radio["INTERFACE"] + "_" + key
            key = key.lower()
            setattr(access_point, key, value)

    for radio in ("wifi0", "wifi1"):
        # use getattr cause string + variable concat getting used as var name
        channel_select_state = getattr(
            access_point, radio + "_channel_select_state", ""
        )
        primary_channel = radio + "_primary_channel"

        # ensure asterisk decoration if channel is manually set
        if channel_select_state == "Disable(User disable)":
            if "*" not in getattr(access_point, primary_channel):
                man_chan = getattr(access_point, primary_channel) + "*"
                setattr(access_point, primary_channel, man_chan)

        interface = getattr(access_point, radio + "_interface")
        chan = getattr(access_point, primary_channel)
        txpower = getattr(access_point, radio + "_tx_power_dbm")
        setattr(access_point, radio + "_Channel", getattr(access_point, primary_channel)) 
        setattr(access_point, radio + "_TX_Power", getattr(access_point, radio + "_tx_power_dbm"))
    return access_point

    #                    #           #      #
    #                                #      #
    #    # ##    ###    ##     ####  ####   ####    ###   # ##    ####
    #    ##  #  #   #    #    #   #  #   #  #   #  #   #  ##     #
    #    #   #  #####    #    #   #  #   #  #   #  #   #  #       ###
    #    #   #  #        #     ####  #   #  #   #  #   #  #          #
    #    #   #   ###    ###       #  #   #  ####    ###   #      ####
    #                          ###


def ap_neighbors(access_point):
    parsed_neighbors = access_point.show_acsp_neighbor()
    bssid_list = []

    neighbor_table = []
    neighbor_table.append(["AP Name", "BSSID", "CH", "RSSI", "SSID", "CU", "CRC", "STA"])

    parsed_neighbors.sort(key=operator.itemgetter("RSSI"))
    parsed_neighbors = natsort.natsorted(
        parsed_neighbors, key=operator.itemgetter("CHANNEL")
    )

    for neighbor in parsed_neighbors:
        # if BBSID !unique, drop it
        if neighbor["BSSID"] not in bssid_list:
            bssid_list.append(neighbor["BSSID"])

            # only show neighbors that we have to share airtime with
            if int(neighbor["RSSI"]) >= -85:
                neighbor["AP_Name"] = access_point.hostname

                # copy radio channel so we can decorate the copy and still
                #   use the original for comparison with neighboring APs
                neighbor["DECORATED_CHANNEL"] = neighbor["CHANNEL"]

                # decorate neighbors with > 20 MHz channel usage
                if neighbor["CHANNEL_WIDTH"] != "20":
                    neighbor["DECORATED_CHANNEL"] += (
                        " (" + neighbor["CHANNEL_WIDTH"] + "MHz)"
                    )

                w0_channel = re.sub("[*]", "", access_point.wifi0_primary_channel)
                w1_channel = re.sub("[*]", "", access_point.wifi1_primary_channel)

                sharepoint_update('Neighbors', neighbor, "<Where><And><Eq><FieldRef Name='AP_Name' /><Value Type='Text'>"+neighbor["AP_Name"]+"</Value></Eq><Eq><FieldRef Name='BSSID' /><Value Type='Text'>"+neighbor["BSSID"]+"</Value></Eq></And></Where>")


    #              #             #      #
    #              #             #
    #      ####  #####   ####  #####   ##     ###   # ##
    #     #        #    #   #    #      #    #   #  ##  #
    #      ###     #    #   #    #      #    #   #  #   #
    #         #    #    #  ##    #      #    #   #  #   #
    #     ####      ##   ## #     ##   ###    ###   #   #


def ap_stations(access_point):
    parsed_stations = access_point.show_station()
    station_table = [
        [
            "AP Name",
            "SSID",
            "MAC",
            "IP",
            "Hostname",
            "Ch",
            "Tx Rate",
            "Rx Rate",
            "Pow(SNR)",
            "Assoc",
            "PHY",
            "State",
        ]
    ]

    parsed_stations.sort(key=operator.itemgetter("MAC_ADDR"))
    parsed_stations = natsort.natsorted(
        parsed_stations, key=operator.itemgetter("SSID")
    )

    for station in parsed_stations:
        station["AP_Name"] = access_point.hostname
        if station["IP_ADDR"] == "0.0.0.0":
            station["Hostname"] = ""
        else:
            station["Hostname"] = socket.gethostbyaddr(station["IP_ADDR"])[0]

        w0_channel = re.sub("[*]", "", access_point.wifi0_primary_channel)
        w1_channel = re.sub("[*]", "", access_point.wifi1_primary_channel)

        sharepoint_update('Stations', station, "<Where><Eq><FieldRef Name='MAC_ADDR' /><Value Type='Text'>"+station["MAC_ADDR"]+"</Value></Eq></Where>")


    #                       #    #
    #                       #
    #     # ##    ####   ####   ##     ###
    #     ##     #   #  #   #    #    #   #
    #     #      #   #  #   #    #    #   #
    #     #      #  ##  #   #    #    #   #
    #     #       ## #   ####   ###    ###


def ap_radios(access_point):
    for radio in ("wifi0", "wifi1"):
        parsed_radio_int = access_point.show_int_wifi(radio)

        # prepend wifiN_ before conversion to  properties
        for (key, value) in parsed_radio_int[0].items():
            key = radio + "_" + key
            key = key.lower()
            setattr(access_point, key, value)

        def AP_info(info):
            return getattr(access_point, radio + "_" + info)

        def percent(numerator, denominator):
            answer = int(AP_info(numerator)) / int(AP_info(denominator))
            rounded = round(answer, 2)
            stringified = str(rounded) + "%"
            return stringified

        setattr(access_point, radio+"_RX_Drops", percent("rx_drops", "rx_packets")) 
        setattr(access_point, radio+"_TX_Drops", percent("tx_drops", "tx_packets")) 
        setattr(access_point, radio+"_RX_Errors", percent("rx_err", "rx_packets"))
        setattr(access_point, radio+"_TX_Errors", percent("tx_err", "tx_packets"))

    return access_point

OPERATOR_SYMBOLS = {
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "in": operator.contains,
}


def sharepoint_update(listName, item, dupQuery):
    SPlist = ctx.web.lists.get_by_title(listName)
    caml_query = CamlQuery.parse(dupQuery)
    items = SPlist.get_items(caml_query)
    ctx.load(SPlist)
    ctx.execute_query()
    if len(items) >= 1:
        #Update the existing item
        item_to_update = items[0]
        for attr, value in item.items():
            item_to_update.set_property(attr,value)
        item_to_update.update().execute_query()
    else:
        #Create a new Item
        SPlist.add_item(item).execute_query()
        
#                            #
#            ## #    ####   ##    # ##
#            # # #  #   #    #    ##  #
#            # # #  #   #    #    #   #
#            # # #  #  ##    #    #   #
#    ######  #   #   ## #   ###   #   # ######

if __name__ == "__main__":
    sys.exit(main())
