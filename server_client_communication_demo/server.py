import asyncio
import logging

from asyncua import Server, ua
from asyncua.common.methods import uamethod


import pyfmi
import numpy as np
from matplotlib import pyplot as plt

@uamethod
def func(parent, value):
    return value * 2



@uamethod
def func(parent, T1_ini,T2_ini):
    return T1_ini,T2_ini


def get_variable_names_from_fmu(fmu):
    model_variables = fmu.get_model_variables()
    print(model_variables)
    variable_names = fmu.get_model_variables().keys()
    return variable_names

    


async def main():
    _logger = logging.getLogger(__name__)
    #Load FMUs
    pth = "../fmus/"
    fnm = "hex_delta.fmu"
    fmu = pyfmi.load_fmu(pth+fnm)



    # setup our server
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    
    
    # set up our own namespace, not really necessary but should as spec
    uri = "http://examples.freeopcua.github.io"
    idx = await server.register_namespace(uri)

    # populating our address space
    # server.nodes, contains links to very common nodes like objects and root
    myobj = await server.nodes.objects.add_object(idx, "MyObject")
    t1_ini = await myobj.add_variable(idx, "T1_ini,", '')
    t2_ini = await myobj.add_variable(idx, "T2_ini", '')

    #Putting Variables from FMU to OPC Variables and making that writable for Client side

    fmu_variables=get_variable_names_from_fmu(fmu)
    opc_variables=[]
    for v in fmu_variables:

        opc_var=await myobj.add_variable(idx, v, float(fmu.get(v)))
        opc_variables.append(opc_var)
        # Set MyVariable to be writable by clients
        await opc_var.set_writable()

        
    await server.nodes.objects.add_method(
        ua.NodeId("ServerMethod", idx),
        ua.QualifiedName("ServerMethod", idx),
        func,
        [ua.VariantType.Int64],
        [ua.VariantType.Int64],
    )
    _logger.info("Starting server!")
    async with server:
        while True:
            await asyncio.sleep(1)
            for variable_name_from_opc in opc_variables:
                fmu_value_stored_in_opc = await variable_name_from_opc.get_value()
                value = fmu_value_stored_in_opc
                print(variable_name_from_opc.get_variables(),value)
            # _logger.info("Set value of %s to %.1f", myvar, new_val)
            # await myvar.write_value(new_val)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main(), debug=True)