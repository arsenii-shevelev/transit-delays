# transit-delays

![CI](https://github.com/arsenii-shevelev/transit-delays/actions/workflows/ci.yml/badge.svg)

Live delays of Helsinki public transport. HSL publishes the position of every bus, tram and train
about once a second. This reads that feed and puts the positions into Kafka, so they can be
processed further. Python, Kafka, Docker.

## How it works

The ingester subscribes to HSL's MQTT feed, checks each message and sends it to the
`vehicle-positions` topic. The key is operator and vehicle number, like `22/1426`, so positions
of one vehicle always stay in order.

A few percent of messages get skipped. Some have no GPS fix and metro never sends its delay at all,
so metro isn't counted for now.

HSL sends the delay as an offset from the timetable, negative means late. In the code `delay`
flips it, so a late bus has a positive delay.

## Running it

Everything in Docker:

```
docker compose up --build
```

Or Kafka in Docker and the ingester on your machine (Python 3.14):

```
docker compose up kafka
pip install -r requirements.txt
python ingest.py
```

Tests:

```
pip install -r requirements-dev.txt
pytest                  # unit tests
pytest -m integration   # with a real Kafka, needs Docker
```

## Status

- [x] read the HSL feed
- [x] send positions to Kafka
- [ ] delays per line and stop
- [ ] store them in PostgreSQL
- [ ] API
- [ ] nightly check against the live feed

## Data

Vehicle positions come from [HSL / Digitransit](https://digitransit.fi/en/developers/apis/5-realtime-api/vehicle-positions/)
under CC BY 4.0.
