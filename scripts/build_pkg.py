#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess

CONTENT_ID = "IV0000-PS4APP000_00-PS4APPMANAGER000"
PASSCODE = "00000000000000000000000000000000"
OO_SDK = os.environ.get("OO_PS4_TOOLCHAIN", "/tmp/oo_root/usr/lib/OpenOrbisSDK")

def create_pkg():
    print("Preparing PKG staging directory...")
    os.makedirs("build/pkg_staging/sce_sys", exist_ok=True)
    os.makedirs("build/pkg_staging/sce_module", exist_ok=True)

    # Copy binary and system files
    shutil.copy("build/eboot.bin", "build/pkg_staging/eboot.bin")
    shutil.copy("assets/param.sfo", "build/pkg_staging/sce_sys/param.sfo")
    shutil.copy("assets/icon0.png", "build/pkg_staging/sce_sys/icon0.png")

    for mod in ["libc.prx", "libSceFios2.prx"]:
        mod_src = f"{OO_SDK}/bin/data/modules/{mod}"
        if os.path.exists(mod_src):
            shutil.copy(mod_src, f"build/pkg_staging/sce_module/{mod}")

    gp4_content = f'''<?xml version="1.0"?>
<psproject xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" fmt="gp4" version="1000">
  <volume>
    <volume_type>pkg_ps4_app</volume_type>
    <volume_id>PS4VOLUME</volume_id>
    <volume_ts>2018-01-30 04:20:11</volume_ts>
    <package content_id="{CONTENT_ID}" passcode="{PASSCODE}" storage_type="digital50" app_type="full" />
    <chunk_info chunk_count="1" scenario_count="1">
      <chunks>
        <chunk id="0" layer_no="0" label="Chunk #0" />
      </chunks>
      <scenarios default_id="0">
        <scenario id="0" type="sp" initial_chunk_count="1" label="Scenario #0">0</scenario>
      </scenarios>
    </chunk_info>
  </volume>
  <files img_no="0">
    <file targ_path="eboot.bin" />
    <file targ_path="sce_sys/param.sfo" />
    <file targ_path="sce_sys/icon0.png" />
    <file targ_path="sce_module/libc.prx" />
    <file targ_path="sce_module/libSceFios2.prx" />
  </files>
  <rootdir>
    <dir targ_name="sce_sys" />
    <dir targ_name="sce_module" />
  </rootdir>
</psproject>'''

    with open("build/pkg_staging/project.gp4", "w") as f:
        f.write(gp4_content)

    print("Building PKG with PkgTool.Core...")
    pkgtool_bin = f"{OO_SDK}/bin/linux/PkgTool.Core"
    env = os.environ.copy()
    env["DOTNET_SYSTEM_GLOBALIZATION_INVARIANT"] = "1"
    env["LD_LIBRARY_PATH"] = f"/tmp/ssl1.1:{env.get('LD_LIBRARY_PATH', '')}"

    os.makedirs("build/pkg", exist_ok=True)
    orig_cwd = os.getcwd()
    os.chdir("build/pkg_staging")
    res = subprocess.run([pkgtool_bin, "pkg_build", "project.gp4", "../pkg"], env=env)
    os.chdir(orig_cwd)

    if res.returncode != 0:
        print("PkgTool.Core failed!")
        sys.exit(1)

    output_pkg = f"build/pkg/{CONTENT_ID}.pkg"
    target_pkg = "build/PS4-App-Manager.pkg"
    if os.path.exists(output_pkg):
        shutil.copy(output_pkg, target_pkg)
        print(f"Successfully generated {target_pkg}")
    else:
        print("Expected output PKG not found!")
        sys.exit(1)

if __name__ == "__main__":
    create_pkg()
