import subprocess
import platform
import time


last_temp = None
last_temp_time = 0


def get_mac_temp():
    """Fetch CPU temperature using istats."""
    global last_temp, last_temp_time

    # update temp once per second
    if time.time() - last_temp_time < 1 and last_temp is not None:
        return last_temp
    try:
        # Try istats first
        output = subprocess.check_output(["istats", "cpu"], encoding="utf-8")
        temp_line = [line for line in output.split("\n") if "CPU temp" in line]
        if temp_line:
            celsius = float(temp_line[0].split(
                ":")[1].strip().replace("°C", ""))
            fahrenheit = (celsius * 9/5) + 32
            last_temp = f"{fahrenheit:.1f}°F"
            last_temp_time = time.time()
            return last_temp

        # Fallback to ioreg
        output = subprocess.check_output(
            ["ioreg", "-c", "AppleSMC"], encoding="utf-8")
        temp_line = [line for line in output.split("\n") if "CPU Die" in line]
        if temp_line:
            temp_value = ''.join(
                filter(str.isdigit, temp_line[0]))  # Extract numbers
            celsius = int(temp_value) / 100  # Convert to Celsius
            fahrenheit = (celsius * 9/5) + 32  # Convert to Fahrenheit
            last_temp = f"{fahrenheit:.1f}°F"
            last_temp_time = time.time()
            return last_temp
    except Exception:
        return "N/A"
    return "N/A"

# print("CPU Temp:", get_mac_temp())


def get_cpu_temp():
    """Fetch CPU Temperature (macOS-specific)"""
    if platform.system() == "Darwin":  # macOS
        return get_mac_temp()
    return "N/A"


print(f"CPU Temp: {get_mac_temp()}")
