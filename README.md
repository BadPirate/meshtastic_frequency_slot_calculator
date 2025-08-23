# meshtastic_frequency_slot_calculator
Calculates the frequency slot for a given Meshtastic channel name across different LoRa regions worldwide.

## Motivation

In the US region, Meshtastic uses the `LONG_FAST` [modem preset](https://meshtastic.org/docs/configuration/radio/lora/#modem-preset) by default. This works well in many areas, but I live in the San Francisco Bay Area which has many nodes and thus the [local group BayMe.sh](https://bayme.sh/) has recommended that users use the `MEDIUM_SLOW` preset instead to minimize network congestion.

[BayMe.sh provides instructions to set up one's node to use that configuration](https://bayme.sh/docs/getting-started/recommended-settings/) on the primary channel. If one keeps the [frequency slot](https://meshtastic.org/docs/configuration/radio/lora/#frequency-slot) set to the default value of `0`, Meshtastic will use a hash-based algorithm for determining the frequency slot corresponding to that channel name. However, it can be desirable to [use a private primary channel and the default as a secondary channel](https://meshtastic.org/docs/configuration/tips/#creating-a-private-primary-with-default-secondary). 

Unfortunately, there's a complication: Meshtastic uses the hash-based algorithm based only on the name of the [*primary channel*](https://meshtastic.org/docs/configuration/radio/channels/) and the number of frequency slots in that region. Put simply, both the primary and any secondary channels share the same frequency slot as the primary channel.

When a node is configured to use the default `LONG_FAST` modem preset, the default primary channel name is `LongFast`[^1]  In the US, the `LongFast` channel uses frequency slot `20` (906.875 MHz). If one uses a private primary channel with a different name and moves the default `LongFast` channel to a secondary channel, they need to explicitly set the frequency slot for the primary channel to `20` (for `LongFast`) in order to see the default traffic on the secondary channel.

I was interested in setting up a private primary channel and moving the defaults to a secondary channel, but I did not know the frequency slot for the `MediumSlow` channel (the name of the default channel for the `MEDIUM_SLOW` modem preset). Using `20` wouldn't work, since that's the slot for `LongFast`, not `MediumSlow`. In order to get the local `MediumSlow` traffic and participate in the mesh, I needed to know the frequency slot for the `MediumSlow` channel.

Fortunately, Meshtastic is open source and I was able to [read the source](https://github.com/meshtastic/firmware/blob/f6ed10f3298abf6896892ca7906d3231c8b3f567/src/mesh/RadioInterface.cpp) and implement the frequency slot calculation algorithm in python so I could calculate the slot for the `MediumSlow` channel. It turns out the slot for `MediumSlow` is `52`.

### Traps for New Players
Since the frequency slot value depends only on the channel name and the number of frequency slots in the region (104, in the US), it's possible calculate the frequency slot for any arbitrary channel name, even ones not associated with the built-in modem presets. However, ***the modem presets, channel names, and frequency slots all must exactly match those of other people one wishes to communicate with***.

For example, it's possible to configure your Meshtastic node to use the `LONG_FAST` modem preset[^2] with slot `52` (which correponds to the `MediumSlow` channel name), but that won't allow one to communicate with people using the `MEDIUM_SLOW` modem preset even if they are also using the `MediumSlow` channel name. I can't think of any reason why someone would *want* to do that, but I wanted to mention that it's possible in case someone accidentally does it and wonders why they can't communicate with anyone.

## Usage

### Basic Usage (US Region - Default)
```
python3 frequency_slot.py

Region: US (North America - 915 MHz ISM Band)
Frequency Range: 902.0 - 928.0 MHz
Channel Name: LongFast
Number of Frequency Slots: 104
Frequency Slot: 20
Selected Frequency: 906.875 MHz
Bandwidth: 250 kHz
```

### Custom Channel Name
```
python3 frequency_slot.py -n MediumSlow

Region: US (North America - 915 MHz ISM Band)
Frequency Range: 902.0 - 928.0 MHz
Channel Name: MediumSlow
Number of Frequency Slots: 104
Frequency Slot: 52
Selected Frequency: 914.875 MHz
Bandwidth: 250 kHz
```

### Different Regions
```
python3 frequency_slot.py --region EU_868 -n LongFast

Region: EU_868 (Europe - 868 MHz ISM Band)
Frequency Range: 863.0 - 870.0 MHz
Channel Name: LongFast
Number of Frequency Slots: 28
Frequency Slot: 20
Selected Frequency: 867.875 MHz
Bandwidth: 250 kHz
```

### View Available Regions
```
python3 frequency_slot.py --region help

Available LoRa regions:
  US: North America - 915 MHz ISM Band
  EU_868: Europe - 868 MHz ISM Band
  EU_433: Europe - 433 MHz ISM Band
  ANZ: Australia/New Zealand - 915 MHz ISM Band
  NZ_865: New Zealand - 865 MHz Band
  CN: China - 470-510 MHz Band
  JP: Japan - 920 MHz Band
  KR: Korea - 920 MHz Band
  TW: Taiwan - 920 MHz Band
  RU: Russia - 868 MHz Band
  IN: India - 865 MHz Band
  NP_865: Nepal - 865 MHz Band
  TH: Thailand - 920 MHz Band
  MY_919: Malaysia - 919 MHz Band
  MY_433: Malaysia - 433 MHz Band
  SG_923: Singapore - 923 MHz Band
  UA_868: Ukraine - 868 MHz Band
  UA_433: Ukraine - 433 MHz Band
```

### Command Line Options
```
usage: frequency_slot.py [-h] [--channel-name CHANNEL_NAME] [--bandwidth BANDWIDTH] [--region REGION]

Calculate Meshtastic channel frequency based on region and channel name.

options:
  -h, --help            show this help message and exit
  --channel-name, -n CHANNEL_NAME
                        Specify the channel name (default: 'LongFast').
  --bandwidth, -bw BANDWIDTH
                        Specify the bandwidth in kHz.
  --region, -r REGION   Specify the LoRa region (default: 'US'). Use --region help to see available
                        regions.
```

## Supported Regions

The calculator now supports 18 different LoRa regions based on the [Meshtastic region documentation](https://meshtastic.org/docs/configuration/region-by-country/):

- **US**: North America (902-928 MHz)
- **EU_868**: Europe 868 MHz Band (863-870 MHz)  
- **EU_433**: Europe 433 MHz Band (433-434.79 MHz)
- **ANZ**: Australia/New Zealand (915-928 MHz)
- **CN**: China (470-510 MHz)
- **JP**: Japan (920-928 MHz)
- **KR**: Korea (920-923 MHz)
- **TW**: Taiwan (920-925 MHz)
- **RU**: Russia (868.7-869.2 MHz)
- **IN**: India (865-867 MHz)
- **NP_865**: Nepal (865-867 MHz)
- **TH**: Thailand (920-925 MHz)
- **MY_919**: Malaysia 919 MHz (919-924 MHz)
- **MY_433**: Malaysia 433 MHz (433-435 MHz)
- **SG_923**: Singapore (920-925 MHz)
- **UA_868**: Ukraine 868 MHz (863-870 MHz)
- **UA_433**: Ukraine 433 MHz (433-434.79 MHz)
- **NZ_865**: New Zealand 865 MHz (864-868 MHz)

Each region uses the appropriate frequency parameters as defined by local regulations and Meshtastic firmware.

### Footnotes
[^1]: Although similarly named, the modem preset and channel name are different things entirely: the modem preset defines the bandwidth, spreading factor, and other parameters for the LoRa mdoem itself, while the channel name being essentially a chat room name.
[^2]: Or any valid, manually-configured modem settings.