from datetime import datetime, timezone

from positions import parse_position

BUS = (
    b'{"VP":{"desi":"57","dir":"2","oper":22,"veh":1426,"tst":"2026-10-20T09:48:59.256Z","tsi":1792489739,'
    b'"spd":0.00,"hdg":69,"lat":60.217129,"long":24.981056,"acc":0.00,"dl":-405,"odo":7347,"drst":1,'
    b'"oday":"2026-10-20","jrn":1187,"line":74,"start":"12:21","loc":"GPS","stop":1270104,"route":"1057","occu":0}}'
)

NO_GPS = (
    b'{"VP":{"desi":"78","dir":"1","oper":22,"veh":1203,"tst":"2026-10-20T09:48:59.251Z","tsi":1792489739,'
    b'"spd":null,"hdg":null,"lat":null,"long":null,"acc":null,"dl":161,"odo":36,"drst":1,"oday":"2026-10-20",'
    b'"jrn":1814,"line":109,"start":"12:51","loc":"ODO","stop":1020113,"route":"1078","occu":0}}'
)

METRO = (
    b'{"VP":{"desi":"M1","dir":"1","oper":50,"veh":320,"tst":"2026-10-20T09:48:59Z","tsi":1792489739,'
    b'"spd":12.27,"hdg":82,"lat":60.175141464,"long":24.805418641,"acc":null,"dl":null,"odo":null,"drst":null,'
    b'"oday":"2026-10-20","start":"12:33","loc":"MAN","stop":null,"route":"31M1","occu":0,"seq":1}}'
)


def test_parses_bus_position():
    position = parse_position(BUS)

    assert position.line == "57"
    assert position.direction == 2
    assert position.operator == 22
    assert position.vehicle == 1426
    assert position.timestamp == datetime(2026, 10, 20, 9, 48, 59, 256000, tzinfo=timezone.utc)
    assert position.latitude == 60.217129
    assert position.longitude == 24.981056
    assert position.stop == 1270104


def test_negative_offset_means_late():
    assert parse_position(BUS).delay == 405


def test_skips_position_without_gps():
    assert parse_position(NO_GPS) is None


def test_skips_position_without_delay():
    assert parse_position(METRO) is None


def test_skips_broken_message():
    assert parse_position(b'{"VP":') is None
    assert parse_position(b"not json") is None
