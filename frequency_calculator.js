/**
 * Meshtastic Frequency Slot Calculator - JavaScript Version
 * 
 * Copyright 2025 Pete Stephenson
 * 
 * This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
 * 
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

// LoRa region frequency parameters
// Based on Meshtastic firmware and regional regulations
// REFERENCE: https://meshtastic.org/docs/configuration/region-by-country/
const REGION_FREQUENCIES = {
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
};

/**
 * Get bandwidth in kHz based on channel name
 * @param {string} channelName - The channel name
 * @returns {number} Bandwidth in kHz
 */
function getBandwidthKhz(channelName) {
    if (channelName === "ShortTurbo") {
        return 500;
    } else if (channelName === "LongMod" || channelName === "LongSlow") {
        return 125;
    } else {
        return 250; // Default bandwidth
    }
}

/**
 * Calculate the total number of frequency slots
 * @param {number} freqStart - Start frequency in MHz
 * @param {number} freqEnd - End frequency in MHz
 * @param {number} spacing - Spacing in MHz
 * @param {number} bw - Bandwidth in kHz
 * @returns {number} Number of frequency slots
 */
function calculateNumFreqSlots(freqStart, freqEnd, spacing, bw) {
    return Math.floor((freqEnd - freqStart) / (spacing + (bw / 1000)));
}

/**
 * Hash function: djb2 by Dan Bernstein
 * Emulates the 32-bit unsigned integer behavior from the C++ implementation
 * @param {string} s - String to hash
 * @returns {number} Hash value
 */
function hashString(s) {
    let hashValue = 5381;
    
    for (let i = 0; i < s.length; i++) {
        // Use Math.imul for proper 32-bit multiplication and >>> 0 for unsigned conversion
        hashValue = (Math.imul(hashValue, 33) + s.charCodeAt(i)) >>> 0;
    }
    
    return hashValue;
}

/**
 * Determine the frequency slot from the channel name
 * @param {string} channelName - The channel name
 * @param {number} numFreqSlots - Number of frequency slots
 * @returns {number} Frequency slot (0-based)
 */
function determineFrequencySlot(channelName, numFreqSlots) {
    return hashString(channelName) % numFreqSlots;
}

/**
 * Calculate the frequency using the formula from the firmware
 * @param {number} freqStart - Start frequency in MHz
 * @param {number} frequencySlot - Frequency slot (0-based)
 * @param {number} bw - Bandwidth in kHz
 * @returns {number} Calculated frequency in MHz
 */
function calculateFrequency(freqStart, frequencySlot, bw) {
    return freqStart + (bw / 2000) + (frequencySlot * (bw / 1000));
}

/**
 * Main frequency slot calculation function
 * @param {string} region - LoRa region code
 * @param {string} channelName - Channel name
 * @param {number|null} customBandwidth - Custom bandwidth in kHz (optional)
 * @returns {Object} Calculation results
 */
function calculateFrequencySlot(region, channelName, customBandwidth = null) {
    // Validate region
    if (!REGION_FREQUENCIES.hasOwnProperty(region)) {
        return {
            error: `Invalid region '${region}' specified.`,
            availableRegions: Object.keys(REGION_FREQUENCIES).map(key => ({
                code: key,
                description: REGION_FREQUENCIES[key].description
            }))
        };
    }
    
    const regionParams = REGION_FREQUENCIES[region];
    
    // Determine bandwidth
    const bw = customBandwidth !== null ? customBandwidth : getBandwidthKhz(channelName);
    
    // Use region-specific frequency parameters
    const freqStart = regionParams.freq_start;
    const freqEnd = regionParams.freq_end;
    const spacing = regionParams.spacing;
    
    // Calculate the number of LoRa channels in the region
    const numFreqSlots = calculateNumFreqSlots(freqStart, freqEnd, spacing, bw);
    
    // Determine the frequency slot
    const frequencySlot = determineFrequencySlot(channelName, numFreqSlots);
    
    // Calculate the frequency
    const freq = calculateFrequency(freqStart, frequencySlot, bw);
    
    return {
        region: region,
        regionDescription: regionParams.description,
        frequencyRange: `${freqStart} - ${freqEnd} MHz`,
        channelName: channelName,
        numFreqSlots: numFreqSlots,
        frequencySlot: frequencySlot + 1, // Convert to 1-based for display
        selectedFrequency: freq,
        bandwidth: bw
    };
}

// Export for Node.js if available, otherwise make globally available
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        calculateFrequencySlot,
        REGION_FREQUENCIES,
        getBandwidthKhz,
        calculateNumFreqSlots,
        hashString,
        determineFrequencySlot,
        calculateFrequency
    };
} else {
    // Make functions globally available for browser use
    window.MeshtasticFrequencyCalculator = {
        calculateFrequencySlot,
        REGION_FREQUENCIES,
        getBandwidthKhz,
        calculateNumFreqSlots,
        hashString,
        determineFrequencySlot,
        calculateFrequency
    };
}
