"""
Copyright 2025 Pete Stephenson

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
"""

import math
import argparse

# REFERENCE1 https://github.com/meshtastic/firmware/blob/f6ed10f3298abf6896892ca7906d3231c8b3f567/src/mesh/RadioInterface.cpp
# REFERENCE2 https://github.com/meshtastic/meshtastic/blob/2ec6cb1ebd819baaf64ea9b00c7bde0b59d24160/docs/about/overview/radio-settings.mdx - table in the "Presets" section.
# REFERENCE3 https://meshtastic.org/docs/configuration/region-by-country/

# LoRa region frequency parameters
# Based on Meshtastic firmware and regional regulations
REGION_FREQUENCIES = {
    "US": {
        "freq_start": 902.0,
        "freq_end": 928.0,
        "spacing": 0,
        "description": "North America - 915 MHz ISM Band"
    },
    "EU_868": {
        "freq_start": 863.0,
        "freq_end": 870.0,
        "spacing": 0,
        "description": "Europe - 868 MHz ISM Band"
    },
    "EU_433": {
        "freq_start": 433.0,
        "freq_end": 434.79,
        "spacing": 0,
        "description": "Europe - 433 MHz ISM Band"
    },
    "ANZ": {
        "freq_start": 915.0,
        "freq_end": 928.0,
        "spacing": 0,
        "description": "Australia/New Zealand - 915 MHz ISM Band"
    },
    "NZ_865": {
        "freq_start": 864.0,
        "freq_end": 868.0,
        "spacing": 0,
        "description": "New Zealand - 865 MHz Band"
    },
    "CN": {
        "freq_start": 470.0,
        "freq_end": 510.0,
        "spacing": 0,
        "description": "China - 470-510 MHz Band"
    },
    "JP": {
        "freq_start": 920.0,
        "freq_end": 928.0,
        "spacing": 0,
        "description": "Japan - 920 MHz Band"
    },
    "KR": {
        "freq_start": 920.0,
        "freq_end": 923.0,
        "spacing": 0,
        "description": "Korea - 920 MHz Band"
    },
    "TW": {
        "freq_start": 920.0,
        "freq_end": 925.0,
        "spacing": 0,
        "description": "Taiwan - 920 MHz Band"
    },
    "RU": {
        "freq_start": 868.7,
        "freq_end": 869.2,
        "spacing": 0,
        "description": "Russia - 868 MHz Band"
    },
    "IN": {
        "freq_start": 865.0,
        "freq_end": 867.0,
        "spacing": 0,
        "description": "India - 865 MHz Band"
    },
    "NP_865": {
        "freq_start": 865.0,
        "freq_end": 867.0,
        "spacing": 0,
        "description": "Nepal - 865 MHz Band"
    },
    "TH": {
        "freq_start": 920.0,
        "freq_end": 925.0,
        "spacing": 0,
        "description": "Thailand - 920 MHz Band"
    },
    "MY_919": {
        "freq_start": 919.0,
        "freq_end": 924.0,
        "spacing": 0,
        "description": "Malaysia - 919 MHz Band"
    },
    "MY_433": {
        "freq_start": 433.0,
        "freq_end": 435.0,
        "spacing": 0,
        "description": "Malaysia - 433 MHz Band"
    },
    "SG_923": {
        "freq_start": 920.0,
        "freq_end": 925.0,
        "spacing": 0,
        "description": "Singapore - 923 MHz Band"
    },
    "UA_868": {
        "freq_start": 863.0,
        "freq_end": 870.0,
        "spacing": 0,
        "description": "Ukraine - 868 MHz Band"
    },
    "UA_433": {
        "freq_start": 433.0,
        "freq_end": 434.79,
        "spacing": 0,
        "description": "Ukraine - 433 MHz Band"
    }
}

# Default frequency parameters for backward compatibility
freq_start = 902.0      # MHz
freq_end = 928.0        # MHz
spacing = 0
bw = 250                # default, unless altered by some preset names

def get_region_parameters(region):
    """Get frequency parameters for the specified region."""
    if region not in REGION_FREQUENCIES:
        print(f"Error: Invalid region '{region}' specified.")
        print("\nAvailable regions:")
        for reg, params in REGION_FREQUENCIES.items():
            print(f"  {reg}: {params['description']}")
        return None
    return REGION_FREQUENCIES[region]

def get_bandwidth_khz(channel_name):
    """Determine the bandwidth in kHz based on channel name."""
    if channel_name == "ShortTurbo":
        return 500
    elif channel_name in ["LongMod", "LongSlow"]:
        return 125
    else:
        return 250  # Default bandwidth
    
def calculate_num_freq_slots(freq_start, freq_end, spacing, bw):
    """Calculate the total number of frequency slots."""
    return math.floor((freq_end - freq_start) / (spacing + (bw / 1000)))
    
# Hash function: djb2 by Dan Bernstein
# See REFERENCE1 @ L395.
def hash_string(s):
    hash_value = 5381
    mask = 0xFFFFFFFF # 32-bit mask to emulate uint32_t behavior
    for c in s:
        hash_value = (((hash_value << 5) + hash_value) + ord(c))  # hash * 33 + c
        hash_value &= mask # Mask to 32 bits.
    return hash_value

def determine_frequency_slot(channel_name, num_freq_slots):
    """Determine the frequency slot from the channel name."""
    return hash_string(channel_name) % num_freq_slots

def calculate_frequency(freq_start, frequency_slot, bw):
    """Calculate the frequency using the new formula."""
    return freq_start + (bw / 2000) + (frequency_slot * (bw / 1000))

def print_results(channel_name, region, num_freq_slots, frequency_slot, freq, bw, region_params):
    """Print results"""
    print(f"Region: {region} ({region_params['description']})")
    print(f"Frequency Range: {region_params['freq_start']} - {region_params['freq_end']} MHz")
    print(f"Channel Name: {channel_name}")
    print(f"Number of Frequency Slots: {num_freq_slots}")
    # See REFERENCE1 @ L552 and L584
    # frequency_slot is actually (frequency_slot - 1), since modulus (%) returns values from 0 to (numFrequencySlots - 1)
    print(f"Frequency Slot: {frequency_slot + 1}") 
    print(f"Selected Frequency: {freq} MHz")
    print(f"Bandwidth: {bw} kHz")

def main():
    # Argument parser setup.
    parser = argparse.ArgumentParser(description="Calculate Meshtastic channel frequency based on region and channel name.")
    parser.add_argument("--channel-name", "-n", type=str, default="LongFast",
                    help="Specify the channel name (default: 'LongFast').")
    parser.add_argument("--bandwidth", "-bw", type=int, 
                    help="Specify the bandwidth in kHz.")
    parser.add_argument("--region", "-r", type=str, default="US",
                    help="Specify the LoRa region (default: 'US'). Use --region help to see available regions.")
    args = parser.parse_args()
    
    # Handle help request for regions
    if args.region == "help":
        print("Available LoRa regions:")
        for reg, params in REGION_FREQUENCIES.items():
            print(f"  {reg}: {params['description']}")
        return
    
    # Get region parameters
    region_params = get_region_parameters(args.region)
    if region_params is None:
        return  # Error already printed
    
    # Get the channel name from arguments.
    channel_name = args.channel_name
    if args.bandwidth is not None:
        bw = args.bandwidth
    else:
        bw = get_bandwidth_khz(channel_name)

    # Use region-specific frequency parameters
    region_freq_start = region_params["freq_start"]
    region_freq_end = region_params["freq_end"]
    region_spacing = region_params["spacing"]

    # Calculate the number of LoRa channels in the region.
    num_freq_slots = calculate_num_freq_slots(region_freq_start, region_freq_end, region_spacing, bw)

    # Determine the frequency slot.
    frequency_slot = determine_frequency_slot(channel_name, num_freq_slots)

    # Calculate the frequency.
    freq = calculate_frequency(region_freq_start, frequency_slot, bw)
    
    # Print results
    print_results(channel_name, args.region, num_freq_slots, frequency_slot, freq, bw, region_params)

# Entry point
if __name__ == "__main__":
    main()
