import asyncio
import subprocess
import datetime
import logging
import socket
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DUMP1090_EXECUTABLE = './external/dump1090/dump1090'  # Path to dump1090 executable
DUMP1090_ARGS = ['--net', '--quiet']  # Arguments for dump1090

DUMP1090_HOST = '127.0.0.1'  # dump1090 network host
DUMP1090_PORT = 30003        # dump1090 network port (SBS format)

COT_HOST = '10.244.169.36'  # Replace with the IP address of your CoT device
COT_PORT = 8087         # CoT device listening port

def parse_sbs_message(message):
    """
    Parses an SBS message from dump1090 into a dictionary.
    """
    fields = message.strip().split(',')
    if len(fields) < 22:
        return None

    sbs_message = {
        'message_type': fields[0],
        'transmission_type': fields[1],
        'session_id': fields[2],
        'aircraft_id': fields[3],
        'hex_ident': fields[4],
        'flight_id': fields[5],
        'generated_date': fields[6],
        'generated_time': fields[7],
        'logged_date': fields[8],
        'logged_time': fields[9],
        'callsign': fields[10].strip() if fields[10] else None,
        'altitude': int(fields[11]) if fields[11] else None,
        'ground_speed': float(fields[12]) if fields[12] else None,
        'track': float(fields[13]) if fields[13] else None,
        'latitude': float(fields[14]) if fields[14] else None,
        'longitude': float(fields[15]) if fields[15] else None,
        'vertical_rate': int(fields[16]) if fields[16] else None,
        'squawk': fields[17],
        'alert': fields[18],
        'emergency': fields[19],
        'spi': fields[20],
        'is_on_ground': fields[21],
    }

    return sbs_message

def create_cot_event(sbs_message):
    """
    Converts an SBS message to a CoT XML event, including altitude and ICAO code with the icon.
    """
    if not sbs_message['hex_ident'] or sbs_message['latitude'] is None or sbs_message['longitude'] is None:
        return None  # Insufficient data to create CoT event

    # Format times in ISO 8601
    time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    stale = (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # Generate UID and extract position data
    uid = f"ICAO-{sbs_message['hex_ident']}"
    lat = sbs_message['latitude']
    lon = sbs_message['longitude']
    hae = sbs_message['altitude'] * 0.3048 if sbs_message['altitude'] else 0  # Convert feet to meters
    ce = le = 9999999  # Circular and linear error estimates
    
    # Extract movement data
    course = sbs_message['track'] if sbs_message['track'] is not None else 0
    speed = (sbs_message['ground_speed'] * 0.514444) if sbs_message['ground_speed'] else 0  # Convert knots to m/s
    
    # Build the display callsign with ICAO code and altitude
    altitude_ft = sbs_message['altitude'] if sbs_message['altitude'] else "Unknown"
    callsign_display = f"{sbs_message['hex_ident']} Alt:{altitude_ft}ft"

    # Build the CoT XML message
    cot_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<event version="2.0" uid="{uid}" type="a-f-A" how="m-g" time="{time}" start="{time}" stale="{stale}">
    <point lat="{lat}" lon="{lon}" hae="{hae}" ce="{ce}" le="{le}"/>
    <detail>
        <contact callsign="{callsign_display}"/>
        <track course="{course}" speed="{speed}"/>
    </detail>
</event>'''
    return cot_xml

async def start_dump1090():
    """
    Starts dump1090 as an asynchronous subprocess.
    """
    process = await asyncio.create_subprocess_exec(
        DUMP1090_EXECUTABLE, *DUMP1090_ARGS,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    logger.info("dump1090 started")
    return process

async def stop_dump1090(process):
    """
    Stops the dump1090 subprocess gracefully.
    """
    process.terminate()
    try:
        await process.wait()
    except:
        process.kill()
    logger.info("dump1090 stopped")

async def main():
    """
    Main entry point for the script.
    """
    # Start dump1090
    dump1090_process = await start_dump1090()

    try:
        # Connect to dump1090
        while True:
            try:
                reader, writer = await asyncio.open_connection(DUMP1090_HOST, DUMP1090_PORT)
                logger.info("Connected to dump1090")
                break
            except ConnectionRefusedError:
                logger.info("Waiting for dump1090 to start...")
                await asyncio.sleep(1)  # Wait and retry connection

        # Set up UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Read ADS-B data and send CoT messages
        while True:
            data = await reader.readline()
            if not data:
                continue
            message = data.decode('utf-8').strip()
            if message:
                sbs_message = parse_sbs_message(message)
                if sbs_message:
                    cot_xml = create_cot_event(sbs_message)
                    if cot_xml:
                        sock.sendto(cot_xml.encode('utf-8'), (COT_HOST, COT_PORT))
    except Exception as e:
        logger.exception("An unexpected error occurred: %s", e)
    finally:
        await stop_dump1090(dump1090_process)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Program interrupted by user.")
    except Exception as e:
        logger.exception("An unexpected error occurred: %s", e)
    finally:
        pass  # Any additional cleanup can be done here
