# Copyright (C) 2010-2011 AG Projects. See LICENSE for details.
#

"""
SIP SIMPLE SDK settings extensions.
"""

__all__ = ['AccountExtension', 'BonjourAccountExtension', 'SylkServerSettingsExtension']

import os

from sipsimple.account import MSRPSettings as AccountMSRPSettings, NATTraversalSettings as AccountNATTraversalSettings
from sipsimple.account import RTPSettings as AccountRTPSettings, SIPSettings as AccountSIPSettings, TLSSettings as AccountTLSSettings
from sipsimple.configuration import CorrelatedSetting, Setting, SettingsObjectExtension
from sipsimple.configuration.datatypes import AudioCodecList, MSRPTransport, NonNegativeInteger, Path, Port, PortRange, SampleRate, SIPProxyAddress, SIPTransportList, SRTPEncryption
from sipsimple.configuration.settings import AudioSettings, LogsSettings, RTPSettings, SIPSettings, TLSSettings

from sylk import __version__ as server_version
from sylk.configuration import ServerConfig, SIPConfig, MSRPConfig, RTPConfig


# Account settings extensions

msrp_transport = 'tls' if MSRPConfig.use_tls else 'tcp'
class AccountMSRPSettingsExtension(AccountMSRPSettings):
    transport = Setting(type=MSRPTransport, default=msrp_transport)

class AccountNATTraversalSettingsExtension(AccountNATTraversalSettings):
    use_msrp_relay_for_inbound = Setting(type=bool, default=False)
    use_msrp_relay_for_outbound = Setting(type=bool, default=False)


class AccountRTPSettingsExtension(AccountRTPSettings):
    audio_codec_list = Setting(type=AudioCodecList, default=RTPConfig.audio_codecs, nillable=True)
    srtp_encryption = Setting(type=SRTPEncryption, default=RTPConfig.srtp_encryption)
    use_srtp_without_tls = Setting(type=bool, default=True)


class AccountSIPSettingsExtension(AccountSIPSettings):
    register = Setting(type=bool, default=False)
    outbound_proxy = Setting(type=SIPProxyAddress, default=SIPConfig.outbound_proxy, nillable=True)


tls_certificate = Path(ServerConfig.certificate) if ServerConfig.certificate and os.path.isfile(ServerConfig.certificate) else None
class AccountTLSSettingsExtension(AccountTLSSettings):
    certificate = Setting(type=Path, default=tls_certificate, nillable=True)
    verify_server = Setting(type=bool, default=ServerConfig.verify_server)

class AccountExtension(SettingsObjectExtension):
    enabled = Setting(type=bool, default=True)

    msrp = AccountMSRPSettingsExtension
    nat_traversal = AccountNATTraversalSettingsExtension
    rtp = AccountRTPSettingsExtension
    sip = AccountSIPSettingsExtension
    tls = AccountTLSSettingsExtension


class BonjourAccountExtension(SettingsObjectExtension):
    enabled = Setting(type=bool, default=False)



# General settings extensions

class AudioSettingsExtension(AudioSettings):
    input_device = Setting(type=str, default=None, nillable=True)
    output_device = Setting(type=str, default=None, nillable=True)
    sample_rate = Setting(type=SampleRate, default=16000)


log_directory = Path(ServerConfig.trace_dir) if ServerConfig.trace_dir else None
class LogsSettingsExtension(LogsSettings):
    directory = Setting(type=Path, default=log_directory)
    trace_sip = Setting(type=bool, default=ServerConfig.trace_sip)
    trace_msrp = Setting(type=bool, default=ServerConfig.trace_msrp)
    trace_pjsip = Setting(type=bool, default=False)
    trace_notifications = Setting(type=bool, default=ServerConfig.trace_notifications)


class RTPSettingsExtension(RTPSettings):
    port_range = Setting(type=PortRange, default=PortRange(RTPConfig.port_range.start, RTPConfig.port_range.end))
    timeout = Setting(type=NonNegativeInteger, default=RTPConfig.timeout)


def sip_port_validator(port, sibling_port):                                                                                                                                                  
    if port == sibling_port != 0:
        raise ValueError("the TCP and TLS ports must be different")

transport_list = []
if SIPConfig.local_udp_port:
    transport_list.append('udp')
if SIPConfig.local_tcp_port:
    transport_list.append('tcp')
if SIPConfig.local_tls_port:
    transport_list.append('tls')

udp_port = SIPConfig.local_udp_port or 0
tcp_port = SIPConfig.local_tcp_port or 0
tls_port = SIPConfig.local_tls_port or 0

class SIPSettingsExtension(SIPSettings):
    udp_port = Setting(type=Port, default=udp_port)
    tcp_port = CorrelatedSetting(type=Port, sibling='tls_port', validator=sip_port_validator, default=tcp_port)
    tls_port = CorrelatedSetting(type=Port, sibling='tcp_port', validator=sip_port_validator, default=tls_port)
    transport_list = Setting(type=SIPTransportList, default=transport_list)


ca_list = Path(ServerConfig.ca_file) if ServerConfig.ca_file and os.path.isfile(ServerConfig.ca_file) else None
class TLSSettingsExtension(TLSSettings):
    ca_list = Setting(type=Path, default=ca_list, nillable=True)


class SylkServerSettingsExtension(SettingsObjectExtension):
    user_agent = Setting(type=str, default='SylkServer-%s' % server_version)

    audio = AudioSettingsExtension
    logs = LogsSettingsExtension
    rtp = RTPSettingsExtension
    sip = SIPSettingsExtension
    tls = TLSSettingsExtension


