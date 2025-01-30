# Adding IPs

The platform is modular and is able to support several monitoring IPs.
In this section we discuss how to add support for additional hardware IPs.
We will consider an IP named `monitor` regardless of its threat or execution model.
To learn how to define a new threat model, see [adding_models.md](adding_models.md).

Three steps are required:

- Add the HDL files of the IP under ips/monitor and a Flist.monitor file containing with relative paths of the HDL files.
- Add a class extending the Wrapper abstract class in tb/wrappers.py and define the functions specific to our specific `monitor` ip and add it to the `supported_ips` dictionnary.
- Define a test in tb/entry.py named `test_monitor_ip` where we define the path to hardware components, the high-level parameters of the IP and the sets of value for each parameters.

Once this is done you can test the integration of `monitor` with:

```bash
make run ip=monitor bmarks=hello_world
```
