import asyncio
import random
import time

async def generate_fake_adsb_data(writer):
    while True:
        # Generate a fake SBS message
        sbs_message = create_fake_sbs_message()
        writer.write((sbs_message + '\n').encode('utf-8'))
        await writer.drain()
        await asyncio.sleep(1)  # Adjust the frequency as needed

def create_fake_sbs_message():
    # Construct a fake SBS message
    message_type = 'MSG'
    transmission_type = '3'
    session_id = '1'
    aircraft_id = '1'
    hex_ident = ''.join(random.choices('0123456789ABCDEF', k=6))
    flight_id = '1'
    generated_date = time.strftime('%Y/%m/%d', time.gmtime())
    generated_time = time.strftime('%H:%M:%S.%f', time.gmtime())[:-3]
    logged_date = generated_date
    logged_time = generated_time
    callsign = 'FAKE' + str(random.randint(100, 999)) + ' '
    altitude = str(random.randint(1000, 40000))
    ground_speed = str(random.randint(100, 500))
    track = str(random.randint(0, 359))
    latitude = str(random.uniform(-90, 90))
    longitude = str(random.uniform(-180, 180))
    vertical_rate = str(random.randint(-5000, 5000))
    squawk = '7000'
    alert = '0'
    emergency = '0'
    spi = '0'
    is_on_ground = '0'

    sbs_message = ','.join([
        message_type,
        transmission_type,
        session_id,
        aircraft_id,
        hex_ident,
        flight_id,
        generated_date,
        generated_time,
        logged_date,
        logged_time,
        callsign,
        altitude,
        ground_speed,
        track,
        latitude,
        longitude,
        vertical_rate,
        squawk,
        alert,
        emergency,
        spi,
        is_on_ground
    ])

    return sbs_message

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 30003)
    async with server:
        print("Fake ADS-B data generator is running on port 30003")
        await server.serve_forever()

async def handle_client(reader, writer):
    await generate_fake_adsb_data(writer)

if __name__ == '__main__':
    asyncio.run(main())
