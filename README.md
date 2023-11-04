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

*repository* - Mandatory needed to be tracked from crDroid repo for dt (common) and kernel  
*target_path* - Path where to clone repo  
*branch* - Defaults to branch of **crdroid** remote from [default.xml](https://github.com/crdroidandroid/android) manifest, however can use different one from tracked repo  
*remote* - Defaults to **github** remote from [default.xml](https://github.com/crdroidandroid/android) manifest, however can use different one from remote list  
  
***Note 1***: *Branch* and *remote* should not be set if using default defined values (ex: with *crDroid 10*, branch is default to *14.0* while remote is *github*)  
***Note 2***: As per rules, repos need to be tracked from crDroid or LOS Github or GitLab
