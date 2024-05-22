import asyncio

from asyncua import Client

url = "opc.tcp://localhost:4840/freeopcua/server/"
namespace = "http://examples.freeopcua.github.io"


async def main():

    print(f"Connecting to {url} ...")
    async with Client(url=url) as client:
        # Find the namespace index
        nsidx = await client.get_namespace_index(namespace)
        print(f"Namespace Index for '{namespace}': {nsidx}")

        #Values from FMU
        var_names=['T1_in', 'm1_in', 'T2_in', 'm2_in', 'T2_out', 'm2_out', 'T1_out', 'm1_out', 'K', 'T1_ini', 'T2_ini', 'cp1', 'cp2', 'm1', 'm2', 'time']
        
        for var_name in var_names:
            # Get the variable node for read / write
            var = await client.nodes.root.get_child(
                f"0:Objects/{nsidx}:MyObject/{nsidx}:{var_name}"
            )
            value = await var.read_value()
            print(f"Value of {var_name} ({var}): {value}")


        


        # new_value = value - 50
        # print(f"Setting value of MyVariable to {new_value} ...")
        # await var.write_value(new_value)

        # Calling a method
        # res = await client.nodes.objects.call_method(f"{nsidx}:ServerMethod", 5)
        # print(f"Calling ServerMethod returned {res}")


if __name__ == "__main__":
    asyncio.run(main())