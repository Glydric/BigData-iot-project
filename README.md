# BigData-iot-project

## Data from simulator example

```json
{
  "id": 1,
  "topic": "/sample.it/jz/device/snapshot/0000/edv/0502",
  "qos": 1,
  "properties": [1, 2, 35, 8, 9, 38, 3, 126, 11],
  "payload": {
    "t": 1702548733156,
    "tz": "2023-12-14T10:12:13.156Z",
    "uuid": "7a031921-e21b-4426-973f-541a36d3a813",
    "cuid": "7eb72645-aeba-4193-bcbf-0f810c10b652",
    "ref": "jzp://edv#0502.0000",
    "type": "gasmeter",
    "cat": "0631",
    "sn": 172,
    "m": [
      {
        "t": 1702548733157,
        "tz": "2023-12-14T10:12:13.157Z",
        "k": "coordinator",
        "d": "jzp://coo#ffffffff000004ff.0000",
        "v": 1,
        "u": ""
      },
      {
        "t": 1702548733157,
        "tz": "2023-12-14T10:12:13.157Z",
        "k": "ppm",
        "v": 376.4123,
        "u": ""
      },
      {
        "t": 1702548733158,
        "tz": "2023-12-14T10:12:13.158Z",
        "k": "rssi",
        "d": "jzp://coo#ffffffff000004ff.0000",
        "v": -103.8863,
        "u": "dB"
      },
      {
        "t": 1702548733158,
        "tz": "2023-12-14T10:12:13.158Z",
        "k": "device_temperature",
        "v": 25.0648,
        "u": "\u2103"
      },
      {
        "t": 1702548733158,
        "tz": "2023-12-14T10:12:13.158Z",
        "k": "battery_level",
        "v": 3.3861,
        "u": "V"
      }
    ]
  },
  "retain": false
}
```

### Explanation
m = measurements
sn = serial number?

t = timestamp
tz = timestamp in ISO format
k = kind
d = device?
v = value
u = unit