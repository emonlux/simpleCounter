import spydrnet as sdn
from spydrnet.uniquify import uniquify
from spydrnet_tmr.support_files.vendor_names import XILINX
from spydrnet_tmr.apply_tmr_to_netlist import apply_tmr_to_netlist
from spydrnet.util.selection import Selection
import sys
from spydrnet.util.architecture import XILINX_7SERIES


FILE_PATH = "testing.txt"
sys.stdout = open(FILE_PATH, "w")

netlist = sdn.parse("simpleCounter1.v",architecture=XILINX_7SERIES)

uniquify(netlist)

hinstances_to_replicate = list(
    netlist.get_hinstances(
        recursive=True, filter=lambda x: x.item.reference.is_leaf() is True
                                                    and "VCC" not in x.name 
                                                    and "GND" not in x.name
                                                    and "ibuf" not in x.name.lower()
                                                    and "IBUF" not in x.item.reference.name ))

# Removes the \ and space after instance names
for hinst in hinstances_to_replicate:
    if "\\" in hinst.name:
        update_name = hinst.item.name.replace("\\", "").replace(" ", "")
        hinst.item.name = update_name

hports_to_replicate = list(netlist.get_hports(filter = lambda x: x.item.direction is sdn.OUT))


for port in netlist.get_ports():
    if "\\" in port.name:
        update_name = port.name.replace("\\", "").replace(" ", "")
        port.name = update_name


for cable in netlist.get_cables():
    if "\\" in cable.name and not "const" in cable.name:
        update_name = cable.name.replace("\\", "").replace(" ", "")
        cable.name = update_name


valid_voter_point_dict = dict()


valid_voter_point_dict["after_ff"] = [
        *hinstances_to_replicate,
        *hports_to_replicate,
    ]


apply_tmr_to_netlist(
        netlist,
        XILINX,
        hinstances_and_hports_to_replicate=[
            *hinstances_to_replicate,
            *hports_to_replicate,
        ],
        valid_voter_point_dict=valid_voter_point_dict,
    )

for inst in netlist.get_instances():
    if "count" in inst.name or "led" in inst.name or "FSM" in inst.name:
        inst.name = ''.join(("\\", inst.name, " "))

for port in netlist.get_ports():
    if "FSM" in port.name:
        port.name = ''.join(("\\", port.name, " "))

for cable in netlist.get_cables():
    if "count" in cable.name or "FSM" in cable.name:
        if "VOTER" in cable.name:
            cable.name = ''.join(("\\", cable.name, "_wire "))
        else:
            cable.name = ''.join(("\\", cable.name, " "))
    if "f1" in cable.name or "f2" in cable.name or "one_shot" in cable.name:
        if "VOTER" in cable.name:
            cable.name = ''.join((cable.name, "_wire"))
    if "led" in cable.name and "VOTER" in cable.name:
        cable.name = ''.join(("\\",cable.name, "_wire "))


netlist.compose("simpleCounter_tmr1.v")


# "primitive_library_name": "SDN.verilog_primitives",

for library in netlist.get_libraries():
    for defintion in library.get_definitions():
        if "debounceCounter" in defintion.name or "simpleCounter" in defintion.name:
            print("\n",defintion.name)
            for instance in library.get_instances():
                print("\t",instance.name)
                for port in instance.get_pins(selection=Selection.OUTSIDE):
                    print("\t\t",port.inner_pin.port.name,port.inner_pin.port.direction)


