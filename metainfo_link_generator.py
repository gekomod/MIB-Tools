import os
import sys
import stat
import subprocess
import shutil
import csv
from pprint import pprint
from pathlib import Path
from io import StringIO

# Ensure the script is run with Python 3
if sys.version_info[0] < 3:
    input("You need to run this script with Python 3!\nPress Enter to exit...")
    sys.exit(1)

# Install configparser if not already installed
try:
    import configparser
except ImportError:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'configparser'], stdout=subprocess.DEVNULL)
    import configparser

# Variants table in CSV format
VARIANT_TABLE = """Variant;Automaker;Vendor;Gen;Platform;Reg;Navi;Speech;DAB;MOST;part numbers;info
17201;VW;Technisat;MIB2;ZR;EU+RoW;no;;yes;;;MST2_EU_VW_ZR
17202;VW;Technisat;MIB2;ZR;EU+RoW;no;;no;;;MST2_EU_VW_ZR
17203;VW;Technisat;MIB2;ZR;EU+RoW;no;;no;;;MST2_EU_VW_ZR
17204;VW;Technisat;MIB2;ZR;EU+RoW;no;;yes;;;MST2_EU_VW_ZR
17205;VW;Technisat;MIB2;ZR;EU+RoW;no;;no;;;MST2_EU_VW_ZR
17206;VW;Technisat;MIB2;ZR;EU+RoW;yes;;yes;;;MST2_EU_VW_ZR
17207;VW;Technisat;MIB2;ZR;EU+RoW;yes;;no;;;MST2_EU_VW_ZR
17210;VW;Technisat;MIB2;;;;;;;;
17212;VW;Technisat;MIB2;;;;;;;;
17214;VW;Technisat;MIB2;PQ;EU+RoW;no;;yes;;;MST2_EU_VW_PQ
17215;VW;Technisat;MIB2;PQ;EU+RoW;no;;no;;;MST2_EU_VW_PQ
17216;VW;Technisat;MIB2;PQ;EU+RoW;yes;;yes;;;MST2_EU_VW_PQ
17217;VW;Technisat;MIB2;PQ;EU+RoW;yes;;no;;;MST2_EU_VW_PQ
17218;VW;Technisat;MIB2;PQ;USA;no;;yes;;;MST2_US_VW_PQ
17220;VW;Technisat;MIB2;PQ;USA;yes;;yes;;;MST2_US_VW_PQ
17220;VW;Technisat;MIB2;;;;;;;;
17222;VW;Technisat;MIB2;PQ;CN;yes;;no;;;MST2_CN_VW_PQ
17223;VW;Technisat;MIB2;PQ;JP+KR;no;;no;;;MST2_RoA_VW_PQ
17224;VW;Technisat;MIB2;ZR;EU+RoW;yes;;no;;;MST2_EU_VW_ZR
17241;VW;Delphi;MIB2;;;;;;;;
17242;VW;Delphi;MIB2;;;;;;;;
17245;VW;Delphi;MIB2;;;;;;;;
17246;VW;Delphi;MIB2;;;;;;;;
17247;VW;Delphi;MIB2;;;;;;;;
17248;VW;Delphi;MIB2;;;;;;;;
17249;VW;Delphi;MIB2;;;;;;;;
17250;VW;Delphi;MIB2;;EU;yes;yes;;;3Q0 035 874 B;STD2Nav_EU_VW
17251;VW;Delphi;MIB2;;;;;;;;
17252;VW;Delphi;MIB2;;;;;;;;
17254;VW;Delphi;MIB2;;;;;;;;
17255;VW;Delphi;MIB2;;;;;;;;
17256;VW;Delphi;MIB2;;EU;no;no;;;;STD2_EU_VW
17257;VW;Delphi;MIB2;;EU;no;yes;;;;STD2Plus_EU_VW
17261;VW;Delphi;MIB2;;;;;;;;
17262;VW;Delphi;MIB2;ZR;EU;no;no;;;;MST2_EU_VW
17263;VW;Delphi;MIB2;ZR;EU;no;yes;;;;MST2_EU_VW
17264;VW;Delphi;MIB2;ZR;NAR;no;;;;;MST2_US_VW
17268;VW;Delphi;MIB2;ZR;EU;Yes;Yes;;;;MST2_EU_VW
17269;VW;Delphi;MIB2;ZR;NAR;Yes;;;;;MST2_US_VW
17270;VW;Delphi;MIB2;;;;;;;;
17271;VW;Delphi;MIB2;;;;;;;;
37201;Skoda;Technisat;MIB2;ZR;EU+RoW;;;yes;;;MST2_EU_SK_ZR
37202;Skoda;Technisat;MIB2;ZR;EU+RoW;;;no;;;MST2_EU_SK_ZR
37203;Skoda;Technisat;MIB2;;;;;;;;
37204;Skoda;Technisat;MIB2;ZR;EU+RoW;;;yes;;;MST2_EU_SK_ZR
37205;Skoda;Technisat;MIB2;ZR;EU+RoW;;;no;;;MST2_EU_SK_ZR
37206;Skoda;Technisat;MIB2;ZR;EU+RoW;yes;;yes;;;MST2_EU_SK_ZR
37207;Skoda;Technisat;MIB2;ZR;EU+RoW;yes;;no;;;MST2_EU_SK_ZR
37208;Skoda;Technisat;MIB2;;;;;;;;
37210;Skoda;Technisat;MIB2;PQ;EU+RoW;no;;no;;;MST2_EU_SK_PQ
37211;Skoda;Technisat;MIB2;PQ;EU+RoW;no;;yes;;;MST2_EU_SK_PQ
37212;Skoda;Technisat;MIB2;PQ;EU+RoW;yes;;no;;;MST2_EU_SK_PQ
37213;Skoda;Technisat;MIB2;PQ;EU+RoW;yes;;yes;;;MST2_EU_SK_PQ
37214;Skoda;Technisat;MIB2;ZR;CN;yes;;no;;;MST2_CN_SK_ZR
47201;Seat;Technisat;MIB2;ZR;EU+RoW;no;yes;yes;;;MST2_EU_SE_ZR
47202;Seat;Technisat;MIB2;ZR;EU+RoW;no;yes;no;;;MST2_EU_SE_ZR
47203;Seat;Technisat;MIB2;ZR;EU+RoW;yes;yes;yes;;;MST2_EU_SE_ZR
47204;Seat;Technisat;MIB2;ZR;EU+RoW;yes;yes;no;;;MST2_EU_SE_ZR
47205;Seat;Technisat;MIB2;;;;;;;;
47206;Seat;Technisat;MIB2;PQ;EU+RoW;no;;yes;;;MST2_EU_SE_PQ
47207;Seat;Technisat;MIB2;PQ;EU+RoW;no;;no;;;MST2_EU_SE_PQ
47208;Seat;Technisat;MIB2;PQ;EU+RoW;yes;;yes;;;MST2_EU_SE_PQ
47209;Seat;Technisat;MIB2;PQ;EU+RoW;yes;;no;;;MST2_EU_SE_PQ
47210;Seat;Technisat;MIB2;;;;;;;;
47213;Seat;Technisat;MIB2;ZR;EU+RoW;no;;yes;;;MST2_EU_SE_ZR
47214;Seat;Technisat;MIB2;ZR;EU+RoW;yes;;yes;;;MST2_EU_SE_ZR
;;;;;;;;;;;
?;Skoda;Panasonic;MIB1;;EU;yes;?;yes;;5E0 035 874 A;MSTD_EU_SK
?;Skoda;Technisat;MIB2;;EU;no;yes?;?;;5Q0 035 840 A;MST2_EU_SK_ZR
?;VW;Technisat;MIB2;;EU;yes;yes;no;;3Q0 035 846;
?;VW;Delphi;MIB2;;EU;yes;yes;no;;3Q0 035 846;
?;VW;;MIB2;;;no;;;;3Q0 035 819 A;
?;VW;;MIB2;;;no;;;;3Q0 035 820 A;
?;VW;Delphi;MIB2;;;;;no?;;3Q0 035 864 A;
?;VW;Delphi;MIB2;;;;;;;3Q0 035 864 B;
?;VW;;MIB2;;;;;yes?;;3Q0 035 874 A;
?;VW;Delphi;MIB2;;;;;;;3Q0 035 874 B;
?;VW;Delphi;MIB2;;;;;;;3Q0 035 874 C;
"""

def load_variant_table(variant):
    reader = csv.DictReader(StringIO(VARIANT_TABLE), delimiter=';')
    """Loads a variants table from CSV."""
    variant_data = {}

    for row in reader:
        if row['Variant'] == variant:  # Skip blank lines
            variant_data[row['Variant']] = row
            # View Variant Information
            print(f"Variant: {row['Variant']}")
            print(f"  Automaker: {row['Automaker']}")
            print(f"  Vendor: {row['Vendor']}")
            print(f"  Gen: {row['Gen']}")
            print(f"  Platform: {row['Platform']}")
            print(f"  Region: {row['Reg']}")
            print(f"  Navi: {'Yes' if row['Navi'] == 'yes' else 'No'}")
            print(f"  Speech: {'Yes' if row['Speech'] == 'yes' else 'No'}")
            print(f"  DAB: {'Yes' if row['DAB'] == 'yes' else 'No'}")
            print(f"  MOST: {row['MOST']}")
            print(f"  Part Numbers: {row['part numbers']}")
            print(f"  Info: {row['info']}")
            print("-" * 40)

    return variant_data
    #return {row['Variant']: row for row in reader if row}

def get_variant_info(variant_table, variant):
    """Retrieves variant information from a table."""
    return variant_table.get(variant, {})

def replace_number_in_file(config, old_number, new_number):
    """Replaces all occurrences of old_number with new_number in the configuration."""
    for section in config.sections():
        for option, value in config.items(section):
            if old_number in value:
                new_value = value.replace(old_number, new_number)
                config.set(section, option, new_value)

def main():
    # Use default filename or user-supplied one
    default_file = "metainfo2.txt"
    input_file = sys.argv[1] if len(sys.argv) > 1 else default_file

    # Check if file exists
    if not Path(input_file).exists():
        input(f"\nERROR! Cannot find {input_file}. Press Enter to exit...")
        sys.exit(1)

    # Ask user to convert region
    us = input("\nConvert US(NAR)/CN/JP/KR(RoW) to EU unit? Enter 'y' for yes, or just press Enter for no: ").strip().lower()
    is_conversion_needed = us in {"y", "yes"}

    # Ask user to change number
    replace_number = input("\nDo you want to replace a number in the file? Enter 'y' for yes, or just press Enter for no: ").strip().lower()
    if replace_number in {"y", "yes"}:
        old_number = input("Enter the number you want to replace: ").strip()
        new_number = input(f"Enter the new number to replace '{old_number}': ").strip()

    # Load configuration from file
    print(f"Reading {input_file}...")
    config = configparser.ConfigParser()
    config.optionxform = str  # Keep letter case in options
    config.read(input_file)

    if len(config.sections()) == 0:
        input(f"\nERROR! Cannot read {input_file}. Press Enter to exit...")
        sys.exit(1)

    # Prepare new configuration
    config2 = configparser.ConfigParser()
    config2.optionxform = str

    # Load variant table
    variant_table = load_variant_table(new_number)

    variant_map = {
        "17204": "17208",
        "17205": "17213",
        "17206": "17210",
        "17207": "17212",
        "17214": "17218",
        "17215": "17223",
        "17216": "17220",
        "17217": "17222",
        "17225": "17221",
        "17226": "17219",
    }

    new_id = ""
    user_id = ""
    for section in config.sections():
        if not config2.has_section(section):
            config2.add_section(section)

            for option, value in config.items(section):
                if option == "RequiredVersionOfDM":
                   config2.set(section, option, '"0"')
                elif is_conversion_needed and option.startswith("Region") and value == '"Europe"':
                   config2.set(section, "Region", '"Europe"')
                   config2.set(section, "Region2", '"RoW"')
                   config2.set(section, "Region3", '"USA"')
                   config2.set(section, "Region4", '"CN"')
                elif is_conversion_needed and option.startswith("Variant") and value.strip('"') in variant_map:
                     new_variant = variant_map[value.strip('"')]
                     config2.set(section, option, f'"{new_variant}"')
                     # Download variant information
                     variant_info = get_variant_info(variant_table, new_variant)
                     if variant_info:
                         print(f"Variant {new_variant} info: {variant_info}")
                else:
                     config2.set(section, option, value)

                # Detect new ID for linking
                split_section = section.split("\\")
                if not new_id and len(split_section) == 5 and split_section[0] == "cpu" and split_section[1] == "customerupdateinfos":
                   new_id = split_section[2]
                   print(f"Found ID: {new_id}")
                   user_id = input("Enter SWDL HwVersion of your unit (see it in GEM>mibstd2_toolbox>mib_info): ").strip()
                   print(f"Linking ID: {user_id} to ID: {new_id}")

            if user_id and new_id and f"\\{new_id}\\" in section:
               new_section = section.replace(f"\\{new_id}\\", f"\\{user_id}\\")
               if not config2.has_section(new_section):
                  config2.add_section(new_section)
                  config2.set(new_section, "Link", f'"[{section}]"')

    # Replace number if required
    if replace_number in {"y", "yes"}:
        replace_number_in_file(config2, old_number, new_number)

    if is_conversion_needed:
        print("\nIMPORTANT! This metainfo2.txt can only be used for converting US(NAR)/CN/JP/KR(RoW) units to EU units!")
        print("Before starting the update, patch `tsd.mibstd2.system.swdownload` using mibstd2_toolbox>Tools to accept any metainfo2.txt.")

    # Make a backup copy of the original file
    backup_file = Path(input_file).with_suffix(".bak")
    shutil.copy(input_file, backup_file)
    print(f"Backup created: {backup_file}")

    # Save the updated configuration to a file
    with open(input_file, "w") as config_file:
        config2.write(config_file)

    os.chmod(input_file, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)

    input("\nDone. Press Enter to exit...")

if __name__ == "__main__":
    main()
