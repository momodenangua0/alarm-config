# Alarm Config

Alarm Config is a custom Home Assistant integration that provides a Lovelace card to manage responsible people for alarm notifications.

## Features

- Lovelace card (`custom:alarm-config-card`) to manage a newline-separated list of responsible people
- Backend storage via Home Assistant services
- Sensor entity with attributes reflecting the saved list

## Installation (HACS)

1. In HACS, add this repository as a Custom Repository (type: Integration).
2. Install "Alarm Config" and restart Home Assistant.
3. Add the integration to `configuration.yaml`:

```yaml
alarm_config:
```

4. Restart Home Assistant again if needed.
5. Add the Lovelace card:

```yaml
type: custom:alarm-config-card
entity: sensor.alarm_config_responsible_people
```

## Services

- `alarm_config.set_responsible_people`
- `alarm_config.clear_responsible_people`

## Notes

The list is stored in the sensor attributes as `people` and `people_raw`.
