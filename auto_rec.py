import sounddevice as sd

# デバイス名で検索してみる
device_name = "USB PnP Sound Device"  # arecordで表示されたデバイス名を使う
devices = sd.query_devices()
device_id = None

for idx, device in enumerate(devices):
    if device_name in device['name']:
        device_id = idx
        break

if device_id is not None:
    print(f"Using device ID: {device_id}")
else:
    print("Device not found")

# デバイスIDが見つかったら、これを使って録音
if device_id is not None:
    sd.default.device = device_id
    duration = 5  # 秒
    fs = 44100  # サンプルレート
    print(f"Recording on device {device_id}")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    print("Recording finished")
else:
    print("USB microphone not found")
