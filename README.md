# Repo usage
This repo is used to store build targets for automated builds  
Server builds off info stored in crdroid.dependencies

### Usage
Add to build_targets based on below info
```
<device> <build_type> <auto-upload> <upload-recovery>
```
Description:
```
<device> - device codename  
<build_type> - user/userdebug/eng  
<auto-upload> - yes/no (this autouploads complete build and recovery to SF)  
<upload-recovery> - yes/no (upload recovery to SF)
```

### Dependencies
Each device that's built, needs to have crdroid.dependencies set properly.  
*Note that you are not allowed to clone via vendor call (git clone).*
  
Format:
```
[
  {
    "repository": "crdroidandroid/android_device_oem_codename",
    "target_path": "device/oem/codename",
    "branch": "specific branch",
    "remote": "specific from manifest"
  }
]
```
