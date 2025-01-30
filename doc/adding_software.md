# Adding software

Additional applications can be added to the platform and classified in different categories.
This is interesting especially when dealing with a particular execution model and specialized applications.
We will consider an application named `app`.

The following steps are required:

- Add a folder sw/app containing all C files and headers of the app.
- In sw/sources.mk, add `app` in the list of __bmarks.
- If applicable, add it to another list of __special_bmarks, for which you can define a specific compilation rule in sw/Makefile.
- Add it in sw/applications.json and specify its type: a legitimate or special application.

You can now test `app` on an IP:

```bash
make run ip=<your ip> bmarks=app
```
