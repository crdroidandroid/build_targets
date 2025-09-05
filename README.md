# Repo usage
This repository is used to store **build targets** for automated builds.  
The server triggers builds based on information stored in `crdroid.dependencies`.

### Usage
To define a new build target, add an entry to `build_targets` using the format below:

```
<device> <build_type> <auto-upload> <saveimages>
```

### Field descriptions
- **`<device>`** → Device codename  
- **`<build_type>`** → One of `user`, `userdebug` or `eng`  
- **`<auto-upload>`** → `yes` or `no`  
  - when set to `yes`, the system automatically uploads the complete build and recovery to SourceForge  
- **`<saveimages>`** → Array of images to preserve, e.g. `[boot.img, vendor_boot.img]`

### Dependencies
Each device to be built must have its **`crdroid.dependencies`** file properly configured.  
> ⚠️ Cloning via `vendor.sh` call (`git clone`) is not allowed.
  
### Example format
```json
[
  {
    "repository": "crdroidandroid/android_device_oem_codename",
    "target_path": "device/oem/codename",
    "branch": "specific branch",
    "remote": "specific from manifest"
  }
]
```

### Field descriptions

`repository` → Required. Must point to the repo tracked from the crDroid organization for device trees (dt, common) and kernel

`target_path` → Required. Destination path where the repo will be cloned

`branch` → Optional. Defaults to the branch of the crdroid remote from the default.xml

`remote` → Optional. Defaults to github remote from the default.xml

### Notes

1. Branch & remote defaults
    - Do not set `branch` or `remote` if using default values.
    - Example: For *crDroid 16*, the branch defaults to `16.0` and the remote defaults to `github`.
2. Repository sources
    - Device trees, kernels and addons must be tracked from crDroid’s GitHub or GitLab.
    - Hardware or smaller dependencies may be tracked from LineageOS.
3. Device acceptance
    - A device will only be officially accepted after two or three quality builds.
    - This requirement helps prevent "bot-like" maintainers.
