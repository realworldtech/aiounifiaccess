"""Device domain models."""

from __future__ import annotations

from aiounifiaccess.models.common import BaseAPIModel


class Device(BaseAPIModel):
    id: str = ""
    name: str = ""
    type: str = ""
    alias: str = ""
    ip: str = ""
    mac: str = ""
    firmware: str = ""
    version: str = ""
    online: bool = False
    start_time: int = 0
    location_id: str = ""
    connected_hub_id: str = ""


class AccessMethodSetting(BaseAPIModel):
    enabled: str = ""


class FaceSettings(BaseAPIModel):
    enabled: str = ""
    anti_spoofing_level: str = ""
    detect_distance: str = ""


class PinCodeSettings(BaseAPIModel):
    enabled: str = ""
    pin_code_shuffle: bool = False


class AccessMethods(BaseAPIModel):
    nfc: AccessMethodSetting = AccessMethodSetting()
    bt_tap: AccessMethodSetting = AccessMethodSetting()
    bt_button: AccessMethodSetting = AccessMethodSetting()
    bt_shake: AccessMethodSetting = AccessMethodSetting()
    mobile_wave: AccessMethodSetting = AccessMethodSetting()
    pin_code: PinCodeSettings = PinCodeSettings()
    face: FaceSettings = FaceSettings()
    wave: AccessMethodSetting = AccessMethodSetting()
    qr_code: AccessMethodSetting = AccessMethodSetting()
    touch_pass: AccessMethodSetting = AccessMethodSetting()


class AccessMethodSettings(BaseAPIModel):
    device_id: str = ""
    access_methods: AccessMethods = AccessMethods()
