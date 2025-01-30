# Adding models

Different threat models might be addressed by the IPs supported by the platform, e.g. security monitoring or trace generation.
The oracle is built based on the tested IP and takes as input the name of the application to run.
Applications are discussed in [adding_software](adding_software.md).
In this section we discuss how to add support for additional models.

Two steps are required:

- Add a class extending the Oracle abstract class in tb/oracle.py and define the functions specific to the model to verify the output of th IP or end the test early.
- If you already have an IP for this threat model, you can link them in the supported_ips dictionnary in tb/oracle.py.
